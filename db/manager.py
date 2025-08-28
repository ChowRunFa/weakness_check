# -*- coding: utf-8 -*-
"""
数据库管理工具
"""
import logging
from typing import Dict, Any
from db.connection import initialize_database, test_connection, close_connection_pool
from db.models import create_all_tables, drop_all_tables
from db.dao import AsyncTaskDAO, StructureCheckDAO, DocumentDAO

logger = logging.getLogger(__name__)

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        self.initialized = False
    
    def initialize(self) -> bool:
        """初始化数据库"""
        try:
            logger.info("开始初始化数据库...")
            
            # 测试数据库连接
            if not initialize_database():
                logger.error("数据库连接初始化失败")
                return False
            
            # 创建所有表
            if not create_all_tables():
                logger.error("数据表创建失败")
                return False
            
            self.initialized = True
            logger.info("数据库初始化完成")
            return True
            
        except Exception as e:
            logger.error(f"数据库初始化异常: {str(e)}")
            return False
    
    def health_check(self) -> Dict[str, Any]:
        """数据库健康检查"""
        try:
            result = {
                'database_connection': False,
                'tables_exist': False,
                'error_message': None
            }
            
            # 检查数据库连接
            if test_connection():
                result['database_connection'] = True
                
                # 检查表是否存在
                from db.models import AsyncTask, StructureCheckResult, StructureCheckItem, DocumentReference
                
                tables_status = {}
                for model in [AsyncTask, StructureCheckResult, StructureCheckItem, DocumentReference]:
                    try:
                        # 尝试查询表来检查是否存在
                        model.count()
                        tables_status[model.table_name] = True
                    except Exception as e:
                        tables_status[model.table_name] = False
                        logger.warning(f"表 {model.table_name} 不存在或不可访问: {str(e)}")
                
                result['tables_status'] = tables_status
                result['tables_exist'] = all(tables_status.values())
            else:
                result['error_message'] = "数据库连接失败"
            
            return result
            
        except Exception as e:
            logger.error(f"数据库健康检查异常: {str(e)}")
            return {
                'database_connection': False,
                'tables_exist': False,
                'error_message': str(e)
            }
    
    def cleanup(self, days: int = 7) -> Dict[str, int]:
        """清理旧数据"""
        try:
            logger.info(f"开始清理 {days} 天前的数据...")
            
            result = {
                'cleaned_tasks': 0,
                'cleaned_files': 0,
                'cleaned_records': 0
            }
            
            # 清理旧任务
            cleaned_tasks = AsyncTaskDAO.cleanup_old_tasks(days=days)
            result['cleaned_tasks'] = cleaned_tasks
            
            # 清理旧文档
            cleaned_files, cleaned_records = DocumentDAO.cleanup_old_documents(days=days)
            result['cleaned_files'] = cleaned_files
            result['cleaned_records'] = cleaned_records
            
            logger.info(f"数据清理完成: {result}")
            return result
            
        except Exception as e:
            logger.error(f"数据清理异常: {str(e)}")
            return {'error': str(e)}
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取数据库统计信息"""
        try:
            from db.models import AsyncTask, StructureCheckResult
            
            stats = {
                'total_tasks': AsyncTask.count(),
                'pending_tasks': AsyncTask.count("status = 'pending'"),
                'processing_tasks': AsyncTask.count("status = 'processing'"),
                'completed_tasks': AsyncTask.count("status = 'success'"),
                'failed_tasks': AsyncTask.count("status = 'failed'"),
                'total_checks': StructureCheckResult.count(),
                'structure_check_stats': StructureCheckDAO.get_statistics(days=30)
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"获取统计信息异常: {str(e)}")
            return {'error': str(e)}
    
    def reset_database(self) -> bool:
        """重置数据库（删除所有表并重新创建）"""
        try:
            logger.warning("开始重置数据库...")
            
            # 删除所有表
            if not drop_all_tables():
                logger.error("删除表失败")
                return False
            
            # 重新创建所有表
            if not create_all_tables():
                logger.error("重新创建表失败")
                return False
            
            logger.info("数据库重置完成")
            return True
            
        except Exception as e:
            logger.error(f"数据库重置异常: {str(e)}")
            return False
    
    def close(self):
        """关闭数据库连接"""
        try:
            close_connection_pool()
            self.initialized = False
            logger.info("数据库连接已关闭")
        except Exception as e:
            logger.error(f"关闭数据库连接异常: {str(e)}")

# 全局数据库管理器实例
db_manager = DatabaseManager()

def init_database() -> bool:
    """初始化数据库的快捷函数"""
    return db_manager.initialize()

def health_check() -> Dict[str, Any]:
    """数据库健康检查的快捷函数"""
    return db_manager.health_check()

def cleanup_database(days: int = 7) -> Dict[str, int]:
    """清理数据库的快捷函数"""
    return db_manager.cleanup(days)

def get_database_stats() -> Dict[str, Any]:
    """获取数据库统计的快捷函数"""
    return db_manager.get_statistics()

def reset_database() -> bool:
    """重置数据库的快捷函数"""
    return db_manager.reset_database()

# CLI 工具函数
def main():
    """命令行工具主函数"""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description='数据库管理工具')
    parser.add_argument('action', choices=['init', 'health', 'cleanup', 'stats', 'reset'],
                       help='要执行的操作')
    parser.add_argument('--days', type=int, default=7,
                       help='清理数据时的天数（默认7天）')
    
    args = parser.parse_args()
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        if args.action == 'init':
            print("初始化数据库...")
            if init_database():
                print("✓ 数据库初始化成功")
                sys.exit(0)
            else:
                print("✗ 数据库初始化失败")
                sys.exit(1)
        
        elif args.action == 'health':
            print("检查数据库健康状态...")
            result = health_check()
            print(f"数据库连接: {'✓' if result['database_connection'] else '✗'}")
            print(f"表存在: {'✓' if result['tables_exist'] else '✗'}")
            if result.get('error_message'):
                print(f"错误: {result['error_message']}")
            if result.get('tables_status'):
                print("表状态:")
                for table, status in result['tables_status'].items():
                    print(f"  {table}: {'✓' if status else '✗'}")
        
        elif args.action == 'cleanup':
            print(f"清理 {args.days} 天前的数据...")
            result = cleanup_database(args.days)
            if 'error' in result:
                print(f"✗ 清理失败: {result['error']}")
                sys.exit(1)
            else:
                print(f"✓ 清理完成:")
                print(f"  清理任务: {result['cleaned_tasks']}")
                print(f"  清理文件: {result['cleaned_files']}")
                print(f"  清理记录: {result['cleaned_records']}")
        
        elif args.action == 'stats':
            print("获取数据库统计信息...")
            stats = get_database_stats()
            if 'error' in stats:
                print(f"✗ 获取统计失败: {stats['error']}")
                sys.exit(1)
            else:
                print("数据库统计:")
                print(f"  总任务数: {stats['total_tasks']}")
                print(f"  待处理: {stats['pending_tasks']}")
                print(f"  处理中: {stats['processing_tasks']}")
                print(f"  已完成: {stats['completed_tasks']}")
                print(f"  失败: {stats['failed_tasks']}")
                print(f"  总检查数: {stats['total_checks']}")
        
        elif args.action == 'reset':
            print("重置数据库...")
            confirm = input("这将删除所有数据，确认吗？(yes/no): ")
            if confirm.lower() == 'yes':
                if reset_database():
                    print("✓ 数据库重置成功")
                else:
                    print("✗ 数据库重置失败")
                    sys.exit(1)
            else:
                print("操作已取消")
    
    except KeyboardInterrupt:
        print("\n操作被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"✗ 执行失败: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
