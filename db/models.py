# -*- coding: utf-8 -*-
"""
数据库模型定义
"""
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, List, Any
from db.base_model import BaseModel
from db.connection import get_db_connection

logger = logging.getLogger(__name__)

@dataclass
class AsyncTask(BaseModel):
    """异步任务模型"""
    table_name = "async_tasks"
    primary_key = "id"
    
    id: Optional[int] = None
    task_id: str = ""
    task_type: str = ""  # structure_check, batch_check, cite_check等
    status: str = "pending"  # pending, processing, success, failed
    callback_url: str = ""
    scheme_id: Optional[int] = None  # 方案ID
    scheme_name: Optional[str] = None  # 方案名称
    request_params: Optional[Dict] = None
    result_data: Optional[Dict] = None
    error_message: Optional[str] = None
    created_time: Optional[datetime] = None
    updated_time: Optional[datetime] = None
    completed_time: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_time is None:
            self.created_time = datetime.now()
        if self.updated_time is None:
            self.updated_time = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """重写to_dict方法，处理JSON字段"""
        result = super().to_dict()
        
        # 处理JSON字段
        if self.request_params:
            result['request_params'] = json.dumps(self.request_params, ensure_ascii=False)
        if self.result_data:
            result['result_data'] = json.dumps(self.result_data, ensure_ascii=False)
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AsyncTask':
        """重写from_dict方法，处理JSON字段"""
        # 处理JSON字段
        if 'request_params' in data and isinstance(data['request_params'], str):
            try:
                data['request_params'] = json.loads(data['request_params']) if data['request_params'] else None
            except:
                data['request_params'] = None
                
        if 'result_data' in data and isinstance(data['result_data'], str):
            try:
                data['result_data'] = json.loads(data['result_data']) if data['result_data'] else None
            except:
                data['result_data'] = None
        
        return cls(**data)
    
    def update_status(self, status: str, error_message: str = None, result_data: Dict = None) -> bool:
        """更新任务状态"""
        self.status = status
        self.updated_time = datetime.now()
        
        if error_message:
            self.error_message = error_message
        
        if result_data:
            self.result_data = result_data
            
        if status in ['success', 'failed']:
            self.completed_time = datetime.now()
        
        return self.save()
    
    @classmethod
    def find_by_task_id(cls, task_id: str) -> Optional['AsyncTask']:
        """根据任务ID查找任务"""
        return cls.find_one("task_id = %s", (task_id,))
    
    @classmethod
    def find_pending_tasks(cls, task_type: str = None) -> List['AsyncTask']:
        """查找待处理的任务"""
        where_clause = "status = 'pending'"
        params = ()
        
        if task_type:
            where_clause += " AND task_type = %s"
            params = (task_type,)
        
        return cls.find_all(where_clause, params)
    
    @classmethod
    def create_table(cls) -> bool:
        """创建async_tasks表"""
        try:
            with get_db_connection() as conn:
                if not conn:
                    return False
                
                with conn.cursor() as cursor:
                    sql = """
                    CREATE TABLE IF NOT EXISTS async_tasks (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        task_id VARCHAR(100) NOT NULL UNIQUE,
                        task_type VARCHAR(50) NOT NULL,
                        status VARCHAR(20) NOT NULL DEFAULT 'pending',
                        callback_url VARCHAR(500),
                        scheme_id BIGINT,
                        scheme_name VARCHAR(255),
                        request_params TEXT,
                        result_data LONGTEXT,
                        error_message TEXT,
                        created_time DATETIME NOT NULL,
                        updated_time DATETIME NOT NULL,
                        completed_time DATETIME,
                        INDEX idx_task_id (task_id),
                        INDEX idx_status (status),
                        INDEX idx_task_type (task_type),
                        INDEX idx_scheme_id (scheme_id),
                        INDEX idx_created_time (created_time)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                    """
                    cursor.execute(sql)
                    logger.info("创建async_tasks表成功")
                    return True
                    
        except Exception as e:
            logger.error(f"创建async_tasks表失败: {str(e)}")
            return False

@dataclass
class StructureCheckResult(BaseModel):
    """结构检查结果模型"""
    table_name = "structure_check_results"
    primary_key = "id"
    
    id: Optional[int] = None
    task_id: str = ""
    scheme_id: Optional[int] = None  # 方案ID
    scheme_name: Optional[str] = None  # 方案名称
    document_filename: str = ""
    document_file_path: Optional[str] = None  # 文档文件路径
    toc_list_filename: str = ""
    toc_file_url: Optional[str] = None  # 模板文件路径
    check_mode: str = ""  # item_by_item, chapter_by_chapter
    plan_id: str = ""
    upload_folder: str = ""
    total_items: int = 0
    complete_items: int = 0
    missing_items: int = 0
    partial_items: int = 0
    failed_checks: int = 0
    completeness_rate: float = 0.0
    created_time: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_time is None:
            self.created_time = datetime.now()
    
    @classmethod
    def find_by_task_id(cls, task_id: str) -> Optional['StructureCheckResult']:
        """根据任务ID查找结果"""
        return cls.find_one("task_id = %s", (task_id,))
    
    @classmethod
    def create_table(cls) -> bool:
        """创建structure_check_results表"""
        try:
            with get_db_connection() as conn:
                if not conn:
                    return False
                
                with conn.cursor() as cursor:
                    sql = """
                    CREATE TABLE IF NOT EXISTS structure_check_results (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        task_id VARCHAR(100) NOT NULL,
                        scheme_id BIGINT,
                        scheme_name VARCHAR(255),
                        document_filename VARCHAR(255) NOT NULL,
                        document_file_path VARCHAR(500),
                        toc_list_filename VARCHAR(255) NOT NULL,
                        toc_file_url VARCHAR(500),
                        check_mode VARCHAR(50) NOT NULL,
                        plan_id VARCHAR(100),
                        upload_folder VARCHAR(100),
                        total_items INT NOT NULL DEFAULT 0,
                        complete_items INT NOT NULL DEFAULT 0,
                        missing_items INT NOT NULL DEFAULT 0,
                        partial_items INT NOT NULL DEFAULT 0,
                        failed_checks INT NOT NULL DEFAULT 0,
                        completeness_rate DECIMAL(5,2) NOT NULL DEFAULT 0.00,
                        created_time DATETIME NOT NULL,
                        INDEX idx_task_id (task_id),
                        INDEX idx_scheme_id (scheme_id),
                        INDEX idx_created_time (created_time),
                        INDEX idx_completeness_rate (completeness_rate)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                    """
                    cursor.execute(sql)
                    logger.info("创建structure_check_results表成功")
                    return True
                    
        except Exception as e:
            logger.error(f"创建structure_check_results表失败: {str(e)}")
            return False

@dataclass
class StructureCheckItem(BaseModel):
    """结构检查项目模型"""
    table_name = "structure_check_items"
    primary_key = "id"
    
    id: Optional[int] = None
    task_id: str = ""
    item_id: str = ""
    chapter: str = ""
    name: str = ""
    required: str = ""
    item_type: str = ""
    ai_applicable: str = ""
    description: str = ""
    completeness_status: str = ""  # 完整, 部分完整, 缺失, 检查失败
    completeness_score: float = 0.0
    evidence: Optional[str] = None
    detailed_result: Optional[str] = None
    created_time: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_time is None:
            self.created_time = datetime.now()
    
    @classmethod
    def find_by_task_id(cls, task_id: str) -> List['StructureCheckItem']:
        """根据任务ID查找所有检查项"""
        return cls.find_all("task_id = %s ORDER BY item_id", (task_id,))
    
    @classmethod
    def batch_insert(cls, items: List['StructureCheckItem']) -> bool:
        """批量插入检查项"""
        if not items:
            return True
        
        try:
            with get_db_connection() as conn:
                if not conn:
                    return False
                
                with conn.cursor() as cursor:
                    sql = """
                    INSERT INTO structure_check_items 
                    (task_id, item_id, chapter, name, required, item_type, ai_applicable, 
                     description, completeness_status, completeness_score, evidence, 
                     detailed_result, created_time)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    
                    values = []
                    for item in items:
                        values.append((
                            item.task_id, item.item_id, item.chapter, item.name,
                            item.required, item.item_type, item.ai_applicable,
                            item.description, item.completeness_status, item.completeness_score,
                            item.evidence, item.detailed_result, item.created_time
                        ))
                    
                    cursor.executemany(sql, values)
                    logger.info(f"批量插入{len(items)}条检查项记录成功")
                    return True
                    
        except Exception as e:
            logger.error(f"批量插入检查项失败: {str(e)}")
            return False
    
    @classmethod
    def create_table(cls) -> bool:
        """创建structure_check_items表"""
        try:
            with get_db_connection() as conn:
                if not conn:
                    return False
                
                with conn.cursor() as cursor:
                    sql = """
                    CREATE TABLE IF NOT EXISTS structure_check_items (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        task_id VARCHAR(100) NOT NULL,
                        item_id VARCHAR(20) NOT NULL,
                        chapter VARCHAR(50),
                        name VARCHAR(200) NOT NULL,
                        required VARCHAR(10),
                        item_type VARCHAR(50),
                        ai_applicable VARCHAR(10),
                        description TEXT,
                        completeness_status VARCHAR(20) NOT NULL,
                        completeness_score DECIMAL(4,3) NOT NULL DEFAULT 0.000,
                        evidence TEXT,
                        detailed_result TEXT,
                        created_time DATETIME NOT NULL,
                        INDEX idx_task_id (task_id),
                        INDEX idx_status (completeness_status),
                        INDEX idx_score (completeness_score),
                        INDEX idx_created_time (created_time)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                    """
                    cursor.execute(sql)
                    logger.info("创建structure_check_items表成功")
                    return True
                    
        except Exception as e:
            logger.error(f"创建structure_check_items表失败: {str(e)}")
            return False

@dataclass
class DocumentReference(BaseModel):
    """文档引用模型 - 用于记录任务相关的文档和模板文件引用"""
    table_name = "document_references"
    primary_key = "id"
    
    id: Optional[int] = None
    task_id: str = ""
    scheme_id: Optional[int] = None  # 方案ID
    original_filename: str = ""
    saved_filename: str = ""
    file_path: str = ""  # 文件实际路径
    file_size: int = 0
    file_type: str = ""  # document, toc_list, template等
    reference_folder: str = ""  # 引用文件夹（原 upload_folder）
    file_hash: Optional[str] = None
    created_time: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_time is None:
            self.created_time = datetime.now()
    
    @classmethod
    def find_by_task_id(cls, task_id: str) -> List['DocumentReference']:
        """根据任务ID查找文档引用"""
        return cls.find_all("task_id = %s", (task_id,))
    
    @classmethod
    def find_by_scheme_id(cls, scheme_id: int) -> List['DocumentReference']:
        """根据方案ID查找文档引用"""
        return cls.find_all("scheme_id = %s", (scheme_id,))
    
    @classmethod
    def create_table(cls) -> bool:
        """创建document_references表"""
        try:
            with get_db_connection() as conn:
                if not conn:
                    return False
                
                with conn.cursor() as cursor:
                    sql = """
                    CREATE TABLE IF NOT EXISTS document_references (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        task_id VARCHAR(100) NOT NULL,
                        scheme_id BIGINT,
                        original_filename VARCHAR(255) NOT NULL,
                        saved_filename VARCHAR(255) NOT NULL,
                        file_path VARCHAR(500) NOT NULL,
                        file_size BIGINT NOT NULL DEFAULT 0,
                        file_type VARCHAR(50),
                        reference_folder VARCHAR(100),
                        file_hash VARCHAR(64),
                        created_time DATETIME NOT NULL,
                        INDEX idx_task_id (task_id),
                        INDEX idx_scheme_id (scheme_id),
                        INDEX idx_file_type (file_type),
                        INDEX idx_file_hash (file_hash),
                        INDEX idx_created_time (created_time)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                    """
                    cursor.execute(sql)
                    logger.info("创建document_references表成功")
                    return True
                    
        except Exception as e:
            logger.error(f"创建document_references表失败: {str(e)}")
            return False

@dataclass
class ContentCheckResult(BaseModel):
    """内容检查结果模型"""
    table_name = "content_check_results"
    primary_key = "id"
    
    id: Optional[int] = None
    task_id: str = ""
    document_filename: str = ""
    checklist_filename: str = ""
    plan_id: str = ""
    upload_folder: str = ""
    total_items: int = 0
    compliant_items: int = 0
    non_compliant_items: int = 0
    failed_items: int = 0
    compliance_rate: float = 0.0
    created_time: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_time is None:
            self.created_time = datetime.now()
    
    @classmethod
    def find_by_task_id(cls, task_id: str) -> Optional['ContentCheckResult']:
        """根据任务ID查找结果"""
        return cls.find_one("task_id = %s", (task_id,))
    
    @classmethod
    def create_table(cls) -> bool:
        """创建content_check_results表"""
        try:
            with get_db_connection() as conn:
                if not conn:
                    return False
                
                with conn.cursor() as cursor:
                    sql = """
                    CREATE TABLE IF NOT EXISTS content_check_results (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        task_id VARCHAR(100) NOT NULL,
                        document_filename VARCHAR(255) NOT NULL,
                        checklist_filename VARCHAR(255) NOT NULL,
                        plan_id VARCHAR(100),
                        upload_folder VARCHAR(100),
                        total_items INT NOT NULL DEFAULT 0,
                        compliant_items INT NOT NULL DEFAULT 0,
                        non_compliant_items INT NOT NULL DEFAULT 0,
                        failed_items INT NOT NULL DEFAULT 0,
                        compliance_rate DECIMAL(5,2) NOT NULL DEFAULT 0.00,
                        created_time DATETIME NOT NULL,
                        INDEX idx_task_id (task_id),
                        INDEX idx_created_time (created_time),
                        INDEX idx_compliance_rate (compliance_rate)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                    """
                    cursor.execute(sql)
                    logger.info("创建content_check_results表成功")
                    return True
                    
        except Exception as e:
            logger.error(f"创建content_check_results表失败: {str(e)}")
            return False

@dataclass
class ContentCheckItem(BaseModel):
    """内容检查项目模型"""
    table_name = "content_check_items"
    primary_key = "id"
    
    id: Optional[int] = None
    task_id: str = ""
    item_number: str = ""
    category: str = ""
    check_scenario: str = ""
    judgment: str = ""  # 合规, 不合规, 无法判断, 检查失败
    probability: float = 0.0
    evidence: Optional[str] = None
    detailed_result: Optional[str] = None
    chunk_count: int = 0
    created_time: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_time is None:
            self.created_time = datetime.now()
    
    @classmethod
    def find_by_task_id(cls, task_id: str) -> List['ContentCheckItem']:
        """根据任务ID查找所有检查项"""
        return cls.find_all("task_id = %s ORDER BY item_number", (task_id,))
    
    @classmethod
    def create_table(cls) -> bool:
        """创建content_check_items表"""
        try:
            with get_db_connection() as conn:
                if not conn:
                    return False
                
                with conn.cursor() as cursor:
                    sql = """
                    CREATE TABLE IF NOT EXISTS content_check_items (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        task_id VARCHAR(100) NOT NULL,
                        item_number VARCHAR(50) NOT NULL,
                        category VARCHAR(100),
                        check_scenario TEXT,
                        judgment VARCHAR(50),
                        probability DECIMAL(5,3) DEFAULT 0.000,
                        evidence TEXT,
                        detailed_result TEXT,
                        chunk_count INT DEFAULT 0,
                        created_time DATETIME NOT NULL,
                        INDEX idx_task_id (task_id),
                        INDEX idx_judgment (judgment),
                        INDEX idx_created_time (created_time)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                    """
                    cursor.execute(sql)
                    logger.info("创建content_check_items表成功")
                    return True
                    
        except Exception as e:
            logger.error(f"创建content_check_items表失败: {str(e)}")
            return False

@dataclass
class CiteCheckResult(BaseModel):
    """引用检查结果模型"""
    table_name = "cite_check_results"
    primary_key = "id"
    
    id: Optional[int] = None
    task_id: str = ""
    document_filename: str = ""
    cite_list_filename: str = ""
    plan_id: str = ""
    upload_folder: str = ""
    total_citations: int = 0
    properly_cited: int = 0
    missing_citations: int = 0
    incorrectly_cited: int = 0
    failed_checks: int = 0
    citation_rate: float = 0.0
    created_time: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_time is None:
            self.created_time = datetime.now()
    
    @classmethod
    def find_by_task_id(cls, task_id: str) -> Optional['CiteCheckResult']:
        """根据任务ID查找结果"""
        return cls.find_one("task_id = %s", (task_id,))
    
    @classmethod
    def create_table(cls) -> bool:
        """创建cite_check_results表"""
        try:
            with get_db_connection() as conn:
                if not conn:
                    return False
                
                with conn.cursor() as cursor:
                    sql = """
                    CREATE TABLE IF NOT EXISTS cite_check_results (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        task_id VARCHAR(100) NOT NULL,
                        document_filename VARCHAR(255) NOT NULL,
                        cite_list_filename VARCHAR(255) NOT NULL,
                        plan_id VARCHAR(100),
                        upload_folder VARCHAR(100),
                        total_citations INT NOT NULL DEFAULT 0,
                        properly_cited INT NOT NULL DEFAULT 0,
                        missing_citations INT NOT NULL DEFAULT 0,
                        incorrectly_cited INT NOT NULL DEFAULT 0,
                        failed_checks INT NOT NULL DEFAULT 0,
                        citation_rate DECIMAL(5,2) NOT NULL DEFAULT 0.00,
                        created_time DATETIME NOT NULL,
                        INDEX idx_task_id (task_id),
                        INDEX idx_created_time (created_time),
                        INDEX idx_citation_rate (citation_rate)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                    """
                    cursor.execute(sql)
                    logger.info("创建cite_check_results表成功")
                    return True
                    
        except Exception as e:
            logger.error(f"创建cite_check_results表失败: {str(e)}")
            return False

@dataclass
class CiteCheckItem(BaseModel):
    """引用检查项目模型"""
    table_name = "cite_check_items"
    primary_key = "id"
    
    id: Optional[int] = None
    task_id: str = ""
    citation_id: str = ""
    title: str = ""
    authors: str = ""
    publication: str = ""
    year: str = ""
    standard_code: str = ""
    standard_name: str = ""
    issuing_dept: str = ""
    implementation_date: str = ""
    status: str = ""
    citation_text: str = ""
    citation_status: str = ""  # 正确引用, 缺失引用, 引用有误, 引用不完整, 检查失败
    accuracy_score: float = 0.0
    evidence: Optional[str] = None
    detailed_result: Optional[str] = None
    chunk_count: int = 0
    created_time: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_time is None:
            self.created_time = datetime.now()
    
    @classmethod
    def find_by_task_id(cls, task_id: str) -> List['CiteCheckItem']:
        """根据任务ID查找所有引用项"""
        return cls.find_all("task_id = %s ORDER BY citation_id", (task_id,))
    
    @classmethod
    def create_table(cls) -> bool:
        """创建cite_check_items表"""
        try:
            with get_db_connection() as conn:
                if not conn:
                    return False
                
                with conn.cursor() as cursor:
                    sql = """
                    CREATE TABLE IF NOT EXISTS cite_check_items (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        task_id VARCHAR(100) NOT NULL,
                        citation_id VARCHAR(100),
                        title VARCHAR(500),
                        authors VARCHAR(200),
                        publication VARCHAR(200),
                        year VARCHAR(20),
                        standard_code VARCHAR(100),
                        standard_name VARCHAR(500),
                        issuing_dept VARCHAR(200),
                        implementation_date VARCHAR(50),
                        status VARCHAR(50),
                        citation_text TEXT,
                        citation_status VARCHAR(50),
                        accuracy_score DECIMAL(5,3) DEFAULT 0.000,
                        evidence TEXT,
                        detailed_result TEXT,
                        chunk_count INT DEFAULT 0,
                        created_time DATETIME NOT NULL,
                        INDEX idx_task_id (task_id),
                        INDEX idx_citation_status (citation_status),
                        INDEX idx_standard_code (standard_code),
                        INDEX idx_created_time (created_time)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                    """
                    cursor.execute(sql)
                    logger.info("创建cite_check_items表成功")
                    return True
                    
        except Exception as e:
            logger.error(f"创建cite_check_items表失败: {str(e)}")
            return False

def create_all_tables() -> bool:
    """创建所有数据表"""
    models = [AsyncTask, StructureCheckResult, StructureCheckItem, DocumentReference, 
              ContentCheckResult, ContentCheckItem, CiteCheckResult, CiteCheckItem]
    
    success_count = 0
    for model in models:
        try:
            if model.create_table():
                success_count += 1
                logger.info(f"表 {model.table_name} 创建成功")
            else:
                logger.error(f"表 {model.table_name} 创建失败")
        except Exception as e:
            logger.error(f"创建表 {model.table_name} 时发生异常: {str(e)}")
    
    logger.info(f"数据表创建完成，成功: {success_count}/{len(models)}")
    return success_count == len(models)

def drop_all_tables() -> bool:
    """删除所有数据表"""
    models = [AsyncTask, StructureCheckResult, StructureCheckItem, DocumentReference,
              ContentCheckResult, ContentCheckItem, CiteCheckResult, CiteCheckItem]
    
    success_count = 0
    for model in models:
        try:
            if model.drop_table():
                success_count += 1
                logger.info(f"表 {model.table_name} 删除成功")
            else:
                logger.error(f"表 {model.table_name} 删除失败")
        except Exception as e:
            logger.error(f"删除表 {model.table_name} 时发生异常: {str(e)}")
    
    logger.info(f"数据表删除完成，成功: {success_count}/{len(models)}")
    return success_count == len(models)
