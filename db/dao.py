# -*- coding: utf-8 -*-
"""
数据访问对象 (Data Access Object)
"""
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from db.connection import get_db_connection
from db.models import AsyncTask, StructureCheckResult, StructureCheckItem, DocumentReference, ContentCheckResult, ContentCheckItem, CiteCheckResult, CiteCheckItem

logger = logging.getLogger(__name__)

class AsyncTaskDAO:
    """异步任务数据访问对象"""
    
    @staticmethod
    def create_task(task_id: str, task_type: str, callback_url: str, 
                   request_params: Dict = None, scheme_id: int = None, 
                   scheme_name: str = None) -> Optional[AsyncTask]:
        """创建新的异步任务"""
        try:
            task = AsyncTask(
                task_id=task_id,
                task_type=task_type,
                status='pending',
                callback_url=callback_url,
                scheme_id=scheme_id,
                scheme_name=scheme_name,
                request_params=request_params,
                created_time=datetime.now(),
                updated_time=datetime.now()
            )
            
            if task.save():
                logger.info(f"创建异步任务成功: {task_id}")
                return task
            else:
                logger.error(f"创建异步任务失败: {task_id}")
                return None
                
        except Exception as e:
            logger.error(f"创建异步任务异常: {str(e)}")
            return None
    
    @staticmethod
    def update_task_status(task_id: str, status: str, error_message: str = None, 
                          result_data: Dict = None) -> bool:
        """更新任务状态"""
        try:
            task = AsyncTask.find_by_task_id(task_id)
            if not task:
                logger.error(f"任务不存在: {task_id}")
                return False
            
            return task.update_status(status, error_message, result_data)
            
        except Exception as e:
            logger.error(f"更新任务状态异常: {str(e)}")
            return False
    
    @staticmethod
    def get_task_by_id(task_id: str) -> Optional[AsyncTask]:
        """根据任务ID获取任务"""
        return AsyncTask.find_by_task_id(task_id)
    
    @staticmethod
    def get_pending_tasks(task_type: str = None, limit: int = 10) -> List[AsyncTask]:
        """获取待处理的任务"""
        where_clause = "status = 'pending'"
        params = ()
        
        if task_type:
            where_clause += " AND task_type = %s"
            params = (task_type,)
        
        where_clause += " ORDER BY created_time ASC"
        
        return AsyncTask.find_all(where_clause, params, limit=limit)
    
    @staticmethod
    def get_tasks_by_status(status: str, hours: int = 24, limit: int = 100) -> List[AsyncTask]:
        """获取指定状态的任务"""
        where_clause = "status = %s AND created_time > %s ORDER BY created_time DESC"
        cutoff_time = datetime.now() - timedelta(hours=hours)
        params = (status, cutoff_time)
        
        return AsyncTask.find_all(where_clause, params, limit=limit)
    
    @staticmethod
    def cleanup_old_tasks(days: int = 30) -> int:
        """清理旧任务"""
        try:
            cutoff_time = datetime.now() - timedelta(days=days)
            
            with get_db_connection() as conn:
                if not conn:
                    return 0
                
                with conn.cursor() as cursor:
                    # 删除旧的已完成任务
                    sql = """
                    DELETE FROM async_tasks 
                    WHERE status IN ('success', 'failed') 
                    AND completed_time < %s
                    """
                    cursor.execute(sql, (cutoff_time,))
                    deleted_count = cursor.rowcount
                    
                    logger.info(f"清理了 {deleted_count} 个旧任务")
                    return deleted_count
                    
        except Exception as e:
            logger.error(f"清理旧任务失败: {str(e)}")
            return 0

class StructureCheckDAO:
    """结构检查数据访问对象"""
    
    @staticmethod
    def save_check_result(task_id: str, check_data: Dict) -> bool:
        """保存结构检查结果"""
        try:
            # 保存主结果
            summary = check_data.get('summary', {})
            result = StructureCheckResult(
                task_id=task_id,
                scheme_id=check_data.get('scheme_id'),
                scheme_name=check_data.get('scheme_name'),
                document_filename=check_data.get('document_filename', ''),
                document_file_path=check_data.get('file_path'),
                toc_list_filename=check_data.get('toc_list_filename', ''),
                toc_file_url=check_data.get('file_url'),
                check_mode=check_data.get('check_mode', ''),
                plan_id=check_data.get('plan_id', ''),
                upload_folder=check_data.get('upload_folder', ''),
                total_items=summary.get('total_items', 0),
                complete_items=summary.get('complete_items', 0),
                missing_items=summary.get('missing_items', 0),
                partial_items=summary.get('partial_items', 0),
                failed_checks=summary.get('failed_checks', 0),
                completeness_rate=summary.get('completeness_rate', 0.0),
                created_time=datetime.now()
            )
            
            if not result.save():
                logger.error(f"保存检查结果失败: {task_id}")
                return False
            
            # 保存检查项目
            check_results = check_data.get('check_results', [])
            if check_results:
                items = []
                for item_data in check_results:
                    item = StructureCheckItem(
                        task_id=task_id,
                        item_id=item_data.get('item_id', ''),
                        chapter=item_data.get('chapter', ''),
                        name=item_data.get('name', ''),
                        required=item_data.get('required', ''),
                        item_type=item_data.get('item_type', ''),
                        ai_applicable=item_data.get('ai_applicable', ''),
                        description=item_data.get('description', ''),
                        completeness_status=item_data.get('completeness_status', ''),
                        completeness_score=item_data.get('completeness_score', 0.0),
                        evidence=item_data.get('evidence', ''),
                        detailed_result=item_data.get('detailed_result', ''),
                        created_time=datetime.now()
                    )
                    items.append(item)
                
                if not StructureCheckItem.batch_insert(items):
                    logger.error(f"保存检查项目失败: {task_id}")
                    return False
            
            logger.info(f"保存结构检查结果成功: {task_id}")
            return True
            
        except Exception as e:
            logger.error(f"保存结构检查结果异常: {str(e)}")
            return False
    
    @staticmethod
    def get_check_result(task_id: str) -> Optional[Dict]:
        """获取结构检查结果"""
        try:
            # 获取主结果
            result = StructureCheckResult.find_by_task_id(task_id)
            if not result:
                return None
            
            # 获取检查项目
            items = StructureCheckItem.find_by_task_id(task_id)
            
            return {
                'summary': {
                    'total_items': result.total_items,
                    'complete_items': result.complete_items,
                    'missing_items': result.missing_items,
                    'partial_items': result.partial_items,
                    'failed_checks': result.failed_checks,
                    'completeness_rate': float(result.completeness_rate)
                },
                'check_results': [item.to_dict() for item in items],
                'check_mode': result.check_mode,
                'scheme_id': result.scheme_id,
                'scheme_name': result.scheme_name,
                'document_filename': result.document_filename,
                'document_file_path': result.document_file_path,
                'toc_list_filename': result.toc_list_filename,
                'toc_file_url': result.toc_file_url,
                'plan_id': result.plan_id,
                'upload_folder': result.upload_folder,
                'created_time': result.created_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"获取结构检查结果异常: {str(e)}")
            return None
    
    @staticmethod
    def get_statistics(days: int = 30) -> Dict:
        """获取检查统计信息"""
        try:
            cutoff_time = datetime.now() - timedelta(days=days)
            
            with get_db_connection() as conn:
                if not conn:
                    return {}
                
                with conn.cursor() as cursor:
                    # 获取基本统计
                    sql = """
                    SELECT 
                        COUNT(*) as total_checks,
                        AVG(completeness_rate) as avg_completeness_rate,
                        SUM(total_items) as total_items_checked,
                        SUM(complete_items) as total_complete_items,
                        SUM(missing_items) as total_missing_items
                    FROM structure_check_results 
                    WHERE created_time > %s
                    """
                    cursor.execute(sql, (cutoff_time,))
                    stats = cursor.fetchone()
                    
                    # 获取按天的统计
                    sql = """
                    SELECT 
                        DATE(created_time) as check_date,
                        COUNT(*) as daily_checks,
                        AVG(completeness_rate) as daily_avg_rate
                    FROM structure_check_results 
                    WHERE created_time > %s
                    GROUP BY DATE(created_time)
                    ORDER BY check_date DESC
                    """
                    cursor.execute(sql, (cutoff_time,))
                    daily_stats = cursor.fetchall()
                    
                    return {
                        'period_days': days,
                        'total_checks': stats['total_checks'] if stats else 0,
                        'avg_completeness_rate': float(stats['avg_completeness_rate']) if stats and stats['avg_completeness_rate'] else 0.0,
                        'total_items_checked': stats['total_items_checked'] if stats else 0,
                        'total_complete_items': stats['total_complete_items'] if stats else 0,
                        'total_missing_items': stats['total_missing_items'] if stats else 0,
                        'daily_statistics': daily_stats or []
                    }
                    
        except Exception as e:
            logger.error(f"获取统计信息异常: {str(e)}")
            return {}

class DocumentDAO:
    """文档引用数据访问对象"""
    
    @staticmethod
    def save_document_reference(task_id: str, scheme_id: int, original_filename: str, 
                               saved_filename: str, file_path: str, file_size: int, 
                               file_type: str, reference_folder: str, file_hash: str = None) -> bool:
        """保存文档引用信息"""
        try:
            document = DocumentReference(
                task_id=task_id,
                scheme_id=scheme_id,
                original_filename=original_filename,
                saved_filename=saved_filename,
                file_path=file_path,
                file_size=file_size,
                file_type=file_type,
                reference_folder=reference_folder,
                file_hash=file_hash,
                created_time=datetime.now()
            )
            
            if document.save():
                logger.info(f"保存文档引用成功: {original_filename}")
                return True
            else:
                logger.error(f"保存文档引用失败: {original_filename}")
                return False
                
        except Exception as e:
            logger.error(f"保存文档引用异常: {str(e)}")
            return False
    
    @staticmethod
    def get_documents_by_task(task_id: str) -> List[DocumentReference]:
        """获取任务相关的文档引用"""
        return DocumentReference.find_by_task_id(task_id)
    
    @staticmethod
    def get_documents_by_scheme(scheme_id: int) -> List[DocumentReference]:
        """获取方案相关的文档引用"""
        return DocumentReference.find_by_scheme_id(scheme_id)
    
    @staticmethod
    def cleanup_old_document_references(days: int = 7) -> Tuple[int, int]:
        """清理旧文档引用记录（注意：不删除实际文件，只清理引用记录）"""
        try:
            import os
            cutoff_time = datetime.now() - timedelta(days=days)
            
            # 获取要删除的文档引用
            old_docs = DocumentReference.find_all(
                "created_time < %s", (cutoff_time,)
            )
            
            deleted_files = 0
            deleted_records = 0
            
            for doc in old_docs:
                # 注意：不删除物理文件，因为文件可能被多个任务引用
                # 仅清理数据库引用记录
                logger.debug(f"跳过文件删除，仅清理引用记录: {doc.file_path}")
                
                # 删除数据库记录
                if doc.delete():
                    deleted_records += 1
            
            logger.info(f"清理旧文档引用完成，删除记录: {deleted_records}")
            return deleted_files, deleted_records
            
        except Exception as e:
            logger.error(f"清理旧文档引用异常: {str(e)}")
            return 0, 0

class ReportDAO:
    """报告数据访问对象"""
    
    @staticmethod
    def get_task_summary_report(limit: int = 50) -> List[Dict]:
        """获取任务摘要报告"""
        try:
            with get_db_connection() as conn:
                if not conn:
                    return []
                
                with conn.cursor() as cursor:
                    sql = """
                    SELECT 
                        t.task_id,
                        t.task_type,
                        t.status,
                        t.created_time,
                        t.completed_time,
                        r.document_filename,
                        r.completeness_rate,
                        r.total_items,
                        r.complete_items,
                        r.missing_items
                    FROM async_tasks t
                    LEFT JOIN structure_check_results r ON t.task_id = r.task_id
                    WHERE t.task_type = 'structure_check'
                    ORDER BY t.created_time DESC
                    LIMIT %s
                    """
                    cursor.execute(sql, (limit,))
                    results = cursor.fetchall()
                    
                    return results or []
                    
        except Exception as e:
            logger.error(f"获取任务摘要报告异常: {str(e)}")
            return []
    
    @staticmethod
    def get_quality_trend_report(days: int = 30) -> Dict:
        """获取质量趋势报告"""
        try:
            cutoff_time = datetime.now() - timedelta(days=days)
            
            with get_db_connection() as conn:
                if not conn:
                    return {}
                
                with conn.cursor() as cursor:
                    # 按完整性等级分组统计
                    sql = """
                    SELECT 
                        CASE 
                            WHEN completeness_rate >= 90 THEN 'excellent'
                            WHEN completeness_rate >= 80 THEN 'good'
                            WHEN completeness_rate >= 60 THEN 'average'
                            ELSE 'poor'
                        END as quality_level,
                        COUNT(*) as count,
                        AVG(completeness_rate) as avg_rate
                    FROM structure_check_results 
                    WHERE created_time > %s
                    GROUP BY quality_level
                    """
                    cursor.execute(sql, (cutoff_time,))
                    quality_stats = cursor.fetchall()
                    
                    # 获取最常见的缺失项目
                    sql = """
                    SELECT 
                        name,
                        chapter,
                        COUNT(*) as missing_count
                    FROM structure_check_items 
                    WHERE completeness_status = '缺失' 
                    AND created_time > %s
                    GROUP BY name, chapter
                    ORDER BY missing_count DESC
                    LIMIT 10
                    """
                    cursor.execute(sql, (cutoff_time,))
                    missing_items = cursor.fetchall()
                    
                    return {
                        'quality_distribution': quality_stats or [],
                        'common_missing_items': missing_items or [],
                        'period_days': days
                    }
                    
        except Exception as e:
            logger.error(f"获取质量趋势报告异常: {str(e)}")
            return {}

class ContentCheckDAO:
    """内容检查数据访问对象"""
    
    @staticmethod
    def save_check_result(task_id: str, result_data: Dict) -> bool:
        """保存内容检查结果"""
        try:
            summary = result_data.get('summary', {})
            
            # 保存主结果
            result = ContentCheckResult(
                task_id=task_id,
                document_filename=result_data.get('document_filename', ''),
                checklist_filename=result_data.get('checklist_filename', ''),
                plan_id=result_data.get('plan_id', ''),
                upload_folder=result_data.get('upload_folder', ''),
                total_items=summary.get('total_items', 0),
                compliant_items=summary.get('compliant_items', 0),
                non_compliant_items=summary.get('non_compliant_items', 0),
                failed_items=summary.get('failed_items', 0),
                compliance_rate=summary.get('compliance_rate', 0.0)
            )
            
            if not result.save():
                logger.error(f"保存内容检查结果失败，任务ID: {task_id}")
                return False
            
            # 保存详细检查项
            check_results = result_data.get('check_results', [])
            for item_data in check_results:
                item = ContentCheckItem(
                    task_id=task_id,
                    item_number=item_data.get('item_number', ''),
                    category=item_data.get('category', ''),
                    check_scenario=item_data.get('check_scenario', ''),
                    judgment=item_data.get('judgment', ''),
                    probability=item_data.get('probability', 0.0),
                    evidence=item_data.get('evidence', ''),
                    detailed_result=item_data.get('detailed_result', ''),
                    chunk_count=item_data.get('chunk_count', 0)
                )
                
                if not item.save():
                    logger.warning(f"保存内容检查项失败，任务ID: {task_id}, 项目: {item_data.get('item_number')}")
            
            logger.info(f"内容检查结果保存成功，任务ID: {task_id}")
            return True
            
        except Exception as e:
            logger.error(f"保存内容检查结果异常: {str(e)}, 任务ID: {task_id}")
            return False
    
    @staticmethod
    def get_check_result(task_id: str) -> Optional[Dict]:
        """获取内容检查结果"""
        try:
            result = ContentCheckResult.find_by_task_id(task_id)
            if not result:
                return None
            
            items = ContentCheckItem.find_by_task_id(task_id)
            
            return {
                'summary': {
                    'total_items': result.total_items,
                    'compliant_items': result.compliant_items,
                    'non_compliant_items': result.non_compliant_items,
                    'failed_items': result.failed_items,
                    'compliance_rate': result.compliance_rate
                },
                'check_results': [item.to_dict() for item in items],
                'document_filename': result.document_filename,
                'checklist_filename': result.checklist_filename,
                'plan_id': result.plan_id,
                'upload_folder': result.upload_folder,
                'created_time': result.created_time.isoformat() if result.created_time else None
            }
            
        except Exception as e:
            logger.error(f"获取内容检查结果异常: {str(e)}, 任务ID: {task_id}")
            return None
    
    @staticmethod
    def get_statistics(days: int = 30) -> Dict:
        """获取内容检查统计信息"""
        try:
            # 这里可以实现统计逻辑，暂时返回空字典
            return {}
        except Exception as e:
            logger.error(f"获取内容检查统计异常: {str(e)}")
            return {}

class CiteCheckDAO:
    """引用检查数据访问对象"""
    
    @staticmethod
    def save_check_result(task_id: str, result_data: Dict) -> bool:
        """保存引用检查结果"""
        try:
            summary = result_data.get('summary', {})
            
            # 保存主结果
            result = CiteCheckResult(
                task_id=task_id,
                document_filename=result_data.get('document_filename', ''),
                cite_list_filename=result_data.get('cite_list_filename', ''),
                plan_id=result_data.get('plan_id', ''),
                upload_folder=result_data.get('upload_folder', ''),
                total_citations=summary.get('total_citations', 0),
                properly_cited=summary.get('properly_cited', 0),
                missing_citations=summary.get('missing_citations', 0),
                incorrectly_cited=summary.get('incorrectly_cited', 0),
                failed_checks=summary.get('failed_checks', 0),
                citation_rate=summary.get('citation_rate', 0.0)
            )
            
            if not result.save():
                logger.error(f"保存引用检查结果失败，任务ID: {task_id}")
                return False
            
            # 保存详细引用项
            citation_results = result_data.get('citation_results', [])
            for item_data in citation_results:
                item = CiteCheckItem(
                    task_id=task_id,
                    citation_id=item_data.get('citation_id', ''),
                    title=item_data.get('title', ''),
                    authors=item_data.get('authors', ''),
                    publication=item_data.get('publication', ''),
                    year=item_data.get('year', ''),
                    standard_code=item_data.get('standard_code', ''),
                    standard_name=item_data.get('standard_name', ''),
                    issuing_dept=item_data.get('issuing_dept', ''),
                    implementation_date=item_data.get('implementation_date', ''),
                    status=item_data.get('status', ''),
                    citation_text=item_data.get('citation_text', ''),
                    citation_status=item_data.get('citation_status', ''),
                    accuracy_score=item_data.get('accuracy_score', 0.0),
                    evidence=item_data.get('evidence', ''),
                    detailed_result=item_data.get('detailed_result', ''),
                    chunk_count=item_data.get('chunk_count', 0)
                )
                
                if not item.save():
                    logger.warning(f"保存引用检查项失败，任务ID: {task_id}, 引用ID: {item_data.get('citation_id')}")
            
            logger.info(f"引用检查结果保存成功，任务ID: {task_id}")
            return True
            
        except Exception as e:
            logger.error(f"保存引用检查结果异常: {str(e)}, 任务ID: {task_id}")
            return False
    
    @staticmethod
    def get_check_result(task_id: str) -> Optional[Dict]:
        """获取引用检查结果"""
        try:
            result = CiteCheckResult.find_by_task_id(task_id)
            if not result:
                return None
            
            items = CiteCheckItem.find_by_task_id(task_id)
            
            return {
                'summary': {
                    'total_citations': result.total_citations,
                    'properly_cited': result.properly_cited,
                    'missing_citations': result.missing_citations,
                    'incorrectly_cited': result.incorrectly_cited,
                    'failed_checks': result.failed_checks,
                    'citation_rate': result.citation_rate
                },
                'citation_results': [item.to_dict() for item in items],
                'document_filename': result.document_filename,
                'cite_list_filename': result.cite_list_filename,
                'plan_id': result.plan_id,
                'upload_folder': result.upload_folder,
                'created_time': result.created_time.isoformat() if result.created_time else None
            }
            
        except Exception as e:
            logger.error(f"获取引用检查结果异常: {str(e)}, 任务ID: {task_id}")
            return None
    
    @staticmethod
    def get_statistics(days: int = 30) -> Dict:
        """获取引用检查统计信息"""
        try:
            # 这里可以实现统计逻辑，暂时返回空字典
            return {}
        except Exception as e:
            logger.error(f"获取引用检查统计异常: {str(e)}")
            return {}
