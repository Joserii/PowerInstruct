document.addEventListener('DOMContentLoaded', function() {
    // const fileUploadContainer = document.getElementById('file-upload-container');
    const singleModeBtn = document.getElementById('single-mode');
    const batchModeBtn = document.getElementById('batch-mode');
    const singleFileUpload = document.getElementById('single-file-upload');
    const batchFileUpload = document.getElementById('batch-file-upload');
    const fileInput = document.getElementById('file-input');
    const zipInput = document.getElementById('zip-input');
    const previewArea = document.getElementById('preview-area');
    const promptModeBtn = document.getElementById('prompt-mode');
    const codegenModeBtn = document.getElementById('codegen-mode');
    const templateTitle = document.getElementById('template-title');
    const templateContent = document.getElementById('template-content');
    const targetData = document.getElementById('target-data');
    const analyzeBtn = document.getElementById('analyze-btn');
    const executeCodeBtn = document.getElementById('execute-code-btn');
    const executeResult = document.getElementById('execute-result');
    // 模型选择按钮
    let selectedModel = null;

    // 上传模式, 默认为非压缩模式
    let isZipMode = false;
    let extractedFiles = [];
    const toggleUploadBtn = document.getElementById('toggle-upload-type');

    // prompt 模板内容
    let promptTemplate = '';
    let codegenTemplate = '';


    let currentMode = 'prompt';
    let uploadedFile = null;
    let uploadedFileInfo = null;
    let currentTemplate = '';
    let analyzeData = null;


    // 添加切换上传模式的函数
    function toggleUploadMode() {
        if (singleModeBtn.checked) {
            singleFileUpload.style.display = 'block';
            batchFileUpload.style.display = 'none';
            // 清除批量上传的状态
            clearBatchUploadState();
        } else {
            singleFileUpload.style.display = 'none';
            batchFileUpload.style.display = 'block';
            // 清除单文件上传的状态
            clearSingleUploadState();
        }
        // 清除预览区域
        if (previewArea) {
            previewArea.innerHTML = '';
        }
        // 禁用分析按钮
        if (analyzeBtn) {
            analyzeBtn.disabled = true;
        }
    }
    
    function clearBatchUploadState() {
        const fileList = document.querySelector('.file-list-content ul');
        if (fileList) {
            fileList.innerHTML = '';
        }
        document.querySelector('.file-list-header').classList.add('d-none');
    }

    function clearSingleUploadState() {
        uploadedFileInfo = null;
    }


    // 修改 validateFile 函数
    function validateSingleFile(file) {
        if (!file) throw new Error('No file selected');

        const allowedTypes = ['application/json', 'text/xml', 'text/plain', 'application/xml'];
        if (!allowedTypes.includes(file.type)) {
            throw new Error('Invalid file type. Please upload JSON, XML, or TXT files.');
        }
        if (file.size > 10 * 1024 * 1024) {
            throw new Error('File size exceeds 10MB limit.');
        }
    }

    function validateZipFile(file) {
        if (!file) throw new Error('No file selected');
        
        const allowedTypes = ['application/zip', 'application/x-rar-compressed', 'application/x-7z-compressed'];
        if (!allowedTypes.includes(file.type)) {
            throw new Error('Invalid archive type. Please upload ZIP, RAR, or 7Z files.');
        }
        
        if (file.size > 50 * 1024 * 1024) {
            throw new Error('File size exceeds 50MB limit.');
        }
    }


    // 修改 handleFileUpload 函数
    function handleFileUpload(file) {
        try {
            if (!file) {
                throw new Error('No file selected');
            }
            validateFile(file);

            const formData = new FormData();
            formData.append('file', file);
            formData.append('mode', currentMode);

            // 显示上传进度
            previewArea.innerHTML = `
                <div class="progress mb-3">
                    <div class="progress-bar" role="progressbar" style="width: 0%"></div>
                </div>
                <div class="upload-status">准备上传...</div>
            `;

            const progressBar = previewArea.querySelector('.progress-bar');
            const statusDiv = previewArea.querySelector('.upload-status');

            const uploadEndpoint = isZipMode ? '/upload_zip' : '/upload';
            
            axios.post(uploadEndpoint, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                },
                onUploadProgress: (progressEvent) => {
                    const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
                    progressBar.style.width = percentCompleted + '%';
                    progressBar.textContent = percentCompleted + '%';
                    statusDiv.textContent = '上传中...';
                }
            })
            .then(response => {
                if (response.status === 200) {
                    if (isZipMode) {
                        // 处理压缩包上传响应
                        extractedFiles = response.data.files;
                        displayFileList(extractedFiles);
                    } else {
                        // 处理单文件上传响应
                        uploadedFileInfo = response.data;
                        statusDiv.innerHTML = `
                            <div class="alert alert-success">
                                Upload Successful: ${uploadedFileInfo.original_filename}<br>
                                Size: ${(uploadedFileInfo.file_size / 1024).toFixed(2)} KB<br>
                                Server Filename: ${uploadedFileInfo.unique_filename}
                            </div>
                        `;
                    }
                    analyzeBtn.disabled = !selectedModel;
                } else {
                    throw new Error(response.data.message || '文件上传失败');
                }
            })
            .catch(error => {
                statusDiv.innerHTML = `
                    <div class="alert alert-danger">
                        ${error.message}
                    </div>
                `;
                analyzeBtn.disabled = true;
                uploadedFileInfo = null;
            });

        } catch (error) {
            previewArea.innerHTML = `
                <div class="alert alert-danger">
                    ${error.message}
                </div>
            `;
            analyzeBtn.disabled = true;
            uploadedFileInfo = null;
        }
    }




    // 添加文件列表显示函数
    function displayFileList(files) {
        const fileListHtml = `
            <div class="file-list mt-3">
                <h6>已解压文件列表：</h6>
                <div class="list-group">
                    ${files.map(file => `
                        <div class="list-group-item list-group-item-action d-flex justify-content-between align-items-center">
                            <span class="file-name">${file.name}</span>
                            <button class="btn btn-sm btn-primary select-file" data-path="${file.path}">
                                选择
                            </button>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
        
        previewArea.innerHTML = fileListHtml;

        // 添加文件选择事件
        document.querySelectorAll('.select-file').forEach(btn => {
            btn.addEventListener('click', function() {
                const selectedFile = extractedFiles.find(f => f.path === this.dataset.path);
                if (selectedFile) {
                    uploadedFileInfo = {
                        original_filename: selectedFile.name,
                        unique_filename: selectedFile.name,
                        save_path: selectedFile.path,
                        file_size: 0  // 如果需要文件大小，可以从后端获取
                    };
                    // 更新选中状态
                    document.querySelectorAll('.select-file').forEach(b => {
                        b.classList.remove('btn-success');
                        b.classList.add('btn-primary');
                        b.textContent = '选择';
                    });
                    this.classList.remove('btn-primary');
                    this.classList.add('btn-success');
                    this.textContent = '已选择';
                    analyzeBtn.disabled = !selectedModel;
                }
            });
        });
    }

    
    // 修改 fetchTemplates 函数
    function fetchTemplates(mode) {
        axios.get('/templates')
        .then(response => {
            const templates = response.data.templates;
            // console.log('Templates:', templates);s
            if (mode === 'prompt') {
                templateTitle.textContent = 'Prompt Template (Editable)';
                templateContent.value = templates.prompt;
                promptTemplate = templates.prompt;
            } else if (mode === 'codegen') {
                templateTitle.textContent = 'Codegen Template (Editable)';
                templateContent.value = templates.codegen;
                codegenTemplate = templates.codegen;
            }
            currentTemplate = templates[mode];
            // console.log('Current Template:', currentTemplate);
        })
        .catch(error => {
            console.error('Error fetching templates:', error);
            templateContent.value = 'Error fetching templates';
        });
    }


    // 添加保存模板的函数
    function saveTemplate() {
        const currentTemplateContent = templateContent.value;
        const templateType = currentMode;  // 'prompt' 或 'codegen'
        
        axios.post('/save_template', {
            type: templateType,
            content: currentTemplateContent
        })
        .then(response => {
            if (response.data.success) {
                // 更新当前模板
                if (templateType === 'prompt') {
                    promptTemplate = currentTemplateContent;
                } else if (templateType === 'codegen') {
                    codegenTemplate = currentTemplateContent;
                }
                currentTemplate = currentTemplateContent;
                
                // 显示成功消息
                alert('模板保存成功！');
            } else {
                alert('保存失败：' + response.data.message);
            }
        })
        .catch(error => {
            console.error('Error saving template:', error);
            alert('保存失败：' + error.message);
        });
    }

    function executeCode() {
        executeCodeBtn.addEventListener('click', () => {
            // 状态检查
            if (!targetData.textContent) {
                executeResult.textContent = 'No code to execute';
                return;
            }
            if (!analyzeData || !analyzeData.filepath) {
                executeResult.textContent = 'Please analyze file first';
                return;
            }

            const pythonCode = targetData.textContent;
            const inputJsonPath = analyzeData.filepath;

            // console.log('Executing code:', pythonCode);
            // console.log('Input file:', inputJsonPath);

            // 显示加载状态
            executeResult.textContent = 'Executing...';
            axios({
                method: 'post',
                url: '/execute',
                headers: {
                    'Content-Type': 'application/json',
                },
                data: {
                    code: pythonCode,
                    input_path: inputJsonPath,
                }
            })
            .then(response => {
                // console.log('完整响应:', response);
                // console.log('标准输出:', response.data);
                // console.log('result:', response.data.result);
                if(response.status == 200) {
                    executeResult.textContent = response.data.result;
                } else {
                    executeResult.textContent = response.data.message || 'Execute error';
                }
            })
            .catch(error => {
                console.error('Error executing code:', error);
                executeResult.textContent = `Error: ${error.message}`;
            });
        });
    }


    function setupFileUploadHandlers() {

        // 单文件上传处理
        if (singleFileUpload && fileInput) {
            setupUploadHandler(singleFileUpload, fileInput, handleSingleFileUpload);
        }

        // 批量文件上传处理
        if (batchFileUpload && zipInput) {
            setupUploadHandler(batchFileUpload, zipInput, handleZipFileUpload);
        }

        // 切换按钮事件
        singleModeBtn.addEventListener('change', toggleUploadMode);
        batchModeBtn.addEventListener('change', toggleUploadMode);
    }

    function setupUploadHandler(container, input, handleFunction) {
        if (!container) return; // 添加安全检查
        // 文件拖拽和选择逻辑
        container.addEventListener('click', () => input.click());
        container.addEventListener('dragover', (e) => {
            e.preventDefault();
            container.style.backgroundColor = '#f0f0f0';
        });
        container.addEventListener('dragleave', (e) => {
            container.style.backgroundColor = 'transparent';
        });
        container.addEventListener('drop', (e) => {
            e.preventDefault();
            container.style.backgroundColor = 'transparent';
            handleFunction(e.dataTransfer.files[0]);
        });
        input.addEventListener('change', (e) => {
            handleFunction(e.target.files[0]);
        });
    }

    function handleSingleFileUpload(file) {
        try {
            validateSingleFile(file);
            uploadFile(file, '/upload');
        } catch (error) {
            showError(error.message);
        }
    }

    function handleZipFileUpload(file) {
        try {
            validateZipFile(file);
            uploadFile(file, '/upload_zip');
        } catch (error) {
            showError(error.message);
        }
    }


    function uploadFile(file, endpoint) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('mode', currentMode);

        showProgress();

        axios.post(endpoint, formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
            onUploadProgress: updateProgress
        })
        .then(handleUploadResponse)
        .catch(handleUploadError);
    }


    function showProgress() {
        previewArea.innerHTML = `
            <div class="progress mb-3">
                <div class="progress-bar" role="progressbar" style="width: 0%"></div>
            </div>
            <div class="upload-status">准备上传...</div>
        `;
    }

    function updateProgress(progressEvent) {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        const progressBar = previewArea.querySelector('.progress-bar');
        const statusDiv = previewArea.querySelector('.upload-status');
        
        if (progressBar && statusDiv) {
            progressBar.style.width = percentCompleted + '%';
            progressBar.textContent = percentCompleted + '%';
            statusDiv.textContent = '上传中...';
        }
    }
    

    function handleUploadResponse(response) {
        if (response.status === 200) {
            if (response.data.files) {
                // 处理压缩包上传响应
                displayFileList(response.data.files);
            } else {
                // 处理单文件上传响应
                uploadedFileInfo = response.data;
                showUploadSuccess(uploadedFileInfo);
            }
            analyzeBtn.disabled = !selectedModel;
        } else {
            throw new Error(response.data.message || '文件上传失败');
        }
    }


    function handleUploadError(error) {
        showError(error.message || '上传失败');
        analyzeBtn.disabled = true;
        uploadedFileInfo = null;
    }

    function showUploadSuccess(fileInfo) {
        previewArea.innerHTML = `
            <div class="alert alert-success">
                Upload Successful: ${fileInfo.original_filename}<br>
                Size: ${(fileInfo.file_size / 1024).toFixed(2)} KB<br>
                Server Filename: ${fileInfo.unique_filename}
            </div>
        `;
    }
    

    function showError(message) {
        previewArea.innerHTML = `
            <div class="alert alert-danger">
                ${message}
            </div>
        `;
    }
    
    function setupModeToggle() {
        // 模式切换逻辑
        promptModeBtn.addEventListener('click', () => {
            currentMode = 'prompt';
            promptModeBtn.classList.remove('btn-secondary');
            promptModeBtn.classList.add('btn-primary');
            codegenModeBtn.classList.remove('btn-primary');
            codegenModeBtn.classList.add('btn-secondary');

            templateTitle.textContent = 'Prompt Template';
            templateContent.value = promptTemplate;
            currentTemplate = promptTemplate;
            // console.log('Current Template:', currentTemplate);
            fetchTemplates('prompt');
        });
    
        codegenModeBtn.addEventListener('click', () => {
            currentMode = 'codegen';
            codegenModeBtn.classList.remove('btn-secondary');
            codegenModeBtn.classList.add('btn-primary');
            promptModeBtn.classList.remove('btn-primary');
            promptModeBtn.classList.add('btn-secondary');
            
            templateTitle.textContent = 'CodeGen Template';
            templateContent.value = codegenTemplate;
            currentTemplate = codegenTemplate;
            // console.log('Current Template:', currentTemplate);
            fetchTemplates('codegen');
        });
    }

    // 添加模型选择处理函数
    function setupModelSelection() {
        // 获取所有模型按钮
        const modelButtons = document.querySelectorAll('.model-btn');
        
        // 为每个模型按钮添加点击事件
        modelButtons.forEach(button => {
            button.addEventListener('click', function() {
                // 移除其他按钮的激活状态
                modelButtons.forEach(btn => {
                    btn.classList.remove('active', 'btn-primary', 'btn-success', 'btn-info', 'btn-warning');
                    btn.classList.add('btn-outline-primary', 'btn-outline-success', 'btn-outline-info', 'btn-outline-warning');
                });
                
                // 添加当前按钮的激活状态
                this.classList.remove('btn-outline-primary', 'btn-outline-success', 'btn-outline-info', 'btn-outline-warning');
                
                // 根据模型类型添加对应的激活样式
                if (this.dataset.model.includes('gpt')) {
                    this.classList.add('btn-primary');
                } else if (this.dataset.model.includes('gemini')) {
                    this.classList.add('btn-success');
                } else if (this.dataset.model.includes('qwen')) {
                    this.classList.add('btn-info');
                } else if (this.dataset.model.includes('claude')) {
                    this.classList.add('btn-warning');
                }
                // 保存选中的模型
                selectedModel = this.dataset.model;
                // 如果文件已上传，启用分析按钮
                if (uploadedFileInfo) {
                    analyzeBtn.disabled = false;
                }
            });
        });
    }

    function analyzeFile() {
        // 确保已经上传文件
        if (!uploadedFileInfo) {
            targetData.textContent = 'Please upload a file first.';
            return;
        }
        analyzeData = {
            filename: uploadedFileInfo.unique_filename,
            filepath: uploadedFileInfo.save_path,
            mode: currentMode,
            model_id: selectedModel,
            template: currentTemplate
        };
        // console.log('Analyze Data:', analyzeData);
    
        // 显示分析中状态和加载动画
        let dots = '';
        const loadingInterval = setInterval(() => {
            dots = dots.length >= 3 ? '' : dots + '.';
            targetData.textContent = '分析中，请稍候' + dots;
        }, 500);
    
        // 发送分析请求
        axios.post('/analyze', analyzeData, {
            headers: {
                'Content-Type': 'application/json',
            },
            timeout: 100000  // 设置超时时间为180秒
        })
        .then(response => {
            clearInterval(loadingInterval);
            mode = response.data.mode;
            if(response.data.code == 200) {
                const aiResponse = response.data.ai_response || 
                                (response.data.data && response.data.data.ai_response);
            
                if (aiResponse) {
                    if (typeof aiResponse === 'object') {
                        targetData.textContent = JSON.stringify(aiResponse, null, 2);
                    } else {
                        targetData.textContent = aiResponse;
                    }
                    if(mode == 'codegen') executeCodeBtn.disabled = false;
                } else {
                    targetData.textContent = '无分析结果';
                }
            } else {
                targetData.textContent = response.data.message || 'Analyze error';
            }
        })
        .catch(error => {
            clearInterval(loadingInterval);
            // 详细的错误处理
            if (error.response) {
                // 服务器返回错误
                targetData.textContent = `服务器错误: ${error.response.data.message || '未知错误'}`;
            } else if (error.request) {
                // 请求已发送但无响应
                targetData.textContent = '网络错误：未收到服务器响应';
            } else {
                // 请求设置时发生错误
                targetData.textContent = `请求错误: ${error.message}`;
            }
        });
    }

    // 初始化
    function init() {
        // 初始时禁用分析按钮
        analyzeBtn.disabled = true;
        executeCodeBtn.disabled = true;
        // 设置文件上传处理
        setupFileUploadHandlers();
        setupModeToggle();
        setupModelSelection();
        fetchTemplates('prompt'); // 默认加载 Prompt 模板

        if(templateContent) {
            templateContent.addEventListener('input', function() {
                currentTemplate = this.value;
            });
        }

        if(analyzeBtn) {
            analyzeBtn.addEventListener('click', analyzeFile); // 注意：没有括号
        }
        executeCode();

        // 保存模板按钮的
        // document.getElementById('save-template').addEventListener('click', saveTemplate);
    }

    // 启动
    init();
});