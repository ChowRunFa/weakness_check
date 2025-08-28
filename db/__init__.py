# -*- coding: utf-8 -*-
"""
数据库模块

提供数据库连接、模型定义、数据访问对象和管理工具
"""

# 数据库配置
from .config import DB_CONFIG, DatabaseConfig

# 数据库连接
from .connection import (
    get_connection, 
    return_connection, 
    get_db_connection,
    test_connection,
    initialize_database,
    close_connection_pool
)

# 基础模型
from .base_model import BaseModel

# 数据库模型
from .models import (
    AsyncTask,
    StructureCheckResult, 
    StructureCheckItem,
    DocumentReference,
    create_all_tables,
    drop_all_tables
)

# 数据访问对象
from .dao import (
    AsyncTaskDAO,
    StructureCheckDAO,
    DocumentDAO,
    ReportDAO
)

# 数据库管理器
from .manager import (
    DatabaseManager,
    db_manager,
    init_database,
    health_check,
    cleanup_database,
    get_database_stats,
    reset_database
)

__all__ = [
    # 配置
    'DB_CONFIG', 'DatabaseConfig',
    
    # 连接
    'get_connection', 'return_connection', 'get_db_connection',
    'test_connection', 'initialize_database', 'close_connection_pool',
    
    # 模型
    'BaseModel', 'AsyncTask', 'StructureCheckResult', 
    'StructureCheckItem', 'DocumentReference',
    'create_all_tables', 'drop_all_tables',
    
    # DAO
    'AsyncTaskDAO', 'StructureCheckDAO', 'DocumentDAO', 'ReportDAO',
    
    # 管理器
    'DatabaseManager', 'db_manager', 'init_database', 
    'health_check', 'cleanup_database', 'get_database_stats', 'reset_database'
]
