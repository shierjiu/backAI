# AiEvaluationy/utils.py
import json, requests, textwrap

# ---------- 公共 Hook ----------
def exec_response_hook(hook: str, raw: dict) -> dict:
    """
    对原始响应 raw 执行实体表里的 response_function。
    - hook 代码必须给 result 变量赋值
    - 若出错则返回 {'error': ..., 'raw': raw}
    """
    ctx = {'raw': raw, 'result': None}
    try:
        exec(textwrap.dedent(hook), {}, ctx)
        return ctx['result'] if ctx['result'] is not None else raw
    except Exception as e:
        return {'error': f'response_function error: {e}', 'raw': raw}


# ---------- 第三方平台会话 ----------
class CozeService:
    @staticmethod
    def dynamic_chat(config: dict) -> dict:
        """
        统一封装 第三方聊天接口。

        - 先拿到“原始响应” raw（dict / 自定义结构）
        - 若 config 里提供了 response_function，则优先交给 hook 自定义解析：
            · hook 返回字典且没有 error → 直接作为最终结果
            · 否则回退到默认解析逻辑
        """
        try:
            r = requests.request(
                method=config["method"],
                url=config["url"],
                headers=config["headers"],
                json=config["body"],
                stream=config.get("stream", False),
            )
            r.raise_for_status()

            # -------- 收集原始响应 raw --------
            if config.get("stream"):
                raw_chunks, answer = [], ""
                for line in r.iter_lines():
                    if line:
                        seg = line.decode().split("data:", 1)[-1].strip()
                        if seg:
                            piece = json.loads(seg)
                            raw_chunks.append(piece)
                            answer += piece.get("content", "")
                raw = {"chunks": raw_chunks, "answer": answer}
            else:
                raw = r.json()

            # -------- 自定义 hook（优先）--------
            if config.get("response_function"):
                parsed = exec_response_hook(config["response_function"], raw)
                if parsed and not parsed.get("error"):   # hook 成功解析 → 直接返回
                    return parsed

            # -------- 默认解析逻辑 ------------
            if config.get("stream"):
                return {"answer": raw["answer"]}   # stream 场景
            else:
                return {
                    "answer": raw.get("messages", [{}])[-1].get("content"),
                    "metadata": raw.get("conversation_id"),
                }

        except Exception as e:
            return {'error': f'请求异常: {str(e)}'}
