# 施工方案审核系统 API

基于RAG（Retrieval-Augmented Generation）技术的建设工程施工方案缺陷检查系统。

## 📁 项目结构

```
check_backend/
├── app.py                           # 🚀 主应用入口
├── requirements.txt                 # 📦 依赖包配置
├── README.md                       # 📖 项目文档
├── apis/                           # 🔌 API接口
│   ├── __init__.py
│   ├── api_ra_check.py            # 施工方案审核API
│   ├── api_upload.py              # 文件上传API
│   ├── api_report.py              # 报告生成API
│   └── ...                        # 其他API文件
├── objs/                          # 🧩 核心对象类
│   ├── PlanAuditor.py            # 施工方案审核器
│   └── EmbeddingRetriever.py     # 文本嵌入检索器
├── utils/                         # 🛠️ 工具模块
│   ├── __init__.py
│   ├── prompts.py                # 提示词模板
│   └── swagger_configs/          # Swagger配置
│       ├── __init__.py
│       └── ra_check_swagger.py   # ra_check API文档配置
├── func_test/                     # 🧪 功能测试
│   ├── __init__.py
│   └── test_ra_check.py          # ra_check功能测试
├── data/                          # 📊 数据文件
│   └── weakness_list.jsonl       # 检查项配置
├── cache/                         # 💾 缓存目录
├── uploads/                       # 📁 上传文件目录
├── config/                        # ⚙️ 配置文件
├── db/                           # 🗄️ 数据库相关
└── ...
```

## 功能特性

- **文档上传**: 支持docx、doc、txt、pdf格式的施工方案文档上传
- **智能检索**: 基于语义相似度的方案内容检索
- **分类检查**: 按照不同类别和场景进行专项缺陷检查
- **完整审核**: 对施工方案进行全面的缺陷审核并生成报告
- **API文档**: 完整的Swagger API文档支持

## 安装依赖

```bash
pip install -r requirements.txt
```

## 启动服务

```bash
python app.py
```

服务启动后访问 http://localhost:5000/swagger/ 查看完整的API文档。

## 主要API接口

### 1. 上传施工方案 `/ra_check/upload_plan`

**POST** - 上传施工方案文档并进行文本提取和向量化处理

**参数:**
- `file`: 施工方案文档文件
- `embedding_model`: 嵌入模型名称（可选）
- `openai_api_key`: API密钥（可选）
- `openai_api_base`: API基础URL（可选）

**返回:**
```json
{
    "status": "success",
    "message": "文档上传成功",
    "plan_id": "abc123456789",
    "text_length": 15420,
    "chunks_count": 52
}
```

### 2. 查询方案内容 `/ra_check/query`

**POST** - 根据查询文本从已上传的施工方案中检索相关内容

**参数:**
```json
{
    "plan_id": "abc123456789",
    "query": "安全防护措施",
    "top_k": 5
}
```

**返回:**
```json
{
    "status": "success",
    "results": [
        {
            "text": "相关文本内容...",
            "similarity": 0.8542,
            "index": 15
        }
    ]
}
```

### 3. 分类场景检查 `/ra_check/check_category`

**POST** - 根据指定的类别和场景对施工方案进行专项检查

**参数:**
```json
{
    "plan_id": "abc123456789",
    "category": "安全管理",
    "scenario": "安全生产责任制",
    "top_k": 5
}
```

### 4. 完整审核 `/ra_check/full_audit`

**POST** - 对施工方案进行全面的缺陷审核，生成详细的审核报告

**参数:**
```json
{
    "plan_id": "abc123456789",
    "check_categories": ["安全管理", "质量控制"]
}
```

### 5. 查看系统状态 `/ra_check/status`

**GET** - 查看当前系统中已加载的方案和系统配置信息

## 使用示例

### 1. Python 客户端示例

```python
import requests
import json

# 1. 上传文档
files = {'file': open('施工方案.docx', 'rb')}
response = requests.post('http://localhost:5000/ra_check/upload_plan', files=files)
result = response.json()
plan_id = result['plan_id']

# 2. 查询内容
query_data = {
    "plan_id": plan_id,
    "query": "安全防护措施",
    "top_k": 3
}
response = requests.post('http://localhost:5000/ra_check/query', json=query_data)
results = response.json()

# 3. 完整审核
audit_data = {
    "plan_id": plan_id,
    "check_categories": ["安全管理", "质量控制"]
}
response = requests.post('http://localhost:5000/ra_check/full_audit', json=audit_data)
audit_results = response.json()
```

### 2. cURL 示例

```bash
# 上传文档
curl -X POST -F "file=@施工方案.docx" http://localhost:5000/ra_check/upload_plan

# 查询内容
curl -X POST -H "Content-Type: application/json" \
     -d '{"plan_id":"abc123","query":"安全措施","top_k":5}' \
     http://localhost:5000/ra_check/query

# 查看状态
curl -X GET http://localhost:5000/ra_check/status
```

## 运行测试

```bash
# 运行功能测试
python func_test/test_ra_check.py

# 或者作为模块运行
python -m func_test.test_ra_check
```

## 配置说明

### 嵌入模型配置

系统支持OpenAI兼容的嵌入模型，包括：
- OpenAI官方模型（如 text-embedding-3-small）
- 本地Ollama部署的模型（如 nomic-embed-text）

### 检查项配置

检查项通过 `data/weakness_list.jsonl` 文件配置，每行一个JSON对象：

```json
{"分类": "安全管理", "序号": "1", "专项施工方案严重缺陷情形": "未建立安全生产责任制或责任制不完善"}
```

### 缓存配置

- 文本向量缓存目录：`cache/`
- 上传文件目录：`uploads/`

## 技术架构

- **Flask**: Web框架
- **Flasgger**: API文档生成
- **FAISS**: 向量相似度搜索
- **OpenAI**: 文本嵌入模型接口
- **python-docx**: Word文档解析

## 开发规范

### 文件组织原则

- **`app.py`**: 主应用入口，保持简洁
- **`apis/`**: 所有API蓝图文件
- **`objs/`**: 核心业务对象类
- **`utils/`**: 工具函数和配置
- **`func_test/`**: 功能测试代码
- **`data/`**: 数据文件和配置

### Swagger文档配置

- API文档配置统一存放在 `utils/swagger_configs/`
- 每个API模块有对应的配置文件
- API路由通过 `@swag_from(config_variable)` 引用配置

## 注意事项

1. 首次上传文档时会进行文本嵌入，处理时间较长
2. 嵌入结果会自动缓存，再次上传相同内容的文档会快速加载
3. 系统使用内存缓存方案实例，重启服务后需要重新上传文档
4. 建议配置足够的内存空间用于向量存储和计算

## 错误处理

所有API都返回统一的错误格式：

```json
{
    "status": "error",
    "message": "错误描述信息"
}
```

常见错误码：
- 400: 请求参数错误
- 404: 方案未找到
- 500: 服务器内部错误 