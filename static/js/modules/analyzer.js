import { apiService } from '../utils/apiService.js';
import { UIHelper } from '../utils/uiHelpers.js';

export class Analyzer {
    static STATUS = {
        IDLE: 'idle',
        PROCESSING: 'processing'
    };

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
        this.generatedData = {
            raw_data: null, 
            seed_data: null,
            generated_code: null,
            execution_result: null
        };
                
        this.selectedData = null;
        this.merged_codegen_prompt = null;
        this.analyzeDataPath = null;
        this.initComponents();
    }

    init() {
        this.setupEventListeners();
    }
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

    collectGeneratedData({ type, data }) {
        this.generatedData[type] = data;
    }

    

    setupEventListeners() {
        const buttonHandlers = {
            generateSamples: this.startProcess.bind(this),
            generateCodeBtn: () => this.generateCode() 
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

        if (this.buttons.copySamplesBtn) {
            this.buttons.copySamplesBtn.addEventListener('click', () => {
                this.copyToClipboard(this.codegenOutput.value);
            });
        }

        if (this.buttons.exportJson) {
            this.buttons.exportJson.addEventListener('click', () => this.exportData('json'));
        }
        if (this.buttons.exportJsonl) {
            this.buttons.exportJsonl.addEventListener('click', () => this.exportData('jsonl'));
        }
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
            const instructionData = await this.prepareInstructionData();
            
            if (!instructionData.length) {
                throw new Error('No instruction data available');
            }

            let content;
            let filename;
            let mimeType;

            if (format === 'jsonl') {
                content = instructionData
                    .map(data => JSON.stringify(data))
                    .join('\n');
                filename = `instruction_data_${Date.now()}.jsonl`;
                mimeType = 'text/plain';
            } else {
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

    async prepareInstructionData() {
        const instructionData = [];
        const executionResult = this.generatedData.execution_result;

        if (executionResult && executionResult.success_results) {
            executionResult.success_results.forEach(result => {
                try {
                    const resultStr = result.result.result;
                    const resultData = JSON.parse(resultStr);
                    
                    const instruction = {
                        // timestamp: new Date().toISOString(),
                        input: resultData.input,
                        output: resultData.output,
                        // raw_data: result.input
                    };
                    
                    instructionData.push(instruction);
                } catch (error) {
                    console.warn('Failed to parse result:', result);
                }
            });
        }

        return instructionData;
    }


    async generateCode() {
        try {
            await this.validateModelSelection();
            const selectedModels = this.config.modelSelector.getSelectedModels();

            const codegenData = {
                mode: 'codegen',
                model_id: selectedModels.codeModel,
                template: this.merged_codegen_prompt,
                raw_content: this.selectedData, // Use the saved original data
                standard_instruction: this.seedgenOutput.value 
            };

            // console.log('Codegen data:', codegenData);

            this.state.isAnalyzing = true;
            this.updateButtonStates(true);
            this.state.loadingInterval = UIHelper.showLoading(this.codegenOutput);

            // Send code generation request
            const response = await apiService.analyzeFile(codegenData);

            if (response.data.code === 200) {
                // Handle successful response
                await this.handleCodeGenSuccess(response.data);
            } else {
                throw new Error(response.data.message || 'Code generation failed');
            }

        } catch (error) {
            this.handleCodeGenError(error);
        } finally {
            this.state.isAnalyzing = false;
            this.updateButtonStates(false);
            UIHelper.clearLoading(this.state.loadingInterval);
        }
    }

    handleCodeGenSuccess(data) {
        const aiResponse = data.ai_response || (data.data && data.data.ai_response);
        
        if (aiResponse) {
            this.collectGeneratedData({
                type: 'generated_code',
                data: aiResponse
            });
            const formattedContent = typeof aiResponse === 'object' 
                ? JSON.stringify(aiResponse, null, 2) 
                : aiResponse;

            this.codegenOutput.textContent = formattedContent;

            if (this.buttons.executeCode) {
                this.buttons.executeCode.disabled = false;
            }
        } else {
            this.codegenOutput.textContent = 'No results generated';
        }
    }

    // Handle code generation errors
    handleCodeGenError(error) {
        console.error('Code generation error:', error);
        
        // Display errors in the code generation output box
        if (this.codegenOutput) {
            this.codegenOutput.innerHTML = `<div class="text-danger">
                Code Generation Errors: ${error.message || 'Unknown error'}
            </div>`;
        }
    }

    // Merge Template Method
    async mergeCodegenTemplate() {
        try {
            // Get the result of seed generation
            const seedOutput = this.seedgenOutput.value;
            if (!seedOutput) {
                throw new Error('No seed generation result available');
            }

            // Preparing merge request data
            const mergeData = {
                raw_content: this.selectedData,
                seed_content: seedOutput,
                mode: 'merge_template',
                template: this.config.templateManager.getCodegenTemplate()
            };

            // Update button state
            this.buttons.mergeTemplate.disabled = true;
            this.buttons.mergeTemplate.innerHTML = '<i class="bi bi-arrow-clockwise"></i> Merging...';

            // Send a merge request
            const response = await apiService.mergeTemplate(mergeData);
            // console.log('Merge template response:', response.data);
            
            this.merged_codegen_prompt = response.data.merged_codegen_prompt;

            if (response.data.code === 200) {
                // Use TemplateManager to update template content
                this.config.templateManager.setCodegenTemplate(response.data.merged_content);
            } else {
                throw new Error(response.data.message || 'Template merge failed');
            }

        } catch (error) {
            this.handleError(error, 'code');
        } finally {
            // Restore button state
            this.buttons.mergeTemplate.disabled = false;
            this.buttons.mergeTemplate.innerHTML = '<i class="bi bi-arrow-right"></i> Merge Codegen Template';
        }
    }

    // Copy to Clipboard
    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            // You can add a temporary success prompt
            const originalText = this.buttons.copySamples.innerHTML;
            this.buttons.copySamples.innerHTML = '<i class="bi bi-check"></i> Copied!';
            setTimeout(() => {
                this.buttons.copySamples.innerHTML = originalText;
            }, 2000);
        } catch (err) {
            console.error('Failed to copy text:', err);
        }
    }

    // Validation model selection
    async validateModelSelection() {
        try {
            return this.config.modelSelector.validateModelSelection();
        } catch (error) {
            throw new Error('Model selection validation failed: ' + error.message);
        }
    }



    async exportData(format = 'json') {
        try {
            // Prepare to export data array
            const exportDataArray = await this.prepareExportData();

            let content;
            let filename;
            let mimeType;

            if (format === 'jsonl') {
                // Convert to JSONL format - one data per line
                content = exportDataArray
                    .map(data => JSON.stringify(data))
                    .join('\n');
                filename = `generated_data_${Date.now()}.jsonl`;
                mimeType = 'text/plain';
            } else {
                // JSON format - array form
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

    // Download File
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

    // Preparing to export data
    async prepareExportData() {
        const exportDataArray = [];
        
        // Get execution results
        const executionResult = this.generatedData.execution_result;
        
        if (executionResult && executionResult.success_results) {
            // Handling successful results
            executionResult.success_results.forEach(result => {
                exportDataArray.push({
                    timestamp: new Date().toISOString(),
                    raw_data: result.input,            // Original input data
                    prediction: result.result,         // Prediction results
                    seed_data: this.generatedData.seed_data,      // Seed data
                    generated_code: this.generatedData.generated_code  // Generated Code
                });
            });
            
            // Add statistics
            exportDataArray.push({
                type: 'statistics',
                data: executionResult.statistics,
                timestamp: new Date().toISOString()
            });
            
            // If there are any failed results, add them in as well.
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
            // If there is no execution result, only basic information is exported
            exportDataArray.push({
                timestamp: new Date().toISOString(),
                raw_data: this.selectedData,
                seed_data: this.generatedData.seed_data,
                generated_code: this.generatedData.generated_code
            });
        }

        return exportDataArray;
    }

    // Randomly select a piece of data from the file
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


    // Generate standard format using seed data
    async generateStandardFormat(seedData, seedModel, all_files_path) {
        this.updateProcessStatus('Generating standard format from seed data...');
        
        const genData = {
            mode: 'prompt',
            model_id: seedModel,
            template: this.config.templateManager.getCurrentTemplate(),
            file_content: JSON.stringify(seedData),  // Convert the seed data to a string
            filepath: all_files_path
        };

        console.log('Generate standard format data:', genData);

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

    // Generate code using standard format
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


    // Unified processing entry
    async startProcess() {
        const currentMode = this.config.fileUploader.getCurrentMode();
        // console.log('Current mode:', currentMode);
        
        try {
            await (currentMode === 'batch' ? this.batchProcess() : this.singleProcess());
        } catch (error) {
            this.handleError(error);
        }
    }
    
    // Verify and prepare for processing
    async prepareProcess() {
        const fileInfo = this.getFileInfo();
        if (!fileInfo) {
            throw new Error('Please upload a file first.');
        }

        await this.validateModelSelection();
        return fileInfo;
    }
    
    // Get file information
    getFileInfo() {
        return this.config.fileUploader.getCurrentMode() === 'batch' 
            ? this.config.fileUploader.getCurrentFileInfo()
            : this.config.fileUploader.getUploadedFileInfo();
    }
    


    // Update processing status
    updateProcessStatus(message, isError = false) {
        const timestamp = new Date().toLocaleTimeString();
        const statusMessage = `[${timestamp}] ${message}`;
        
        // console.log(statusMessage);
        this.updateOutput(`${this.seedgenOutput.textContent}\n${statusMessage}`, isError);
        this.seedgenOutput.scrollTop = this.seedgenOutput.scrollHeight;
    }

    // Batch Process
    async batchProcess() {
        await this.executeProcess(async () => {
            const fileInfo = await this.prepareProcess();
            const selectedModels = this.config.modelSelector.getSelectedModels();
            this.analyzeDataPath = fileInfo.all_files_path;
            // console.log('All files path:', fileInfo.all_files_path);

            // 1. Choose random seed
            const randomSeed = await this.selectRandomSeed(fileInfo.all_files_path);
            this.updateProcessStatus('Selected random seed data');

            // 2. Generate standard format
            const standardData = await this.generateStandardFormat(randomSeed, selectedModels.seedModel, this.analyzeDataPath);
            
            // 3. Processing results
            await this.handleProcessResult(standardData);
        });
    }
    
    // Single file processing flow
    async singleProcess() {
        await this.executeProcess(async () => {
            const fileInfo = await this.prepareProcess();
            const selectedModels = this.config.modelSelector.getSelectedModels();

            // Processing Logic
            const response = await this.generateStandardFormat(fileInfo, selectedModels.seedModel);
            await this.handleProcessResult(response);
        });
    }
    // Unified execution process encapsulation
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
    startProcessing() {
        this.state.isAnalyzing = true;
        this.updateButtonStates(true);
        this.state.loadingInterval = UIHelper.showLoading(this.seedgenOutput);
    }

    endProcessing() {
        this.state.isAnalyzing = false;
        this.updateButtonStates(false);
        UIHelper.clearLoading(this.state.loadingInterval);
    }


    updateButtonStates(isProcessing) {
        Object.values(this.buttons).forEach(button => {
            if (button) {
                button.disabled = isProcessing;
                button.style.cursor = isProcessing ? 'not-allowed' : 'pointer';
                this.updateButtonText(button, isProcessing);
            }
        });
    }


    updateButtonText(button, isProcessing) {
        if (isProcessing) {
            button.originalText = button.textContent;
            button.textContent = 'Processing...';
        } else {
            button.textContent = button.originalText || 'Generate';
        }
    }

    async handleProcessResult(response) {
        if (response.data.code === 200) {
            await this.handleSuccess(response.data);
        } else {
            throw new Error(response.data.message || 'Process failed');
        }
    }

    async handleSuccess(data) {
        const aiResponse = data.ai_response || (data.data && data.data.ai_response);
        if (aiResponse) {
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

    handleError(error) {
        console.error('Process error:', error);
        this.updateOutput(error.message, true);
    }


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
