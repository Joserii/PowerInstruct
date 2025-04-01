from flask import jsonify, request
from utils.api_utils import api_request
from utils.logger import logger
from utils.system_prompt import *
from io import StringIO
from utils.run_python_utils import TimeoutException, run_code, process_markdown_code, format_output, get_executed_python_code
from utils.prompt_template.codegen_prompt import merge_codegen_template_en
from client.powerInstruct import run_single_data

class AnalysisService:
    def __init__(self):
        self.templates = load_user_templates()
    
    # 数据清洗
    def data_cleaning(self, data):
        try:
            data = request.json or {}
            raw_data = data.get('raw_data', [])
            return jsonify({
                'cleaned_data': raw_data,
                'message': 'successfully cleaned data'
            }), 200
        
        except Exception as e:
            logger.error(f"Data cleaning failed: {str(e)}", exc_info=True)
            return jsonify({'code': 500, 'message': str(e)}), 500

    def analyze_fault(self, data):
        """故障分析接口"""
        try:
            # 记录完整的请求数据，用于调试
            logger.info(f"Received analysis request: {request.json}")
            
            # 从请求中获取参数
            data = request.json or {}
            filepath = data.get('filepath', '')
            file_content = data.get('file_content', '')
            mode = data.get('mode', 'prompt')
            template = data.get('template', '')
            model_id = data.get('model_id', 'qwen2.5-7b-instruct')

            logger.info(f"Analysis parameters - Mode: {mode}, File: {filepath}")
            
            # 读取文件内容
            try:
                logger.info(f"Reading file content from: {filepath}")
                logger.info(f"File content read successfully, length: {len(file_content)}")
            except Exception as e:
                logger.error(f"File read error: {str(e)}")
                return jsonify({
                    'code': 500,
                    'message': f'文件读取错误: {str(e)}'
                }), 500
            
            logger.info(f"Starting analysis with mode: {mode}")
            logger.info(f"Model ID: {model_id}")

            templates = load_user_templates()

            # TODO 根据模式选择分析方法
            # 需要实现以下两种分析方法
            if mode == 'prompt':
                current_template = template or templates['prompt']
                result = self._analyze_with_prompt(file_content=file_content, system_prompt=current_template, model_id=model_id)
            elif mode == 'codegen':
                current_template = template or templates['codegen']
                result = self._analyze_with_codegen(file_content, codegen_prompt=current_template, model_id=model_id)
            elif mode == 'prompt-codegen':
                current_template = template if type(template) == str else templates['prompt']
                result = self._analyze_with_prompt(file_content=file_content, system_prompt=current_template, model_id=model_id)
            else:
                logger.error(f"Unsupported analysis mode: {mode}")
                result = {
                    'error': f'不支持的分析模式: {mode}'
                }

            return jsonify({
                'code': 200,
                'ai_response': result.get('ai_response', ''),
                'mode': mode,
                'token_prompt': result.get('token_prompt', ''),
                'token_compli': result.get('token_compli', '')
            })
        
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            return jsonify({
                'code': 500,
                'message': str(e)
            }), 500
            
    def execute_code(self, data):
        try:
            # 获取代码
            code = request.json.get('code', '')             # markdown 格式的代码
            input_path = request.json.get('input_path', '') # 输入数据路径
            print("Code: ", code)
            print("Input path: ", input_path)
            logger.debug(f"Original code: {code}")
            logger.debug(f"Input path: {input_path}")
            final_code = process_markdown_code(code, input_path)
            logger.debug(f"Processed code: {final_code}")
            # 捕获输出
            output = StringIO()
            # 执行代码
            try:
                result = run_code(code=final_code, output=output)
                logger.debug(f"Code execution result: {result}")
            except Exception as e:
                logger.error(f"Code execution error: {str(e)}")
                raise

            stdout_content = output.getvalue()
            logger.debug(f"Stdout content: {stdout_content}")
            
            formatted_output = format_output(result)
            logger.debug(f"Formatted output: {formatted_output}")
            
            
            return jsonify({
                'code': 200,
                'success': True,
                'result': str(formatted_output),
                'stdout': stdout_content,
                'executed_code': final_code
            })
            
        except TimeoutException as e:
            return jsonify({
                'code': 500,
                'success': False,
                'error': '代码执行超时'
            })
        except Exception as e:
            return jsonify({
                'code': 500,
                'success': False,
                'error': str(e),
                'executed_code': final_code if 'final_code' in locals() else None
            })
        
    def execute_batch(self, data):
        try:
            raw_code = request.json.get('code', '')             # markdown 格式的代码
            batch_data_path = request.json.get('input_path', '') # 输入数据路径
            executed_code = get_executed_python_code(raw_code)
            with open(batch_data_path, "r", encoding='utf-8') as f:
                batch_data = json.load(f)
            
            success_results = []
            failed_results = []
            total = len(batch_data)
            success_count = 0
            failure_count = 0
            
            
            for i, data in enumerate(batch_data):
                try:
                    result = run_single_data(executed_code=executed_code, input_data=data)
                    success_results.append({
                        "index": i-1,
                        "input": data,
                        "result": result
                    })
                    success_count += 1
                except Exception as e:
                    failure_count += 1
                    error_info = {
                        "index": i-1,
                        "input": data,
                        "error": str(e),
                        "error_type": type(e).__name__
                    }
                    failed_results.append(error_info)
                    logger.error(f"处理第 {i} 条数据失败: {str(e)}")
                    continue  # 继续处理下一条数据
                    # 统计信息
            
            statistics = {
                "total": total,
                "success": success_count,
                "failure": failure_count,
                "success_rate": f"{(success_count/total)*100:.2f}%"
            }

            # 保存最终结果
            final_results = {
                "success_results": success_results,
                "failed_results": failed_results,
                "statistics": statistics
            }
            return jsonify({
                    'code': 200,
                    'success': True,
                    'result': final_results,
                    'statistics': statistics
                })
        except TimeoutException as e:
            return jsonify({
                'code': 500,
                'success': False,
                'error': 'Timeout error'
            })
        except Exception as e:
            return jsonify({
                'code': 500,
                'success': False,
                'error': str(e),
                'executed_code': executed_code if 'executed_code' in locals() else None
            })

    def _analyze_with_prompt(self, file_content, system_prompt, model_id):
        """
        Prompt模式分析
        :param content: 文件内容
        :param system_prompt: 系统提示词
        :return: 分析结果
        """
        system_prompt = str(system_prompt['prompt'])
        final_prompt = system_prompt + file_content
        try:
            logger.info(f"Starting prompt analysis \nSystem prompt length: {len(system_prompt)} \Content length: {len(file_content)}")
            # import ipdb; ipdb.set_trace()
            messages, token_prompt, token_compli = api_request(prompt=final_prompt, model_name=model_id)
            # 实现具体的 Prompt 分析逻辑
            logger.info("Analysis completed successfully")
            result = {
                'mode': 'prompt',
                'template': final_prompt,
                'model_id': model_id,
                'content_length': len(final_prompt),
                'ai_response': messages,
                'token_prompt': token_prompt,
                'token_compli': token_compli
            }
            logger.info(f"Analysis result: {messages}")
            logger.info(f"Input token: {token_prompt}")
            logger.info(f"Output token: {token_compli}")

            return result

        except Exception as e:
            return {'error': str(e)}

    def _analyze_with_codegen(self, file_content, codegen_prompt, model_id):
        """
        CodeGen模式分析
        :param content: 文件内容
        :param template: 生成模板
        :return: 分析结果
        """
        final_prompt = codegen_prompt + file_content
        try:
            # 实现具体的 CodeGen 分析逻辑
            logger.info(f"Starting codegen analysis \nSystem prompt length: {len(codegen_prompt)} \Content length: {len(file_content)}")
            
            messages, token_prompt, token_compli = api_request(prompt=final_prompt, model_name=model_id)
            logger.info("Analysis completed successfully")
            result = {
                'mode': 'codegen',
                'template': file_content,
                'model_id': model_id,
                'content_length': len(final_prompt),
                'ai_response': messages,
                'token_prompt': token_prompt,
                'token_compli': token_compli
            }
            logger.info(f"Analysis result: {messages}")
            logger.info(f"Input token: {token_prompt}")
            logger.info(f"Output token: {token_compli}")

            return result
        except Exception as e:
            return {'error': str(e)}
    
    def merge_codegen_template(self, raw_data, seed_content, template):
        try:
            # 解析种子内容
            # print("Seed content: ", seed_content)
            # print("Template: ", template)
            # print("Raw data: ", raw_data)
            seed_data = json.loads(seed_content) if isinstance(seed_content, str) else seed_content
            
            # 在这里实现模板合并逻辑
            # 例如：将种子数据插入到模板中的适当位置
            merged_content = merge_codegen_template_en(raw_data, seed_data)
            print("Merged content: ", merged_content)
            
            return merged_content
            
        except Exception as e:
            raise Exception(f'Template merge failed: {str(e)}')
