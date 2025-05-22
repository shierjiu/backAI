# 数科智测平台后端项目（test-platform-backend）

## 项目结构

```

|-- test-platform-backend
    
    |-- AppName  // app名称
        |-- migrations  // 数据库变更相关记录
        |-- __init__.py  // app初始化文件
        |-- admin.py  // django后台管理文件
        |-- apps.py  // app配置文件
        |-- models.py  // app模型文件，数据库相关
        |-- scheduler.py // 定时器文件
        |-- serializers.py  // 序列化器文件
        |-- tests.py  // 单元测试文件
        |-- urls.py  // 路由管理文件
        |-- utils.py  // 业务函数文件
        |-- views.py  // 视图函数文件
        
    |-- Static  // 静态资源文件
        |-- Media  // 媒体资源文件，按app进行分类
        |-- Log  // 日志文件，按app进行分类
        
    |-- TestPlantform  // 项目资源文件
        |-- __init__.py  // 项目初始化文件
        |-- asgi.py  // 网关接口协议
        |-- renderers.py // DRF API的渲染器
        |-- settings.py  // 项目配置文件，数据库、app配置等均在其中
        |-- urls.py  // 项目总路由文件
        |-- wsgi.py  // 网关接口协议
    
    |-- .gitignore  // git忽略文件
    
    |-- manage.py  // 项目管理脚本
    
    |-- readme.py  // 项目描述文件
    
    |-- requirements.py  // python依赖包

```

## 更新说明

`V1.0.1.250331_beta`
- 待上线

`V1.0.0.250228_release`
- 测试用例生成app上线
- 接口用例生成app上线
- 菜单巡检app上线
- 通知推送app上线
