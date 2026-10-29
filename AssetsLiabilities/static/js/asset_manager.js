/**
 * AssetManager - Generic CRUD Manager for Assets/Liabilities
 * Handles all CRUD operations with modal management
 * Reusable across all asset types
 */
class AssetManager {
    constructor(config) {
        this.assetType = config.assetType;
        this.apiEndpoints = config.apiEndpoints;
        this.hasTypes = config.hasTypes || false;
        this.typeField = config.typeField || 'type';
        // Sorting is opt-in per page; the chosen order is remembered per asset type
        this.sortable = config.sortable || false;
        this.sortStorageKey = `sort-${this.assetType}`;
        const savedSortKey = this.sortable ? localStorage.getItem(this.sortStorageKey) : null;
        this.sortKey = AssetManager.SORT_KEYS.includes(savedSortKey) ? savedSortKey : AssetManager.DEFAULT_SORT_KEY;
        this.assets = [];
        this.messages = Object.assign({
            added: gettext('js_asset_added'),
            updated: gettext('js_asset_updated'),
            deleted: gettext('js_asset_deleted'),
            deleteFailed: gettext('js_delete_failed'),
            loadFailed: gettext('js_load_assets_failed'),
            loadDetailsFailed: gettext('js_load_details_failed')
        }, config.messages || {});
        this.init();
    }

    init() {
        console.log('AssetManager initialized for:', this.assetType);
        this.bindEvents();
        this.loadAssets();
        
        // Bind global delete confirmation button (only once)
        if (!window.deleteConfirmBound) {
            $('#confirmDeleteBtn').on('click', () => {
                if (window.currentAssetManager) {
                    window.currentAssetManager.performDelete();
                }
            });
            window.deleteConfirmBound = true;
        }
        
        // Set this instance as the current manager
        window.currentAssetManager = this;
    }

    bindEvents() {
        console.log('Binding events for:', this.assetType);
        
        // Add button click
        $(`#add-${this.assetType}-btn`).on('click', () => {
            console.log('Add button clicked');
            this.showAddModal();
        });
        
        // Form submit
        $(`#${this.assetType}-form`).on('submit', (e) => {
            console.log('Form submitted');
            this.handleSubmit(e);
        });
        
        // Modal close
        $(`#${this.assetType}-modal`).on('hidden.bs.modal', () => this.resetForm());
        
        // Delegate edit/delete events
        $(document).on('click', `.edit-${this.assetType}`, (e) => {
            const id = $(e.currentTarget).data('id');
            console.log('Edit clicked for id:', id);
            this.showEditModal(id);
        });
        
        $(document).on('click', `.delete-${this.assetType}`, (e) => {
            const id = $(e.currentTarget).data('id');
            console.log('Delete clicked for id:', id);
            this.confirmDelete(id);
        });
        
        // Sort buttons: clicking a field sorts by it, clicking the active field again reverses the direction
        if (this.sortable) {
            this.sortControl = $(`#${this.assetType}-sort`);
            this.updateSortControl();
            this.sortControl.on('click', '.sort-option', (e) => {
                const button = $(e.currentTarget);
                const field = button.data('sort-field');
                const [currentField, currentDirection] = this.sortKey.split('_');
                const direction = field === currentField
                    ? (currentDirection === 'asc' ? 'desc' : 'asc')
                    : button.data('default-direction');
                this.sortKey = `${field}_${direction}`;
                localStorage.setItem(this.sortStorageKey, this.sortKey);
                this.updateSortControl();
                this.renderAssets(this.assets);
            });
        }
    }

    updateSortControl() {
        const [activeField, activeDirection] = this.sortKey.split('_');
        this.sortControl.find('.sort-option').each((index, element) => {
            const button = $(element);
            const field = button.data('sort-field');
            const isActive = field === activeField;
            const direction = isActive ? activeDirection : button.data('default-direction');
            button.toggleClass('active', isActive)
                .attr('aria-pressed', isActive)
                .attr('data-direction', isActive ? direction : null)
                .attr('title', gettext(`sort_${field}_${direction}`));
        });
    }

    async loadAssets() {
        try {
            console.log('Loading assets from:', this.apiEndpoints.list);
            const response = await $.ajax({
                url: this.apiEndpoints.list,
                method: 'GET',
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });
            
            console.log('Assets loaded:', response);
            this.assets = response.assets;
            this.renderAssets(this.assets);
            if (response.total !== undefined) {
                this.updateTotal(response.total);
            }
        } catch (error) {
            console.error('Error loading assets:', error);
            const container = $(`#${this.assetType}-list`);
            container.removeClass('loading'); // Remove loading state on error
            this.showError(this.messages.loadFailed);
        }
    }

    renderAssets(assets) {
        const container = $(`#${this.assetType}-list`);
        container.removeClass('loading kanban-container card-grid'); // Reset layout before re-rendering
        container.empty();

        if (assets.length === 0) {
            container.append(this.getEmptyState());
            return;
        }

        if (this.hasTypes) {
            this.renderKanban(assets, container);
        } else {
            this.renderCards(this.sortAssets(assets), container);
        }
    }

    /**
     * Return a sorted copy based on the selected sort key (field_direction)
     */
    sortAssets(assets) {
        const byName = (a, b) => a.name.localeCompare(b.name, undefined, { sensitivity: 'base', numeric: true });
        const byDate = (a, b) => (new Date(a.created_at) - new Date(b.created_at)) || (a.id - b.id);
        const comparators = {
            date_asc: byDate,
            date_desc: (a, b) => byDate(b, a),
            name_asc: byName,
            name_desc: (a, b) => byName(b, a),
            value_asc: (a, b) => a.amount - b.amount,
            value_desc: (a, b) => b.amount - a.amount
        };
        return [...assets].sort(comparators[this.sortKey] || comparators[AssetManager.DEFAULT_SORT_KEY]);
    }

    renderKanban(assets, container) {
        // Group by type in server order so columns keep their place; only items inside a column are sorted
        const grouped = assets.reduce((acc, asset) => {
            const type = asset[this.typeField];
            if (!acc[type]) acc[type] = [];
            acc[type].push(asset);
            return acc;
        }, {});

        container.addClass('kanban-container');
        
        Object.entries(grouped).forEach(([type, items]) => {
            const column = this.createKanbanColumn(type, this.sortAssets(items));
            container.append(column);
        });
    }

    createKanbanColumn(type, items) {
        const total = items.reduce((sum, item) => sum + item.amount, 0);
        
        return $(`
            <div class="kanban-column">
                <div class="kanban-header">
                    <h6>${type}</h6>
                    <span class="column-total">${this.formatCurrency(total)}</span>
                </div>
                <div class="kanban-body">
                    ${items.map(item => this.createCard(item)).join('')}
                </div>
            </div>
        `);
    }

    renderCards(assets, container) {
        container.addClass('card-grid');
        assets.forEach(asset => {
            container.append(this.createCard(asset));
        });
    }

    createCard(asset) {
        // Build extra info HTML for percentage fields (mutual funds)
        let extraInfo = '';
        if (asset.large_cap_percentage !== undefined) {
            extraInfo = `
                <div class="allocation-info">
                    <div class="allocation-item">
                        <span class="allocation-label">${gettext('stock_asset_type_large_cap')}:</span>
                        <span class="allocation-value">${asset.large_cap_percentage}%</span>
                    </div>
                    <div class="allocation-item">
                        <span class="allocation-label">${gettext('stock_asset_type_mid_cap')}:</span>
                        <span class="allocation-value">${asset.mid_cap_percentage}%</span>
                    </div>
                    <div class="allocation-item">
                        <span class="allocation-label">${gettext('stock_asset_type_small_cap')}:</span>
                        <span class="allocation-value">${asset.small_cap_percentage}%</span>
                    </div>
                    <div class="allocation-item">
                        <span class="allocation-label">${gettext('label_debt')}:</span>
                        <span class="allocation-value">${asset.debt_percentage}%</span>
                    </div>
                </div>
            `;
        }
        
        // Build extra info HTML for transaction parties
        if (asset.from_party !== undefined) {
            extraInfo = `
                <div class="transaction-info">
                    <div class="transaction-item">
                        <span class="transaction-label">${gettext('form_label_from_party')}:</span>
                        <span class="transaction-value">${this.escapeHtml(asset.from_party)}</span>
                    </div>
                    <div class="transaction-item">
                        <span class="transaction-label">${gettext('form_label_to_party')}:</span>
                        <span class="transaction-value">${this.escapeHtml(asset.to_party)}</span>
                    </div>
                </div>
            `;
        }
        
        return `
            <div class="asset-card" data-id="${asset.id}">
                <div class="card-header">
                    <h6 class="card-title">${this.escapeHtml(asset.name)}</h6>
                    <div class="card-actions">
                        <button class="btn-icon edit-${this.assetType}" data-id="${asset.id}" title="${gettext('btn_edit')}">
                            <i class="icon-edit"></i>
                        </button>
                        <button class="btn-icon delete-${this.assetType}" data-id="${asset.id}" title="${gettext('btn_delete')}">
                            <i class="icon-delete"></i>
                        </button>
                    </div>
                </div>
                <div class="card-body">
                    <div class="amount">${this.formatCurrency(asset.amount)}</div>
                    ${extraInfo}
                    ${asset.created_at ? `<div class="meta">${gettext('label_added')} ${this.formatDate(asset.created_at)}</div>` : ''}
                </div>
            </div>
        `;
    }

    getEmptyState() {
        return `
            <div class="empty-state">
                <div class="empty-icon">📊</div>
                <h6>${gettext('js_empty_title')}</h6>
                <p>${interpolate(gettext('js_empty_hint'), [this.getDisplayName().toLocaleLowerCase()])}</p>
            </div>
        `;
    }

    showAddModal() {
        this.currentMode = 'add';
        this.currentId = null;
        $(`#${this.assetType}-modal-title`).text(interpolate(gettext('js_modal_add_title'), [this.getDisplayName()]));
        const modalEl = document.getElementById(`${this.assetType}-modal`);
        const modal = new bootstrap.Modal(modalEl);
        modal.show();
    }

    async showEditModal(id) {
        this.currentMode = 'edit';
        this.currentId = id;
        
        try {
            const asset = await $.ajax({
                url: `${this.apiEndpoints.detail}${id}/`,
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            this.populateForm(asset);
            $(`#${this.assetType}-modal-title`).text(interpolate(gettext('js_modal_edit_title'), [this.getDisplayName()]));
            const modalEl = document.getElementById(`${this.assetType}-modal`);
            const modal = new bootstrap.Modal(modalEl);
            modal.show();
        } catch (error) {
            console.error('Error loading asset details:', error);
            this.showError(this.messages.loadDetailsFailed);
        }
    }

    populateForm(asset) {
        Object.keys(asset).forEach(key => {
            const input = $(`#${this.assetType}-${key}`);
            if (input.length) {
                input.val(asset[key]);
            }
        });
    }

    async handleSubmit(e) {
        e.preventDefault();
        console.log('Handle submit called, mode:', this.currentMode);
        
        const formData = this.getFormData();
        const url = this.currentMode === 'add' 
            ? this.apiEndpoints.create 
            : `${this.apiEndpoints.update}${this.currentId}/update/`;
        
        const method = this.currentMode === 'add' ? 'POST' : 'PUT';
        
        console.log('Submitting to:', url, 'with method:', method);
        
        try {
            await $.ajax({
                url,
                method,
                data: JSON.stringify(formData),
                contentType: 'application/json',
                headers: {
                    'X-CSRFToken': this.getCsrfToken()
                }
            });
            
            const modalEl = document.getElementById(`${this.assetType}-modal`);
            const modal = bootstrap.Modal.getInstance(modalEl);
            if (modal) modal.hide();
            
            this.showSuccess(this.currentMode === 'add' ? this.messages.added : this.messages.updated);
            this.loadAssets();
        } catch (error) {
            console.error('Submit error:', error);
            this.handleFormErrors(error.responseJSON);
        }
    }

    getFormData() {
        const form = $(`#${this.assetType}-form`);
        const data = {};
        
        form.serializeArray().forEach(item => {
            data[item.name] = item.value;
        });
        
        return data;
    }

    confirmDelete(id) {
        // Store the id for the actual delete operation
        this.deleteId = id;
        
        // Show custom delete confirmation modal
        const modal = new bootstrap.Modal(document.getElementById('deleteConfirmModal'));
        modal.show();
    }
    
    async performDelete() {
        const id = this.deleteId;
        console.log('Deleting asset:', id);
        
        // Hide the confirmation modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('deleteConfirmModal'));
        if (modal) modal.hide();
        
        try {
            await $.ajax({
                url: `${this.apiEndpoints.delete}${id}/delete/`,
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': this.getCsrfToken()
                }
            });
            
            this.showSuccess(this.messages.deleted);
            this.loadAssets();
        } catch (error) {
            console.error('Delete error:', error);
            this.showError(this.messages.deleteFailed);
        }
    }

    resetForm() {
        $(`#${this.assetType}-form`)[0].reset();
        $('.form-error').remove();
        $('.form-error-alert').remove();
        $('.is-invalid').removeClass('is-invalid');
    }

    handleFormErrors(errorResponse) {
        // Clear previous errors
        $('.form-error').remove();
        $('.form-error-alert').remove();
        $('.is-invalid').removeClass('is-invalid');
        
        if (!errorResponse) {
            this.showError(gettext('js_generic_error'));
            return;
        }
        
        // Handle errors from form validation (responseJSON.errors)
        const errors = errorResponse.errors || {};
        
        // Handle form-level errors (like percentage sum validation)
        if (errors.__all__) {
            const modalBody = $(`#${this.assetType}-modal .modal-body`);
            const errorAlert = $(`
                <div class="alert alert-danger form-error-alert" role="alert">
                    <strong>${gettext('js_validation_error_title')}</strong> ${errors.__all__[0]}
                </div>
            `);
            modalBody.prepend(errorAlert);
        }
        
        // Handle field-specific errors
        Object.entries(errors).forEach(([field, messages]) => {
            if (field !== '__all__') {
                const input = $(`#${this.assetType}-${field}`);
                if (input.length) {
                    input.addClass('is-invalid');
                    input.after(`<div class="form-error text-danger small mt-1">${messages[0]}</div>`);
                }
            }
        });
        
        // Handle generic error message
        if (errorResponse.error) {
            this.showError(errorResponse.error);
        }
        
        // If no specific errors, show generic message
        if (Object.keys(errors).length === 0 && !errorResponse.error) {
            this.showError(gettext('js_validation_failed'));
        }
    }

    updateTotal(total) {
        $(`#${this.assetType}-total`).text(this.formatCurrency(total));
    }

    getDisplayName() {
        const displayNames = {
            'debt-assets': gettext('asset_name_debt_assets'),
            'stock-assets': gettext('asset_name_stock_assets'),
            'mutual-funds': gettext('asset_name_mutual_funds'),
            'gold-assets': gettext('asset_name_gold_assets'),
            'crypto-assets': gettext('asset_name_crypto_assets'),
            'real-estate': gettext('asset_name_real_estate'),
            'liabilities': gettext('asset_name_liabilities'),
            'transactions': gettext('asset_name_transactions')
        };
        return displayNames[this.assetType] || this.assetType;
    }

    formatCurrency(amount) {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR',
            maximumFractionDigits: 0
        }).format(amount);
    }

    formatDate(dateString) {
        return new Date(dateString).toLocaleDateString('en-IN', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }

    escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, m => map[m]);
    }

    getCsrfToken() {
        return $('[name=csrfmiddlewaretoken]').val() || 
               document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    }

    showSuccess(message) {
        this.showToast(message, 'success');
    }

    showError(message) {
        this.showToast(message, 'error');
    }

    showToast(message, type) {
        const toast = $(`
            <div class="toast toast-${type}">
                <div class="toast-icon">${type === 'success' ? '✓' : '✕'}</div>
                <div class="toast-message">${message}</div>
                <button class="toast-close" aria-label="${gettext('btn_close')}">&times;</button>
            </div>
        `);
        
        // Close button handler
        toast.find('.toast-close').on('click', function() {
            toast.removeClass('show');
            setTimeout(() => toast.remove(), 300);
        });
        
        $('.toast-container').append(toast);
        
        setTimeout(() => toast.addClass('show'), 100);
        setTimeout(() => {
            toast.removeClass('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
}

// Sort options shared by all sortable pages; oldest first matches the original order
AssetManager.SORT_KEYS = ['date_asc', 'date_desc', 'name_asc', 'name_desc', 'value_asc', 'value_desc'];
AssetManager.DEFAULT_SORT_KEY = 'date_asc';

// Export for use in other files
window.AssetManager = AssetManager;
