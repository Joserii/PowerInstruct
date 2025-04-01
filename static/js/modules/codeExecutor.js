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


    // 更新进度
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

    // async executeCode() {
    //     if (!this.validateExecution()) {
    //         return;
    //     }
    //     const targetData = this.config.targetData;
    //     const executeResult = this.config.executeResult;
    //     const analyzeDataPath = this.config.analyzer.getanalyzeDataPath();
    //     this.updateExecutionStatus(true);

    //     if (!targetData.textContent) {
    //         executeResult.textContent = 'No code to execute';
    //         return;
    //     }

    //     if (!analyzeDataPath) {
    //         executeResult.textContent = 'Please analyze file first';
    //         return;
    //     }

    //     const pythonCode = targetData.textContent;
    //     const batchInputPath = analyzeDataPath;
    //     let execute_data = null;

    //     executeResult.textContent = 'Executing...';

    //     execute_data = {
    //         code: pythonCode,
    //         input_path: batchInputPath
    //     }

    //     console.log('Executing data:', execute_data);

    //     try {
    //         const response = await apiService.executeCode(execute_data);
    //         console.log('Execute response:', response);

    //         if (response.status === 200) {
    //             executeResult.textContent = response.data.result;
    //         } else {
    //             throw new Error(response.data.message || 'Execute error');
    //         }
    //     } catch (error) {
    //         console.error('Error executing code:', error);
    //         executeResult.textContent = `Error: ${error.message}`;
    //     }
    // }

    async executeCode() {
        // 检查是否有代码和数据
        if (!this.validateExecution()) {
            return;
        }

        // 准备执行数据
        const executeData = this.prepareExecuteData();
        
        // 更新UI状态
        this.updateExecutionStatus(true);

        try {
            // 显示进度条
            this.progressBar.style.display = 'block';
            this.updateProgress(0, 100);
            
            // 执行代码
            const response = await this.performExecution(executeData);
            // 处理执行结果
            this.handleExecutionResult(response);
        } catch (error) {
            // 处理错误
            this.handleExecutionError(error);
        } finally {
            // 恢复UI状态
            this.updateExecutionStatus(false);
        }
    }

    handleExecutionResult(response) {
        if (response.data.code === 200) {
            const result = response.data.result;
            // console.log('执行结果:', result);
            
            // 收集执行结果
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
            input_path: fileInfo?.all_files_path,    // 批量数据文件路径
            test_data: this.analyzer.selectedData     // 用于测试的单条数据
        };
    }

    async performExecution(executeData) {
        // console.log('Executing with data:', executeData);
        return await apiService.executeCode(executeData);
    }

    handleExecutionError(error) {
        console.error('Execution error:', error);
        this.showError(`执行错误: ${error.message}`);
    }

    updateExecutionStatus(isExecuting) {
        if (this.executeBtn) {
            this.executeBtn.disabled = isExecuting;
            this.executeBtn.textContent = isExecuting ? 'Executing...' : 'Execute Code';
        }

        // if (isExecuting) {
        //     this.executeResult.textContent = 'Executing...';
        // }
    }

    // 显示执行结果
    showResult(result) {
        try {
            const resultObj = typeof result === 'string' ? JSON.parse(result) : result;
            const stats = resultObj.statistics || {};
            
            // 隐藏进度条
            this.progressBar.style.display = 'none';
            
            // 更新统计数据
            this.statsElements.total.textContent = stats.total || 0;
            this.statsElements.success.textContent = stats.success || 0;
            this.statsElements.failure.textContent = stats.failure || 0;
            this.statsElements.rate.textContent = stats.success_rate || '0%';
            
            // 根据成功率改变颜色
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
