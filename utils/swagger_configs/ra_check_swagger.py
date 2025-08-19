# -*- coding: utf-8 -*-
"""
施工方案审核API的Swagger文档配置
"""

# 上传施工方案文档的swagger配置
upload_plan_swagger = {
    'tags': ['施工方案审核'],
    'summary': '上传施工方案文档',
    'description': '上传施工方案文档（支持docx格式），提取文本内容并生成嵌入向量',
    'parameters': [
        {
            'name': 'file',
            'in': 'formData',
            'type': 'file',
            'required': True,
            'description': '施工方案文档文件'
        },
        {
            'name': 'embedding_model',
            'in': 'formData',
            'type': 'string',
            'required': False,
            'default': 'nomic-embed-text:latest',
            'description': '嵌入模型名称'
        },
        {
            'name': 'openai_api_key',
            'in': 'formData',
            'type': 'string',
            'required': False,
            'default': 'ollama',
            'description': 'OpenAI API密钥'
        },
        {
            'name': 'openai_api_base',
            'in': 'formData',
            'type': 'string',
            'required': False,
            'default': 'http://localhost:11434/v1/',
            'description': 'OpenAI API基础URL'
        }
    ],
    'responses': {
        200: {
            'description': '上传成功',
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string'},
                    'message': {'type': 'string'},
                    'plan_id': {'type': 'string'},
                    'text_length': {'type': 'integer'},
                    'chunks_count': {'type': 'integer'}
                }
            }
        },
        400: {'description': '请求错误'},
        500: {'description': '服务器错误'}
    }
}

# 批量检查的swagger配置
batch_check_swagger = {
    'tags': ['施工方案审核'],
    'summary': '批量检查上传文件',
    'description': '上传检查项JSON文件和待检查的DOCX文档，逐个返回每个检查项的检查结果，包括原文依据、判断结果和概率',
    'consumes': ['multipart/form-data'],
    'parameters': [
        {
            'name': 'checklist',
            'in': 'formData',
            'type': 'file',
            'required': True,
            'description': '检查项文件（JSON或JSONL格式，类似weakness_list.jsonl）'
        },
        {
            'name': 'document',
            'in': 'formData',
            'type': 'file',
            'required': True,
            'description': '待检查的DOCX文档'
        },
        {
            'name': 'embedding_model',
            'in': 'formData',
            'type': 'string',
            'required': False,
            'default': 'nomic-embed-text:latest',
            'description': '嵌入模型名称'
        },
        {
            'name': 'openai_api_key',
            'in': 'formData',
            'type': 'string',
            'required': False,
            'default': 'ollama',
            'description': 'OpenAI API密钥'
        },
        {
            'name': 'openai_api_base',
            'in': 'formData',
            'type': 'string',
            'required': False,
            'default': 'http://localhost:11434/v1/',
            'description': 'OpenAI API基础URL'
        },
        {
            'name': 'top_k',
            'in': 'formData',
            'type': 'integer',
            'required': False,
            'default': 5,
            'description': '每个检查项返回的相关文本片段数量'
        },
        {
            'name': 'chat_model',
            'in': 'formData',
            'type': 'string',
            'required': False,
            'default': 'qwen2.5:32b',
            'description': '用于智能判断的聊天模型名称'
        },
        {
            'name': 'stream',
            'in': 'formData',
            'type': 'boolean',
            'required': False,
            'default': False,
            'description': '是否使用流式输出返回大模型生成结果'
        }
    ],
    'responses': {
        200: {
            'description': '批量检查成功',
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string'},
                    'message': {'type': 'string'},
                    'data': {
                        'type': 'object',
                        'properties': {
                            'upload_folder': {'type': 'string'},
                            'document_filename': {'type': 'string'},
                            'checklist_filename': {'type': 'string'},
                            'plan_id': {'type': 'string'},
                            'summary': {
                                'type': 'object',
                                'properties': {
                                    'total_items': {'type': 'integer'},
                                    'compliant_items': {'type': 'integer'},
                                    'non_compliant_items': {'type': 'integer'},
                                    'failed_items': {'type': 'integer'},
                                    'compliance_rate': {'type': 'number'}
                                }
                            },
                            'check_results': {
                                'type': 'array',
                                'items': {
                                    'type': 'object',
                                    'properties': {
                                        'item_number': {'type': 'string'},
                                        'category': {'type': 'string'},
                                        'check_scenario': {'type': 'string'},
                                        'evidence': {'type': 'string'},
                                        'judgment': {'type': 'string'},
                                        'probability': {'type': 'number'},
                                        'detailed_result': {'type': 'string'},
                                        'chunk_count': {'type': 'integer'},
                                        'error': {'type': 'string'}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        400: {'description': '请求错误'},
        500: {'description': '服务器错误'}
    }
}

# 查询方案内容的swagger配置
query_plan_swagger = {
    'tags': ['施工方案审核'],
    'summary': '查询方案内容',
    'description': '根据查询条件从施工方案中检索相关内容',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'plan_id': {
                        'type': 'string',
                        'description': '方案ID'
                    },
                    'query': {
                        'type': 'string',
                        'description': '查询内容'
                    },
                    'top_k': {
                        'type': 'integer',
                        'default': 5,
                        'description': '返回结果数量'
                    },
                    'stream': {
                        'type': 'boolean',
                        'default': False,
                        'description': '是否使用流式输出返回大模型生成结果'
                    }
                },
                'required': ['plan_id', 'query']
            }
        }
    ],
    'responses': {
        200: {
            'description': '查询成功',
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string'},
                    'results': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'text': {'type': 'string'},
                                'similarity': {'type': 'number'},
                                'index': {'type': 'integer'}
                            }
                        }
                    }
                }
            }
        },
        400: {'description': '请求错误'},
        404: {'description': '方案未找到'}
    }
}

# 分类场景检查的swagger配置
check_category_swagger = {
    'tags': ['施工方案审核'],
    'summary': '分类场景检查',
    'description': '根据类别和场景对施工方案进行专项检查',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'plan_id': {
                        'type': 'string',
                        'description': '方案ID'
                    },
                    'category': {
                        'type': 'string',
                        'description': '检查类别'
                    },
                    'scenario': {
                        'type': 'string',
                        'description': '检查场景'
                    },
                    'top_k': {
                        'type': 'integer',
                        'default': 5,
                        'description': '返回结果数量'
                    },
                    'stream': {
                        'type': 'boolean',
                        'default': False,
                        'description': '是否使用流式输出返回大模型生成结果'
                    }
                },
                'required': ['plan_id', 'category', 'scenario']
            }
        }
    ],
    'responses': {
        200: {
            'description': '检查成功',
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string'},
                    'plan_content': {'type': 'array'},
                    'check_items': {'type': 'array'}
                }
            }
        },
        400: {'description': '请求错误'},
        404: {'description': '方案未找到'}
    }
}

# 完整审核的swagger配置
full_audit_swagger = {
    'tags': ['施工方案审核'],
    'summary': '完整审核',
    'description': '对施工方案进行完整的缺陷审核，返回详细的审核报告',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'plan_id': {
                        'type': 'string',
                        'description': '方案ID'
                    },
                    'check_categories': {
                        'type': 'array',
                        'items': {'type': 'string'},
                        'description': '要检查的类别列表（为空则检查所有）'
                    },
                    'stream': {
                        'type': 'boolean',
                        'default': False,
                        'description': '是否使用流式输出返回大模型生成结果'
                    }
                },
                'required': ['plan_id']
            }
        }
    ],
    'responses': {
        200: {
            'description': '审核成功',
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string'},
                    'audit_results': {'type': 'object'},
                    'summary': {
                        'type': 'object',
                        'properties': {
                            'total_checks': {'type': 'integer'},
                            'compliant_count': {'type': 'integer'},
                            'non_compliant_count': {'type': 'integer'}
                        }
                    }
                }
            }
        },
        400: {'description': '请求错误'},
        404: {'description': '方案未找到'}
    }
}

# 查看系统状态的swagger配置
get_status_swagger = {
    'tags': ['施工方案审核'],
    'summary': '查看系统状态',
    'description': '查看当前已加载的方案和系统状态',
    'responses': {
        200: {
            'description': '状态查询成功',
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string'},
                    'loaded_plans': {'type': 'array'},
                    'system_info': {'type': 'object'}
                }
            }
        }
    }
}

# 简单检索的swagger配置
simple_search_swagger = {
    'tags': ['施工方案审核'],
    'summary': '简单检索',
    'description': '从施工方案中检索相关文档片段，仅返回检索结果不进行生成',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'plan_id': {
                        'type': 'string',
                        'description': '方案ID'
                    },
                    'query': {
                        'type': 'string',
                        'description': '查询内容'
                    },
                    'top_k': {
                        'type': 'integer',
                        'default': 5,
                        'description': '返回结果数量'
                    }
                },
                'required': ['plan_id', 'query']
            }
        }
    ],
    'responses': {
        200: {
            'description': '检索成功',
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string'},
                    'query': {'type': 'string'},
                    'document': {'type': 'string'},
                    'total_results': {'type': 'integer'},
                    'results': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'index': {'type': 'integer'},
                                'similarity': {'type': 'number'},
                                'text': {'type': 'string'},
                                'preview': {'type': 'string'}
                            }
                        }
                    }
                }
            }
        },
        400: {'description': '请求错误'},
        404: {'description': '方案未找到'},
        500: {'description': '服务器错误'}
    }
}

# 流式RAG查询的swagger配置
stream_query_swagger = {
    'tags': ['施工方案审核'],
    'summary': '流式RAG查询',
    'description': '基于检索增强生成的流式查询，先检索相关内容，再调用大模型生成专业回复',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'plan_id': {
                        'type': 'string',
                        'description': '方案ID'
                    },
                    'query': {
                        'type': 'string',
                        'description': '查询问题'
                    },
                    'top_k': {
                        'type': 'integer',
                        'default': 5,
                        'description': '检索的文档片段数量'
                    },
                    'model': {
                        'type': 'string',
                        'default': 'qwen2.5:32b',
                        'description': 'Ollama模型名称'
                    }
                },
                'required': ['plan_id', 'query']
            }
        }
    ],
    'responses': {
        200: {
            'description': '流式响应成功 (Server-Sent Events)',
            'schema': {
                'type': 'string',
                'description': 'SSE流式数据，格式为 data: {JSON}\n\n'
            },
            'headers': {
                'Content-Type': {
                    'description': 'text/plain',
                    'type': 'string'
                },
                'Cache-Control': {
                    'description': 'no-cache',
                    'type': 'string'
                }
            },
            'examples': {
                'application/json': [
                    {'type': 'start', 'message': '开始查询...'},
                    {'type': 'progress', 'message': '加载文档缓存...'},
                    {'type': 'info', 'message': '已加载文档: plan1.docx (167 个文本块)'},
                    {'type': 'progress', 'message': '正在检索相关内容...'},
                    {'type': 'progress', 'message': '找到 5 个相关文本块，正在生成回复...'},
                    {'type': 'generation_start', 'message': '正在生成回复...'},
                    {'type': 'token', 'content': '根据'},
                    {'type': 'token', 'content': '提供的'},
                    {'type': 'complete', 'message': '生成完成', 'full_response': '...', 'context_chunks_count': 5}
                ]
            }
        },
        400: {'description': '请求错误'},
        404: {'description': '方案未找到'},
        500: {'description': '服务器错误'}
    }
}

# 获取可用嵌入文件列表的swagger配置
available_embeddings_swagger = {
    'tags': ['施工方案审核'],
    'summary': '获取可用嵌入文件列表',
    'description': '获取所有已处理的施工方案文档嵌入文件列表',
    'responses': {
        200: {
            'description': '获取成功',
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string'},
                    'count': {'type': 'integer'},
                    'available_embeddings': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'plan_id': {'type': 'string'},
                                'original_filename': {'type': 'string'},
                                'upload_time': {'type': 'string'},
                                'embedding_model': {'type': 'string'},
                                'chunks_count': {'type': 'integer'},
                                'text_length': {'type': 'integer'},
                                'is_loaded': {'type': 'boolean'}
                            }
                        }
                    }
                }
            }
        },
        500: {'description': '服务器错误'}
    }
}

# 获取文件列表的swagger配置
list_files_swagger = {
    'tags': ['文件管理'],
    'summary': '获取文件列表',
    'description': '获取已缓存的施工方案文件列表',
    'responses': {
        200: {
            'description': '获取成功',
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string'},
                    'files': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'plan_id': {'type': 'string'},
                                'filename': {'type': 'string'},
                                'upload_time': {'type': 'string'},
                                'file_size': {'type': 'number'}
                            }
                        }
                    }
                }
            }
        },
        500: {'description': '服务器错误'}
    }
}

# 删除文件的swagger配置
delete_file_swagger = {
    'tags': ['文件管理'],
    'summary': '删除文件',
    'description': '根据文件hash删除对应的缓存文件和映射记录',
    'parameters': [
        {
            'name': 'file_hash',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': '文件hash标识'
        }
    ],
    'responses': {
        200: {
            'description': '删除成功',
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string'},
                    'message': {'type': 'string'}
                }
            }
        },
        404: {'description': '文件未找到'},
        500: {'description': '服务器错误'}
    }
}

# 获取上传文件夹列表的swagger配置
list_upload_folders_swagger = {
    'tags': ['文件管理'],
    'summary': '获取上传文件夹列表',
    'description': '获取所有时间戳上传文件夹的列表和文件信息',
    'responses': {
        200: {
            'description': '获取成功',
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string'},
                    'upload_folders_count': {'type': 'integer'},
                    'upload_structure': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'timestamp_folder': {'type': 'string'},
                                'created_time': {'type': 'string'},
                                'files': {
                                    'type': 'array',
                                    'items': {
                                        'type': 'object',
                                        'properties': {
                                            'filename': {'type': 'string'},
                                            'size_bytes': {'type': 'integer'},
                                            'size_mb': {'type': 'number'}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        500: {'description': '服务器错误'}
    }
}

# 清理上传文件夹的swagger配置
cleanup_uploads_swagger = {
    'tags': ['文件管理'],
    'summary': '清理上传文件夹',
    'description': '清理超过指定天数的上传文件夹',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': False,
            'schema': {
                'type': 'object',
                'properties': {
                    'days_old': {
                        'type': 'integer',
                        'default': 7,
                        'description': '清理多少天前的文件夹'
                    }
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': '清理成功',
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string'},
                    'message': {'type': 'string'},
                    'cleaned_folders_count': {'type': 'integer'},
                    'criteria': {'type': 'string'}
                }
            }
        },
        400: {'description': '请求错误'},
        500: {'description': '服务器错误'}
    }
}

# 引用检查的swagger配置
cite_check_swagger = {
    'tags': ['施工方案审核'],
    'summary': '引用检查上传文件',
    'description': '上传引用检查文件cite_list.jsonl和待检查的DOCX文档，检查文档是否正确引用了指定的条目，返回每个引用条目的检查结果',
    'consumes': ['multipart/form-data'],
    'parameters': [
        {
            'name': 'cite_list',
            'in': 'formData',
            'type': 'file',
            'required': True,
            'description': '引用检查文件（JSON或JSONL格式，包含待检查的引用条目信息）'
        },
        {
            'name': 'document',
            'in': 'formData',
            'type': 'file',
            'required': True,
            'description': '待检查的DOCX文档'
        },
        {
            'name': 'embedding_model',
            'in': 'formData',
            'type': 'string',
            'required': False,
            'default': 'nomic-embed-text:latest',
            'description': '嵌入模型名称'
        },
        {
            'name': 'openai_api_key',
            'in': 'formData',
            'type': 'string',
            'required': False,
            'default': 'ollama',
            'description': 'OpenAI API密钥'
        },
        {
            'name': 'openai_api_base',
            'in': 'formData',
            'type': 'string',
            'required': False,
            'default': 'http://localhost:11434/v1/',
            'description': 'OpenAI API基础URL'
        },
        {
            'name': 'top_k',
            'in': 'formData',
            'type': 'integer',
            'required': False,
            'default': 5,
            'description': '每个引用条目返回的相关文本片段数量'
        },
        {
            'name': 'chat_model',
            'in': 'formData',
            'type': 'string',
            'required': False,
            'default': 'qwen2.5:32b',
            'description': '用于引用判断的聊天模型名称'
        },
        {
            'name': 'stream',
            'in': 'formData',
            'type': 'boolean',
            'required': False,
            'default': False,
            'description': '是否使用流式输出返回大模型生成结果'
        }
    ],
    'responses': {
        200: {
            'description': '引用检查成功',
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string'},
                    'message': {'type': 'string'},
                    'data': {
                        'type': 'object',
                        'properties': {
                            'upload_folder': {'type': 'string'},
                            'document_filename': {'type': 'string'},
                            'cite_list_filename': {'type': 'string'},
                            'plan_id': {'type': 'string'},
                            'summary': {
                                'type': 'object',
                                'properties': {
                                    'total_citations': {'type': 'integer'},
                                    'properly_cited': {'type': 'integer'},
                                    'missing_citations': {'type': 'integer'},
                                    'incorrectly_cited': {'type': 'integer'},
                                    'failed_checks': {'type': 'integer'},
                                    'citation_rate': {'type': 'number'}
                                }
                            },
                            'citation_results': {
                                'type': 'array',
                                'items': {
                                    'type': 'object',
                                    'properties': {
                                        'citation_id': {'type': 'string'},
                                        'title': {'type': 'string'},
                                        'authors': {'type': 'string'},
                                        'publication': {'type': 'string'},
                                        'year': {'type': 'string'},
                                        'standard_code': {'type': 'string'},
                                        'standard_name': {'type': 'string'},
                                        'issuing_dept': {'type': 'string'},
                                        'implementation_date': {'type': 'string'},
                                        'status': {'type': 'string'},
                                        'citation_text': {'type': 'string'},
                                        'evidence': {'type': 'string'},
                                        'citation_status': {'type': 'string'},
                                        'accuracy_score': {'type': 'number'},
                                        'detailed_result': {'type': 'string'},
                                        'chunk_count': {'type': 'integer'},
                                        'error': {'type': 'string'}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        400: {'description': '请求错误'},
        500: {'description': '服务器错误'}
    }
}

# 文档结构完整性检查的swagger配置
structure_check_swagger = {
    'tags': ['施工方案审核'],
    'summary': '文档结构完整性检查',
    'description': '''
    基于目录结构清单(TOC List)检查文档的结构完整性
    
    支持两种检查模式：
    - item_by_item: 逐条检查，每个目录项单独分析
    - chapter_by_chapter: 逐章节检查，同一章节的内容一起分析
    
    检查结果状态：
    - 完整：目录项内容齐全，满足施工方案要求
    - 部分完整：目录项内容存在但不够完整或详细  
    - 缺失：未找到相关内容或内容严重不足
    - 检查失败：检查过程出错
    ''',
    'consumes': ['multipart/form-data'],
    'produces': ['application/json'],
    'parameters': [
        {
            'name': 'toc_list',
            'in': 'formData',
            'type': 'file',
            'required': True,
            'description': '目录结构清单文件(JSON/JSONL格式)，包含章节、名称、是否必有、类型、AI适用、说明等字段'
        },
        {
            'name': 'document',
            'in': 'formData', 
            'type': 'file',
            'required': True,
            'description': '待检查的DOCX格式文档'
        },
        {
            'name': 'check_mode',
            'in': 'formData',
            'type': 'string',
            'required': False,
            'default': 'item_by_item',
            'enum': ['item_by_item', 'chapter_by_chapter'],
            'description': '检查模式: item_by_item(逐条检查) 或 chapter_by_chapter(逐章节检查)'
        },
        {
            'name': 'embedding_model',
            'in': 'formData',
            'type': 'string',
            'required': False,
            'default': 'nomic-embed-text:latest',
            'description': '嵌入模型名称'
        },
        {
            'name': 'chat_model',
            'in': 'formData',
            'type': 'string',
            'required': False,
            'default': 'qwen2.5:32b',
            'description': '聊天模型名称，用于AI分析'
        },
        {
            'name': 'openai_api_key',
            'in': 'formData',
            'type': 'string',
            'required': False,
            'default': 'ollama',
            'description': 'OpenAI API密钥'
        },
        {
            'name': 'openai_api_base',
            'in': 'formData',
            'type': 'string',
            'required': False,
            'default': 'http://localhost:11434/v1/',
            'description': 'OpenAI API基础URL'
        },
        {
            'name': 'top_k',
            'in': 'formData',
            'type': 'integer',
            'required': False,
            'default': 5,
            'description': '检索返回的相关文档片段数量'
        },
        {
            'name': 'stream',
            'in': 'formData',
            'type': 'boolean',
            'required': False,
            'default': False,
            'description': '是否使用流式输出返回大模型生成结果'
        }
    ],
    'responses': {
        200: {
            'description': '结构完整性检查成功',
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {
                        'type': 'string',
                        'example': 'success'
                    },
                    'message': {
                        'type': 'string', 
                        'example': '文档结构完整性检查完成'
                    },
                    'data': {
                        'type': 'object',
                        'properties': {
                            'summary': {
                                'type': 'object',
                                'properties': {
                                    'total_items': {
                                        'type': 'integer',
                                        'description': '总检查项目数'
                                    },
                                    'complete_items': {
                                        'type': 'integer',
                                        'description': '完整项目数'
                                    },
                                    'missing_items': {
                                        'type': 'integer',
                                        'description': '缺失项目数'
                                    },
                                    'partial_items': {
                                        'type': 'integer',
                                        'description': '部分完整项目数'
                                    },
                                    'failed_checks': {
                                        'type': 'integer',
                                        'description': '检查失败项目数'
                                    },
                                    'completeness_rate': {
                                        'type': 'number',
                                        'description': '完整性比率(%)'
                                    }
                                }
                            },
                            'check_results': {
                                'type': 'array',
                                'items': {
                                    'type': 'object',
                                    'properties': {
                                        'item_id': {
                                            'type': 'string',
                                            'description': '项目ID'
                                        },
                                        'chapter': {
                                            'type': 'string',
                                            'description': '章节号'
                                        },
                                        'name': {
                                            'type': 'string',
                                            'description': '项目名称'
                                        },
                                        'required': {
                                            'type': 'string',
                                            'description': '是否必有'
                                        },
                                        'item_type': {
                                            'type': 'string',
                                            'description': '项目类型'
                                        },
                                        'ai_applicable': {
                                            'type': 'string',
                                            'description': '是否适用AI检查'
                                        },
                                        'description': {
                                            'type': 'string',
                                            'description': '检查说明'
                                        },
                                        'completeness_status': {
                                            'type': 'string',
                                            'description': '完整性状态: 完整/部分完整/缺失/检查失败'
                                        },
                                        'completeness_score': {
                                            'type': 'number',
                                            'description': '完整性评分(0.0-1.0)'
                                        },
                                        'evidence': {
                                            'type': 'string',
                                            'description': '相关证据文本'
                                        },
                                        'detailed_result': {
                                            'type': 'string',
                                            'description': '详细分析结果'
                                        }
                                    }
                                }
                            },
                            'check_mode': {
                                'type': 'string',
                                'description': '使用的检查模式'
                            },
                            'toc_list_filename': {
                                'type': 'string',
                                'description': '目录清单文件名'
                            },
                            'document_filename': {
                                'type': 'string',
                                'description': '文档文件名'
                            },
                            'plan_id': {
                                'type': 'string',
                                'description': '文档处理ID'
                            },
                            'upload_folder': {
                                'type': 'string',
                                'description': '上传文件夹'
                            }
                        }
                    }
                }
            }
        },
        400: {
            'description': '请求参数错误',
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {
                        'type': 'string',
                        'example': 'error'
                    },
                    'message': {
                        'type': 'string',
                        'example': '请上传目录结构清单文件(toc_list)和待检查文档(document)'
                    }
                }
            }
        },
        500: {
            'description': '服务器内部错误',
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {
                        'type': 'string',
                        'example': 'error'
                    },
                    'message': {
                        'type': 'string',
                        'example': '检查失败: 服务器内部错误'
                    }
                }
            }
        }
    }
} 