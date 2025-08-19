#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prompt模板文件
存放所有用于LLM交互的prompt模板
"""

# ========== 系统角色定义 ==========

CONSTRUCTION_EXPERT_SYSTEM = "你是一位专业的建设工程质量审查专家。请基于提供的施工方案内容，判断是否存在指定的缺陷情形。"

CITATION_EXPERT_SYSTEM = "你是一位专业的文档引用检查专家。请基于提供的文档内容，判断是否正确引用了指定的标准或文献。"

STRUCTURE_EXPERT_SYSTEM = "你是一位专业的文档结构分析专家。请基于提供的文档内容，分析文档结构的完整性。"

QUERY_ASSISTANT_SYSTEM = "你是一位专业的施工方案审查助手。请基于提供的文档内容，回答用户的问题。"

# ========== 批量检查相关模板 ==========

def get_batch_check_prompt(check_scenario, category, context):
    """获取批量检查的prompt"""
    return f"""
请分析以下施工方案内容，判断是否存在"{check_scenario}"的缺陷情形。

【检查项分类】: {category}
【缺陷情形】: {check_scenario}

【施工方案相关内容】:
{context}

请按以下格式回答：
1. 合规性判断：[合规/不合规]
2. 置信度：[0.1-1.0之间的数值]
3. 判断依据：[详细说明分析过程和依据]

注意：
- 如果方案中有相关的规定或措施来避免该缺陷，则判断为"合规"
- 如果方案中明显缺失相关内容或存在问题，则判断为"不合规"
- 置信度反映你对判断结果的确信程度
"""

# ========== 分类场景检查相关模板 ==========

def get_category_check_prompt(category, scenario, context):
    """获取分类场景检查的prompt"""
    return f"""
请基于提供的施工方案内容，针对"{category}"分类下的"{scenario}"缺陷情形进行专业分析。

【分析重点】:
- 缺陷情形：{scenario}
- 所属分类：{category}

【相关文档内容】:
{context}

请提供专业的分析结果，包括：
1. 是否存在该缺陷情形
2. 具体的问题识别或合规确认
3. 改进建议（如存在问题）
4. 风险评估等级
"""

# ========== 引用检查相关模板 ==========

def get_citation_check_prompt(citation_info, context):
    """获取引用检查的prompt"""
    return f"""
请分析文档中是否正确引用了以下标准或文献：

【引用信息】:
{citation_info}

【文档相关内容】:
{context}

请按以下格式分析：
1. 引用状态：[正确引用/部分引用/缺失引用/错误引用]
2. 准确性评分：[0.0-1.0之间的数值]
3. 具体分析：[详细说明引用情况]
4. 改进建议：[如有问题，提供改进建议]

评判标准：
- 正确引用：标准编号、名称、发布部门、实施日期等信息准确完整
- 部分引用：引用了部分信息但不够完整
- 缺失引用：应该引用但未引用
- 错误引用：引用信息有误
"""

# ========== 文档结构检查相关模板 ==========

def get_structure_check_prompt(item_info, context):
    """获取文档结构检查的prompt"""
    return f"""
请分析文档结构中以下章节的完整性：

【章节信息】:
- 章节名称：{item_info.get('名称', '')}
- 是否必有：{item_info.get('必有', '')}
- 类型：{item_info.get('类型', '')}
- 说明：{item_info.get('说明', '')}

【文档相关内容】:
{context}

请按以下格式分析：
1. 完整性评估：[完整/部分完整/缺失/不适用]
2. 内容充实度：[0.0-1.0之间的数值]
3. 质量评价：[详细说明内容质量]
4. 改进建议：[如有不足，提供具体建议]

评判标准：
- 完整：章节内容齐全，符合要求
- 部分完整：有相关内容但不够充分
- 缺失：缺少必要的章节内容
- 不适用：该项目不需要此章节
"""

# ========== 查询问答相关模板 ==========

def get_query_prompt(question, context):
    """获取查询问答的prompt"""
    return f"""
基于以下施工方案内容，请回答用户的问题：

【用户问题】: {question}

【相关文档内容】:
{context}

请提供详细、准确的答案，包括：
1. 直接回答用户问题
2. 引用具体的文档内容作为依据
3. 如果信息不足，请明确指出
4. 提供相关的补充信息或建议
"""

# ========== 全面审计相关模板 ==========

def get_full_audit_prompt(checklist_items, document_content):
    """获取全面审计的prompt"""
    checklist_summary = "\n".join([f"- {item.get('分类', '')}: {item.get('专项施工方案严重缺陷情形', '')}" 
                                   for item in checklist_items[:10]])  # 只显示前10项作为示例
    
    return f"""
请对以下施工方案进行全面审计分析：

【检查清单要点】:
{checklist_summary}
{'...(更多检查项)' if len(checklist_items) > 10 else ''}

【文档内容】:
{document_content[:2000]}...  # 只显示部分内容

请提供综合性的审计报告，包括：
1. 总体合规性评估
2. 主要风险点识别
3. 关键缺陷情形分析
4. 改进优先级建议
5. 整体质量评级
"""

# ========== 置信度解析相关 ==========

CONFIDENCE_PATTERNS = [
    r'置信度[：:]\s*\[?([0-9.]+)\]?',
    r'置信度[：:]\s*([0-9.]+)',
    r'置信度：\s*([0-9.]+)',
    r'2\.\s*置信度[：:]\s*([0-9.]+)',
    r'准确性评分[：:]\s*([0-9.]+)',
    r'内容充实度[：:]\s*([0-9.]+)'
]

# ========== 判断结果解析相关 ==========

COMPLIANCE_KEYWORDS = {
    'compliant': ['合规', '符合要求', '满足标准', '正确引用', '完整'],
    'non_compliant': ['不合规', '非合规', '不符合', '缺失引用', '错误引用', '缺失'],
    'partial': ['部分', '不够', '有待改进', '部分完整'],
    'unable_to_judge': ['无法判断', '信息不足', '不清楚']
}

def parse_llm_judgment(response_text):
    """解析LLM回复中的判断结果"""
    response_lower = response_text.lower()
    
    # 判断合规性
    if any(keyword in response_lower for keyword in COMPLIANCE_KEYWORDS['non_compliant']):
        judgment = "不合规"
    elif any(keyword in response_lower for keyword in COMPLIANCE_KEYWORDS['partial']):
        judgment = "部分合规"
    elif any(keyword in response_lower for keyword in COMPLIANCE_KEYWORDS['compliant']):
        judgment = "合规"
    elif any(keyword in response_lower for keyword in COMPLIANCE_KEYWORDS['unable_to_judge']):
        judgment = "无法判断"
    else:
        judgment = "合规"  # 默认
    
    return judgment

def parse_confidence_score(response_text):
    """解析LLM回复中的置信度分数"""
    import re
    
    for pattern in CONFIDENCE_PATTERNS:
        match = re.search(pattern, response_text)
        if match:
            try:
                score = float(match.group(1))
                return max(0.0, min(1.0, score))  # 确保在0-1范围内
            except ValueError:
                continue
    
    return 0.5  # 默认置信度

def generate_single_check_prompt(check_item):
    """
    为单个检查项构造审查提示
    """
    # 使用单个检查项构造专项检查提示
    check_prompt = f'''
作为建设工程质量审查AI助手，请依据规范对施工方案进行缺陷判定，采用合理性推定原则（无明显缺失即视为合规）。
具体要求：

专项检查：{check_item}

合规条件：当文本中未包含能够证明"{check_item['专项施工方案严重缺陷情形']}"的情况时，即视为合规

输出要求：
(1) 检查结果必须严格包含三部分结构：
【检索依据】：引用具体文本片段，要求尽可能详细（不少于200字），直接引用方案中用于得出结论的相关原文；
【逻辑判定】：说明引用内容与"{check_item['专项施工方案严重缺陷情形']}"缺陷情形之间的逻辑关系，要求详尽明确（不少于150字）；
【结论声明】：严格按照以下格式输出结论，格式如下：
    1. 合规情况：
    "<font color='blue'>合规</font>：{{分类}}条款，序号{{序号}}不存在{{专项施工方案严重缺陷情形}}"
    或者
    2. 不合规情况：
    "<font color='red'>不合规</font>：发现{{专项施工方案严重缺陷情形}}缺陷（{{分类}}-{{序号}}）"

【输出格式要求】
请严格按照以下 Markdown 模板格式输出，确保层级标题、缩进和标点完全一致：


- **检索依据**：
- {{引用的原文片段1}}
- {{引用的原文片段2}}
- {{引用的原文片段3}}（如有）
- **逻辑判定**：
- {{说明引用内容与缺陷判定的逻辑关系}}
- **结论声明**：
- <font color='blue'>合规</font>：{check_item['分类']}条款，序号{{序号}}不存在{{专项施工方案严重缺陷情形}}
或
- <font color='red'>不合规</font>：发现{{专项施工方案严重缺陷情形}}缺陷（{check_item['分类']}-{{序号}}）

【额外说明】
- 请勿输出任何与审查任务无关的内容（如问候语或多余解释）；
- 各检查项结果之间无需额外空行；
- 所有输出内容应支持直接导入 Markdown 文件，无需后续格式调整。
'''
    return check_prompt

def generate_category_prompt(category, combined_items):
    return f'''
    作为建设工程质量审查AI助手，请依据规范对施工方案进行缺陷判定，采用合理性推定原则（无明显缺失即视为合规）。具体要求：

    专项检查（分类：【{category}】下所有检查项）：
    {combined_items}

    合规条件：当文本中包含能够证明对应缺陷情形的情况不存在时，即视为合规
    输出要求：
    (1) 对每个检查项必须包含三部分结构：
        【检索依据】：引用具体文本片段；(尽可能详细,不少于200字)
        【逻辑判定】：说明引用内容与缺陷情形之间的关系；(尽可能详细并且逻辑清晰,不少于150字)
        【结论声明】：严格按格式输出结论，格式如下：
            1.合规情况：
            "<font color='blue'>合规</font>：{{分类}}条款，序号{{序号}}不存在{{专项施工方案严重缺陷情形}}"
            或者
            2.不合规情况：
            "<font color='red'>不合规</font>：发现{{专项施工方案严重缺陷情形}}缺陷（{{分类}}-{{序号}}）"

        【输出格式要求】
        请严格按以下 Markdown 模板格式输出，确保层级标题、缩进、标点完全一致：

        ### 分析结果

        #### {{序号}}. 检查项：{{检查项名称}}
        - **检索依据**：
          - {{引用的原文片段1}}
          - {{引用的原文片段2}}
          - {{引用的原文片段3}}（如有）
        - **逻辑判定**：
          - {{说明引用内容与缺陷判定的逻辑关系}}
        - **结论声明**：
          - <font color='blue'>合规</font>：{category}条款，序号{{序号}}不存在{{专项施工方案严重缺陷情形}}
          或
          - <font color='red'>不合规</font>：发现{{专项施工方案严重缺陷情形}}缺陷（{category}-{{序号}}）

        【额外说明】
        - 不要输出任何与审查无关的内容（如问候语、解释说明）；
        - 每个检查项结果之间无需额外空行；
        - 所有输出内容需支持直接写入 Markdown 文件，无需再后处理。
    '''

def generate_minicheck_prompt(doc, claim):
    minicheck_prompt = f"""
    Document: {doc}
    Claim: {claim}
    """
    return minicheck_prompt

def generate_retrieval_prompt(category, scenario):
    retrieval_prompt = f"""
    作为建设工程质量审查AI助手，请依据规范对施工方案进行缺陷判定，采用合理性推定原则（无明显缺失即视为合规）。
    请根据以下信息，检索文本中可用于验证是否存在专项施工方案严重缺陷的证据内容。
    
    - 分类："{category}"
    - 专项施工方案严重缺陷情形："{scenario}"

    请查找施工方案中是否存在能够体现该缺陷情形的证据（例如缺失、描述不完整、内容矛盾等）。输出应包括：
    
    1. 匹配到的原始证据文本；
    2. - 合规情况：
    "合规：{{分类}}条款，不存在{{专项施工方案严重缺陷情形}}"
    或者
    - 不合规情况：
    "不合规：发现{{专项施工方案严重缺陷情形}}缺陷（{{分类}}）"
    3. 简要说明理由。
    
    若未找到相关内容，也请明确说明"未找到相关证据,无法判断，默认合规"。
    """
    return retrieval_prompt

def generate_query_prompt(query):
    retrieval_prompt = f"""
    用户的查询信息为：{query}
    请检索文本中与{query}最相关的文本，并给出原始的证据文本，并回答用户
    """
    return retrieval_prompt 