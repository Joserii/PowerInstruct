export class JsonViewer {
    constructor(config, containerId) {
        this.container = document.getElementById(containerId);
        this.expandAllBtn = document.getElementById('expand-all');
        this.collapseAllBtn = document.getElementById('collapse-all');
        this.copyBtn = document.getElementById('copy-json');
        this.jsonData = null;
        this.defaultCollapsed = true; // 默认折叠

        this.setupEventListeners();
    }

    setupEventListeners() {
        if (this.expandAllBtn) {
            this.expandAllBtn.addEventListener('click', () => this.expandAll());
        }
        if (this.collapseAllBtn) {
            this.collapseAllBtn.addEventListener('click', () => this.collapseAll());
        }
        if (this.copyBtn) {
            this.copyBtn.addEventListener('click', () => this.copyToClipboard());
        }
    }

    show(jsonData) {
        this.jsonData = jsonData;
        const container = document.getElementById('json-preview-container');
        if (container) {
            container.style.display = 'block';
        }
        this.render();
    }

    hide() {
        const container = document.getElementById('json-preview-container');
        if (container) {
            container.style.display = 'none';
        }
    }

    render() {
        if (!this.container || !this.jsonData) return;
        
        this.container.innerHTML = this.formatJson(this.jsonData, 0);
        this.setupCollapsible();
    }

    formatJson(obj, level) {
        if (obj === null) return '<span class="null">null</span>';
        
        switch (typeof obj) {
            case 'string':
                return `<span class="string">"${this.escapeHtml(obj)}"</span>`;
            case 'number':
                return `<span class="number">${obj}</span>`;
            case 'boolean':
                return `<span class="boolean">${obj}</span>`;
            case 'object':
                if (Array.isArray(obj)) {
                    return this.formatArray(obj, level);
                } else {
                    return this.formatObject(obj, level);
                }
            default:
                return obj.toString();
        }
    }

    formatObject(obj, level) {
        if (Object.keys(obj).length === 0) return '{}';

        const indent = '  '.repeat(level);
        const pieces = Object.entries(obj).map(([key, value]) => {
            const formattedValue = this.formatJson(value, level + 1);
            return `
                <div class="json-line" ${this.defaultCollapsed ? 'style="display: none;"' : ''}>
                    <span class="key">${this.escapeHtml(key)}</span>: ${formattedValue}
                </div>`;
        });

        return `<div class="collapsible ${this.defaultCollapsed ? 'collapsed' : 'expanded'}">
            <span class="bracket">{</span>
            ${pieces.join('')}
            <span class="bracket">}</span>
        </div>`;
    }

    formatArray(arr, level) {
        if (arr.length === 0) return '[]';

        const indent = '  '.repeat(level);
        const pieces = arr.map(item => {
            return `
                <div class="json-line" ${this.defaultCollapsed ? 'style="display: none;"' : ''}>
                    ${this.formatJson(item, level + 1)}
                </div>`;
        });

        return `<div class="collapsible ${this.defaultCollapsed ? 'collapsed' : 'expanded'}">
            <span class="bracket">[</span>
            ${pieces.join('')}
            <span class="bracket">]</span>
        </div>`;
    }

    escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    setupCollapsible() {
        const collapsibles = this.container.getElementsByClassName('collapsible');
        Array.from(collapsibles).forEach(element => {
            element.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleCollapse(element);
            });
        });
    }

    toggleCollapse(element) {
        element.classList.toggle('expanded');
        element.classList.toggle('collapsed');
        
        const children = Array.from(element.children);
        children.forEach(child => {
            if (child.classList.contains('json-line')) {
                child.style.display = element.classList.contains('collapsed') ? 'none' : '';
            }
        });
    }

    expandAll() {
        const collapsibles = this.container.getElementsByClassName('collapsible');
        Array.from(collapsibles).forEach(element => {
            element.classList.remove('collapsed');
            element.classList.add('expanded');
            Array.from(element.children).forEach(child => {
                if (child.classList.contains('json-line')) {
                    child.style.display = '';
                }
            });
        });
    }

    collapseAll() {
        const collapsibles = this.container.getElementsByClassName('collapsible');
        Array.from(collapsibles).forEach(element => {
            element.classList.remove('expanded');
            element.classList.add('collapsed');
            Array.from(element.children).forEach(child => {
                if (child.classList.contains('json-line')) {
                    child.style.display = 'none';
                }
            });
        });
    }

    async copyToClipboard() {
        try {
            await navigator.clipboard.writeText(JSON.stringify(this.jsonData, null, 2));
            // 可以添加一个复制成功的提示
            this.copyBtn.innerHTML = '<i class="bi bi-check"></i> 已复制';
            setTimeout(() => {
                this.copyBtn.innerHTML = '<i class="bi bi-clipboard"></i> 复制';
            }, 2000);
        } catch (err) {
            console.error('Failed to copy:', err);
        }
    }
}
