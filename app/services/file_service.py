from flask import Flask, request, jsonify
import os, json
from pathlib import Path
import zipfile
from config.settings import UPLOAD_FOLDER, DATA_FOLDER
from utils.file_utils import allowed_single_file, generate_unique_filename
from utils.logger import logger
from utils.file_utils import *

class FileService:
    def __init__(self):
        self.upload_folder = UPLOAD_FOLDER

    def handle_file_upload(self, request):
        try:
            logger.info("Starting file upload process")
            # 检查文件是否上传
            if 'file' not in request.files:
                logger.warning("No file uploaded in request")
                return jsonify({'error': 'No file uploaded'}), 400
            
            file = request.files['file']
            # 检查文件名是否为空
            if file.filename == '':
                logger.warning("Empty filename received")
                return jsonify({'error': 'No selected file'}), 400

            filename = file.filename
            logger.info(f"Processing file: {filename}")
            
            if file and allowed_single_file(filename):
                # 获取原始文件扩展名
                original_filename = filename
                _, original_extension = os.path.splitext(original_filename)

                # 生成唯一文件名，保留原始扩展名
                unique_filename = generate_unique_filename(original_filename, existing_extension=original_extension)
                # 构建保存路径
                save_path = os.path.join(UPLOAD_FOLDER, unique_filename)
                mode = request.form.get('mode', 'prompt')
                file.save(save_path)
                logger.info(f"File successfully saved: {unique_filename}")

                return jsonify({
                    'message': 'File uploaded successfully',
                    'unique_filename': unique_filename,
                    'original_filename': original_filename,
                    'save_path': save_path,
                    'file_size': os.path.getsize(save_path)
                }), 200
            
        except Exception as e:
            logger.error(f"Analysis error: {str(e)}")
            return jsonify({
                'error': f'File save failed: {str(e)}'
            }), 500
        
    def handle_zip_upload(self, request):
        try:
            if 'file' not in request.files:
                return jsonify({'success': False, 'error': 'No file uploaded'})
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'success': False, 'error': 'No selected file'})
            def decode_zip_filename(name):
                encodings = ['utf-8', 'gbk', 'gb18030', 'cp936']
                raw_bytes = name.encode('cp437')
                
                for encoding in encodings:
                    try:
                        decoded = raw_bytes.decode(encoding)
                        return decoded
                    except:
                        continue
                return name

            def is_system_file(filename):
                return (filename.startswith('__MACOSX') or 
                    filename.startswith('._') or 
                    filename.startswith('.') or 
                    '/.DS_Store' in filename)

            if file and allowed_zip_file(file.filename):
                # 获取原始文件扩展名
                original_filename = file.filename
                _, original_extension = os.path.splitext(original_filename)

                # 生成唯一文件名，保留原始扩展名
                unique_filename = generate_unique_filename(original_filename, existing_extension=original_extension)
                # 构建保存路径
                save_zip_path = os.path.join(UPLOAD_FOLDER, unique_filename)
                folder_name = Path(save_zip_path).stem
                save_path = os.path.join(os.path.dirname(save_zip_path), folder_name)

                file.save(save_zip_path)
                logger.info(f"File successfully saved: {save_zip_path}")

                # 解压文件
                extracted_files = []

                with zipfile.ZipFile(save_zip_path, 'r') as zip_ref:
                    for name in zip_ref.namelist():
                        try:
                            # 解码文件名
                            real_name = decode_zip_filename(name)                    
                            # 跳过系统文件
                            if is_system_file(real_name):
                                continue
                            # 检查文件类型
                            if not real_name.lower().endswith(('.json', '.xml', '.txt')):
                                continue
                            # 构建解压路径
                            extract_path = os.path.join(save_path, real_name)
                            os.makedirs(os.path.dirname(extract_path), exist_ok=True)
                            with zip_ref.open(name) as source, open(extract_path, 'wb') as target:
                                target.write(source.read())

                            if os.path.isfile(extract_path):
                                extracted_files.append({
                                    'name': real_name,
                                    'path': extract_path,
                                    'relative_path': os.path.relpath(extract_path, save_path),
                                    'gt': real_name.split('/')[1]
                                })
                            
                        except Exception as e:
                            print(f"Error processing {name}: {str(e)}")
                            continue
                
                if not extracted_files:
                    return jsonify({
                        'success': False,
                        'error': 'No valid files found in archive'
                    })
                
                all_files, all_files_path = self._merge_train_data(extracted_files, unique_filename)


                return jsonify({
                    'success': True,
                    'message': f'Successfully extracted {len(extracted_files)} files',
                    'unique_filename': unique_filename,
                    'original_filename': original_filename,
                    'save_path': save_path,
                    'file_size': os.path.getsize(save_path),
                    'files': extracted_files,
                    'all_files_path': all_files_path
                }), 200

        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            })

    def _merge_train_data(self, extracted_files, unique_zipname):
        try:
            root_path = os.path.join(DATA_FOLDER, 'test_data')
            os.makedirs(root_path, exist_ok=True)

            total_json_file = []
            for file in extracted_files:
                if file['name'].endswith('.json'):
                    with open(file['path'], 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        data['gt'] = file['gt']
                        total_json_file.append(data)
            unique_zipname = unique_zipname.split('.')[0]
            with open(os.path.join(root_path, f'{unique_zipname}.json'), 'w', encoding='utf-8') as f:
                json.dump(total_json_file, f, ensure_ascii=False, indent=4)
            
            total_json_path = os.path.join(root_path, f'{unique_zipname}.json')
            return total_json_file, total_json_path
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            })
        
    def handle_file_deletion(self, file_path):
        """删除指定文件的路由"""
        try:
            logger.info(f"Starting file deletion process for: {file_path}")
            
            # 获取文件名（去除路径）
            filename = os.path.basename(file_path)
            
            # 构建完整的文件路径
            full_path = os.path.join(UPLOAD_FOLDER, filename)
            
            # 规范化路径
            normalized_path = os.path.normpath(full_path)
            normalized_upload_folder = os.path.normpath(UPLOAD_FOLDER)
            
            # 安全检查：确保文件路径在上传目录内
            if not normalized_path.startswith(normalized_upload_folder):
                logger.warning(f"Attempted to delete file outside upload directory: {file_path}")
                return jsonify({
                    'status': 'error',
                    'message': '非法的文件路径'
                }), 403

            # 检查文件是否存在
            if not os.path.exists(normalized_path):
                logger.warning(f"File not found: {file_path}")
                return jsonify({
                    'status': 'error',
                    'message': '文件不存在'
                }), 404

            # 检查文件是否在允许删除的目录中
            if not normalized_path.startswith(normalized_upload_folder):
                logger.warning(f"Attempted to delete file outside upload directory: {file_path}")
                return jsonify({
                    'status': 'error',
                    'message': '无权删除此文件'
                }), 403

            # 删除文件
            os.remove(normalized_path)
            logger.info(f"File successfully deleted: {filename}")

            return jsonify({
                'status': 'success',
                'message': '文件删除成功',
                'deleted_file': filename
            }), 200

        except Exception as e:
            logger.error(f"File deletion error: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': f'删除文件失败: {str(e)}'
            }), 500


    # file_service.py
    def load_json_batch(self):
        try:
            # 从查询参数获取文件路径
            file_path = request.args.get('path')
            print(f"Requested file path: {file_path}")  # 调试日志
            
            if not file_path:
                return jsonify({
                    'code': 400,
                    'message': 'Missing file path parameter'
                }), 400

            # 检查文件是否存在
            if not os.path.exists(file_path):
                return jsonify({
                    'code': 404,
                    'message': f'File not found: {file_path}'
                }), 404

            # 读取并解析 JSON 文件
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                return jsonify({
                    'code': 200,
                    'data': data
                })
                
            except json.JSONDecodeError:
                return jsonify({
                    'code': 400,
                    'message': 'Invalid JSON file'
                }), 400
                
            except Exception as e:
                return jsonify({
                    'code': 500,
                    'message': f'Error reading file: {str(e)}'
                }), 500

        except Exception as e:
            return jsonify({
                'code': 500,
                'message': f'Server error: {str(e)}'
            }), 500