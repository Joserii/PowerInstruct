import { FileUploader } from './modules/fileUpload.js';
import { TemplateManager } from './modules/templateManager.js';
import { ModeManager } from './modules/modeManager.js';
import { ModelSelector } from './modules/modelSelector.js';
import { Analyzer } from './modules/analyzer.js';
import { CodeExecutor } from './modules/codeExecutor.js';
import { SidebarManager } from './modules/sidebarManager.js';
import { JsonViewer } from './modules/fileViewer.js';

document.addEventListener('DOMContentLoaded', function() {

    const config = {
        singleFileUpload: document.getElementById('single-file-upload'),
        batchFileUpload: document.getElementById('batch-file-upload'),
        fileInput: document.getElementById('file-input'),
        zipInput: document.getElementById('zip-input'),
        previewArea: document.getElementById('preview-area'),
        templateTitle: document.getElementById('template-title'),

        templateContent: document.getElementById('template-content'),
        promptTemplate: document.getElementById('prompt-template'),
        codegenTemplate: document.getElementById('codegen-template'),
        mergeTemplate: document.getElementById('fill-code'),
        copysampleBtn: document.getElementById('copy-sample'),
        // promptModeBtn: document.getElementById('prompt-mode'),
        // codegenModeBtn: document.getElementById('codegen-mode'),

        // Multiple mode buttons ( for prompt-codegen mode )
        modeSwitchBtns: document.querySelectorAll('.btn-mode'),
        splitContainer: document.getElementById('split-container'),
        singleContainer: document.getElementById('single-container'),
        analyzeBtn: document.getElementById('analyze-btn'),
        generateSamplesBtn: document.getElementById('generate-samples'),
        generateSamplesContainer: document.getElementById('sample-output'),
        generateCodeBtn: document.getElementById('generate-code-btn'),
        exportJsonBtn: document.getElementById('export-json'),
        exportJsonlBtn: document.getElementById('export-jsonl'),
        exportInstructionJsonBtn: document.getElementById('export-instruction-json'),
        exportInstructionJsonlBtn: document.getElementById('export-instruction-jsonl'),

        executeCodeBtn: document.getElementById('execute-code-btn'),
        targetData: document.getElementById('target-data'),
        executeResult: document.getElementById('execute-result'),
        singleModeBtn: document.getElementById('single-mode'),
        batchModeBtn: document.getElementById('batch-mode'),
        messageArea: document.getElementById('message-area'),

        sidebar: document.getElementById('sidebar'),
        sidebarToggle: document.getElementById('sidebarToggle'),
    };

    const sidebarManager = new SidebarManager(config);
    config.sidebarManager = sidebarManager;
    const jsonViewer = new JsonViewer(config, 'json-viewer');
    config.jsonViewer = jsonViewer;
    const templateManager = new TemplateManager(config);
    const modelSelector = new ModelSelector(config);
    const fileUploader = new FileUploader(config);
    
    config.templateManager = templateManager;
    config.modelSelector = modelSelector;
    config.fileUploader = fileUploader;

    const modeManager = new ModeManager(config);
    const analyzer = new Analyzer(config);
    
    config.modeManager = modeManager;
    config.analyzer = analyzer;

    const codeExecutor = new CodeExecutor(config);

    config.analyzeBtn.disabled = true;
    config.executeCodeBtn.disabled = true;
});