/**
 * UserProfileManager - Data import for the User Profile page
 * Uploads a JSON export file and shows the result or validation errors
 */
class UserProfileManager {
    constructor(config) {
        this.importUrl = config.importUrl;
        this.maxFileSize = config.maxFileSize;
        this.form = $('#profile-import-form');
        this.fileInput = $('#profile-import-file');
        this.bindEvents();
    }

    bindEvents() {
        this.form.on('submit', (e) => this.handleSubmit(e));
        $('#profile-import-confirm-btn').on('click', () => {
            const modal = bootstrap.Modal.getInstance(document.getElementById('profile-import-confirm-modal'));
            if (modal) modal.hide();
            this.uploadFile();
        });
    }

    handleSubmit(e) {
        e.preventDefault();
        this.clearMessages();

        const fileError = this.validateFile(this.fileInput[0].files[0]);
        if (fileError) {
            this.showFieldError(fileError);
            return;
        }

        if ($('#profile-import-replace_existing').is(':checked')) {
            new bootstrap.Modal(document.getElementById('profile-import-confirm-modal')).show();
            return;
        }
        this.uploadFile();
    }

    validateFile(file) {
        if (!file) {
            return gettext('import_file_required');
        }
        if (!file.name.toLowerCase().endsWith('.json')) {
            return gettext('import_file_type_error');
        }
        if (file.size > this.maxFileSize) {
            return interpolate(gettext('import_file_size_error'), { size: this.maxFileSize / (1024 * 1024) }, true);
        }
        return null;
    }

    async uploadFile() {
        const submitButton = $('#profile-import-btn');
        submitButton.prop('disabled', true);

        try {
            const response = await $.ajax({
                url: this.importUrl,
                method: 'POST',
                data: new FormData(this.form[0]),
                processData: false,
                contentType: false,
                headers: {
                    'X-CSRFToken': this.getCsrfToken()
                }
            });

            const message = interpolate(
                ngettext('js_import_success', 'js_import_success_plural', response.total),
                { count: response.total },
                true
            );
            this.showResult(message, response.created);
            this.showToast(message, 'success');
            this.form[0].reset();
        } catch (error) {
            console.error('Import error:', error);
            this.handleErrors(error.responseJSON);
        } finally {
            submitButton.prop('disabled', false);
        }
    }

    handleErrors(errorResponse) {
        if (!errorResponse) {
            this.showToast(gettext('js_generic_error'), 'error');
            return;
        }

        const errors = errorResponse.errors || {};
        if (errors.file) {
            this.showFieldError(errors.file[0]);
        }

        if (errorResponse.details && errorResponse.details.length) {
            const list = $('<ul class="import-message-list"></ul>');
            errorResponse.details.forEach(detail => list.append($('<li></li>').text(detail)));
            $('#profile-import-errors').empty().append(list).removeClass('d-none');
        }

        if (errorResponse.error) {
            this.showToast(errorResponse.error, 'error');
        } else if (!errors.file) {
            this.showToast(gettext('js_validation_failed'), 'error');
        }
    }

    showResult(message, created) {
        const result = $('#profile-import-result').empty();
        result.append($('<strong></strong>').text(message));
        const list = $('<ul class="import-message-list"></ul>');
        created.forEach(item => list.append($('<li></li>').text(`${item.section}: ${item.count}`)));
        result.append(list).removeClass('d-none');
    }

    showFieldError(message) {
        this.fileInput.addClass('is-invalid');
        this.fileInput.after($('<div class="form-error text-danger small mt-1"></div>').text(message));
    }

    clearMessages() {
        this.form.find('.form-error').remove();
        this.fileInput.removeClass('is-invalid');
        $('#profile-import-result, #profile-import-errors').addClass('d-none').empty();
    }

    getCsrfToken() {
        return $('[name=csrfmiddlewaretoken]').val();
    }

    showToast(message, type) {
        const toast = $(`
            <div class="toast toast-${type}">
                <div class="toast-icon">${type === 'success' ? '✓' : '✕'}</div>
                <div class="toast-message"></div>
                <button class="toast-close" aria-label="${gettext('btn_close')}">&times;</button>
            </div>
        `);
        toast.find('.toast-message').text(message);

        toast.find('.toast-close').on('click', function() {
            toast.removeClass('show');
            setTimeout(() => toast.remove(), 300);
        });

        $('.toast-container').first().append(toast);

        setTimeout(() => toast.addClass('show'), 100);
        setTimeout(() => {
            toast.removeClass('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
}

// Export for use in other files
window.UserProfileManager = UserProfileManager;
