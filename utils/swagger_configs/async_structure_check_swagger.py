# -*- coding: utf-8 -*-
"""
异步结构检查API的Swagger文档配置
"""

# 异步结构完整性检查的swagger配置
async_structure_check_swagger = {
    'tags': ['异步结构检查'],
    'summary': '异步文档结构完整性检查',
    'description': '通过方案ID和文件路径，异步执行结构完整性检查，完成后回调指定接口',
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
            'name': 'fileUrl',
            'in': 'formData',
            'type': 'string',
            'required': True,
            'description': '模板文件路径（目录结构清单文件）',
            'default': './data/checklist/toc_list.jsonl'
        },
        {
            'name': 'check_mode',
            'in': 'formData',
            'type': 'string',
            'required': False,
            'description': '检查模式：item_by_item（逐条检查）或 chapter_by_chapter（逐章节检查）',
            'default': 'chapter_by_chapter'
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
            'description': '请求提交成功',
            'schema': {
                'type': 'object',
                'properties': {
                    'code': {'type': 'integer', 'example': 200},
                    'message': {'type': 'string', 'example': 'success'},
                    'data': {
                        'type': 'object',
                        'properties': {
                            'result': {'type': 'string', 'example': 'true'},
                            'task_id': {'type': 'string', 'example': '20231201_143022_123'},
                            'callback_url': {'type': 'string', 'example': 'http://localhost:8080/dev-api/system/callback'},
                            'estimated_time': {'type': 'string', 'example': '预计3-10分钟内完成'}
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
                    'code': {'type': 'integer', 'example': 400},
                    'message': {'type': 'string', 'example': '参数验证失败，请检查schemeId、filePath、schemeName、fileUrl参数'},
                    'data': {
                        'type': 'object',
                        'properties': {
                            'result': {'type': 'string', 'example': 'false'}
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
                    'code': {'type': 'integer', 'example': 500},
                    'message': {'type': 'string', 'example': '服务器内部错误'},
                    'data': {
                        'type': 'object',
                        'properties': {
                            'result': {'type': 'string', 'example': 'false'}
                        }
                    }
                }
            }
        }
    }
}

# 查询任务状态的swagger配置
get_task_status_swagger = {
    'tags': ['异步结构检查'],
    'summary': '查询异步任务状态',
    'description': '根据任务ID查询异步结构检查任务的当前状态和基本信息',
    'parameters': [
        {
            'name': 'task_id',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': '任务ID'
        }
    ],
    'responses': {
        200: {
            'description': '任务状态信息',
            'schema': {
                'type': 'object',
                'properties': {
                    'code': {'type': 'integer', 'example': 200},
                    'message': {'type': 'string', 'example': 'success'},
                    'data': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer', 'example': 1},
                            'task_id': {'type': 'string', 'example': '20231201_143022_123'},
                            'task_type': {'type': 'string', 'example': 'structure_check'},
                            'status': {'type': 'string', 'example': 'success'},
                            'callback_url': {'type': 'string', 'example': 'http://localhost:8080/dev-api/system/callback'},
                            'request_params': {'type': 'object', 'description': '请求参数'},
                            'result_data': {'type': 'object', 'description': '结果数据'},
                            'error_message': {'type': 'string', 'example': None},
                            'created_time': {'type': 'string', 'example': '2023-12-01T14:30:22'},
                            'updated_time': {'type': 'string', 'example': '2023-12-01T14:35:22'},
                            'completed_time': {'type': 'string', 'example': '2023-12-01T14:35:22'}
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
                    'code': {'type': 'integer', 'example': 404},
                    'message': {'type': 'string', 'example': '任务不存在'},
                    'data': {'type': 'null'}
                }
            }
        },
        500: {
            'description': '服务器内部错误',
            'schema': {
                'type': 'object',
                'properties': {
                    'code': {'type': 'integer', 'example': 500},
                    'message': {'type': 'string', 'example': '查询失败'},
                    'data': {'type': 'null'}
                }
            }
        }
    }
}

# 获取检查结果的swagger配置
get_check_result_swagger = {
    'tags': ['异步结构检查'],
    'summary': '获取结构检查结果',
    'description': '根据任务ID获取详细的结构完整性检查结果',
    'parameters': [
        {
            'name': 'task_id',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': '任务ID'
        }
    ],
    'responses': {
        200: {
            'description': '检查结果详情',
            'schema': {
                'type': 'object',
                'properties': {
                    'code': {'type': 'integer', 'example': 200},
                    'message': {'type': 'string', 'example': 'success'},
                    'data': {
                        'type': 'object',
                        'properties': {
                            'summary': {
                                'type': 'object',
                                'properties': {
                                    'total_items': {'type': 'integer', 'example': 25},
                                    'complete_items': {'type': 'integer', 'example': 20},
                                    'missing_items': {'type': 'integer', 'example': 3},
                                    'partial_items': {'type': 'integer', 'example': 2},
                                    'failed_checks': {'type': 'integer', 'example': 0},
                                    'completeness_rate': {'type': 'number', 'example': 80.0}
                                }
                            },
                            'check_results': {
                                'type': 'array',
                                'items': {
                                    'type': 'object',
                                    'properties': {
                                        'item_id': {'type': 'string', 'example': '1'},
                                        'chapter': {'type': 'string', 'example': '1.1'},
                                        'name': {'type': 'string', 'example': '工程概况'},
                                        'required': {'type': 'string', 'example': '是'},
                                        'item_type': {'type': 'string', 'example': '文本'},
                                        'ai_applicable': {'type': 'string', 'example': '是'},
                                        'description': {'type': 'string', 'example': '项目基本信息'},
                                        'completeness_status': {'type': 'string', 'example': '完整'},
                                        'completeness_score': {'type': 'number', 'example': 0.95},
                                        'evidence': {'type': 'string', 'example': '相关度0.850: 本工程为某住宅小区施工...'},
                                        'detailed_result': {'type': 'string', 'example': '1. 完整性状态：完整\n2. 完整性评分：0.95\n3. 分析说明：...'}
                                    }
                                }
                            },
                            'check_mode': {'type': 'string', 'example': 'item_by_item'},
                            'toc_list_filename': {'type': 'string', 'example': 'checklist.json'},
                            'document_filename': {'type': 'string', 'example': 'construction_plan.docx'},
                            'plan_id': {'type': 'string', 'example': 'abc123def456'},
                            'upload_folder': {'type': 'string', 'example': '20231201_143022_123'},
                            'created_time': {'type': 'string', 'example': '2023-12-01T14:30:22'}
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
                    'code': {'type': 'integer', 'example': 404},
                    'message': {'type': 'string', 'example': '检查结果不存在'},
                    'data': {'type': 'null'}
                }
            }
        },
        500: {
            'description': '服务器内部错误',
            'schema': {
                'type': 'object',
                'properties': {
                    'code': {'type': 'integer', 'example': 500},
                    'message': {'type': 'string', 'example': '获取结果失败'},
                    'data': {'type': 'null'}
                }
            }
        }
    }
}

# 获取任务列表的swagger配置
list_tasks_swagger = {
    'tags': ['异步结构检查'],
    'summary': '获取任务列表',
    'description': '获取异步结构检查任务列表，支持按状态过滤和分页',
    'parameters': [
        {
            'name': 'status',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': '任务状态过滤 (pending/processing/success/failed)',
            'enum': ['pending', 'processing', 'success', 'failed']
        },
        {
            'name': 'limit',
            'in': 'query',
            'type': 'integer',
            'required': False,
            'default': 20,
            'description': '返回记录数限制（1-100）',
            'minimum': 1,
            'maximum': 100
        }
    ],
    'responses': {
        200: {
            'description': '任务列表',
            'schema': {
                'type': 'object',
                'properties': {
                    'code': {'type': 'integer', 'example': 200},
                    'message': {'type': 'string', 'example': 'success'},
                    'data': {
                        'type': 'object',
                        'properties': {
                            'tasks': {
                                'type': 'array',
                                'items': {
                                    'type': 'object',
                                    'properties': {
                                        'id': {'type': 'integer', 'example': 1},
                                        'task_id': {'type': 'string', 'example': '20231201_143022_123'},
                                        'task_type': {'type': 'string', 'example': 'structure_check'},
                                        'status': {'type': 'string', 'example': 'success'},
                                        'callback_url': {'type': 'string', 'example': 'http://localhost:8080/dev-api/system/callback'},
                                        'created_time': {'type': 'string', 'example': '2023-12-01T14:30:22'},
                                        'updated_time': {'type': 'string', 'example': '2023-12-01T14:35:22'},
                                        'completed_time': {'type': 'string', 'example': '2023-12-01T14:35:22'}
                                    }
                                }
                            },
                            'total': {'type': 'integer', 'example': 15}
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
                    'code': {'type': 'integer', 'example': 500},
                    'message': {'type': 'string', 'example': '获取任务列表失败'},
                    'data': {'type': 'null'}
                }
            }
        }
    }
}
