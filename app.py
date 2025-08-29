from flask import Flask, jsonify
from flask_cors import CORS
from flasgger import Swagger
import logging
import atexit

# 导入数据库模块
from db import init_database, health_check, close_connection_pool, db_manager

app = Flask(__name__)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

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
            "name": "异步结构检查",
            "description": "异步文档结构完整性检查接口"
        },
        {
            "name": "异步内容检查",
            "description": "异步内容检查接口"
        },
        {
            "name": "异步引用检查",
            "description": "异步引用检查接口"
        },
        {
            "name": "文件管理",
            "description": "文件列表、删除、上传文件夹管理接口"
        },
        {
            "name": "系统管理", 
            "description": "系统状态查询和管理接口"
        },
        {
            "name": "数据库管理",
            "description": "数据库健康检查和统计接口"
        }
    ]
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

# 导入API蓝图
from apis.api_ra_check import api_ra_check
from apis.api_async_structure_check import api_async_structure_check
from apis.api_content_check_async import api_content_check_async
from apis.api_cite_check_async import api_cite_check_async

# 注册蓝图
app.register_blueprint(api_ra_check, url_prefix="/")
app.register_blueprint(api_async_structure_check, url_prefix="/")
app.register_blueprint(api_content_check_async, url_prefix="/")
app.register_blueprint(api_cite_check_async, url_prefix="/")

# 初始化CORS
cors = CORS(app, resources={r"/*": {"origins": "*"}})

# 数据库管理API
@app.route('/api/database/health', methods=['GET'])
def database_health():
    """
    数据库健康检查接口
    ---
    tags:
      - 数据库管理
    responses:
      200:
        description: 数据库状态信息
        schema:
          type: object
          properties:
            status:
              type: string
              example: healthy
            database_connection:
              type: boolean
              example: true
            tables_exist:
              type: boolean
              example: true
            error_message:
              type: string
              example: null
    """
    try:
        health_info = health_check()
        status = "healthy" if health_info.get('database_connection') and health_info.get('tables_exist') else "unhealthy"
        
        return jsonify({
            "status": status,
            **health_info
        }), 200
        
    except Exception as e:
        logger.error(f"数据库健康检查失败: {str(e)}")
        return jsonify({
            "status": "error",
            "database_connection": False,
            "tables_exist": False,
            "error_message": str(e)
        }), 500

@app.route('/api/database/stats', methods=['GET'])
def database_stats():
    """
    获取数据库统计信息
    ---
    tags:
      - 数据库管理
    responses:
      200:
        description: 数据库统计信息
        schema:
          type: object
          properties:
            total_tasks:
              type: integer
              example: 100
            pending_tasks:
              type: integer
              example: 5
            completed_tasks:
              type: integer
              example: 90
            failed_tasks:
              type: integer
              example: 5
    """
    try:
        stats = db_manager.get_statistics()
        return jsonify(stats), 200
        
    except Exception as e:
        logger.error(f"获取数据库统计失败: {str(e)}")
        return jsonify({
            "error": str(e)
        }), 500

@app.route('/api/database/cleanup', methods=['POST'])
def database_cleanup():
    """
    清理数据库旧数据
    ---
    tags:
      - 数据库管理
    parameters:
      - name: days
        in: query
        type: integer
        default: 7
        description: 清理多少天前的数据
    responses:
      200:
        description: 清理结果
        schema:
          type: object
          properties:
            cleaned_tasks:
              type: integer
            cleaned_files:
              type: integer
            cleaned_records:
              type: integer
    """
    try:
        from flask import request
        days = request.args.get('days', 7, type=int)
        
        cleanup_result = db_manager.cleanup(days)
        return jsonify(cleanup_result), 200
        
    except Exception as e:
        logger.error(f"数据库清理失败: {str(e)}")
        return jsonify({
            "error": str(e)
        }), 500

# 应用初始化函数
def init_app():
    """初始化应用"""
    logger.info("开始初始化应用...")
    
    # 初始化数据库
    try:
        if init_database():
            logger.info("数据库初始化成功")
        else:
            logger.error("数据库初始化失败")
            raise Exception("数据库初始化失败")
    except Exception as e:
        logger.error(f"数据库初始化异常: {str(e)}")
        raise
    
    logger.info("应用初始化完成")

# 应用清理函数
def cleanup_app():
    """应用清理"""
    logger.info("开始清理应用资源...")
    try:
        close_connection_pool()
        logger.info("数据库连接池已关闭")
    except Exception as e:
        logger.error(f"清理应用资源时发生错误: {str(e)}")

# 注册应用清理函数
atexit.register(cleanup_app)

if __name__ == '__main__':
    try:
        # 初始化应用
        init_app()
        
        # 启动应用
        logger.info("启动Flask应用...")
        app.run(host='0.0.0.0', port=5000, debug=False)
        
    except Exception as e:
        logger.error(f"应用启动失败: {str(e)}")
        exit(1)


