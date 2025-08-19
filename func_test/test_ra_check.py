#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
施工方案审核系统测试脚本
"""
import requests
import json
import time
from io import BytesIO

# 配置
API_BASE = "http://59.77.7.24:5001"

def test_status():
    """测试系统状态接口"""
    print("=== 测试系统状态 ===")
    response = requests.get(f"{API_BASE}/ra_check/status")
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    print()

def test_upload_plan():
    """测试上传方案（使用文本文件模拟）"""
    print("=== 测试上传施工方案 ===")
    
    # 创建示例施工方案文本
    plan_text = """
    某建筑工程施工方案
    
    一、工程概况
    本工程为某住宅小区建设项目，总建筑面积约50000平方米，地上18层，地下2层。
    
    二、安全管理措施
    1. 建立健全安全生产责任制，明确各级人员安全职责
    2. 配备专职安全管理人员，持证上岗
    3. 制定安全技术交底制度，对各工种进行安全技术交底
    4. 设置安全防护设施，包括临边防护、洞口防护等
    
    三、质量控制措施
    1. 建立完善的质量管理体系
    2. 明确检验批质量验收标准和程序
    3. 对关键工序实施严格的质量控制
    4. 建立质量检查和验收制度
    
    四、进度管理
    1. 制定详细的施工进度计划
    2. 合理配置人力、物力资源
    3. 建立进度检查和调整机制
    
    五、技术方案
    1. 采用成熟可靠的施工工艺
    2. 明确关键技术参数和控制要点
    3. 对新技术新材料应用进行充分论证
    
    六、环境保护措施
    1. 制定环境保护管理制度
    2. 采取有效的降尘、降噪措施
    3. 建立废物分类处理方案
    
    七、应急预案
    1. 制定完整的应急预案体系
    2. 配备充足的应急资源和设备
    3. 定期开展应急演练
    """
    
    # 创建文本文件
    files = {
        'file': ('test_plan.txt', BytesIO(plan_text.encode('utf-8')), 'text/plain')
    }
    
    # 可选参数
    data = {
        'embedding_model': 'nomic-embed-text',
        'openai_api_key': 'ollama',
        'openai_api_base': 'http://localhost:11434/v1/'
    }
    
    try:
        response = requests.post(f"{API_BASE}/ra_check/upload_plan", files=files, data=data)
        print(f"状态码: {response.status_code}")
        result = response.json()
        print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        if result.get('status') == 'success':
            plan_id = result.get('plan_id')
            print(f"方案ID: {plan_id}")
            return plan_id
        else:
            print("上传失败!")
            return None
            
    except Exception as e:
        print(f"上传时发生错误: {e}")
        return None
    
    print()

def test_query(plan_id):
    """测试查询功能"""
    if not plan_id:
        print("跳过查询测试 - 没有有效的方案ID")
        return
        
    print("=== 测试查询方案内容 ===")
    
    test_queries = [
        "安全防护措施",
        "质量控制",
        "进度管理",
        "环境保护"
    ]
    
    for query in test_queries:
        print(f"查询: {query}")
        data = {
            "plan_id": plan_id,
            "query": query,
            "top_k": 3
        }
        
        try:
            response = requests.post(f"{API_BASE}/ra_check/query", json=data)
            print(f"状态码: {response.status_code}")
            result = response.json()
            
            if result.get('status') == 'success':
                results = result.get('results', [])
                print(f"找到 {len(results)} 个相关结果:")
                for i, res in enumerate(results):
                    print(f"  {i+1}. 相似度: {res.get('similarity', 0):.4f}")
                    print(f"     文本: {res.get('text', '')[:100]}...")
            else:
                print(f"查询失败: {result.get('message', '')}")
                
        except Exception as e:
            print(f"查询时发生错误: {e}")
        
        print("-" * 50)
    
    print()

def test_check_category(plan_id):
    """测试分类检查功能"""
    if not plan_id:
        print("跳过分类检查测试 - 没有有效的方案ID")
        return
        
    print("=== 测试分类场景检查 ===")
    
    test_cases = [
        {"category": "安全管理", "scenario": "安全生产责任制"},
        {"category": "质量控制", "scenario": "质量管理体系"},
        {"category": "技术方案", "scenario": "施工工艺方案"}
    ]
    
    for case in test_cases:
        print(f"检查类别: {case['category']}, 场景: {case['scenario']}")
        data = {
            "plan_id": plan_id,
            "category": case["category"],
            "scenario": case["scenario"],
            "top_k": 3
        }
        
        try:
            response = requests.post(f"{API_BASE}/ra_check/check_category", json=data)
            print(f"状态码: {response.status_code}")
            result = response.json()
            
            if result.get('status') == 'success':
                plan_content = result.get('plan_content', [])
                check_items = result.get('check_items', [])
                print(f"相关方案内容: {len(plan_content)} 项")
                print(f"匹配检查项: {len(check_items)} 项")
                
                if plan_content:
                    print("最相关内容:")
                    print(f"  {plan_content[0].get('text', '')[:100]}...")
            else:
                print(f"检查失败: {result.get('message', '')}")
                
        except Exception as e:
            print(f"检查时发生错误: {e}")
        
        print("-" * 50)
    
    print()

def test_full_audit(plan_id):
    """测试完整审核功能"""
    if not plan_id:
        print("跳过完整审核测试 - 没有有效的方案ID")
        return
        
    print("=== 测试完整审核 ===")
    
    data = {
        "plan_id": plan_id,
        "check_categories": ["安全管理", "质量控制"]
    }
    
    try:
        response = requests.post(f"{API_BASE}/ra_check/full_audit", json=data)
        print(f"状态码: {response.status_code}")
        result = response.json()
        
        if result.get('status') == 'success':
            summary = result.get('summary', {})
            print(f"审核汇总:")
            print(f"  总检查项: {summary.get('total_checks', 0)}")
            print(f"  合规项: {summary.get('compliant_count', 0)}")
            print(f"  不合规项: {summary.get('non_compliant_count', 0)}")
            
            audit_results = result.get('audit_results', {})
            print(f"详细结果: {len(audit_results)} 项")
        else:
            print(f"审核失败: {result.get('message', '')}")
            
    except Exception as e:
        print(f"审核时发生错误: {e}")
    
    print()

def main():
    """主测试函数"""
    print("施工方案审核系统功能测试")
    print("=" * 60)
    
    # 测试系统状态
    test_status()
    
    # 测试上传方案
    plan_id = test_upload_plan()
    
    if plan_id:
        # 等待一下让系统处理
        print("等待系统处理...")
        time.sleep(2)
        
        # 测试查询功能
        test_query(plan_id)
        
        # 测试分类检查
        test_check_category(plan_id)
        
        # 测试完整审核
        test_full_audit(plan_id)
        
        # 再次查看状态
        test_status()
    else:
        print("由于上传失败，跳过后续测试")
    
    print("测试完成!")

if __name__ == "__main__":
    main() 