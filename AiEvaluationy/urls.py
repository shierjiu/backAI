# AiEvaluationy/urls.py
from django.urls import path
from .views import *

urlpatterns = [


    # 批量按智能体组评测数据集并写入历史
    path('dataset/evaluate_by_agents', DatasetEvaluateByAgentsView.as_view(), name='EvaluateByAgents'),

    path('record/server', AiEvaluationRecordServer.as_view(), name='AiEvaluationRecordServer'),

    # 根据dataset的id获得文件列表
    path('dataset/file/list', AiEvaluationFileDatasetView.as_view(), name='AiEvaluationFileDatasetList'),
    path('file/list', AiEvaluationFileView.as_view(), name='AiEvaluationFileList'),
    path('file/info', AiEvaluationFileInfo.as_view(), name='AiEvaluationFileInfo'),
    #  创建多个节点的树
    path('dataset/tree', AiEvaluationDatasetTree.as_view(), name='AiEvaluationDatasetTree'),

    path('dataset/info', AiEvaluationDatasetInfo.as_view(), name='AiEvaluationDatasetInfo'),
    # path('dataset/tree/info', Ai_evaluation_datasetInfo.as_view(), name='Ai_evaluation_datasetInfo'),

    path('dataset/tag/list', AiEvaluationDatasetTagView.as_view(), name='AiEvaluationDatasetTagList'),
    path('dataset/tag/info', AiEvaluationDatasetTagInfo.as_view(), name='AiEvaluationDatasetTagInfo'),

    path('evaluation/object/list', AiEvaluationEntityView.as_view(), name='AiEvaluationEntityList'),
    path('evaluation/object/info', AiEvaluationEntityInfo.as_view(), name='AiEvaluationEntityInfo'),

    path('dataset/item/list', AiEvaluationDatasetEntryView.as_view(), name='AiEvaluationDatasetEntry'),
    path('dataset/item/info', AiEvaluationDatasetEntryInfo.as_view(), name='AiEvaluationDatasetEntry'),
    #历史记录
    path('evaluation/history/list', AiEvaluationRecordView.as_view(), name='AiEvaluationRecordList'),
    path('evaluation/history/info', AiEvaluationRecordInfo.as_view(), name='AiEvaluationRecordInfo'),
    # 开始评测的list

    # 详情的记录
    path('history/list', AiEvaluationHistoryList.as_view(), name='AiEvaluationHistoryList'),
    path('history/info', AiEvaluationHistoryInfo.as_view(), name='AiEvaluationHistoryInfo'),
    #历史记录详情
    path('evaluation/history/detail/list', AiEvaluationRecordEntryView.as_view(),name='AiEvaluationRecordEntryList'),
    path('evaluation/history/detail/info', AiEvaluationRecordEntryInfo.as_view(),name='AiEvaluationRecordEntryInfo'),

    # """excel 导入 """
    path('dataset/import', ExcelImportView.as_view(), name='import_dataset'),

    # 文件上传与下载
    path('dataset/file/upload', DatasetFileUploadView.as_view(), name='Dataset_file_upload'),

    path('dataset/file/download', DatasetFileDownloadView.as_view(), name='Dataset_file_download'),

    #  一键更新和评估
    # path('dataset/evaluate',DatasetEvaluateView.as_view(),name='AiEvaluationDatasetEvaluate'),
    path('dataset/evaluate', DatasetEvaluateView.as_view(), name='AiEvaluationDatasetEvaluate'),

]
