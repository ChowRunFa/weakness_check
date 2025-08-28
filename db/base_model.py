# -*- coding: utf-8 -*-
"""
基础模型类
"""
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field, fields
from db.connection import get_db_connection

logger = logging.getLogger(__name__)

class BaseModel:
    """基础模型类"""
    
    # 子类需要定义的属性
    table_name: str = ""
    primary_key: str = "id"
    
    def __init__(self, **kwargs):
        """初始化模型实例"""
        # 设置字段值
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    @classmethod
    def get_fields(cls) -> List[str]:
        """获取模型字段列表"""
        if hasattr(cls, '__dataclass_fields__'):
            return list(cls.__dataclass_fields__.keys())
        else:
            # 如果不是dataclass，返回非私有属性
            return [attr for attr in dir(cls) if not attr.startswith('_') and not callable(getattr(cls, attr))]
    
    def to_dict(self) -> Dict[str, Any]:
        """将模型转换为字典"""
        result = {}
        for field_name in self.get_fields():
            if hasattr(self, field_name):
                value = getattr(self, field_name)
                # 处理特殊类型
                if isinstance(value, datetime):
                    result[field_name] = value.isoformat()
                elif isinstance(value, (dict, list)):
                    result[field_name] = json.dumps(value, ensure_ascii=False) if value else None
                else:
                    result[field_name] = value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseModel':
        """从字典创建模型实例"""
        # 处理特殊字段
        processed_data = {}
        for key, value in data.items():
            if key.endswith('_time') and isinstance(value, str):
                # 尝试解析时间字符串
                try:
                    processed_data[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                except:
                    processed_data[key] = value
            elif key.endswith('_data') and isinstance(value, str) and value:
                # 尝试解析JSON字符串
                try:
                    processed_data[key] = json.loads(value)
                except:
                    processed_data[key] = value
            else:
                processed_data[key] = value
        
        return cls(**processed_data)
    
    def save(self) -> bool:
        """保存模型到数据库"""
        try:
            data = self.to_dict()
            
            # 检查是否存在主键值
            primary_key_value = data.get(self.primary_key)
            
            with get_db_connection() as conn:
                if not conn:
                    logger.error("无法获取数据库连接")
                    return False
                
                with conn.cursor() as cursor:
                    if primary_key_value and self.exists(primary_key_value):
                        # 更新记录
                        return self._update(cursor, data)
                    else:
                        # 插入新记录
                        return self._insert(cursor, data)
        except Exception as e:
            logger.error(f"保存模型失败: {str(e)}")
            return False
    
    def _insert(self, cursor, data: Dict[str, Any]) -> bool:
        """插入新记录"""
        try:
            # 移除None值和主键（如果是自增的）
            insert_data = {k: v for k, v in data.items() if v is not None}
            if self.primary_key in insert_data and insert_data[self.primary_key] is None:
                del insert_data[self.primary_key]
            
            if not insert_data:
                logger.warning("没有数据需要插入")
                return False
            
            columns = list(insert_data.keys())
            placeholders = ', '.join(['%s'] * len(columns))
            column_names = ', '.join(columns)
            
            sql = f"INSERT INTO {self.table_name} ({column_names}) VALUES ({placeholders})"
            values = list(insert_data.values())
            
            cursor.execute(sql, values)
            
            # 如果是自增主键，设置新的ID
            if cursor.lastrowid and hasattr(self, self.primary_key):
                setattr(self, self.primary_key, cursor.lastrowid)
            
            logger.debug(f"插入记录成功: {self.table_name}")
            return True
            
        except Exception as e:
            logger.error(f"插入记录失败: {str(e)}")
            return False
    
    def _update(self, cursor, data: Dict[str, Any]) -> bool:
        """更新记录"""
        try:
            primary_key_value = data.get(self.primary_key)
            if not primary_key_value:
                logger.error("更新记录时缺少主键值")
                return False
            
            # 移除主键和None值
            update_data = {k: v for k, v in data.items() if k != self.primary_key and v is not None}
            
            if not update_data:
                logger.warning("没有数据需要更新")
                return True
            
            set_clause = ', '.join([f"{k} = %s" for k in update_data.keys()])
            sql = f"UPDATE {self.table_name} SET {set_clause} WHERE {self.primary_key} = %s"
            values = list(update_data.values()) + [primary_key_value]
            
            cursor.execute(sql, values)
            logger.debug(f"更新记录成功: {self.table_name}, ID: {primary_key_value}")
            return True
            
        except Exception as e:
            logger.error(f"更新记录失败: {str(e)}")
            return False
    
    @classmethod
    def find_by_id(cls, record_id: Union[int, str]) -> Optional['BaseModel']:
        """根据ID查找记录"""
        try:
            with get_db_connection() as conn:
                if not conn:
                    return None
                
                with conn.cursor() as cursor:
                    sql = f"SELECT * FROM {cls.table_name} WHERE {cls.primary_key} = %s"
                    cursor.execute(sql, (record_id,))
                    result = cursor.fetchone()
                    
                    if result:
                        return cls.from_dict(result)
                    return None
                    
        except Exception as e:
            logger.error(f"查找记录失败: {str(e)}")
            return None
    
    @classmethod
    def find_all(cls, where_clause: str = "", params: tuple = (), limit: int = None, offset: int = None) -> List['BaseModel']:
        """查找多条记录"""
        try:
            with get_db_connection() as conn:
                if not conn:
                    return []
                
                with conn.cursor() as cursor:
                    sql = f"SELECT * FROM {cls.table_name}"
                    
                    if where_clause:
                        sql += f" WHERE {where_clause}"
                    
                    if limit:
                        sql += f" LIMIT {limit}"
                        if offset:
                            sql += f" OFFSET {offset}"
                    
                    cursor.execute(sql, params)
                    results = cursor.fetchall()
                    
                    return [cls.from_dict(row) for row in results]
                    
        except Exception as e:
            logger.error(f"查找记录失败: {str(e)}")
            return []
    
    @classmethod
    def find_one(cls, where_clause: str = "", params: tuple = ()) -> Optional['BaseModel']:
        """查找单条记录"""
        results = cls.find_all(where_clause, params, limit=1)
        return results[0] if results else None
    
    @classmethod
    def count(cls, where_clause: str = "", params: tuple = ()) -> int:
        """统计记录数量"""
        try:
            with get_db_connection() as conn:
                if not conn:
                    return 0
                
                with conn.cursor() as cursor:
                    sql = f"SELECT COUNT(*) as count FROM {cls.table_name}"
                    
                    if where_clause:
                        sql += f" WHERE {where_clause}"
                    
                    cursor.execute(sql, params)
                    result = cursor.fetchone()
                    
                    return result['count'] if result else 0
                    
        except Exception as e:
            logger.error(f"统计记录失败: {str(e)}")
            return 0
    
    def exists(self, record_id: Union[int, str] = None) -> bool:
        """检查记录是否存在"""
        if record_id is None:
            record_id = getattr(self, self.primary_key, None)
        
        if not record_id:
            return False
        
        return self.count(f"{self.primary_key} = %s", (record_id,)) > 0
    
    def delete(self) -> bool:
        """删除记录"""
        primary_key_value = getattr(self, self.primary_key, None)
        if not primary_key_value:
            logger.error("删除记录时缺少主键值")
            return False
        
        return self.delete_by_id(primary_key_value)
    
    @classmethod
    def delete_by_id(cls, record_id: Union[int, str]) -> bool:
        """根据ID删除记录"""
        try:
            with get_db_connection() as conn:
                if not conn:
                    return False
                
                with conn.cursor() as cursor:
                    sql = f"DELETE FROM {cls.table_name} WHERE {cls.primary_key} = %s"
                    cursor.execute(sql, (record_id,))
                    
                    logger.debug(f"删除记录成功: {cls.table_name}, ID: {record_id}")
                    return True
                    
        except Exception as e:
            logger.error(f"删除记录失败: {str(e)}")
            return False
    
    @classmethod
    def create_table(cls) -> bool:
        """创建数据表（需要子类实现）"""
        raise NotImplementedError("子类需要实现 create_table 方法")
    
    @classmethod
    def drop_table(cls) -> bool:
        """删除数据表"""
        try:
            with get_db_connection() as conn:
                if not conn:
                    return False
                
                with conn.cursor() as cursor:
                    sql = f"DROP TABLE IF EXISTS {cls.table_name}"
                    cursor.execute(sql)
                    
                    logger.info(f"删除表成功: {cls.table_name}")
                    return True
                    
        except Exception as e:
            logger.error(f"删除表失败: {str(e)}")
            return False
