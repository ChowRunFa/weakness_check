# -*- coding: utf-8 -*-
"""
数据库使用示例
"""
import logging
from datetime import datetime
from db import (
    init_database, health_check, cleanup_database,
    AsyncTaskDAO, StructureCheckDAO, DocumentDAO,
    AsyncTask, StructureCheckResult
)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def basic_usage_example():
    """基础使用示例"""
    print("=== 数据库基础使用示例 ===")
    
    # 1. 初始化数据库
    print("1. 初始化数据库...")
    if init_database():
        print("✓ 数据库初始化成功")
    else:
        print("✗ 数据库初始化失败")
        return
    
    # 2. 健康检查
    print("\n2. 数据库健康检查...")
    health = health_check()
    print(f"数据库连接: {'✓' if health['database_connection'] else '✗'}")
    print(f"表存在: {'✓' if health['tables_exist'] else '✗'}")
    
    # 3. 创建异步任务
    print("\n3. 创建异步任务...")
    task_id = f"test_task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    task = AsyncTaskDAO.create_task(
        task_id=task_id,
        task_type="structure_check",
        callback_url="http://localhost:8080/dev-api/system/callback",
        request_params={
            "check_mode": "item_by_item",
            "document_filename": "test.docx",
            "toc_list_filename": "checklist.json"
        }
    )
    
    if task:
        print(f"✓ 任务创建成功: {task_id}")
    else:
        print("✗ 任务创建失败")
        return
    
    # 4. 更新任务状态
    print("\n4. 更新任务状态...")
    if AsyncTaskDAO.update_task_status(task_id, "processing"):
        print("✓ 任务状态更新为处理中")
    
    # 5. 保存结构检查结果
    print("\n5. 保存结构检查结果...")
    check_data = {
        "summary": {
            "total_items": 10,
            "complete_items": 8,
            "missing_items": 1,
            "partial_items": 1,
            "failed_checks": 0,
            "completeness_rate": 80.0
        },
        "check_results": [
            {
                "item_id": "1",
                "chapter": "1.1",
                "name": "工程概况",
                "required": "是",
                "item_type": "文本",
                "ai_applicable": "是",
                "description": "项目基本信息",
                "completeness_status": "完整",
                "completeness_score": 0.95,
                "evidence": "找到相关内容...",
                "detailed_result": "检查完整，内容符合要求"
            },
            {
                "item_id": "2", 
                "chapter": "1.2",
                "name": "编制依据",
                "required": "是",
                "item_type": "列表",
                "ai_applicable": "是", 
                "description": "相关法规标准",
                "completeness_status": "缺失",
                "completeness_score": 0.0,
                "evidence": "",
                "detailed_result": "未找到相关内容"
            }
        ],
        "check_mode": "item_by_item",
        "document_filename": "test.docx",
        "toc_list_filename": "checklist.json",
        "plan_id": "abc123",
        "upload_folder": "20231201_120000"
    }
    
    if StructureCheckDAO.save_check_result(task_id, check_data):
        print("✓ 结构检查结果保存成功")
    
    # 6. 更新任务为完成状态
    print("\n6. 更新任务状态为完成...")
    if AsyncTaskDAO.update_task_status(
        task_id, 
        "success", 
        result_data=check_data['summary']
    ):
        print("✓ 任务状态更新为完成")
    
    # 7. 查询任务和结果
    print("\n7. 查询任务和结果...")
    task = AsyncTaskDAO.get_task_by_id(task_id)
    if task:
        print(f"任务状态: {task.status}")
        print(f"创建时间: {task.created_time}")
        print(f"完成时间: {task.completed_time}")
    
    result = StructureCheckDAO.get_check_result(task_id)
    if result:
        print(f"检查完整率: {result['summary']['completeness_rate']}%")
        print(f"检查项目数: {len(result['check_results'])}")

def model_usage_example():
    """模型直接使用示例"""
    print("\n=== 模型直接使用示例 ===")
    
    # 1. 使用模型类直接操作
    print("1. 直接使用模型类...")
    
    # 创建任务
    task = AsyncTask(
        task_id=f"direct_task_{datetime.now().strftime('%H%M%S')}",
        task_type="batch_check",
        status="pending",
        callback_url="http://example.com/callback"
    )
    
    if task.save():
        print(f"✓ 直接创建任务成功: {task.task_id}")
        
        # 查找任务
        found_task = AsyncTask.find_by_id(task.id)
        if found_task:
            print(f"✓ 查找任务成功: {found_task.task_id}")
        
        # 更新任务
        found_task.status = "completed"
        if found_task.save():
            print("✓ 任务更新成功")
        
        # 删除任务
        if found_task.delete():
            print("✓ 任务删除成功")

def query_examples():
    """查询示例"""
    print("\n=== 查询示例 ===")
    
    # 1. 查询待处理任务
    print("1. 查询待处理任务...")
    pending_tasks = AsyncTaskDAO.get_pending_tasks("structure_check", limit=5)
    print(f"待处理任务数: {len(pending_tasks)}")
    
    # 2. 统计信息
    print("\n2. 获取统计信息...")
    stats = StructureCheckDAO.get_statistics(days=7)
    print(f"最近7天检查数: {stats.get('total_checks', 0)}")
    print(f"平均完整率: {stats.get('avg_completeness_rate', 0):.2f}%")
    
    # 3. 查询最近的任务
    print("\n3. 查询最近的任务...")
    recent_tasks = AsyncTask.find_all(
        "created_time > DATE_SUB(NOW(), INTERVAL 7 DAY) ORDER BY created_time DESC",
        limit=5
    )
    print(f"最近7天任务数: {len(recent_tasks)}")
    for task in recent_tasks:
        print(f"  - {task.task_id}: {task.status} ({task.created_time})")

def maintenance_examples():
    """维护示例"""
    print("\n=== 维护示例 ===")
    
    # 1. 数据清理
    print("1. 清理旧数据...")
    cleanup_result = cleanup_database(days=30)
    if 'error' not in cleanup_result:
        print(f"✓ 清理完成:")
        print(f"  清理任务: {cleanup_result['cleaned_tasks']}")
        print(f"  清理文件: {cleanup_result['cleaned_files']}")
    
    # 2. 健康检查
    print("\n2. 完整健康检查...")
    health = health_check()
    print(f"数据库连接: {'✓' if health['database_connection'] else '✗'}")
    if health.get('tables_status'):
        print("表状态:")
        for table, status in health['tables_status'].items():
            print(f"  {table}: {'✓' if status else '✗'}")

if __name__ == "__main__":
    try:
        # 基础使用示例
        basic_usage_example()
        
        # 模型使用示例  
        model_usage_example()
        
        # 查询示例
        query_examples()
        
        # 维护示例
        maintenance_examples()
        
        print("\n=== 所有示例执行完成 ===")
        
    except Exception as e:
        logger.error(f"示例执行失败: {str(e)}")
        import traceback
        traceback.print_exc()
