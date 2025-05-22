# MessageServer/utils.py
import requests
import markdown
from markdown.preprocessors import Preprocessor
from django.utils.safestring import mark_safe

def send_message(webhook, template):
    headers = {"Content-Type": "text/plain"}
    data = {"msgtype": "markdown", "markdown": {"content": template}}
    res = requests.post(url=webhook, headers=headers, json=data)
    return res.json()


class MarkdownVariableReplacer:
    """
    替换Markdown中的变量，保持原始Markdown格式

    使用示例:
    replacer = MarkdownVariableReplacer(get_value=get_value_function)
    processed_md = replacer.replace(markdown_text)
    """

    def __init__(self, get_value, start_delim='{{', end_delim='}}'):
        """
        初始化替换器

        :param get_value: 获取变量值的函数
        :param start_delim: 变量开始分隔符
        :param end_delim: 变量结束分隔符
        """
        self.get_value = get_value
        self.start_delim = start_delim
        self.end_delim = end_delim

    def replace(self, text):
        """
        替换文本中的变量占位符

        :param text: 包含变量的Markdown文本
        :return: 替换变量后的Markdown文本
        """
        lines = text.split('\n')
        processed_lines = []

        for line in lines:
            while self.start_delim in line and self.end_delim in line:
                start = line.find(self.start_delim)
                end = line.find(self.end_delim)
                if start < end:
                    var_name = line[start + len(self.start_delim):end].strip()
                    try:
                        var_value = str(self.get_value(var_name))
                    except Exception as e:
                        var_value = f"[Error: {str(e)}]"
                    line = line[:start] + var_value + line[end + len(self.end_delim):]
            processed_lines.append(line)

        return '\n'.join(processed_lines)