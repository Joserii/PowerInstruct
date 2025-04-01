from flask import Flask, send_from_directory
from app.middleware.request_filter import RequestFilter
from app.middleware.error_handler import ErrorHandler
import logging
import os
from config.settings import UPLOAD_FOLDER, TEMPLATE_FOLDER, STATIC_FOLDER

def create_app():

    app = Flask(__name__,
                static_folder=STATIC_FOLDER,
                template_folder=TEMPLATE_FOLDER)
    
    # 创建必要的文件夹
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(TEMPLATE_FOLDER, exist_ok=True)
    
    # 配置日志
    if app.debug:
        logging.basicConfig(level=logging.DEBUG)
    
    # 配置日志
    logging.getLogger('werkzeug').addFilter(RequestFilter())
    
    # 注册错误处理器
    ErrorHandler.register_handlers(app)
    
    # 注册主页路由
    @app.route('/')
    def index():
        return send_from_directory(TEMPLATE_FOLDER, 'index.html')
    
    # 注册路由蓝图
    from app.routes import file_routes, analysis_routes, template_routes
    app.register_blueprint(file_routes.bp)
    app.register_blueprint(analysis_routes.bp)
    app.register_blueprint(template_routes.bp)
    
    # 添加CORS支持
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE')
        return response
        
    return app
