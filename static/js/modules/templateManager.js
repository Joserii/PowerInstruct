import { apiService } from '../utils/apiService.js';
import { UIHelper } from '../utils/uiHelpers.js';
import { MODES } from '../config/constants.js';

export class TemplateManager {
    constructor(config) {
        this.config = config;
        this.templateTitle = config.templateTitle;
        this.templateContent = config.templateContent;
        this.promptTemplate = '';
        this.codegenTemplate = '';
        this.currentTemplate = '';
        this.currentMode = MODES.PROMPT_CODEGEN;
        this.splitPromptTemplate = config.promptTemplate;
        this.splitCodegenTemplate = config.codegenTemplate;

        this.init();
    }

    init() {
        this.setupEventListeners();
        this.fetchTemplates(this.currentMode);
    }

    setupEventListeners() {
        this.templateContent.addEventListener('input', (e) => {
            this.currentTemplate = e.target.value;
        });

        if (this.splitPromptTemplate) {
            this.splitPromptTemplate.addEventListener('input', (e) => {
                this.promptTemplate = e.target.value;
            });
        }
        if (this.splitCodegenTemplate) {
            this.splitCodegenTemplate.addEventListener('input', (e) => {
                this.codegenTemplate = e.target.value;
            });
        }

        if (this.config.saveTemplateBtn) {
            this.config.saveTemplateBtn.addEventListener('click', () => this.saveTemplate());
        }
    }

    async fetchTemplates(mode) {
        try {
            const response = await apiService.fetchTemplates();
            const templates = response.data.templates;
            // Save template content
            this.promptTemplate = templates.prompt;
            this.codegenTemplate = templates.codegen;

            // Update the view according to the pattern
            switch(mode) {
                case MODES.PROMPT:
                    this.updateTemplateView('Prompt Mode (Editable)', templates.prompt);
                    break;
                case MODES.CODEGEN:
                    this.updateTemplateView('Codegen Mode (Editable)', templates.codegen);
                    break;
                case MODES.PROMPT_CODEGEN:
                    this.updateSplitTemplateView('Prompt->Codegen Mode (Editable)', templates.prompt, templates.codegen);
                    break;
            }

            this.currentTemplate = templates[mode];
        } catch (error) {
            console.error('Error fetching templates:', error);
            this.templateContent.value = 'Error fetching templates';
        }
    }

    updateTemplateView(title, content) {
        if (this.templateTitle) {
            this.templateTitle.textContent = title;
        }
        if (this.templateContent) {
            this.templateContent.value = content;
        }
    }

    updateSplitTemplateView(title, promptContent, codegenContent) {
        if (this.templateTitle) {
            this.templateTitle.textContent = title;
        }
        // 更新分栏视图
        if (this.splitPromptTemplate) {
            this.splitPromptTemplate.value = promptContent;
        }
        if (this.splitCodegenTemplate) {
            this.splitCodegenTemplate.value = codegenContent;
        }
    }

    handleTemplateError(message) {
        if (this.templateContent) {
            this.templateContent.value = message;
        }
        if (this.splitPromptTemplate) {
            this.splitPromptTemplate.value = message;
        }
        if (this.splitCodeTemplate) {
            this.splitCodeTemplate.value = message;
        }
    }


    async saveTemplate() {
        try {
            let content;
            if (this.currentMode === MODES.PROMPT_CODEGEN) {
                content = {
                    prompt: this.splitPromptTemplate?.value || '',
                    codegen: this.splitCodegenTemplate?.value || ''
                };
            } else {
                content = this.templateContent.value;
            }

            const response = await apiService.saveTemplate({
                type: this.currentMode,
                content: this.content
            });

            if (response.data.success) {
                if (this.currentMode === MODES.PROMPT) {
                    this.promptTemplate = this.currentTemplate;
                } else if (this.currentMode === MODES.CODEGEN) {
                    this.codegenTemplate = this.currentTemplate;
                } else {
                    this.promptTemplate = content.prompt;
                    this.codegenTemplate = content.codegen;
                }
                UIHelper.showSuccess('Template saved successfully!', this.config.messageArea);
            } else {
                throw new Error(response.data.message);
            }
        } catch (error) {
            UIHelper.showError(`Failed to save template: ${error.message}`, this.config.messageArea);
        }
    }

    setMode(mode) {
        this.currentMode = mode;
        this.fetchTemplates(mode);
    }

    getCurrentTemplate() {
        if (this.currentMode === MODES.PROMPT_CODEGEN) {
            return {
                prompt: this.promptTemplate,
                codegen: this.codegenTemplate
            };
        }
        return this.currentTemplate;
    }

    getPromptTemplate() {
        return this.promptTemplate;
    }

    getCodegenTemplate() {
        return this.codegenTemplate;
    }

    setCodegenTemplate(content) {
        this.codegenTemplate = content;
        // 如果在分栏模式下，同时更新视图
        if (this.splitCodegenTemplate) {
            this.splitCodegenTemplate.value = content;
        }
        // 触发change事件
        if (this.splitCodegenTemplate) {
            const event = new Event('change');
            this.splitCodegenTemplate.dispatchEvent(event);
        }
    }

    // 添加获取编辑器元素的方法
    getCodegenTemplateEditor() {
        return this.splitCodegenTemplate;
    }
}
