# -*- coding: utf-8 -*-
"""
异步引用检查API的Swagger文档配置
"""

# 异步引用检查的swagger配置
async_cite_check_swagger = {
    'tags': ['异步引用检查'],
    'summary': '异步引用检查',
    'description': '通过方案ID、文档文件路径和引用检查文件路径，异步执行引用检查，完成后回调指定接口',
    'consumes': ['application/x-www-form-urlencoded'],
    'parameters': [
        {
            'name': 'schemeId',
            'in': 'formData',
            'type': 'integer',
            'required': True,
            'description': '方案ID',
            'default': 1
        },
        {
            'name': 'filePath',
            'in': 'formData',
            'type': 'string',
            'required': True,
            'description': '文档文件路径',
            'default': './data/docs/plan1.docx'
        },
        {
            'name': 'schemeName',
            'in': 'formData',
            'type': 'string',
            'required': True,
            'description': '方案名称',
            'default': '方案1'
        },
        {
            'name': 'citeListPath',
            'in': 'formData',
            'type': 'string',
            'required': True,
            'description': '引用检查文件路径（JSON或JSONL格式）',
            'default': './data/checklist/cite_list.jsonl'
        },
        {
            'name': 'callback_base_url',
            'in': 'formData',
            'type': 'string',
            'required': False,
            'description': '回调接口基础URL，默认为本地测试回调',
            'default': 'http://127.0.0.1:5000'
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
            'default': 'http://59.77.7.24:11434/v1/',
            'description': 'OpenAI API基础URL'
        },
        {
            'name': 'embedding_model',
            'in': 'formData',
            'type': 'string',
            'required': False,
            'description': '嵌入模型名称',
            'default': 'nomic-embed-text:latest'
        },
        {
            'name': 'chat_model',
            'in': 'formData',
            'type': 'string',
            'required': False,
            'description': '对话模型名称',
            'default': 'qwen2.5:32b'
        },
        {
            'name': 'top_k',
            'in': 'formData',
            'type': 'integer',
            'required': False,
            'description': '检索相关文档片段数量',
            'default': 5
        }
    ],
    'responses': {
        200: {
            'description': '任务创建成功',
            'schema': {
                'type': 'object',
                'properties': {
                    'code': {
                        'type': 'integer',
                        'example': 200
                    },
                    'message': {
                        'type': 'string',
                        'example': 'success'
                    },
                    'data': {
                        'type': 'object',
                        'properties': {
                            'result': {
                                'type': 'string',
                                'example': 'true'
                            },
                            'task_id': {
                                'type': 'string',
                                'example': 'cite_check_20241201_123456_789'
                            },
                            'callback_url': {
                                'type': 'string',
                                'example': 'http://127.0.0.1:5000/test/callback'
                            },
                            'estimated_time': {
                                'type': 'string',
                                'example': '预计3-10分钟内完成'
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
                    'code': {
                        'type': 'integer',
                        'example': 400
                    },
                    'message': {
                        'type': 'string',
                        'example': '方案ID不能为空'
                    },
                    'data': {
                        'type': 'object',
                        'properties': {
                            'result': {
                                'type': 'string',
                                'example': 'false'
                            }
                        }
                    }
                }
            }
        },
        500: {
            'description': '服务器内部错误',
            'schema': {
                'type': 'object',
                'properties': {
                    'code': {
                        'type': 'integer',
                        'example': 500
                    },
                    'message': {
                        'type': 'string',
                        'example': '服务器内部错误'
                    },
                    'data': {
                        'type': 'object',
                        'properties': {
                            'result': {
                                'type': 'string',
                                'example': 'false'
                            }
                        }
                    }
                }
            }
        }
    }
}

# 获取任务状态的swagger配置
get_cite_check_task_status_swagger = {
    'tags': ['异步引用检查'],
    'summary': '查询引用检查任务状态',
    'description': '根据任务ID查询异步引用检查任务的状态',
    'parameters': [
        {
            'name': 'task_id',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': '任务ID',
            'default': 'cite_check_20241201_123456_789'
        }
    ],
    'responses': {
        200: {
            'description': '任务状态信息',
            'schema': {
                'type': 'object',
                'properties': {
                    'code': {
                        'type': 'integer',
                        'example': 200
                    },
                    'message': {
                        'type': 'string',
                        'example': 'success'
                    },
                    'data': {
                        'type': 'object',
                        'properties': {
                            'task_id': {
                                'type': 'string',
                                'example': 'cite_check_20241201_123456_789'
                            },
                            'status': {
                                'type': 'string',
                                'example': 'success'
                            },
                            'task_type': {
                                'type': 'string',
                                'example': 'cite_check'
                            },
                            'created_time': {
                                'type': 'string',
                                'example': '2024-12-01T12:34:56'
                            },
                            'updated_time': {
                                'type': 'string',
                                'example': '2024-12-01T12:45:30'
                            },
                            'result_data': {
                                'type': 'object',
                                'description': '检查结果数据（仅当状态为success时）'
                            }
                        }
                    }
                }
            }
        },
        404: {
            'description': '任务不存在',
            'schema': {
                'type': 'object',
                'properties': {
                    'code': {
                        'type': 'integer',
                        'example': 404
                    },
                    'message': {
                        'type': 'string',
                        'example': '任务不存在'
                    },
                    'data': {
                        'type': 'object',
                        'example': None
                    }
                }
            }
        }
    }
}

# 获取检查结果的swagger配置
get_cite_check_result_swagger = {
    'tags': ['异步引用检查'],
    'summary': '获取引用检查结果',
    'description': '根据任务ID获取异步引用检查的详细结果',
    'parameters': [
        {
            'name': 'task_id',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': '任务ID',
            'default': 'cite_check_20241201_123456_789'
        }
    ],
    'responses': {
        200: {
            'description': '检查结果详情',
            'schema': {
                'type': 'object',
                'properties': {
                    'code': {
                        'type': 'integer',
                        'example': 200
                    },
                    'message': {
                        'type': 'string',
                        'example': 'success'
                    },
                    'data': {
                        'type': 'object',
                        'properties': {
                            'summary': {
                                'type': 'object',
                                'properties': {
                                    'total_citations': {
                                        'type': 'integer',
                                        'example': 15
                                    },
                                    'properly_cited': {
                                        'type': 'integer',
                                        'example': 10
                                    },
                                    'missing_citations': {
                                        'type': 'integer',
                                        'example': 3
                                    },
                                    'incorrectly_cited': {
                                        'type': 'integer',
                                        'example': 1
                                    },
                                    'failed_checks': {
                                        'type': 'integer',
                                        'example': 1
                                    },
                                    'citation_rate': {
                                        'type': 'number',
                                        'example': 66.67
                                    }
                                }
                            },
                            'citation_results': {
                                'type': 'array',
                                'items': {
                                    'type': 'object',
                                    'properties': {
                                        'citation_id': {
                                            'type': 'string',
                                            'example': 'GB50010-2020'
                                        },
                                        'title': {
                                            'type': 'string',
                                            'example': '混凝土结构设计规范'
                                        },
                                        'authors': {
                                            'type': 'string',
                                            'example': '住房和城乡建设部'
                                        },
                                        'standard_code': {
                                            'type': 'string',
                                            'example': 'GB50010-2020'
                                        },
                                        'citation_status': {
                                            'type': 'string',
                                            'example': '正确引用'
                                        },
                                        'accuracy_score': {
                                            'type': 'number',
                                            'example': 0.90
                                        },
                                        'evidence': {
                                            'type': 'string',
                                            'example': '相关文档证据文本...'
                                        },
                                        'detailed_result': {
                                            'type': 'string',
                                            'example': 'AI分析结果详情...'
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        404: {
            'description': '结果不存在',
            'schema': {
                'type': 'object',
                'properties': {
                    'code': {
                        'type': 'integer',
                        'example': 404
                    },
                    'message': {
                        'type': 'string',
                        'example': '检查结果不存在或任务未完成'
                    },
                    'data': {
                        'type': 'object',
                        'example': None
                    }
                }
            }
        }
    }
}
