from flask import jsonify, request
from utils.api_utils import api_request
from utils.logger import logger
from utils.system_prompt import *
from io import StringIO
from utils.run_python_utils import TimeoutException, run_code, process_markdown_code, format_output, get_executed_python_code
from utils.prompt_template.codegen_prompt import merge_codegen_template_en
from client.powerInstruct import run_single_data



from flask import request, jsonify
import logging

logger = logging.getLogger(__name__)



class AnalysisService:
    def __init__(self):
        self.templates = load_user_templates()
    
    # Data cleaning
    def data_cleaning(self, data):
        try:
            # Get JSON data
            data = request.json or {}
            raw_data = data.get('raw_data', [])

            if not isinstance(raw_data, list):
                return jsonify({'code': 400, 'message': 'Invalid input format: raw_data should be a list'}), 400

            cleaned_data = []
            for item in raw_data:
                if isinstance(item, dict):
                    # Clean each dictionary item
                    cleaned_item = {k: self.clean_value(v) for k, v in item.items()}
                    cleaned_data.append(cleaned_item)
                else:
                    logger.warning(f"Skipping non-dict item: {item}")

            return jsonify({
                'cleaned_data': cleaned_data,
                'message': 'Successfully cleaned data'
            }), 200

        except Exception as e:
            logger.error(f"Data cleaning failed: {str(e)}", exc_info=True)
            return jsonify({'code': 500, 'message': str(e)}), 500

    def clean_value(self, value):
        """Clean a single value"""
        if isinstance(value, str):
            value = value.strip()           # Remove leading and trailing spaces
            value = value.replace("\n", " ").replace("\r", "")  # Remove line breaks
        elif isinstance(value, (int, float)):
            pass        # The value type remains unchanged
        elif value is None:
            value = ""  # Replace None with an empty string
        return value

    def analyze_fault(self, data):
        """Fault Analysis Interface"""
        try:
            # Record complete request data for debugging
            logger.info(f"Received analysis request: {request.json}")
            
            # Get parameters from the request
            data = request.json or {}
            filepath = data.get('filepath', '')
            file_content = data.get('file_content', '')
            mode = data.get('mode', 'prompt')
            template = data.get('template', '')
            model_id = data.get('model_id', 'qwen2.5-7b-instruct')

            logger.info(f"Analysis parameters - Mode: {mode}, File: {filepath}")
            
            # Read file contents
            try:
                logger.info(f"Reading file content from: {filepath}")
                logger.info(f"File content read successfully, length: {len(file_content)}")
            except Exception as e:
                logger.error(f"File read error: {str(e)}")
                return jsonify({
                    'code': 500,
                    'message': f'File read error: {str(e)}'
                }), 500
            
            logger.info(f"Starting analysis with mode: {mode}")
            logger.info(f"Model ID: {model_id}")

            templates = load_user_templates()

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
                    'error': f'Unsupported analysis mode: {mode}'
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
            code = request.json.get('code', '')             # Code in markdown format
            input_path = request.json.get('input_path', '') # Input data path
            print("Code: ", code)
            print("Input path: ", input_path)
            logger.debug(f"Original code: {code}")
            logger.debug(f"Input path: {input_path}")
            final_code = process_markdown_code(code, input_path)
            logger.debug(f"Processed code: {final_code}")
            # Capture output
            output = StringIO()
            # Execute code
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
                'error': 'Code execution timeout'
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
            raw_code = request.json.get('code', '')
            batch_data_path = request.json.get('input_path', '')
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
                    logger.error(f"Failed to process the {i}th data: {str(e)}")
                    continue  # 继续处理下一条数据
                    # 统计信息
            
            statistics = {
                "total": total,
                "success": success_count,
                "failure": failure_count,
                "success_rate": f"{(success_count/total)*100:.2f}%"
            }

            # Save the final result
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
        Prompt mode analysis
        :param content: file content
        :param system_prompt: system prompt words
        :return: analysis results
        """
        system_prompt = str(system_prompt['prompt'])
        final_prompt = system_prompt + file_content
        try:
            logger.info(f"Starting prompt analysis \nSystem prompt length: {len(system_prompt)} \Content length: {len(file_content)}")
            messages, token_prompt, token_compli = api_request(prompt=final_prompt, model_name=model_id)
            # Implement specific prompt analysis logic
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
        CodeGen mode analysis
        :param content: file content
        :param template: generated template
        :return: analysis results
        """
        final_prompt = codegen_prompt + file_content
        try:
            # Implement specific CodeGen analysis logic
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
            seed_data = json.loads(seed_content) if isinstance(seed_content, str) else seed_content
            
            # Implement template merging logic here
            # For example: insert seed data into the appropriate position in the template
            merged_content = merge_codegen_template_en(raw_data, seed_data)
            
            return merged_content
            
        except Exception as e:
            raise Exception(f'Template merge failed: {str(e)}')
