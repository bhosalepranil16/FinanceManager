/**
 * DocumentManager - Document upload manager
 * Extends AssetManager with multipart file uploads, file validation and document cards
 */
class DocumentManager extends AssetManager {
    constructor(config) {
        super(Object.assign({
            messages: {
                added: gettext('js_document_added'),
                updated: gettext('js_document_updated'),
                deleted: gettext('js_document_deleted'),
                deleteFailed: gettext('js_document_delete_failed'),
                loadFailed: gettext('js_document_load_failed'),
                loadDetailsFailed: gettext('js_document_load_details_failed')
            }
        }, config));
        this.maxFileSize = config.maxFileSize;
        this.allowedExtensions = ['pdf', 'png', 'jpg', 'jpeg'];
    }

    getDisplayName() {
        return gettext('document');
    }

    getEmptyState() {
        return `
            <div class="empty-state">
                <div class="empty-icon">📁</div>
                <h6>${gettext('js_document_empty_title')}</h6>
                <p>${gettext('js_document_empty_hint')}</p>
            </div>
        `;
    }

    createCard(doc) {
        const icon = doc.file_extension === 'pdf' ? '📄' : '🖼️';
        return `
            <div class="asset-card" data-id="${doc.id}">
                <div class="card-header">
                    <h6 class="card-title">${this.escapeHtml(doc.name)}</h6>
                    <div class="card-actions">
                        <button class="btn-icon edit-${this.assetType}" data-id="${doc.id}" title="${gettext('btn_edit')}">
                            <i class="icon-edit"></i>
                        </button>
                        <button class="btn-icon delete-${this.assetType}" data-id="${doc.id}" title="${gettext('btn_delete')}">
                            <i class="icon-delete"></i>
                        </button>
                    </div>
                </div>
                <div class="card-body">
                    <div class="document-info">
                        <span class="document-icon">${icon}</span>
                        <div class="document-details">
                            <div class="document-file-name">${this.escapeHtml(doc.file_name)}</div>
                            <div class="document-file-meta">${this.escapeHtml(doc.file_extension.toUpperCase())} · ${this.formatFileSize(doc.file_size)}</div>
                        </div>
                    </div>
                    <div class="document-actions">
                        <a class="btn-document" href="${doc.file_url}" target="_blank" rel="noopener">${gettext('btn_view')}</a>
                        <a class="btn-document" href="${doc.download_url}">${gettext('btn_download')}</a>
                    </div>
                    ${doc.created_at ? `<div class="meta">${gettext('label_uploaded')} ${this.formatDate(doc.created_at)}</div>` : ''}
                </div>
            </div>
        `;
    }

    updateTotal(total) {
        $(`#${this.assetType}-total`).text(
            interpolate(ngettext('document_count', 'document_count_plural', total), { counter: total }, true)
        );
    }

    showAddModal() {
        $(`#${this.assetType}-file`).prop('required', true);
        this.hideCurrentFile();
        super.showAddModal();
    }

    populateForm(doc) {
        super.populateForm(doc);
        // A new file is optional when editing; the stored file is kept if none is chosen
        $(`#${this.assetType}-file`).prop('required', false);
        $(`#${this.assetType}-current-file`)
            .text(interpolate(gettext('js_document_current_file'), [doc.file_name]))
            .removeClass('d-none');
    }

    hideCurrentFile() {
        $(`#${this.assetType}-current-file`).addClass('d-none').text('');
    }

    resetForm() {
        super.resetForm();
        this.hideCurrentFile();
    }

    validateFile(file) {
        const extension = file.name.includes('.') ? file.name.split('.').pop().toLowerCase() : '';
        if (!this.allowedExtensions.includes(extension)) {
            return gettext('document_file_type_error');
        }
        if (file.size > this.maxFileSize) {
            return interpolate(gettext('document_file_size_error'), { size: this.maxFileSize / (1024 * 1024) }, true);
        }
        return null;
    }

    async handleSubmit(e) {
        e.preventDefault();

        const fileInput = $(`#${this.assetType}-file`)[0];
        if (fileInput.files.length > 0) {
            const fileError = this.validateFile(fileInput.files[0]);
            if (fileError) {
                this.handleFormErrors({ errors: { file: [fileError] } });
                return;
            }
        }

        const url = this.currentMode === 'add'
            ? this.apiEndpoints.create
            : `${this.apiEndpoints.update}${this.currentId}/update/`;

        try {
            await $.ajax({
                url,
                method: 'POST',
                data: new FormData($(`#${this.assetType}-form`)[0]),
                processData: false,
                contentType: false,
                headers: {
                    'X-CSRFToken': this.getCsrfToken()
                }
            });

            const modal = bootstrap.Modal.getInstance(document.getElementById(`${this.assetType}-modal`));
            if (modal) modal.hide();

            this.showSuccess(this.currentMode === 'add' ? this.messages.added : this.messages.updated);
            this.loadAssets();
        } catch (error) {
            console.error('Submit error:', error);
            this.handleFormErrors(error.responseJSON);
        }
    }

    formatFileSize(bytes) {
        if (bytes >= 1024 * 1024) {
            return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
        }
        return `${Math.max(1, Math.round(bytes / 1024))} KB`;
    }
}

// Export for use in other files
window.DocumentManager = DocumentManager;
