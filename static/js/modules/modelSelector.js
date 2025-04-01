export class ModelSelector {
    constructor(config) {
        this.config = config;
        this.selectedModel = {
            seed: null,
            code: null
        };
        // 分别获取两种类型的按钮
        this.seedModelButtons = document.querySelectorAll('.seed-model-btn');
        this.codeModelButtons = document.querySelectorAll('.code-model-btn'); 
        this.initializeButtons();
        this.init();
    }

    initializeButtons() {
        // 确保按钮元素被正确获取
        this.seedModelButtons = Array.from(document.querySelectorAll('.seed-model-btn'));
        this.codeModelButtons = Array.from(document.querySelectorAll('.code-model-btn'));
    }

    init() {
        this.setupEventListeners();
    }

    setupEventListeners() {
        // 为种子生成模型按钮添加事件监听
        this.seedModelButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleModelSelection(button, 'seed');
            });
        });

        // 为代码生成模型按钮添加事件监听
        this.codeModelButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleModelSelection(button, 'code');
            });
        });
    }

    handleModelSelection(button, type) {
        try {
            // 验证参数
            if (!type || !button) {
                throw new Error('Invalid selection parameters');
            }
            
            if (!this.selectedModels) {
                this.selectedModels = { seed: null, code: null };
            }

            // 重置对应类型的按钮
            this.resetButtonsByType(type);
            
            // 更新选中状态
            this.selectedModels[type] = button.dataset.model;
            
            // 更新按钮样式
            this.updateButtonStyle(button);
            
            // 检查是否可以启用分析按钮
            this.checkEnableAnalyzeButton();
            // console.log('Current selection:', this.selectedModels);
            
        } catch (error) {
            console.error('Model selection error:', error);
        }
    }


    selectModel(button, type) {
        if (!type || !button) {
            console.error('Invalid parameters:', { button, type });
            return;
        }

        // 重置对应类型的所有按钮
        this.resetButtonsByType(type);
        
        // 设置选中的模型
        this.selectedModels[type] = button.dataset.model;
        
        // 更新按钮样式
        this.updateButtonStyle(button);
        
        // 检查是否可以启用分析按钮
        this.checkEnableAnalyzeButton();
    }

    // resetButtonsByType(type) {
    //     const buttons = type === 'seed' ? this.seedModelButtons : this.codeModelButtons;
        
    //     buttons.forEach(btn => {
    //         btn.classList.remove('active', 'btn-primary', 'btn-success', 'btn-info', 'btn-warning');
    //         btn.classList.add('btn-outline-primary', 'btn-outline-success', 'btn-outline-info', 'btn-outline-warning');
    //     });
    // }
    resetButtonsByType(type) {
        const buttons = type === 'seed' ? this.seedModelButtons : this.codeModelButtons;
        
        buttons.forEach(btn => {
            btn.classList.remove('active', 'btn-primary', 'btn-info', 'btn-warning');
            if (btn.dataset.model.includes('gpt')) {
                btn.classList.add('btn-outline-primary');
            } else if (btn.dataset.model.includes('o1')) {
                btn.classList.add('btn-outline-primary');
            } else if (btn.dataset.model.includes('qwen')) {
                btn.classList.add('btn-outline-info');
            } else if (btn.dataset.model.includes('claude')) {
                btn.classList.add('btn-outline-warning');
            }
        });
    }

    updateButtonStyle(button) {
        button.classList.remove('btn-outline-primary', 'btn-outline-info', 'btn-outline-warning');
        button.classList.add('active');
        
        if (button.dataset.model.includes('gpt')) {
            button.classList.add('btn-primary');
        } else if (button.dataset.model.includes('o1')) {
            button.classList.add('btn-primary');
        } else if (button.dataset.model.includes('qwen')) {
            button.classList.add('btn-info');
        } else if (button.dataset.model.includes('claude')) {
            button.classList.add('btn-warning');
        }
    }

    checkEnableAnalyzeButton() {
        if (!this.config || !this.config.analyzeBtn) {
            console.warn('Analyze button not configured');
            return;
        }

        // 检查是否两个模型都已选择且文件已上传
        const bothModelsSelected = this.selectedModels.seed && this.selectedModels.code;
        const fileUploaded = this.config.fileUploader.getUploadedFileInfo();
        this.config.analyzeBtn.disabled = !(bothModelsSelected && fileUploaded);
    }

    getSelectedModels() {
        return {
            seedModel: this.selectedModels.seed,
            codeModel: this.selectedModels.code
        };
    }

    // 验证是否已选择两个模型
    validateModelSelection() {
        const {seedModel, codeModel} = this.getSelectedModels();
        if (!seedModel || !codeModel) {
            throw new Error('Please select both models for seed generation and code generation.');
        }
        return true;
    }

    // 重置所有选择
    resetAllSelections() {
        this.selectedModels = {
            seed: null,
            code: null
        };
        
        this.resetButtonsByType('seed');
        this.resetButtonsByType('code');
        this.checkEnableAnalyzeButton();
    }
}
