# import requests
# import os
#
#
# def test_excel_upload(file_path):
#     """
#     Test script to upload an existing Excel file to the Django API endpoint for data import.
#
#     Args:
#         file_path: Path to the Excel file to upload
#     """
#     # The correct API endpoint URL based on error message
#     # The actual path should be prefixed with one of the route patterns shown in the error
#     api_url = "http://localhost:8000/ai_evaluation/dataset/import"  # Changed from ai/ to ai_evaluation/
#
#     # Check if file exists
#     if not os.path.exists(file_path):
#         print(f"Error: File '{file_path}' not found")
#         return False
#
#     # Prepare file for upload
#     with open(file_path, 'rb') as file:
#         files = {'file': (os.path.basename(file_path), file,
#                           'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
#
#         # Send POST request
#         print(f"Uploading file '{file_path}' to {api_url}...")
#         response = requests.post(api_url, files=files)
#
#         # Check and print response
#         print(f"Status Code: {response.status_code}")
#         print(f"Response: {response.text}")
#
#         return response.status_code == 200
#
#
# if __name__ == "__main__":
#     # Path to your Excel file
#     excel_file_path = "test.xls"  # Update this to the actual path if necessary
#
#     success = test_excel_upload(excel_file_path)
#     if success:
#         print("✓ Test passed: Excel upload was successful")
#     else:
#         print("✗ Test failed: Excel upload encountered issues")
# import requests
#
#
# def create_prerequisite_data():
#     """Create the required objects in the database"""
#     # Base URL for your API
#     base_url = "http://localhost:8000/ai_evaluation/"
#
#     # 1. First, create a file if needed
#     file_payload = {
#         "name": "测试文件",
#         "file": "test.txt"  # This might need to be an actual file upload
#     }
#     resp = requests.post(f"{base_url}file/info", json=file_payload)
#     print(f"Creating file: {resp.status_code}, {resp.text}")
#     file_id = 1  # Assume ID 1 or extract from response
#
#     # 2. Create dataset nodes
#     datasets = ["场景题", "金融"]  # Add all dataset names from your Excel
#     for i, name in enumerate(datasets):
#         dataset_payload = {
#             "name": name,
#             "parent_id": f"dataset_{i}",
#             "file": file_id
#         }
#         resp = requests.post(f"{base_url}dataset/tree/info", json=dataset_payload)
#         print(f"Creating dataset '{name}': {resp.status_code}, {resp.text}")
#
#     # 3. Create tags
#     tags = ["日常", "金融"]  # Add all tag names from your Excel
#     for tag in tags:
#         tag_payload = {"name": tag}
#         resp = requests.post(f"{base_url}dataset/tag/info", json=tag_payload)
#         print(f"Creating tag '{tag}': {resp.status_code}, {resp.text}")
#
#     # 4. Create evaluation objects
#     eval_objects = ["官问", "机器人"]  # Add all object names from your Excel
#     for obj in eval_objects:
#         obj_payload = {
#             "name": obj,
#             "url": "http://example.com/api",
#             "method": "POST",
#             "header": "{}",
#             "body": "{}",
#             "stream": False,
#             "response_function": "return response.json()"
#         }
#         resp = requests.post(f"{base_url}evaluation/object/info", json=obj_payload)
#         print(f"Creating eval object '{obj}': {resp.status_code}, {resp.text}")
#
#
# if __name__ == "__main__":
#     create_prerequisite_data()
# import requests
# import os
#
#
# def test_excel_upload(file_path):
#     """
#     测试Excel文件上传到Django API端点
#     """
#     # API端点URL
#     api_url = "http://localhost:8000/ai_evaluation/dataset/import"
#
#     # 检查文件是否存在
#     if not os.path.exists(file_path):
#         print(f"错误: 找不到文件 '{file_path}'")
#         return False
#
#     # 准备上传文件
#     with open(file_path, 'rb') as file:
#         files = {'file': (os.path.basename(file_path), file,
#                           'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
#
#         # 发送POST请求
#         print(f"正在上传文件 '{file_path}' 到 {api_url}...")
#         response = requests.post(api_url, files=files)
#
#         # 检查并打印响应
#         print(f"状态码: {response.status_code}")
#         print(f"响应: {response.text}")
#
#         return response.status_code == 200
#
#
# if __name__ == "__main__":
#     # Excel文件路径
#     excel_file_path = "test.xls"  # 如果需要请更新为实际路径
#
#     success = test_excel_upload(excel_file_path)
#     if success:
#         print("✓ 测试通过: Excel上传成功")
#     else:
#         print("✗ 测试失败: Excel上传遇到问题")
import requests
import os
import json
import logging
import http.client as http_client

# === Enable detailed HTTP logging ===
http_client.HTTPConnection.debuglevel = 1
logging.basicConfig(level=logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

def test_excel_upload(file_path):
    api_url = "http://localhost:8000/ai_evaluation/dataset/import"
    if not os.path.exists(file_path):
        print(f"错误: 找不到文件 '{file_path}'")
        return False

    with open(file_path, 'rb') as f:
        files = {
            'file': (
                os.path.basename(file_path),
                f,
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        }
        print(f"正在上传 '{file_path}' …")
        try:
            resp = requests.post(api_url, files=files, timeout=30)
        except requests.RequestException as e:
            print("网络请求异常:", str(e))
            return False

    # 基本信息
    print("状态码:", resp.status_code)
    print("响应头:")
    for k, v in resp.headers.items():
        print(f"  {k}: {v}")

    # 解析并打印返回内容
    data = None
    try:
        data = resp.json()
        print("\n返回 JSON:")
        print(json.dumps(data, ensure_ascii=False, indent=2))
        # 如果有 errors 数组，则逐条打印
        if isinstance(data, dict) and "errors" in data:
            print("\n行级错误详情：")
            for err in data["errors"]:
                print("  -", err)
    except ValueError:
        print("\n返回文本:")
        print(resp.text)

    # 额外提示
    if resp.status_code == 200 and (not isinstance(data, dict) or "errors" not in data):
        print("\n注意：服务器返回文本，未解析到 JSON 错误列表。")

    return resp.status_code == 200

if __name__ == "__main__":
    # 替换成你实际的 Excel 文件名
    excel_file_path = "test.xlsx"
    success = test_excel_upload(excel_file_path)
    print("\n✅ 上传成功" if success else "\n❌ 上传失败")


