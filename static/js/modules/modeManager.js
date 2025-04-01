import { MODES } from '../config/constants.js';

export class ModeManager {
    constructor(config) {
        this.config = config;
        this.currentMode = MODES.PROMPT_CODEGEN;
        this.templateManager = config.templateManager;
        this.buttons = config.modeSwitchBtns;
        this.splitContainer = config.splitContainer;
        this.singleContainer = config.singleContainer;

        this.fillCodeBtn = document.getElementById('fill-code');
        
        this.init();
    }

    init() {
        const copySamplesBtn = document.getElementById('copy-samples');
        if (copySamplesBtn) {
            copySamplesBtn.addEventListener('click', async () => {
                const sampleOutput = document.getElementById('sample-output');
                try {
                    await navigator.clipboard.writeText(sampleOutput.value);
                    const originalText = copySamplesBtn.innerHTML;
                    copySamplesBtn.innerHTML = '<i class="bi bi-check"></i> Copied';
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

        if (this.promptTemplate) {
            this.promptTemplate.value = promptContent;
            // console.log('Prompt template set:', this.promptTemplate.value);
        }
        if (this.codeTemplate) {
            this.codeTemplate.value = codegenContent;
            // console.log('Code template set:', this.codeTemplate.value);
        }

        const templateContent = document.getElementById('template-content');
        if (templateContent) {
            templateContent.value = promptContent;
        }
    }

    setupEventListeners() {
        this.buttons.forEach(button => {
            button.addEventListener('click', (e) => {
                const mode = button.dataset.mode;
                this.handleModeChange(button, mode);
            });
        });
    }

    handleModeChange(clickedButton, newMode) {
        this.buttons.forEach(btn => btn.classList.remove('active'));
        clickedButton.classList.add('active');
        this.addClickAnimation(clickedButton);
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
        this.templateManager.setMode(mode);
        this.triggerModeChangeEvent(mode);
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
                
                if (this.templateContent) {
                    const content = mode === MODES.PROMPT 
                        ? this.promptTemplate?.value || ''
                        : this.codeTemplate?.value || '';
                    this.templateContent.value = content;
                }
                break;
        }
        
        const templateTitle = document.getElementById('template-title');
        if (templateTitle) {
            templateTitle.innerHTML = mode === MODES.PROMPT 
                ? '<i class="bi bi-chat-dots"></i> Prompt Template'
                : '<i class="bi bi-code-slash"></i> Codegen Template';
        }
    }

    triggerModeChangeEvent(mode) {
        const event = new CustomEvent('modeChange', {
            detail: { mode: mode }
        });
        document.dispatchEvent(event);
    }

    getCurrentMode() {
        return this.currentMode;
    }

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
    
    switchMode(mode) {
        const button = this.buttons.find(btn => btn.dataset.mode === mode);
        if (button && !button.disabled) {
            this.handleModeChange(button, mode);
        }
    }

}
