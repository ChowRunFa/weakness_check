# -*- coding: utf-8 -*-
"""
数据库连接管理器
"""
import logging
import threading
from contextlib import contextmanager
from typing import Optional, Generator
import pymysql
from pymysql.connections import Connection
from pymysql.cursors import DictCursor
from db.config import DB_CONFIG

logger = logging.getLogger(__name__)

class DatabaseConnectionPool:
    """数据库连接池"""
    
    def __init__(self, config=None, pool_size=10):
        self.config = config or DB_CONFIG
        self.pool_size = pool_size
        self._pool = []
        self._used_connections = set()
        self._lock = threading.Lock()
        self._initialized = False
        
    def initialize(self):
        """初始化连接池"""
        if self._initialized:
            return
            
        try:
            with self._lock:
                if self._initialized:
                    return
                    
                # 创建初始连接
                for _ in range(min(3, self.pool_size)):
                    conn = self._create_connection()
                    if conn:
                        self._pool.append(conn)
                
                self._initialized = True
                logger.info(f"数据库连接池初始化完成，初始连接数: {len(self._pool)}")
                
        except Exception as e:
            logger.error(f"数据库连接池初始化失败: {str(e)}")
            raise
    
    def _create_connection(self) -> Optional[Connection]:
        """创建新的数据库连接"""
        try:
            connection = pymysql.connect(
                host=self.config.host,
                port=self.config.port,
                user=self.config.user,
                password=self.config.password,
                database=self.config.database,
                charset=self.config.charset,
                cursorclass=DictCursor,
                autocommit=self.config.autocommit,
                connect_timeout=10,
                read_timeout=30,
                write_timeout=30
            )
            return connection
        except Exception as e:
            logger.error(f"创建数据库连接失败: {str(e)}")
            return None
    
    def get_connection(self) -> Optional[Connection]:
        """从连接池获取连接"""
        if not self._initialized:
            self.initialize()
            
        with self._lock:
            # 尝试从池中获取可用连接
            while self._pool:
                conn = self._pool.pop()
                
                # 检查连接是否有效
                if self._is_connection_valid(conn):
                    self._used_connections.add(conn)
                    return conn
                else:
                    # 连接无效，关闭它
                    try:
                        conn.close()
                    except:
                        pass
            
            # 池中没有可用连接，创建新连接
            if len(self._used_connections) < self.pool_size:
                conn = self._create_connection()
                if conn:
                    self._used_connections.add(conn)
                    return conn
            
        logger.warning("无法获取数据库连接，连接池已满")
        return None
    
    def return_connection(self, connection: Connection):
        """将连接返回到连接池"""
        if not connection:
            return
            
        with self._lock:
            if connection in self._used_connections:
                self._used_connections.remove(connection)
                
                # 检查连接是否仍然有效
                if self._is_connection_valid(connection) and len(self._pool) < self.pool_size:
                    self._pool.append(connection)
                else:
                    # 连接无效或池已满，关闭连接
                    try:
                        connection.close()
                    except:
                        pass
    
    def _is_connection_valid(self, connection: Connection) -> bool:
        """检查连接是否有效"""
        try:
            connection.ping(reconnect=False)
            return True
        except:
            return False
    
    def close_all(self):
        """关闭所有连接"""
        with self._lock:
            # 关闭池中的连接
            for conn in self._pool:
                try:
                    conn.close()
                except:
                    pass
            self._pool.clear()
            
            # 关闭正在使用的连接
            for conn in list(self._used_connections):
                try:
                    conn.close()
                except:
                    pass
            self._used_connections.clear()
            
            self._initialized = False
            logger.info("所有数据库连接已关闭")

# 全局连接池实例
_connection_pool = DatabaseConnectionPool()

def get_connection() -> Optional[Connection]:
    """获取数据库连接"""
    return _connection_pool.get_connection()

def return_connection(connection: Connection):
    """返回数据库连接到池中"""
    _connection_pool.return_connection(connection)

@contextmanager
def get_db_connection() -> Generator[Optional[Connection], None, None]:
    """数据库连接上下文管理器"""
    connection = None
    try:
        connection = get_connection()
        yield connection
    except Exception as e:
        if connection:
            try:
                connection.rollback()
            except:
                pass
        logger.error(f"数据库操作发生错误: {str(e)}")
        raise
    finally:
        if connection:
            return_connection(connection)

def test_connection() -> bool:
    """测试数据库连接"""
    try:
        with get_db_connection() as conn:
            if conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    result = cursor.fetchone()
                    return result is not None
        return False
    except Exception as e:
        logger.error(f"数据库连接测试失败: {str(e)}")
        return False

def close_connection_pool():
    """关闭连接池"""
    _connection_pool.close_all()

# 模块初始化时测试连接
def initialize_database():
    """初始化数据库连接"""
    try:
        if test_connection():
            logger.info("数据库连接测试成功")
            return True
        else:
            logger.error("数据库连接测试失败")
            return False
    except Exception as e:
        logger.error(f"数据库初始化失败: {str(e)}")
        return False
