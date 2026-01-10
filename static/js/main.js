/**
 * Main JavaScript file for Task Tracker
 * Handles form validation, delete confirmations, and user interactions
 */

document.addEventListener('DOMContentLoaded', function() {
    // Delete confirmation
    const deleteForms = document.querySelectorAll('.delete-form');
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
            if (themeToggle) {
                themeToggle.classList.remove('outline-mode-dark');
                themeToggle.classList.add('outline-mode-light');
            }
            if (pomodoroToggle) {
                pomodoroToggle.classList.remove('outline-mode-dark');
                pomodoroToggle.classList.add('outline-mode-light');
            }
        } else {
            body.classList.remove('dark-mode');
            if (themeIcon) themeIcon.className = 'bi bi-moon';
            if (themeToggle) {
                themeToggle.classList.remove('outline-mode-light');
                themeToggle.classList.add('outline-mode-dark');
            }
            if (pomodoroToggle) {
                pomodoroToggle.classList.remove('outline-mode-light');
                pomodoroToggle.classList.add('outline-mode-dark');
            }
        }
    }

    // Initialize theme from localStorage or system preference
    let savedTheme = localStorage.getItem('theme');
    if (!savedTheme) {
        const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
        savedTheme = prefersDark ? 'dark' : 'light';
    }
    applyTheme(savedTheme);

    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const current = document.body.classList.contains('dark-mode') ? 'dark' : 'light';
            const next = current === 'dark' ? 'light' : 'dark';
            localStorage.setItem('theme', next);
            applyTheme(next);
        });
    }

    // Pomodoro timer (client-side only)
    const pomodoroToggle = document.getElementById('pomodoro-toggle');
    const pomodoroModalEl = document.getElementById('pomodoroModal');
    const pomodoroDisplay = document.getElementById('pomodoro-display');
    const pomodoroStart = document.getElementById('pomodoro-start');
    const pomodoroPause = document.getElementById('pomodoro-pause');
    const pomodoroReset = document.getElementById('pomodoro-reset');

    let pomodoroModal = null;
    if (pomodoroModalEl) pomodoroModal = new bootstrap.Modal(pomodoroModalEl);

    let timerSecs = 25 * 60; // default 25 minutes
    let timerInterval = null;
    let running = false;

    function formatTime(s) {
        const mm = String(Math.floor(s / 60)).padStart(2, '0');
        const ss = String(s % 60).padStart(2, '0');
        return `${mm}:${ss}`;
    }

    function renderTimer() {
        if (pomodoroDisplay) pomodoroDisplay.textContent = formatTime(timerSecs);
    }

    function startTimer() {
        if (running) return;
        running = true;
        timerInterval = setInterval(() => {
            timerSecs -= 1;
            renderTimer();
            if (timerSecs <= 0) {
                clearInterval(timerInterval);
                running = false;
                // simple notification
                try { new Notification('Pomodoro', { body: 'Time is up!' }); } catch (e) {}
                alert('Pomodoro finished — take a short break!');
            }
        }, 1000);
    }

    function pauseTimer() {
        if (!running) return;
        clearInterval(timerInterval);
        running = false;
    }

    function resetTimer() {
        clearInterval(timerInterval);
        running = false;
        timerSecs = 25 * 60;
        renderTimer();
    }

    if (pomodoroToggle && pomodoroModal) {
        pomodoroToggle.addEventListener('click', () => pomodoroModal.show());
    }
    if (pomodoroStart) pomodoroStart.addEventListener('click', startTimer);
    if (pomodoroPause) pomodoroPause.addEventListener('click', pauseTimer);
    if (pomodoroReset) pomodoroReset.addEventListener('click', resetTimer);

    renderTimer();
});

