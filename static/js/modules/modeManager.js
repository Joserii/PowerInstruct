import { MODES } from '../config/constants.js';

export class ModeManager {
    constructor(config) {
        this.config = config;
        this.currentMode = MODES.PROMPT_CODEGEN;
        this.templateManager = config.templateManager;
        this.buttons = config.modeSwitchBtns;
        this.splitContainer = config.splitContainer;
        this.singleContainer = config.singleContainer;

        // 添加新的DOM元素引用
        this.fillCodeBtn = document.getElementById('fill-code');
        
        this.init();
    }

    init() {
        // 复制按钮的点击事件
        const copySamplesBtn = document.getElementById('copy-samples');
        if (copySamplesBtn) {
            copySamplesBtn.addEventListener('click', async () => {
                const sampleOutput = document.getElementById('sample-output');
                try {
                    await navigator.clipboard.writeText(sampleOutput.value);
                    // 可选：添加复制成功的视觉反馈
                    const originalText = copySamplesBtn.innerHTML;
                    copySamplesBtn.innerHTML = '<i class="bi bi-check"></i> 已复制';
                    setTimeout(() => {
                        copySamplesBtn.innerHTML = originalText;
                    }, 2000);
                } catch (err) {
                    console.error('Fail to Copy:', err);
                }
            });
        }
        if (!this.templateManager) {
            console.error('Template manager is not initialized');
            return;
        }
        const defaultButton = this.buttons[0]
        if (defaultButton) {
            defaultButton.classList.add('active');
            this.setMode(this.currentMode);
            this.setDefaultContent();
        }
        this.setupEventListeners();
        // this.setupSplitViewHandlers();
    }

    setDefaultContent() {
        const promptContent = this.templateManager.prompt;
        const codegenContent = this.templateManager.codegen;

        // 设置分栏内容
        if (this.promptTemplate) {
            this.promptTemplate.value = promptContent;
            // console.log('Prompt template set:', this.promptTemplate.value);
        }
        if (this.codeTemplate) {
            this.codeTemplate.value = codegenContent;
            // console.log('Code template set:', this.codeTemplate.value);
        }

        // 设置单栏内容
        const templateContent = document.getElementById('template-content');
        if (templateContent) {
            templateContent.value = promptContent;
        }
    }

    setupEventListeners() {
        // 模式切换按钮的监听
        this.buttons.forEach(button => {
            button.addEventListener('click', (e) => {
                const mode = button.dataset.mode;
                this.handleModeChange(button, mode);
            });
        });
    }

    handleModeChange(clickedButton, newMode) {
        // 更新按钮状态
        this.buttons.forEach(btn => btn.classList.remove('active'));
        clickedButton.classList.add('active');
        // 添加点击动画效果
        this.addClickAnimation(clickedButton);
        // 设置新模式
        this.setMode(newMode);
    }

    addClickAnimation(button) {
        button.style.transform = 'scale(0.95)';
        setTimeout(() => {
            button.style.transform = 'scale(1)';
        }, 100);
    }

    setMode(mode) {
        if (this.currentMode === mode) return;
        this.currentMode = mode;
        this.updateViewMode(mode);
        // 更新模板管理器
        this.templateManager.setMode(mode);
        // 触发模式改变事件
        this.triggerModeChangeEvent(mode);
        // console.log(`Switched to ${mode} mode`);
    }

    updateViewMode(mode) {
        switch(mode) {
            case MODES.PROMPT_CODEGEN:
                this.splitContainer.style.display = 'flex';
                this.singleContainer.style.display = 'none';
                break;
                
            case MODES.PROMPT:
            case MODES.CODEGEN:
                this.splitContainer.style.display = 'none';
                this.singleContainer.style.display = 'block';
                
                // 更新单栏内容
                if (this.templateContent) {
                    const content = mode === MODES.PROMPT 
                        ? this.promptTemplate?.value || ''
                        : this.codeTemplate?.value || '';
                    this.templateContent.value = content;
                }
                break;
        }
        
        // 更新模板标题
        const templateTitle = document.getElementById('template-title');
        if (templateTitle) {
            templateTitle.innerHTML = mode === MODES.PROMPT 
                ? '<i class="bi bi-chat-dots"></i> Prompt Template'
                : '<i class="bi bi-code-slash"></i> Codegen Template';
        }
    }

    triggerModeChangeEvent(mode) {
        // 创建自定义事件
        const event = new CustomEvent('modeChange', {
            detail: { mode: mode }
        });
        document.dispatchEvent(event);
    }

    getCurrentMode() {
        return this.currentMode;
    }

    // 禁用/启用指定模式
    disableMode(mode) {
        const button = this.buttons.find(btn => btn.dataset.mode === mode);
        if (button) {
            button.disabled = true;
            button.classList.add('disabled');
        }
    }
    enableMode(mode) {
        const button = this.buttons.find(btn => btn.dataset.mode === mode);
        if (button) {
            button.disabled = false;
            button.classList.remove('disabled');
        }
    }
    
    // 程序化切换模式
    switchMode(mode) {
        const button = this.buttons.find(btn => btn.dataset.mode === mode);
        if (button && !button.disabled) {
            this.handleModeChange(button, mode);
        }
    }

}
