import { apiService } from '../utils/apiService.js';
import { UIHelper } from '../utils/uiHelpers.js';

export class Analyzer {
    static STATUS = {
        IDLE: 'idle',
        PROCESSING: 'processing'
    };

    // 模式常量
    static MODES = {
        PROMPT: 'prompt',
        CODEGEN: 'codegen',
        BATCH: 'batch'
    };

    constructor(config) {
        this.config = config;
        this.state = {
            isAnalyzing: false,
            currentMode: null,
            loadingInterval: null
        };
        // 添加数据收集数组
        this.generatedData = {
            raw_data: null,          // 原始数据
            seed_data: null,         // 种子数据
            generated_code: null,    // 生成的代码
            execution_result: null   // 执行结果
        };
                
        this.selectedData = null;
        this.merged_codegen_prompt = null;
        this.analyzeDataPath = null;
        this.initComponents();
    }

    init() {
        this.setupEventListeners();
    }
    // 初始化组件
    initComponents() {
        this.codegenOutput = this.config.targetData;
        this.seedgenOutput = this.config.generateSamplesContainer;
        this.buttons = {
            analyze: this.config.analyzeBtn,
            generateSamples: this.config.generateSamplesBtn,
            generateCodeBtn: this.config.generateCodeBtn,
            executeCode: this.config.executeCodeBtn,
            mergeTemplate: this.config.mergeTemplate,
            copysampleBtn: this.config.copysampleBtn,
            codegenTemplate: this.config.codegenTemplate,
            exportJson: this.config.exportJsonBtn,
            exportJsonl: this.config.exportJsonlBtn,
            exportInstructionJson: this.config.exportInstructionJsonBtn,
            exportInstructionJsonl: this.config.exportInstructionJsonlBtn
        };
        this.setupEventListeners();
    }

    // 收集生成的数据
    collectGeneratedData({ type, data }) {
        this.generatedData[type] = data;
    }

    

    setupEventListeners() {
        const buttonHandlers = {
            generateSamples: this.startProcess.bind(this),
            generateCodeBtn: () => this.generateCode()  // 修改这里
        };

        Object.entries(buttonHandlers).forEach(([key, handler]) => {
            const button = this.buttons[key];
            if (button) {
                button.addEventListener('click', () => {
                    if (!this.state.isAnalyzing) {
                        handler();
                    }
                });
            }
        });

        if (this.buttons.mergeTemplate) {
            this.buttons.mergeTemplate.addEventListener('click', () => {
                if (!this.state.isAnalyzing) {
                    this.mergeCodegenTemplate();
                }
            });
        }

        // 添加复制按钮事件
        if (this.buttons.copySamplesBtn) {
            this.buttons.copySamplesBtn.addEventListener('click', () => {
                this.copyToClipboard(this.codegenOutput.value);
            });
        }

        // 添加导出按钮事件监听
        if (this.buttons.exportJson) {
            this.buttons.exportJson.addEventListener('click', () => this.exportData('json'));
        }
        if (this.buttons.exportJsonl) {
            this.buttons.exportJsonl.addEventListener('click', () => this.exportData('jsonl'));
        }
        // 添加指令数据导出按钮事件监听
        if (this.buttons.exportInstructionJson) {
            this.buttons.exportInstructionJson.addEventListener('click', () => 
                this.exportInstructionData('json'));
        }
        if (this.buttons.exportInstructionJsonl) {
            this.buttons.exportInstructionJsonl.addEventListener('click', () => 
                this.exportInstructionData('jsonl'));
        }
    }


    async exportInstructionData(format = 'json') {
        try {
            // 准备指令数据
            const instructionData = await this.prepareInstructionData();
            
            if (!instructionData.length) {
                throw new Error('No instruction data available');
            }

            let content;
            let filename;
            let mimeType;

            if (format === 'jsonl') {
                // JSONL格式
                content = instructionData
                    .map(data => JSON.stringify(data))
                    .join('\n');
                filename = `instruction_data_${Date.now()}.jsonl`;
                mimeType = 'text/plain';
            } else {
                // JSON格式
                content = JSON.stringify(instructionData, null, 2);
                filename = `instruction_data_${Date.now()}.json`;
                mimeType = 'application/json';
            }

            this.downloadFile(content, filename, mimeType);

        } catch (error) {
            console.error('Export instruction data error:', error);
            this.handleError(error);
        }
    }

    // 准备指令数据
    async prepareInstructionData() {
        const instructionData = [];
        const executionResult = this.generatedData.execution_result;

        if (executionResult && executionResult.success_results) {
            executionResult.success_results.forEach(result => {
                try {
                    // 获取结果字符串并解析为JSON
                    const resultStr = result.result.result;
                    const resultData = JSON.parse(resultStr);
                    
                    // 构建指令数据对象
                    const instruction = {
                        // timestamp: new Date().toISOString(),
                        input: resultData.input,
                        output: resultData.output,
                        // raw_data: result.input  // 保留原始数据以供参考
                    };
                    
                    instructionData.push(instruction);
                } catch (error) {
                    console.warn('Failed to parse result:', result);
                }
            });
        }

        return instructionData;
    }


    // 添加代码生成方法
    async generateCode() {
        try {
            // 验证模型选择
            await this.validateModelSelection();
            
            // 获取所选模型
            const selectedModels = this.config.modelSelector.getSelectedModels();

            // 准备代码生成数据
            const codegenData = {
                mode: 'codegen',
                model_id: selectedModels.codeModel,
                template: this.merged_codegen_prompt,
                raw_content: this.selectedData,  // 使用保存的原始数据
                standard_instruction: this.seedgenOutput.value // 使用种成的标准格式
            };

            // console.log('Codegen data:', codegenData);

            // 更新按钮状态
            this.state.isAnalyzing = true;
            this.updateButtonStates(true);
            this.state.loadingInterval = UIHelper.showLoading(this.codegenOutput);

            // 发送代码生成请求
            const response = await apiService.analyzeFile(codegenData);

            if (response.data.code === 200) {
                // 处理成功响应
                await this.handleCodeGenSuccess(response.data);
            } else {
                throw new Error(response.data.message || 'Code generation failed');
            }

        } catch (error) {
            this.handleCodeGenError(error);
        } finally {
            // 恢复状态
            this.state.isAnalyzing = false;
            this.updateButtonStates(false);
            UIHelper.clearLoading(this.state.loadingInterval);
        }
    }

    // 处理代码生成成功
    handleCodeGenSuccess(data) {
        const aiResponse = data.ai_response || (data.data && data.data.ai_response);
        
        if (aiResponse) {
            // 收集生成的代码
            this.collectGeneratedData({
                type: 'generated_code',
                data: aiResponse
            });
            // 更新代码生成输出框
            const formattedContent = typeof aiResponse === 'object' 
                ? JSON.stringify(aiResponse, null, 2) 
                : aiResponse;

            this.codegenOutput.textContent = formattedContent;

            // 启用执行代码按钮
            if (this.buttons.executeCode) {
                this.buttons.executeCode.disabled = false;
            }
        } else {
            this.codegenOutput.textContent = '无生成结果';
        }
    }

    // 处理代码生成错误
    handleCodeGenError(error) {
        console.error('Code generation error:', error);
        
        // 在代码生成输出框中显示错误
        if (this.codegenOutput) {
            this.codegenOutput.innerHTML = `<div class="text-danger">
                代码生成错误: ${error.message || '未知错误'}
            </div>`;
        }
    }

    // 合并模板方法
    async mergeCodegenTemplate() {
        try {
            // 获取种子生成的结果
            const seedOutput = this.seedgenOutput.value;
            if (!seedOutput) {
                throw new Error('No seed generation result available');
            }

            // 准备合并请求数据
            const mergeData = {
                raw_content: this.selectedData,
                seed_content: seedOutput,
                mode: 'merge_template',
                template: this.config.templateManager.getCodegenTemplate()
            };

            // 更新按钮状态
            this.buttons.mergeTemplate.disabled = true;
            this.buttons.mergeTemplate.innerHTML = '<i class="bi bi-arrow-clockwise"></i> Merging...';

            // 发送合并请求
            const response = await apiService.mergeTemplate(mergeData);
            // console.log('Merge template response:', response.data);
            
            this.merged_codegen_prompt = response.data.merged_codegen_prompt;

            if (response.data.code === 200) {
                // 使用 TemplateManager 更新模板内容
                this.config.templateManager.setCodegenTemplate(response.data.merged_content);
            } else {
                throw new Error(response.data.message || 'Template merge failed');
            }

        } catch (error) {
            this.handleError(error, 'code');
        } finally {
            // 恢复按钮状态
            this.buttons.mergeTemplate.disabled = false;
            this.buttons.mergeTemplate.innerHTML = '<i class="bi bi-arrow-right"></i> Merge Codegen Template';
        }
    }

    // 复制到剪贴板
    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            // 可以添加一个临时的成功提示
            const originalText = this.buttons.copySamples.innerHTML;
            this.buttons.copySamples.innerHTML = '<i class="bi bi-check"></i> Copied!';
            setTimeout(() => {
                this.buttons.copySamples.innerHTML = originalText;
            }, 2000);
        } catch (err) {
            console.error('Failed to copy text:', err);
        }
    }

    // 验证模型选择
    async validateModelSelection() {
        try {
            return this.config.modelSelector.validateModelSelection();
        } catch (error) {
            throw new Error('Model selection validation failed: ' + error.message);
        }
    }



    async exportData(format = 'json') {
        try {
            // 准备导出数据数组
            const exportDataArray = await this.prepareExportData();

            let content;
            let filename;
            let mimeType;

            if (format === 'jsonl') {
                // 转换为JSONL格式 - 每行一条数据
                content = exportDataArray
                    .map(data => JSON.stringify(data))
                    .join('\n');
                filename = `generated_data_${Date.now()}.jsonl`;
                mimeType = 'text/plain';
            } else {
                // JSON格式 - 数组形式
                content = JSON.stringify(exportDataArray, null, 2);
                filename = `generated_data_${Date.now()}.json`;
                mimeType = 'application/json';
            }

            this.downloadFile(content, filename, mimeType);

        } catch (error) {
            console.error('Export error:', error);
            this.handleError(error);
        }
    }

    // 下载文件
    downloadFile(content, filename, mimeType) {
        const blob = new Blob([content], { type: mimeType });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    // 准备导出数据
    async prepareExportData() {
        const exportDataArray = [];
        
        // 获取执行结果
        const executionResult = this.generatedData.execution_result;
        
        if (executionResult && executionResult.success_results) {
            // 处理成功的结果
            executionResult.success_results.forEach(result => {
                exportDataArray.push({
                    timestamp: new Date().toISOString(),
                    raw_data: result.input,            // 原始输入数据
                    prediction: result.result,         // 预测结果
                    seed_data: this.generatedData.seed_data,      // 种子数据
                    generated_code: this.generatedData.generated_code  // 生成的代码
                });
            });
            
            // 添加统计信息
            exportDataArray.push({
                type: 'statistics',
                data: executionResult.statistics,
                timestamp: new Date().toISOString()
            });
            
            // 如果有失败的结果，也添加进去
            if (executionResult.failed_results && executionResult.failed_results.length > 0) {
                executionResult.failed_results.forEach(result => {
                    exportDataArray.push({
                        type: 'failed',
                        timestamp: new Date().toISOString(),
                        raw_data: result.input,
                        error: result.error
                    });
                });
            }
        } else {
            // 如果没有执行结果，只导出基本信息
            exportDataArray.push({
                timestamp: new Date().toISOString(),
                raw_data: this.selectedData,
                seed_data: this.generatedData.seed_data,
                generated_code: this.generatedData.generated_code
            });
        }

        return exportDataArray;
    }

    // 从文件中随机选择一条数据
    async selectRandomSeed(filePath) {
        try {
            this.updateProcessStatus('Reading data file...');
            // console.log('Selecting random seed from file:', filePath);
            const response = await apiService.fetchJsonContent(filePath);
            // console.log('File content:', response.data.data);
            if (!response.data || !response.data.data) {
                throw new Error('Invalid data format in file');
            }

            const allData = response.data.data;
            const randomIndex = Math.floor(Math.random() * allData.length);
            const selectedData = allData[randomIndex];
            this.updateProcessStatus(`Selected seed data (index: ${randomIndex})`);
            this.selectedData = selectedData;
            return selectedData;

        } catch (error) {
            throw new Error(`Failed to select random seed: ${error.message}`);
        }
    }


    // 使用种子数据生成标准格式
    async generateStandardFormat(seedData, seedModel) {
        this.updateProcessStatus('Generating standard format from seed data...');
        
        const genData = {
            mode: 'prompt',
            model_id: seedModel,
            template: this.config.templateManager.getCurrentTemplate(),
            file_content: JSON.stringify(seedData)  // 将种子数据转换为字符串
        };

        // console.log('Generate standard format data:', genData);

        try {
            const response = await apiService.analyzeFile(genData);
            if (response.data.code !== 200) {
                throw new Error(response.data.message || 'Standard format generation failed');
            }
            return response;
        } catch (error) {
            throw new Error(`Standard format generation error: ${error.message}`);
        }
    }

    // 使用标准格式生成代码
    async processCodeGeneration(fileInfo, codeModel) {
        this.updateProcessStatus('Generating code based on standard format...');

        const codeGenData = {
            ...fileInfo,
            model_id: codeModel,
            template: this.config.templateManager.getCodegenTemplate()
        };

        try {
            const response = await apiService.analyzeFile(codeGenData);
            if (response.data.code !== 200) {
                throw new Error(response.data.message || 'Code generation failed');
            }
            return response.data;
        } catch (error) {
            throw new Error(`Code generation error: ${error.message}`);
        }
    }


    // 统一的处理入口
    async startProcess() {
        const currentMode = this.config.fileUploader.getCurrentMode();
        // console.log('Current mode:', currentMode);
        
        try {
            await (currentMode === 'batch' ? this.batchProcess() : this.singleProcess());
        } catch (error) {
            this.handleError(error);
        }
    }
    
    // 验证和准备处理
    async prepareProcess() {
        const fileInfo = this.getFileInfo();
        if (!fileInfo) {
            throw new Error('Please upload a file first.');
        }

        await this.validateModelSelection();
        return fileInfo;
    }
    
    // 获取文件信息
    getFileInfo() {
        return this.config.fileUploader.getCurrentMode() === 'batch' 
            ? this.config.fileUploader.getCurrentFileInfo()
            : this.config.fileUploader.getUploadedFileInfo();
    }
    


    // 更新处理状态
    updateProcessStatus(message, isError = false) {
        const timestamp = new Date().toLocaleTimeString();
        const statusMessage = `[${timestamp}] ${message}`;
        
        // console.log(statusMessage);
        this.updateOutput(`${this.seedgenOutput.textContent}\n${statusMessage}`, isError);
        this.seedgenOutput.scrollTop = this.seedgenOutput.scrollHeight;
    }

    // 批处理流程
    async batchProcess() {
        await this.executeProcess(async () => {
            const fileInfo = await this.prepareProcess();
            const selectedModels = this.config.modelSelector.getSelectedModels();
            this.analyzeDataPath = fileInfo.all_files_path;

            // 1. 选择随机种子
            const randomSeed = await this.selectRandomSeed(fileInfo.all_files_path);
            this.updateProcessStatus('Selected random seed data');

            // 2. 生成标准格式
            const standardData = await this.generateStandardFormat(randomSeed, selectedModels.seedModel);
            
            // 3. 处理结果
            await this.handleProcessResult(standardData);
        });
    }
    
    // 单文件处理流程
    async singleProcess() {
        await this.executeProcess(async () => {
            const fileInfo = await this.prepareProcess();
            const selectedModels = this.config.modelSelector.getSelectedModels();

            // 处理逻辑
            const response = await this.generateStandardFormat(fileInfo, selectedModels.seedModel);
            await this.handleProcessResult(response);
        });
    }
    // 统一的执行过程封装
    async executeProcess(processFunc) {
        try {
            this.startProcessing();
            await processFunc();
        } catch (error) {
            this.handleError(error);
        } finally {
            this.endProcessing();
        }
    }
    // 开始处理
    startProcessing() {
        this.state.isAnalyzing = true;
        this.updateButtonStates(true);
        this.state.loadingInterval = UIHelper.showLoading(this.seedgenOutput);
    }

    // 结束处理
    endProcessing() {
        this.state.isAnalyzing = false;
        this.updateButtonStates(false);
        UIHelper.clearLoading(this.state.loadingInterval);
    }


    // 更新按钮状态
    updateButtonStates(isProcessing) {
        Object.values(this.buttons).forEach(button => {
            if (button) {
                button.disabled = isProcessing;
                button.style.cursor = isProcessing ? 'not-allowed' : 'pointer';
                this.updateButtonText(button, isProcessing);
            }
        });
    }

    // 更新按钮文本
    updateButtonText(button, isProcessing) {
        if (isProcessing) {
            button.originalText = button.textContent;
            button.textContent = 'Processing...';
        } else {
            button.textContent = button.originalText || 'Generate';
        }
    }

    // 处理响应结果
    async handleProcessResult(response) {
        if (response.data.code === 200) {
            await this.handleSuccess(response.data);
        } else {
            throw new Error(response.data.message || 'Process failed');
        }
    }

    // 统一的成功处理
    async handleSuccess(data) {
        const aiResponse = data.ai_response || (data.data && data.data.ai_response);
        if (aiResponse) {
            // 收集种子数据
            this.collectGeneratedData({
                type: 'seed_data',
                data: aiResponse
            });
            this.updateOutput(aiResponse);
            if (data.mode === Analyzer.MODES.CODEGEN) {
                this.buttons.executeCode.disabled = false;
            }
        } else {
            this.updateOutput('No results available');
        }
    }
    // 统一的错误处理
    handleError(error) {
        console.error('Process error:', error);
        this.updateOutput(error.message, true);
    }

    // 更新输出
    updateOutput(content, isError = false) {
        if (this.seedgenOutput) {
            const formattedContent = typeof content === 'object' 
                ? JSON.stringify(content, null, 2) 
                : content;

            if (isError) {
                this.seedgenOutput.innerHTML = `<div class="text-danger">${formattedContent}</div>`;
            } else {
                this.seedgenOutput.textContent = formattedContent;
            }
        }
    }

    getAnalyzeData() {
        return this.analyzeData;
    }

    getanalyzeDataPath() {
        return this.analyzeDataPath;
    }
 }
