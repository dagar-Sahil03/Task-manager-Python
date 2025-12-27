/**
 * Main JavaScript file for Task Tracker
 * Handles form validation, delete confirmations, and user interactions
 */

document.addEventListener('DOMContentLoaded', function() {
    // Delete confirmation
    const deleteForms = document.querySelectorAll('.delete-form');
    
    deleteForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const taskTitle = this.closest('.card')?.querySelector('.card-title')?.textContent.trim() || 'this task';
            
            if (confirm(`Are you sure you want to delete "${taskTitle}"? This action cannot be undone.`)) {
                this.submit();
            }
        });
    });
    
    // Form validation
    const forms = document.querySelectorAll('form[id$="Form"]');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const titleInput = this.querySelector('input[name="title"]');
            
            if (titleInput) {
                const title = titleInput.value.trim();
                
                if (!title) {
                    e.preventDefault();
                    alert('Task title is required!');
                    titleInput.focus();
                    return false;
                }
                
                if (title.length > 200) {
                    e.preventDefault();
                    alert('Task title must be less than 200 characters!');
                    titleInput.focus();
                    return false;
                }
            }
            
            const descriptionInput = this.querySelector('textarea[name="description"]');
            if (descriptionInput) {
                const description = descriptionInput.value.trim();
                
                if (description.length > 1000) {
                    e.preventDefault();
                    alert('Task description must be less than 1000 characters!');
                    descriptionInput.focus();
                    return false;
                }
            }
        });
    });
    
    // Character counter for text inputs
    const titleInputs = document.querySelectorAll('input[name="title"]');
    titleInputs.forEach(input => {
        const maxLength = input.getAttribute('maxlength');
        if (maxLength) {
            input.addEventListener('input', function() {
                const remaining = maxLength - this.value.length;
                const formText = this.parentElement.querySelector('.form-text');
                if (formText) {
                    formText.textContent = `${remaining} characters remaining (max ${maxLength})`;
                }
            });
        }
    });
    
    // Character counter for textareas
    const descriptionInputs = document.querySelectorAll('textarea[name="description"]');
    descriptionInputs.forEach(textarea => {
        const maxLength = textarea.getAttribute('maxlength');
        if (maxLength) {
            textarea.addEventListener('input', function() {
                const remaining = maxLength - this.value.length;
                const formText = this.parentElement.querySelector('.form-text');
                if (formText) {
                    formText.textContent = `${remaining} characters remaining (max ${maxLength})`;
                }
            });
        }
    });
    
    // Auto-dismiss flash messages after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
    
    // Smooth scroll to top on form submission
    const submitButtons = document.querySelectorAll('button[type="submit"]');
    submitButtons.forEach(button => {
        button.addEventListener('click', function() {
            if (this.form && this.form.checkValidity()) {
                setTimeout(() => {
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                }, 100);
            }
        });
    });
});

