document.addEventListener('DOMContentLoaded', function() {
    
    const Validators = {
        validateNumber(value, min, max, input) {
            if (input.validity.badInput) {
                return { valid: false, message: 'Invalid number' };
            }
            
            if (value === '') {
                return { valid: false, message: 'Required' };
            }
            
            const numValue = parseFloat(value);
            if (isNaN(numValue)) {
                return { valid: false, message: 'Invalid number' };
            }
            
            const isFloat = input.dataset.float === 'true';
            if (!isFloat && !Number.isInteger(numValue)) {
                return { valid: false, message: 'Must be an integer' };
            }
            
            if (min !== null && numValue < min) {
                return { valid: false, message: `Min: ${min}` };
            }
            
            if (max !== null && numValue > max) {
                return { valid: false, message: `Max: ${max}` };
            }
            
            return { valid: true };
        },
        
        validateString(value, minlength, maxlength, pattern, patternMessage) {
            if (value === '') {
                return { valid: false, message: 'Required' };
            }
            
            if (minlength !== null && value.length < minlength) {
                return { valid: false, message: `Min length: ${minlength}` };
            }
            
            if (maxlength !== null && value.length > maxlength) {
                return { valid: false, message: `Max length: ${maxlength}` };
            }
            
            if (pattern !== null) {
                try {
                    const regex = new RegExp(pattern);
                    if (!regex.test(value)) {
                        return { valid: false, message: patternMessage || 'Invalid format' };
                    }
                } catch (e) {
                    return { valid: false, message: `Pattern error: ${e.message}` };
                }
            }
            
            return { valid: true };
        },
        
        isHidden(element) {
            const optionalContent = element.closest('.pytypeinput-optional-content');
            return optionalContent?.classList.contains('hidden');
        }
    };
    
    const DOM = {
        getConstraints(input) {
            const isNumber = input.type === 'number';
            
            if (isNumber) {
                return {
                    min: input.dataset.min ? parseFloat(input.dataset.min) : null,
                    max: input.dataset.max ? parseFloat(input.dataset.max) : null
                };
            }
            
            return {
                minlength: input.dataset.minlength ? parseInt(input.dataset.minlength) : null,
                maxlength: input.dataset.maxlength ? parseInt(input.dataset.maxlength) : null,
                pattern: input.dataset.pattern || null,
                patternMessage: input.dataset.patternMessage || null
            };
        },
        
        showError(container, input, message, isListItem = false) {
            container.classList.add('pytypeinput-field--error');
            input.classList.add('pytypeinput-input--error');
            
            let errorEl = container.querySelector('.pytypeinput-error');
            
            if (!errorEl) {
                errorEl = document.createElement('div');
                errorEl.className = 'pytypeinput-error';
                
                if (isListItem) {
                    const listItemWrapper = container.closest('.pytypeinput-list-item-wrapper');
                    if (listItemWrapper) {
                        listItemWrapper.appendChild(errorEl);
                    } else {
                        const wrapper = input.closest('.pytypeinput-number-wrapper');
                        if (wrapper) {
                            wrapper.after(errorEl);
                        } else {
                            input.after(errorEl);
                        }
                    }
                } else {
                    const wrapper = input.closest('.pytypeinput-number-wrapper');
                    if (wrapper) {
                        wrapper.after(errorEl);
                    } else {
                        input.after(errorEl);
                    }
                }
            }
            
            errorEl.textContent = message;
        },
        
        removeError(container, isListItem = false) {
            container.classList.remove('pytypeinput-field--error');
            
            const input = container.querySelector(
                isListItem ? '.pytypeinput-list-input' : '.pytypeinput-input:not(.pytypeinput-list-input), .pytypeinput-checkbox, .pytypeinput-select'
            );
            
            if (input) {
                input.classList.remove('pytypeinput-input--error');
            }
            
            if (isListItem) {
                const listItemWrapper = container.closest('.pytypeinput-list-item-wrapper');
                if (listItemWrapper) {
                    const errorEl = listItemWrapper.querySelector('.pytypeinput-error');
                    errorEl?.remove();
                }
            } else {
                const errorEl = container.querySelector('.pytypeinput-error');
                errorEl?.remove();
            }
        }
    };
    
    function validateField(input, field) {
        if (Validators.isHidden(input)) {
            DOM.removeError(field);
            return;
        }
        
        if (input.type === 'checkbox' || input.tagName === 'SELECT' || input.type === 'file') {
            DOM.removeError(field);
            return;
        }
        
        const constraints = DOM.getConstraints(input);
        let result;
        
        if (input.type === 'number') {
            result = Validators.validateNumber(input.value, constraints.min, constraints.max, input);
        } else {
            result = Validators.validateString(input.value, constraints.minlength, constraints.maxlength, constraints.pattern, constraints.patternMessage);
        }
        
        DOM.removeError(field);
        
        if (!result.valid) {
            DOM.showError(field, input, result.message);
        }
    }
    
    function validateListItem(input) {
        if (input.type === 'checkbox' || input.tagName === 'SELECT' || input.type === 'file') {
            return;
        }
        
        const constraints = DOM.getConstraints(input);
        const content = input.closest('.pytypeinput-list-item-content');
        let result;
        
        if (input.type === 'number') {
            result = Validators.validateNumber(input.value, constraints.min, constraints.max, input);
        } else {
            result = Validators.validateString(input.value, constraints.minlength, constraints.maxlength, constraints.pattern, constraints.patternMessage);
        }
        
        DOM.removeError(content, true);
        
        if (!result.valid) {
            DOM.showError(content, input, result.message, true);
        }
    }
    
    function handleOptionalToggle(toggle) {
        const targetName = toggle.dataset.target;
        const targetContent = document.querySelector(`[data-optional-content="${targetName}"]`);
        
        if (!targetContent) return;
        
        if (toggle.checked) {
            targetContent.classList.remove('hidden');
            
            const field = targetContent.closest('.pytypeinput-field');
            const input = targetContent.querySelector('.pytypeinput-input:not(.pytypeinput-list-input), .pytypeinput-checkbox, .pytypeinput-select');
            
            if (input) {
                validateField(input, field);
            }
            
            targetContent.querySelectorAll('.pytypeinput-list-input').forEach(validateListItem);
        } else {
            targetContent.classList.add('hidden');
            
            const field = targetContent.closest('.pytypeinput-field');
            DOM.removeError(field);
            
            targetContent.querySelectorAll('.pytypeinput-list-item-content').forEach(content => {
                DOM.removeError(content, true);
            });
        }
    }
    
    function handleNumberControls() {
        document.addEventListener('click', (e) => {
            if (!e.target.classList.contains('pytypeinput-number-btn')) return;
            
            const wrapper = e.target.closest('.pytypeinput-number-wrapper');
            const input = wrapper.querySelector('.pytypeinput-input[type="number"]');
            const step = parseFloat(input.step) || 1;
            const min = input.dataset.min ? parseFloat(input.dataset.min) : null;
            const max = input.dataset.max ? parseFloat(input.dataset.max) : null;
            const currentValue = input.value === '' ? 0 : parseFloat(input.value);
            
            let newValue;
            if (e.target.classList.contains('pytypeinput-number-up')) {
                newValue = currentValue + step;
                if (max !== null && newValue > max) {
                    newValue = max;
                }
            } else {
                newValue = currentValue - step;
                if (min !== null && newValue < min) {
                    newValue = min;
                }
            }
            
            input.value = newValue;
            input.dispatchEvent(new Event('input', { bubbles: true }));
        });
    }
    
    function formatBytes(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    }
    
    function createFileListItem(file, index, input) {
        const item = document.createElement('div');
        item.className = 'pytypeinput-file-list-item';
        item.dataset.fileIndex = index;
        
        const fileInfo = document.createElement('div');
        fileInfo.className = 'pytypeinput-file-info';
        
        const name = document.createElement('span');
        name.className = 'pytypeinput-file-name';
        name.textContent = file.name;
        name.title = file.name;
        
        const size = document.createElement('span');
        size.className = 'pytypeinput-file-size';
        size.textContent = formatBytes(file.size);
        
        fileInfo.appendChild(name);
        fileInfo.appendChild(size);
        
        const removeBtn = document.createElement('button');
        removeBtn.type = 'button';
        removeBtn.className = 'pytypeinput-file-remove-btn';
        removeBtn.textContent = '×';
        removeBtn.title = 'Remove file';
        removeBtn.onclick = () => removeFileFromInput(input, index);
        
        item.appendChild(fileInfo);
        item.appendChild(removeBtn);
        
        return item;
    }
    
    function updateFileList(input) {
        const fieldName = input.dataset.fileInput;
        const fileListDiv = document.getElementById(`fileList-${fieldName}`);
        if (!fileListDiv) return;
        
        fileListDiv.innerHTML = '';
        
        Array.from(input.files).forEach((file, index) => {
            const item = createFileListItem(file, index, input);
            fileListDiv.appendChild(item);
        });
    }
    
    function removeFileFromInput(input, indexToRemove) {
        const dt = new DataTransfer();
        
        Array.from(input.files).forEach((file, index) => {
            if (index !== indexToRemove) {
                dt.items.add(file);
            }
        });
        
        input.files = dt.files;
        updateFileList(input);
    }
    
    function setupFileInputs() {
        document.querySelectorAll('[data-file-input]').forEach(input => {
            input.addEventListener('change', () => {
                updateFileList(input);
            });
        });
        
        document.querySelectorAll('[data-add-more-files]').forEach(btn => {
            const fieldName = btn.dataset.addMoreFiles;
            const input = document.querySelector(`[data-file-input="${fieldName}"]`);
            
            if (!input) return;
            
            btn.addEventListener('click', () => {
                const tempInput = document.createElement('input');
                tempInput.type = 'file';
                tempInput.multiple = true;
                if (input.accept) tempInput.accept = input.accept;
                
                tempInput.addEventListener('change', (e) => {
                    const dt = new DataTransfer();

                    Array.from(input.files).forEach(file => dt.items.add(file));
                    Array.from(e.target.files).forEach(file => dt.items.add(file));
                    
                    input.files = dt.files;
                    updateFileList(input);
                });
                
                tempInput.click();
            });
        });
    }
    
    function setupSliders() {
        document.querySelectorAll('.pytypeinput-slider').forEach(slider => {
            const output = slider.parentElement.querySelector('.pytypeinput-slider-value');
            
            if (output) {
                slider.addEventListener('input', () => {
                    output.textContent = slider.value;
                });
            }
        });
    }
    
    class ListManager {
        constructor(field) {
            this.field = field;
            this.wrapper = field.querySelector('.pytypeinput-list-wrapper');
            this.addBtn = this.wrapper.querySelector('.pytypeinput-list-add-btn');
            this.container = this.wrapper.querySelector('.pytypeinput-list-container');
            this.maxItems = field.dataset.maxItems ? parseInt(field.dataset.maxItems) : null;
            this.minItems = field.dataset.minItems ? parseInt(field.dataset.minItems) : 1;
            
            this.init();
        }
        
        init() {
            this.addBtn.addEventListener('click', () => this.addItem());
            this.container.addEventListener('click', (e) => this.handleRemove(e));
            
            this.container.querySelectorAll('.pytypeinput-list-input').forEach(input => {
                if (input.type !== 'checkbox' && input.tagName !== 'SELECT' && input.type !== 'file') {
                    input.addEventListener('input', () => validateListItem(input));
                    input.addEventListener('blur', () => validateListItem(input));
                }
            });
            
            this.updateButtons();
        }
        
        addItem() {
            if (this.maxItems !== null && this.container.children.length >= this.maxItems) {
                return;
            }
            
            const firstItemWrapper = this.container.querySelector('.pytypeinput-list-item-wrapper');
            const newItemWrapper = firstItemWrapper.cloneNode(true);
            const newItem = newItemWrapper.querySelector('.pytypeinput-list-item');
            const input = newItem.querySelector('.pytypeinput-list-input');
            
            if (input.type === 'checkbox') {
                input.checked = false;
            } else if (input.tagName === 'SELECT') {
                input.selectedIndex = 0;
            } else if (input.type === 'color') {
                input.value = '#000000';
            } else if (input.type === 'date' || input.type === 'time') {
                const defaultValue = input.dataset.default;
                input.value = defaultValue || '';
            } else if (input.type === 'range') {
                const min = input.min || 0;
                input.value = min;
                
                const output = newItem.querySelector('.pytypeinput-slider-value');
                if (output) {
                    output.textContent = min;
                }
            } else {
                input.value = '';
            }
            
            input.classList.remove('pytypeinput-input--error');
            
            const errorEl = newItemWrapper.querySelector('.pytypeinput-error');
            errorEl?.remove();
            
            if (input.type !== 'checkbox' && input.tagName !== 'SELECT' && input.type !== 'file') {
                input.addEventListener('input', () => validateListItem(input));
                input.addEventListener('blur', () => validateListItem(input));
            }
            
            if (input.type === 'range') {
                const output = newItem.querySelector('.pytypeinput-slider-value');
                if (output) {
                    input.addEventListener('input', () => {
                        output.textContent = input.value;
                    });
                }
            }
            
            this.container.appendChild(newItemWrapper);
            this.updateButtons();
        }
        
        handleRemove(e) {
            if (!e.target.classList.contains('pytypeinput-list-remove')) return;
            
            if (this.container.children.length > this.minItems) {
                e.target.closest('.pytypeinput-list-item-wrapper').remove();
                this.updateButtons();
            }
        }
        
        updateButtons() {
            const items = this.container.querySelectorAll('.pytypeinput-list-item');
            const itemCount = items.length;
            
            this.addBtn.classList.toggle('hidden', this.maxItems !== null && itemCount >= this.maxItems);
            
            items.forEach(item => {
                const removeBtn = item.querySelector('.pytypeinput-list-remove');
                const shouldHide = itemCount <= this.minItems;
                
                removeBtn.classList.toggle('hidden', shouldHide);
                item.classList.toggle('no-remove', shouldHide);
            });
        }
    }
    
    document.querySelectorAll('.pytypeinput-input, .pytypeinput-checkbox, .pytypeinput-select').forEach(input => {
        input.addEventListener('invalid', (e) => {
            e.preventDefault();
        });
    });
    
    document.querySelectorAll('.pytypeinput-optional-toggle').forEach(toggle => {
        toggle.addEventListener('change', () => handleOptionalToggle(toggle));
    });
    
    document.querySelectorAll('.pytypeinput-input:not(.pytypeinput-list-input), .pytypeinput-checkbox:not(.pytypeinput-list-input), .pytypeinput-select:not(.pytypeinput-list-input)').forEach(input => {
        const field = input.closest('.pytypeinput-field');
        
        if (input.type !== 'checkbox' && input.tagName !== 'SELECT' && input.type !== 'file') {
            input.addEventListener('input', () => validateField(input, field));
            input.addEventListener('blur', () => validateField(input, field));
        }
    });
    
    document.querySelectorAll('.pytypeinput-list-field').forEach(field => {
        const hasFileInput = field.querySelector('[data-file-input]');
        if (hasFileInput) return;
        
        new ListManager(field);
    });
    
    handleNumberControls();
    setupFileInputs();
    setupSliders();
});