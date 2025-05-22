# AiEvaluationy/utils.py
import json
from typing import Any, Dict, Tuple, Callable
import requests
from openai import OpenAI


# -------------------------------------------------
# 通用 AI 服务
# -------------------------------------------------
class GenericAIService:
    """
    统一负责：
      1. 发送 HTTP 请求（支持流式）
      2. 用实体配置的 response_function 把原始响应 → answer
    """
    SAFE_BUILTINS = {
        "json": json,
        "len": len,
        "str": str,
        "int": int,
        "float": float,
        "bool": bool,
        "list": list,
        "dict": dict,
        "tuple": tuple,
        "set": set,
        "print": print,  # 调试用
    }

    @classmethod
    def send(cls, cfg: Dict[str, Any]) -> Tuple[Any, str]:
        """
        返回 (raw_response, error_msg)
        raw_response: bytes / dict / str   按 stream 与否决定
        error_msg   : None 表示成功
        """
        try:
            resp = requests.request(
                method=cfg["method"],
                url=cfg["url"],
                headers=cfg.get("headers"),
                json=cfg.get("body"),
                timeout=cfg.get("timeout", 30),
                stream=cfg.get("stream", False)
            )
            resp.raise_for_status()

            if cfg.get("stream", False):
                # 直接把迭代器返回给解析函数以节省内存
                return resp.iter_lines(), None
            else:
                # 非流式就转 json / text
                try:
                    return resp.json(), None
                except ValueError:
                    return resp.text, None

        except Exception as e:
            return None, f"请求失败: {str(e)}"

    # ------------  受限执行  -------------

    @classmethod
    def _compile_func(cls, code_str: str) -> Callable:
        """
        把单行或多行 Python 代码包裹成函数:
        输入 raw_response, cfg        输出 answer:str
        示例代码（前端传）:
            answer = raw_response["choices"][0]["message"]["content"]
        """
        wrapper = f"def _user_fn(raw_response, cfg):\n"
        for line in code_str.splitlines():
            wrapper += f"    {line}\n"
        # 若用户忘了赋值 answer，默认转 str
        wrapper += "\n    return locals().get('answer', str(raw_response))\n"

        loc = {}
        exec(compile(wrapper, "<response_function>", "exec"), {}, loc)
        return loc["_user_fn"]

    @classmethod
    def _safe_exec(cls, func: Callable, raw_response: Any, cfg: Dict[str, Any]) -> Tuple[str, str]:
        """
        运行用户代码，限制内置函数，返回 (answer, error)
        """
        try:
            # 创建受限全局环境
            safe_globals = {"__builtins__": cls.SAFE_BUILTINS}
            result = func(raw_response, cfg)
            return str(result), None
        except Exception as e:
            return "", f"解析失败: {str(e)}"

    # ------------  主入口 -------------

    @classmethod
    def get_answer(cls, cfg: Dict[str, Any]) -> Dict[str, Any]:
        """
        高层封装：一步到位 -> {"answer": "..."} 或 {"error": "..."}
        """
        raw_resp, err = cls.send(cfg)
        if err:
            return {"error": err}

        # 编译/缓存 response_function
        rfunc_code = (cfg.get("response_function") or "").strip()
        if not rfunc_code:
            # 默认策略：尝试常见 JSON 路径
            return {"answer": cls._default_parse(raw_resp)}

        try:
            compiled = cls._compile_func(rfunc_code)
        except SyntaxError as e:
            return {"error": f"response_function 语法错误: {e}"}

        answer, p_err = cls._safe_exec(compiled, raw_resp, cfg)
        return {"answer": answer} if not p_err else {"error": p_err}

    # -------- 默认兜底解析 --------

    @staticmethod
    def _default_parse(raw_resp: Any) -> str:
        """
        尝试在 ChatGPT/OpenAI 格式 或 text 中提取
        """
        if isinstance(raw_resp, (dict,)):
            # OpenAI style
            content = (
                raw_resp.get("choices", [{}])[0]
                    .get("message", {})
                    .get("content")
            )
            if content:
                return content
            return json.dumps(raw_resp, ensure_ascii=False)
        elif isinstance(raw_resp, (str, bytes)):
            return raw_resp.decode() if isinstance(raw_resp, bytes) else raw_resp
        else:
            return str(raw_resp)


class AIAgentServer(object):

    def __init__(self, agent_config: dict, user_content:str):
        self.agent_config = agent_config
        self.user_content = user_content
        self.__agent_config_init()

    def __agent_config_init(self):
        self.agent_config["temperature"] = float(self.agent_config["temperature"])
        self.agent_config["max_token"] = int(self.agent_config["max_token"])

    def agent_server_stream(self):
        """流式返回"""
        if self.agent_config["model"]["type"] == "SDK(OpenAI)":
            client = OpenAI(api_key=self.agent_config["model"]["key"],base_url=self.agent_config["model"]["url"])
            res = client.chat.completions.create(model=self.agent_config["model"]["model"],messages=[{"role": "system", "content": self.agent_config["system_content"]},{"role": "user", "content": self.user_content}],temperature=self.agent_config["temperature"],max_tokens=self.agent_config["max_token"],stream=True,)
            for chunk in res:
                if chunk.choices[0].finish_reason == "stop":
                    break
                delta = chunk.choices[0].delta
                if hasattr(delta, "content") and delta.content:
                    yield f"{delta.content}\n\n"


    def agent_server(self):
        """非流式返回"""
        if self.agent_config["model"]["type"] == "SDK(OpenAI)":
            client = OpenAI(api_key=self.agent_config["model"]["key"],base_url=self.agent_config["model"]["url"])
            res = client.chat.completions.create(model=self.agent_config["model"]["model"],messages=[{"role": "system", "content": self.agent_config["system_content"]},{"role": "user", "content": self.user_content}],temperature=self.agent_config["temperature"],max_tokens=self.agent_config["max_token"],stream=False,)
            return res.choices[0].message.content
