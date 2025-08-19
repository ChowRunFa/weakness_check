from flask import Flask
from flask_cors import CORS
from flasgger import Swagger

app = Flask(__name__)

# 配置 Swagger
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/apispec_1.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/swagger/"
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "施工方案审核系统 API",
        "description": "基于RAG技术的建设工程施工方案缺陷检查系统",
        "version": "1.0.0",
        "contact": {
            "name": "API支持",
            "email": "wtqiu@qq.com"
        }
    },
    # "host": "59.77.7.24:5001",
    "basePath": "/",
    "schemes": ["http", "https"],
    "tags": [
        {
            "name": "施工方案审核",
            "description": "施工方案文档上传、检索、审核相关接口"
        },
        {
            "name": "文件管理",
            "description": "文件列表、删除、上传文件夹管理接口"
        },
        {
            "name": "系统管理", 
            "description": "系统状态查询和管理接口"
        }
    ]
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

# 导入API蓝图
from apis.api_ra_check import api_ra_check

# 注册蓝图
app.register_blueprint(api_ra_check, url_prefix="/")

# 初始化CORS
cors = CORS(app, resources={r"/*": {"origins": "*"}})

if __name__ == '__main__':
    # app.run(port=5001, debug=False)
    app.run()


