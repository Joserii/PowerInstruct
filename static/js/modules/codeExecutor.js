import { apiService } from '../utils/apiService.js';
import { UIHelper } from '../utils/uiHelpers.js';

export class CodeExecutor {
    constructor(config) {
        this.config = config;
        this.progressBar = document.querySelector('#execution-progress');
        this.progressBarInner = this.progressBar.querySelector('.progress-bar');
        this.progressText = this.progressBar.querySelector('.progress-text');
        this.statsElements = {
            total: document.querySelector('#stat-total'),
            success: document.querySelector('#stat-success'),
            failure: document.querySelector('#stat-failure'),
            rate: document.querySelector('#stat-rate')
        };
        this.init();
    }

    init() {
        this.executeCodeBtn = this.config.executeCodeBtn;
        this.codeOutput = this.config.targetData;
        this.executeResult = this.config.executeResult;
        this.analyzer = this.config.analyzer;
        this.setupEventListeners();
    }

    setupEventListeners() {
        this.config.executeCodeBtn.addEventListener('click', () => this.executeCode());
    }

    // Update progress
    updateProgress(current, total) {
        const percentage = Math.round((current / total) * 100);
        
        this.progressBar.style.display = 'block';
        this.progressBarInner.style.width = `${percentage}%`;
        this.progressBarInner.setAttribute('aria-valuenow', percentage);
        this.progressText.textContent = `Processing ${current}/${total} (${percentage}%)`;
    }

    validateExecution() {
        if (!this.codeOutput.textContent) {
            this.showError('No code to execute');
            return false;
        }
        if (!this.analyzer?.selectedData) {
            this.showError('No test data available. Please generate code first.');
            return false;
        }
        return true;
    }

    async executeCode() {
        // Check if code and data are available
        if (!this.validateExecution()) {
            return;
        }

        // Prepare execution data
        const executeData = this.prepareExecuteData();
        
        // Update UI status
        this.updateExecutionStatus(true);

        try {
            // Show progress bar
            this.progressBar.style.display = 'block';
            this.updateProgress(0, 100);
            
            // Execute code
            const response = await this.performExecution(executeData);
            // Handle execution result
            this.handleExecutionResult(response);
        } catch (error) {
            // Handle execution error
            this.handleExecutionError(error);
        } finally {
            // Restore UI status
            this.updateExecutionStatus(false);
        }
    }

    handleExecutionResult(response) {
        if (response.data.code === 200) {
            const result = response.data.result;
            // console.log('Execution result:', result);
            
            // Collect execution result
            if (this.analyzer) {
                this.analyzer.collectGeneratedData({
                    type: 'execution_result',
                    data: result
                });
            }
            
            this.showResult(result);
        } else {
            throw new Error(response.data.message || 'Execution failed');
        }
    }

    prepareExecuteData() {
        const pythonCode = this.codeOutput.textContent;
        const fileInfo = this.analyzer.getFileInfo();
        
        return {
            code: pythonCode,
            input_path: fileInfo?.all_files_path,    // Path to batch data files
            test_data: this.analyzer.selectedData     // Single test data entry
        };
    }

    async performExecution(executeData) {
        // console.log('Executing with data:', executeData);
        return await apiService.executeCode(executeData);
    }

    handleExecutionError(error) {
        console.error('Execution error:', error);
        this.showError(`Execution error: ${error.message}`);
    }

    updateExecutionStatus(isExecuting) {
        if (this.executeBtn) {
            this.executeBtn.disabled = isExecuting;
            this.executeBtn.textContent = isExecuting ? 'Executing...' : 'Execute Code';
        }
    }

    // Display execution result
    showResult(result) {
        try {
            const resultObj = typeof result === 'string' ? JSON.parse(result) : result;
            const stats = resultObj.statistics || {};
            
            // Hide progress bar
            this.progressBar.style.display = 'none';
            
            // Update statistics
            this.statsElements.total.textContent = stats.total || 0;
            this.statsElements.success.textContent = stats.success || 0;
            this.statsElements.failure.textContent = stats.failure || 0;
            this.statsElements.rate.textContent = stats.success_rate || '0%';
            
            // Change color based on success rate
            const successRate = parseFloat(stats.success_rate);
            if (successRate === 100) {
                this.statsElements.rate.className = 'text-success';
            } else if (successRate >= 80) {
                this.statsElements.rate.className = 'text-warning';
            } else {
                this.statsElements.rate.className = 'text-danger';
            }

        } catch (error) {
            console.error('Error parsing result:', error);
            Object.values(this.statsElements).forEach(el => {
                el.textContent = 'Error';
                el.className = 'text-danger';
            });
        }
    }

    showError(message) {
        this.progressBar.style.display = 'none';
        Object.values(this.statsElements).forEach(el => {
            el.textContent = 'Error';
            el.className = 'text-danger';
        });
    }
}
