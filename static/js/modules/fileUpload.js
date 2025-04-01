import { FileValidator } from '../utils/validators.js';
import { UIHelper } from '../utils/uiHelpers.js';
import { apiService } from '../utils/apiService.js';

export class FileUploader {
    constructor(config) {
        this.config = config;
        this.uploadedFileInfo = null;
        this.extractedFiles = [];
        this.currentMode = 'batch';
        this.jsonViewer = config.jsonViewer;

        this.init();
        this.toggleUploadMode(this.currentMode);
    }

    init() {
        this.setupEventListeners();
    }

    setupEventListeners() {
        // 单文件上传区域事件
        // this.setupDropZone(
        //     this.config.singleFileUpload,
        //     this.config.fileInput,
        //     this.handleSingleFileUpload.bind(this)
        // );

        // 压缩包上传区域事件
        this.setupDropZone(
            this.config.batchFileUpload,
            this.config.zipInput,
            this.handleZipFileUpload.bind(this)
        );

        // 模式切换事件
        // this.config.singleModeBtn.addEventListener('change', () => this.toggleUploadMode('single'));
        this.config.batchModeBtn.addEventListener('change', () => this.toggleUploadMode('batch'));
    }

    setupDropZone(container, input, handler) {
        if (!container || !input) return;

        container.addEventListener('click', () => input.click());
        
        container.addEventListener('dragover', (e) => {
            e.preventDefault();
            container.classList.add('dragover');
        });

        container.addEventListener('dragleave', () => {
            container.classList.remove('dragover');
        });

        container.addEventListener('drop', (e) => {
            e.preventDefault();
            container.classList.remove('dragover');
            handler(e.dataTransfer.files[0]);
        });

        input.addEventListener('change', (e) => {
            handler(e.target.files[0]);
        });
    }

    async handleSingleFileUpload(file) {
        try {
            FileValidator.validateSingleFile(file);
            // 如果是 JSON 文件，预览其内容
            if (file.type === 'application/json' || file.name.endsWith('.json')) {
                this.previewJsonFile(file);
            }
            await this.uploadFile(file, false);
        } catch (error) {
            UIHelper.showError(error.message, this.config.previewArea);
        }
    }

    // 添加 JSON 预览方法
    previewJsonFile(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const jsonData = JSON.parse(e.target.result);
                this.jsonViewer.show(jsonData);
            } catch (error) {
                console.error('Error parsing JSON:', error);
                UIHelper.showError('Invalid JSON file', this.config.previewArea);
            }
        };
        reader.readAsText(file);
    }

    async handleZipFileUpload(file) {
        try {
            FileValidator.validateZipFile(file);
            await this.uploadFile(file, true);
        } catch (error) {
            UIHelper.showError(error.message, this.config.previewArea);
        }
    }

    async uploadFile(file, isZip) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('mode', this.config.currentMode);

        UIHelper.showProgress(this.config.previewArea);

        try {
            const response = await (isZip ? 
                apiService.uploadZipFile(formData, this.updateProgress.bind(this)) :
                apiService.uploadFile(formData, this.updateProgress.bind(this))
            );
            // console.log(response.data)
            this.handleUploadSuccess(response.data, isZip);
        } catch (error) {
            this.handleUploadError(error);
        }
    }

    updateProgress(progressEvent) {
        UIHelper.updateProgress(progressEvent, this.config.previewArea);
    }

    handleUploadSuccess(data, isZip) {
        if (isZip) {
            this.extractedFiles = data.files;
            this.all_files_path = data.all_files_path;

            UIHelper.updateFileList(this.extractedFiles, this.config.previewArea);
        } else {
            this.handleSingleData(data)
        }
        
        this.config.analyzeBtn.disabled = !this.config.selectedModel;
    }


    handleSingleData(data) {
        this.uploadedFileInfo = data;
        UIHelper.updateSingleFile(data, this.config.previewArea, (deleteFilePath, newUploadData) => {
            // 处理删除后的重新上传
            if (newUploadData) {
                this.uploadedFileInfo = newUploadData;
                UIHelper.showSuccess(newUploadData, this.config.previewArea);
                // 如果是 JSON 文件，预览内容
                if (newUploadData.file_type === 'json') {
                    this.fetchAndPreviewJson(newUploadData.file_path);
                } else {
                    this.jsonViewer.hide();
                }
                // 更新按钮状态
                this.config.analyzeBtn.disabled = !this.config.selectedModel;
                
                // 触发自定义事件
                const event = new CustomEvent('fileUploaded', {
                    detail: { fileData: newUploadData }
                });
                window.dispatchEvent(event);
            } else {
                // 仅删除的情况
                this.uploadedFileInfo = null;
                this.config.analyzeBtn.disabled = true;
                this.jsonViewer.hide();
                if(this.config.templateContent) {
                    this.config.templateContent.value = '';
                }
            }
        });
    }


    // 添加获取并预览 JSON 文件的方法
    async fetchAndPreviewJson(filePath) {
        try {
            const response = await apiService.fetchJsonContent(filePath);
            if (response.data) {
                this.jsonViewer.show(response.data);
            }
        } catch (error) {
            console.error('Error fetching JSON content:', error);
            UIHelper.showError('Error loading JSON preview', this.config.previewArea);
        }
    }

    handleUploadError(error) {
        UIHelper.showError(error.message, this.config.previewArea);
        this.config.analyzeBtn.disabled = true;
        this.uploadedFileInfo = null;
    }

    toggleUploadMode(mode) {
        this.currentMode = mode;
        
        if (mode === 'single') {
            this.config.singleFileUpload.style.display = 'block';
            this.config.batchFileUpload.style.display = 'none';
            this.clearBatchUploadState();
        } else {
            this.config.singleFileUpload.style.display = 'none';
            this.config.batchFileUpload.style.display = 'block';
            this.clearSingleUploadState();
        }

        this.config.previewArea.innerHTML = '';
        this.config.analyzeBtn.disabled = true;
        this.jsonViewer.hide(); // 切换模式时隐藏 JSON 预览
    }

    clearSingleUploadState() {
        this.uploadedFileInfo = null;
        this.config.fileInput.value = '';
        this.jsonViewer.hide();
    }

    clearBatchUploadState() {
        this.extractedFiles = [];
        this.config.zipInput.value = '';
        this.jsonViewer.hide();
    }

    getUploadedFileInfo() {
        return this.uploadedFileInfo;
    }

    // 获取压缩包中的所有文件信息
    getExtractedFiles() {
        return this.extractedFiles;
    }

    // 获取所有文件的路径
    getAllFilesPath() {
        return this.all_files_path;
    }

    // 获取当前上传模式
    getCurrentMode() {
        return 'batch';
    }

    // 获取当前上传的文件信息（统一接口，根据模式返回不同的数据）
    getCurrentFileInfo() {
        if (this.currentMode === 'single') {
            return this.uploadedFileInfo;
        } else {
            return {
                files: this.extractedFiles,
                all_files_path: this.all_files_path
            };
        }
    }
}
