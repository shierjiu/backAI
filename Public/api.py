# Public/api.py
import os
import mimetypes
from urllib.parse import quote
from django.http import FileResponse
from django.core.files.storage import default_storage
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.text import get_valid_filename
from rest_framework.response import Response
# ----------------------------------------
# 通用：数据集附件上传 / 下载
# ----------------------------------------
def dataset_file_upload(request, dataset_model, dataset_id):
    """
    上传文件并绑定到数据集.dataset.file。
    如果该数据集已绑定文件，则：
    1) 删除旧存储文件；
    2) 复用原来的 AiEvaluationFile 记录。
    但如果当前数据集节点有子节点（父节点），则禁止上传。
    """
    file_obj = request.FILES.get("file")
    if not file_obj:
        return api_response(status=400, message="缺少上传文件 file")

    # 1. 校验数据集
    try:
        dataset = dataset_model.objects.get(id=dataset_id)
    except dataset_model.DoesNotExist:
        return api_response(status=404, message=f"数据集 ID={dataset_id} 不存在")

    # 1.1 如果是父节点（存在子节点），则拒绝上传
    if dataset.children.exists():
        return api_response(status=200, message="当前节点存在子节点，不能上传文件")

    # 2. 构造保存路径
    sub_dir = os.path.join("ai_evaluation", str(dataset_id))
    # 2.1 构造新文件名：使用数据集节点的 name + 原始后缀
    orig_ext = os.path.splitext(file_obj.name)[1]            # 获取扩展名，如 ".xlsx"
    base_name = f"{dataset.name}{orig_ext}"                  # 例如 "我的数据集.xlsx"
    safe_name = get_valid_filename(base_name)                # 清洗文件名
    save_path = default_storage.save(os.path.join(sub_dir, safe_name), file_obj)

    # 3. 创建 / 更新 AiEvaluationFile 记录
    from AiEvaluationy.models import AiEvaluationFile

    if dataset.file:  # 已有附件 → 删除旧文件并更新记录
        old_rec = dataset.file
        try:
            if default_storage.exists(old_rec.file):
                default_storage.delete(old_rec.file)
        except Exception:
            pass
        old_rec.name = safe_name
        old_rec.file = save_path
        old_rec.save(update_fields=["name", "file"])
        file_record = old_rec
    else:  # 新建附件记录
        file_record = AiEvaluationFile.objects.create(
            name=safe_name,
            file=save_path,
        )

    # 4. 绑定到数据集
    dataset.file = file_record
    dataset.save(update_fields=["file"])

    return api_response(
        status=200,
        message="文件上传成功（如有旧文件已替换）",
        data={
            "dataset_id": dataset_id,
            "file_id": file_record.id,
            "path": save_path,
            "name": safe_name
        },
    )
def dataset_file_download(dataset_model, dataset_id):
    """
    下载数据集附件：保持原始文件扩展名不丢失
    """
    # 1. 数据集校验
    try:
        dataset = dataset_model.objects.select_related("file").get(id=dataset_id)
    except dataset_model.DoesNotExist:
        return api_response(status=404, message=f"数据集 ID={dataset_id} 不存在")

    if not dataset.file:
        return api_response(status=404, message="该数据集未绑定任何文件")

    # 2. 路径 & 文件名
    file_path = dataset.file.file                       # 存储路径
    if not default_storage.exists(file_path):
        return api_response(status=404, message="文件不存在或已被删除")

    filename = dataset.file.name or os.path.basename(file_path)  # NEW: 使用记录里的 name 字段
    content_type, _ = mimetypes.guess_type(filename)
    if not content_type:
        content_type = "application/octet-stream"

    # 3. 生成响应
    fh   = default_storage.open(file_path, "rb")
    resp = FileResponse(fh, as_attachment=True, filename=filename, content_type=content_type)  # NEW

    # 一些旧浏览器不识别 filename*= → 同时保留两种写法
    quoted = quote(filename)
    resp["Content-Disposition"] = (
        f'attachment; filename="{quoted}"; filename*=UTF-8\'\'{quoted}'
    )
    print("DEBUG‑filename:", filename)
    return resp


def api_response(status=200, data=None, message=None):
    """
    api格式化返回
    :param status: response status
    :param data: response data["data"]
    :param message: response data["message"]
    """
    if 100 <= status <= 199:
        code = "info"
    elif 200 <= status <= 299:
        code = "success"
    elif 300 <= status <= 399:
        code = "warning"
    else:
        code = "error"
    response = {
        'code': code,
        'message': message,
        'data': data
    }
    return Response(status=status, data=response)

def pagination_query(cls, cls_serializer, request):
    """
    分页查询接口
    :param cls: model
    :param cls_serializer: serializer
    :param request: {"pageEnable": Ture,"pageSize": 20,"pageNum": 1,"pageRule": [{"field": "agent_group","rule": "is","value": 1},{...}]}
    :return: api_response
    """
    page_enable = request.data.get('pageEnable', True)  # 是否分页
    page_size = request.data.get('pageSize', 20)  # 分页大小
    page_number = request.data.get('pageNum', 1)  # 分页页码
    page_rule = request.data.get('pageRule', None)  # 查询规则

    query = Q()  # 初始化空的查询条件
    if page_rule:
        for rule in page_rule:
            field = rule.get('field')
            rule_type = rule.get('rule')
            value = rule.get('value')

            if field and value:
                if rule_type == 'is':  # 精确匹配
                    query &= Q(**{field: value})
                elif rule_type == 'contains':  # 模糊匹配
                    query &= Q(**{f"{field}__icontains": value})
                elif rule_type == 'gt':  # 大于
                    query &= Q(**{f"{field}__gt": value})
                elif rule_type == 'lt':  # 小于
                    query &= Q(**{f"{field}__lt": value})
                elif rule_type == 'gte':  # 大于等于
                    query &= Q(**{f"{field}__gte": value})
                elif rule_type == 'lte':  # 小于等于
                    query &= Q(**{f"{field}__lte": value})
                elif rule_type == 'in':  # 在列表中
                    query &= Q(**{f"{field}__in": value})
                elif rule_type == 'startswith':  # 以...开头
                    query &= Q(**{f"{field}__startswith": value})
                elif rule_type == 'endswith':  # 以...结尾
                    query &= Q(**{f"{field}__endswith": value})
                else:
                    return api_response(status=400, message=f"字段 {field} 查询条件 {rule_type} 错误")

    queryset = cls.objects.filter(query)  # 查询数据
    if page_enable:  # 分页情况
        paginator = Paginator(queryset, page_size)
        try:
            page_obj = paginator.page(page_number)
        except Exception as e:
            return api_response(status=400, message=f"页码 {page_number} 不存在")
        serializer = cls_serializer(page_obj.object_list, many=True)  # 序列化分页器
        data = {
            "total": paginator.count,
            "pageSize": page_size,
            "pageNum": page_number,
            "data": serializer.data
        }
    else:  # 不分页情况
        serializer = cls_serializer(queryset, many=True)
        data = {
            "total": queryset.count(),
            "data": serializer.data
        }
    return api_response(status=200, data=data, message="查询成功")

def tree_query(cls, cls_serializer):
    """
    树形结构查询接口
    :param cls: model
    :param cls_serializer: serializer
    :return: api_response
    """
    # 查询所有数据
    queryset = cls.objects.all()

    def build_tree(nodes):
        """构建树结构"""
        tree = []
        node_dict = {node.id: node for node in nodes}
        for node in nodes:
            if node.parent_id is None:  # 根节点
                tree.append(node)
            else:
                parent = node_dict.get(node.parent_id)
                if parent:
                    if not hasattr(parent, 'children'):
                        parent.children = []
                    parent.children.add(node)
        return tree

    # 构建树形结构
    tree = build_tree(queryset)
    # 序列化树形结构
    serializer = cls_serializer(tree, many=True)
    data = {
        "total": queryset.count(),
        "data": serializer.data
    }
    return api_response(status=200, data=data, message="查询成功")

def get_by_id(cls, cls_serializer, request):
    """
    按id查询
    :param cls: model
    :param cls_serializer: serializer
    :param request: ?id=1
    :return: api_response
    """
    if request.GET.get('id'):
        try:
            data = cls.objects.get(id=request.GET.get('id'))
            serializer = cls_serializer(data)
            return api_response(status=200, message="查询成功", data=serializer.data)
        except cls.DoesNotExist:
            return api_response(status=404, message=f"数据ID {request.GET.get('id')} 不存在")
        except Exception as e:
            return api_response(status=500, message=str(e))
    else:
        return api_response(status=400, message="缺少参数id")

def post_by_id(cls, cls_serializer, request):
    """
    按id修改（无id时新增）
    :param cls: model
    :param cls_serializer: serializer
    :param request: {"id":1, "field": "xxx", ...}
    :return: api_response
    """
    try:
        if request.data.get("id"):
            instance = cls.objects.get(id=request.data.get("id"))
            serializer = cls_serializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return api_response(status=200, message="修改成功", data=serializer.data)
        else:
            serializer = cls_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return api_response(status=200, message="新增成功", data=serializer.data)
    except Exception as e:
        return api_response(status=500, message=str(e))

def delete_by_id(cls, request):
    """
    按id删除
    :param cls: model
    :param request: ?id=1
    :return: api_response
    """
    if request.GET.get('id'):
        try:
            instance = cls.objects.get(id=request.GET.get('id'))
            instance.delete()
            return api_response(status=200, message="删除成功")
        except cls.DoesNotExist:
            return api_response(status=404, message="数据ID {request.GET.get('id')} 不存在")
        except Exception as e:
            return api_response(status=500, message=str(e))
    else:
        return api_response(status=400, message="缺少参数id")


