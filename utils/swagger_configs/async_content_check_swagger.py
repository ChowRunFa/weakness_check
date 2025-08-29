# -*- coding: utf-8 -*-
"""
异步内容检查API的Swagger文档配置
"""

# 异步内容检查的swagger配置
async_content_check_swagger = {
    'tags': ['异步内容检查'],
    'summary': '异步内容检查',
    'description': '通过方案ID、文档文件路径和检查项文件路径，异步执行内容检查，完成后回调指定接口',
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
            'name': 'checklistPath',
            'in': 'formData',
            'type': 'string',
            'required': True,
            'description': '检查项文件路径（JSON或JSONL格式）',
            'default': './data/checklist/weakness_list.jsonl'
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
                                'example': 'content_check_20241201_123456_789'
                            },
                            'callback_url': {
                                'type': 'string',
                                'example': 'http://127.0.0.1:5000/test/callback'
                            },
                            'estimated_time': {
                                'type': 'string',
                                'example': '预计5-15分钟内完成'
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
get_content_check_task_status_swagger = {
    'tags': ['异步内容检查'],
    'summary': '查询内容检查任务状态',
    'description': '根据任务ID查询异步内容检查任务的状态',
    'parameters': [
        {
            'name': 'task_id',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': '任务ID',
            'default': 'content_check_20241201_123456_789'
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
                                'example': 'content_check_20241201_123456_789'
                            },
                            'status': {
                                'type': 'string',
                                'example': 'success'
                            },
                            'task_type': {
                                'type': 'string',
                                'example': 'content_check'
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
get_content_check_result_swagger = {
    'tags': ['异步内容检查'],
    'summary': '获取内容检查结果',
    'description': '根据任务ID获取异步内容检查的详细结果',
    'parameters': [
        {
            'name': 'task_id',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': '任务ID',
            'default': 'content_check_20241201_123456_789'
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
                                    'total_items': {
                                        'type': 'integer',
                                        'example': 10
                                    },
                                    'compliant_items': {
                                        'type': 'integer',
                                        'example': 7
                                    },
                                    'non_compliant_items': {
                                        'type': 'integer',
                                        'example': 2
                                    },
                                    'failed_items': {
                                        'type': 'integer',
                                        'example': 1
                                    },
                                    'compliance_rate': {
                                        'type': 'number',
                                        'example': 70.0
                                    }
                                }
                            },
                            'check_results': {
                                'type': 'array',
                                'items': {
                                    'type': 'object',
                                    'properties': {
                                        'item_number': {
                                            'type': 'string',
                                            'example': '1'
                                        },
                                        'category': {
                                            'type': 'string',
                                            'example': '安全措施'
                                        },
                                        'check_scenario': {
                                            'type': 'string',
                                            'example': '安全防护措施不到位'
                                        },
                                        'judgment': {
                                            'type': 'string',
                                            'example': '合规'
                                        },
                                        'probability': {
                                            'type': 'number',
                                            'example': 0.85
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
