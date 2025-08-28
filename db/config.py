# -*- coding: utf-8 -*-
"""
数据库配置文件
"""
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class DatabaseConfig:
    """数据库配置类"""
    host: str
    port: int
    user: str
    password: str
    database: str
    charset: str = "utf8mb4"
    max_connections: int = 20
    autocommit: bool = True
    
    @property
    def connection_url(self) -> str:
        """获取数据库连接URL"""
        return f"mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}?charset={self.charset}"

# 数据库配置
DB_CONFIG = DatabaseConfig(
    host="47.99.86.118",
    port=3308,
    user="root",
    password="123456",
    database="plan_check",
    charset="utf8mb4",
    max_connections=20,
    autocommit=True
)

# 环境变量配置（可选，用于不同环境的配置）
def get_db_config_from_env() -> Optional[DatabaseConfig]:
    """从环境变量获取数据库配置"""
    host = os.getenv('MYSQL_HOST')
    port = os.getenv('MYSQL_PORT')
    user = os.getenv('MYSQL_USER')
    password = os.getenv('MYSQL_PASSWORD')
    database = os.getenv('MYSQL_DBNAME')
    charset = os.getenv('MYSQL_CHARSET', 'utf8mb4')
    
    if all([host, port, user, password, database]):
        return DatabaseConfig(
            host=host,
            port=int(port),
            user=user,
            password=password,
            database=database,
            charset=charset
        )
    return None

# 根据环境变量覆盖默认配置
env_config = get_db_config_from_env()
if env_config:
    DB_CONFIG = env_config
