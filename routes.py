"""
Route handlers for Task Tracker application.
Handles both web routes and RESTful API endpoints.
"""

from flask import render_template, request, redirect, url_for, flash, jsonify, session
from functools import wraps
from typing import Dict, Any, Optional


def get_current_user(user_model):
    """Get the current logged-in user from session."""
    if 'user_id' in session:
        return user_model.get_user_by_id(session['user_id'])
    return None


def login_required(f):
    """Decorator to require login for a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(user_model):
    """Decorator factory to require admin privileges for a route."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to access this page.', 'error')
                return redirect(url_for('login'))
            
            # Check admin status from session
            if not session.get('is_admin', False):
                flash('Admin privileges required.', 'error')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def register_routes(app, task_model, user_model):
    """Register all routes with the Flask app."""
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """User login page."""
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            
            if not username or not password:
                flash('Username and password are required!', 'error')
                return render_template('login.html')
            
            user = user_model.authenticate_user(username, password)
            
            if user:
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['is_admin'] = user['is_admin']
                flash(f'Welcome back, {user["username"]}!', 'success')
                
                # Redirect to next page if specified, otherwise go to index
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('index'))
            else:
                flash('Invalid username or password!', 'error')
        
        # If already logged in, redirect to index
        if 'user_id' in session:
            return redirect(url_for('index'))
        
        return render_template('login.html')
    
    @app.route('/logout', methods=['POST'])
    def logout():
        """User logout."""
        username = session.get('username', 'User')
        session.clear()
        flash(f'Goodbye, {username}! You have been logged out.', 'success')
        return redirect(url_for('login'))

    # ---------- User profile & goals routes ----------
    @app.route('/profile')
    @login_required
    def profile_view():
        current_user = get_current_user(user_model)
        if not current_user:
            flash('User not found.', 'error')
            return redirect(url_for('index'))
        # Load goals for the user
        try:
            goals = user_model.get_goals(current_user['id'])
        except Exception:
            goals = []
        return render_template('profile.html', user=current_user, goals=goals, current_user=current_user)

    @app.route('/profile/edit', methods=['GET', 'POST'])
    @login_required
    def edit_profile():
        current_user = get_current_user(user_model)
        if not current_user:
            flash('User not found.', 'error')
            return redirect(url_for('index'))

        if request.method == 'POST':
            try:
                # Basic info
                full_name = request.form.get('full_name', '').strip() or None
                occupation = request.form.get('occupation', '').strip() or None
                location = request.form.get('location', '').strip() or None
                birthday = request.form.get('birthday', '').strip() or None

                # Personal details
                bio = request.form.get('bio', '').strip() or None
                interests = request.form.get('interests', '').strip() or None
                skills = request.form.get('skills', '').strip() or None
                strengths_weaknesses = request.form.get('strengths_weaknesses', '').strip() or None

                updated = user_model.update_user_profile(
                    current_user['id'],
                    full_name=full_name,
                    occupation=occupation,
                    location=location,
                    birthday=birthday,
                    bio=bio,
                    interests=interests,
                    skills=skills,
                    strengths_weaknesses=strengths_weaknesses
                )

                if updated:
                    flash('Profile updated successfully.', 'success')
                else:
                    flash('No changes made to profile.', 'info')

                return redirect(url_for('profile_view'))
            except Exception as e:
                flash(f'Error updating profile: {e}', 'error')

        return render_template('edit_profile.html', user=current_user, current_user=current_user)

    # Goals: add, edit, delete
    @app.route('/goals/add', methods=['GET', 'POST'])
    @login_required
    def add_goal():
        current_user = get_current_user(user_model)
        if request.method == 'POST':
            try:
                title = request.form.get('title', '').strip()
                description = request.form.get('description', '').strip() or ''
                category = request.form.get('category', 'short_term')
                custom_category = request.form.get('custom_category', '').strip() or None
                target_date = request.form.get('target_date', '').strip() or None

                if not title:
                    flash('Goal title is required.', 'error')
                    return render_template('add_goal.html', current_user=current_user)

                goal_id = user_model.create_goal(current_user['id'], title, description, category, custom_category, target_date)
                flash('Goal added.', 'success')
                return redirect(url_for('profile_view'))
            except Exception as e:
                flash(f'Error adding goal: {e}', 'error')
        return render_template('add_goal.html', current_user=current_user)

    @app.route('/goals/<int:goal_id>/edit', methods=['GET', 'POST'])
    @login_required
    def edit_goal(goal_id):
        current_user = get_current_user(user_model)
        goal = user_model.get_goal_by_id(goal_id, user_id=current_user['id'])
        if not goal:
            flash('Goal not found or access denied.', 'error')
            return redirect(url_for('profile_view'))

        if request.method == 'POST':
            try:
                title = request.form.get('title', '').strip()
                description = request.form.get('description', '').strip() or ''
                category = request.form.get('category', 'short_term')
                custom_category = request.form.get('custom_category', '').strip() or None
                target_date = request.form.get('target_date', '').strip() or None
                is_completed = 1 if request.form.get('is_completed') == 'on' else 0

                if not title:
                    flash('Goal title is required.', 'error')
                    return render_template('edit_goal.html', goal=goal, current_user=current_user)

                updated = user_model.update_goal(goal_id, current_user['id'], title=title, description=description, category=category, custom_category=custom_category, target_date=target_date, is_completed=is_completed)
                if updated:
                    flash('Goal updated.', 'success')
                else:
                    flash('No changes made to goal.', 'info')
                return redirect(url_for('profile_view'))
            except Exception as e:
                flash(f'Error updating goal: {e}', 'error')

        return render_template('edit_goal.html', goal=goal, current_user=current_user)

    @app.route('/goals/<int:goal_id>/delete', methods=['POST'])
    @login_required
    def delete_goal(goal_id):
        current_user = get_current_user(user_model)
        success = user_model.delete_goal(goal_id, current_user['id'])
        if success:
            flash('Goal deleted.', 'success')
        else:
            flash('Could not delete goal.', 'error')
        return redirect(url_for('profile_view'))
    
    @app.route('/calendar')
    @login_required
    def calendar_view():
        """Calendar view showing tasks by month."""
        from datetime import datetime, date, timedelta
        from calendar import monthrange
        
        current_user = get_current_user(user_model)
        user_id = current_user['id'] if current_user else None
        
        # Get month and year from query params, default to current month
        try:
            year = int(request.args.get('year', date.today().year))
            month = int(request.args.get('month', date.today().month))
        except (ValueError, TypeError):
            year = date.today().year
            month = date.today().month
        
        # Get first and last day of month
        first_day = date(year, month, 1)
        last_day = date(year, month, monthrange(year, month)[1])
        today = date.today()
        
        # Get all tasks for this month
        tasks = task_model.get_tasks_by_date_range(
            first_day.isoformat(), 
            last_day.isoformat(), 
            user_id=user_id
        )
        
        # Group tasks by date
        tasks_by_date = {}
        for task in tasks:
            task_date = task.get('due_date')
            if task_date:
                if task_date not in tasks_by_date:
                    tasks_by_date[task_date] = []
                tasks_by_date[task_date].append(task)
            # Handle recurring tasks
            elif task.get('recurring_type'):
                recurring_type = task.get('recurring_type')
                # Show recurring tasks on days they occur
                if recurring_type == 'daily':
                    # Show on all days in month
                    for day in range(1, monthrange(year, month)[1] + 1):
                        day_date = date(year, month, day).isoformat()
                        # Check if within recurring end date
                        if not task.get('recurring_end_date') or day_date <= task.get('recurring_end_date'):
                            if day_date not in tasks_by_date:
                                tasks_by_date[day_date] = []
                            tasks_by_date[day_date].append(task)
        
        # Calculate previous and next month
        if month == 1:
            prev_month, prev_year = 12, year - 1
        else:
            prev_month, prev_year = month - 1, year
        
        if month == 12:
            next_month, next_year = 1, year + 1
        else:
            next_month, next_year = month + 1, year
        
        return render_template('calendar.html',
                             year=year,
                             month=month,
                             month_name=first_day.strftime('%B'),
                             tasks_by_date=tasks_by_date,
                             first_day=first_day,
                             last_day=last_day,
                             prev_month=prev_month,
                             prev_year=prev_year,
                             next_month=next_month,
                             next_year=next_year,
                             today=today,
                             timedelta=timedelta,
                             current_user=current_user)

    @app.route('/habits', methods=['GET', 'POST'])
    @login_required
    def habits_view():
        """List and add habits for the current user."""
        current_user = get_current_user(user_model)
        if request.method == 'POST':
            try:
                name = request.form.get('name', '').strip()
                description = request.form.get('description', '').strip() or ''
                if not name:
                    flash('Habit name is required.', 'error')
                    return redirect(url_for('habits_view'))

                user_model.create_habit(current_user['id'], name, description)
                flash('Habit added.', 'success')
            except Exception as e:
                flash(f'Error adding habit: {e}', 'error')
            return redirect(url_for('habits_view'))

        habits = []
        try:
            habits = user_model.get_habits(current_user['id']) if current_user else []
        except Exception:
            habits = []

        return render_template('habits.html', habits=habits, user=current_user, current_user=current_user)

    @app.route('/habits/<int:habit_id>/mark', methods=['POST'])
    @login_required
    def mark_habit(habit_id):
        """Mark or unmark today's completion for a habit."""
        current_user = get_current_user(user_model)
        mark_val = request.form.get('mark', '1')
        done = True if str(mark_val) == '1' else False
        try:
            success = user_model.mark_habit(habit_id, done=done)
            if success:
                flash('Habit updated.', 'success')
            else:
                flash('Could not update habit.', 'error')
        except Exception as e:
            flash(f'Error updating habit: {e}', 'error')
        return redirect(url_for('habits_view'))

    @app.route('/habits/<int:habit_id>/delete', methods=['POST'])
    @login_required
    def delete_habit(habit_id):
        """Delete a habit and its entries."""
        current_user = get_current_user(user_model)
        try:
            success = user_model.delete_habit(habit_id, current_user['id'])
            if success:
                flash('Habit deleted.', 'success')
            else:
                flash('Could not delete habit (not found or permission denied).', 'error')
        except Exception as e:
            flash(f'Error deleting habit: {e}', 'error')
        return redirect(url_for('habits_view'))

    @app.route('/habits/<int:habit_id>/toggle', methods=['POST'])
    @login_required
    def toggle_habit(habit_id):
        """Toggle a habit entry for an arbitrary date (expects form field 'date' in YYYY-MM-DD)."""
        current_user = get_current_user(user_model)
        entry_date = request.form.get('date')
        if not entry_date:
            flash('Date is required to toggle habit.', 'error')
            return redirect(url_for('index'))
        # Only allow toggling for today's date
        from datetime import date as _date
        today_iso = _date.today().isoformat()
        if entry_date != today_iso:
            # If AJAX return JSON error, otherwise redirect silently
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'error': 'Only today can be updated.'}), 400
            return redirect(url_for('index'))
        try:
            new_state = user_model.toggle_habit_entry(habit_id, entry_date)
            # If AJAX request return JSON
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'done': bool(new_state)})
            flash('Habit updated.', 'success')
        except Exception as e:
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'error': str(e)}), 500
            flash(f'Error updating habit: {e}', 'error')
        return redirect(url_for('index'))
    
    @app.route('/')
    @login_required
    def index():
        """Homepage displaying all tasks."""
        try:
            current_user = get_current_user(user_model)
            user_id = current_user['id'] if current_user else None
            
            # Get filter and sort parameters
            status_filter = request.args.get('status', None)
            sort_by = request.args.get('sort', 'due_date')
            priority_filter = request.args.get('priority', None)
            
            # Get tasks from database (filtered by user)
            tasks = task_model.get_all_tasks(status=status_filter, sort_by=sort_by, user_id=user_id, priority_filter=priority_filter)
            
            # Get task statistics
            stats = task_model.get_task_count(user_id=user_id)

            # Prepare habit tracker data for current month
            from datetime import date
            import calendar

            try:
                year = int(request.args.get('year', date.today().year))
                month = int(request.args.get('month', date.today().month))
            except (ValueError, TypeError):
                year = date.today().year
                month = date.today().month

            num_days = calendar.monthrange(year, month)[1]
            # list of ISO date strings for the month
            month_days = [date(year, month, d).isoformat() for d in range(1, num_days + 1)]
            today_iso = date.today().isoformat()

            habits = user_model.get_habits(user_id) if current_user else []
            habit_ids = [h['id'] for h in habits]
            entries = user_model.get_habit_entries_for_range(habit_ids, month_days[0], month_days[-1]) if habit_ids else {}

            from datetime import datetime as _dt

            current_datetime = _dt.now().strftime('%Y-%m-%d %H:%M:%S')

            return render_template('index.html', 
                                 tasks=tasks, 
                                 stats=stats,
                                 current_filter=status_filter,
                                 current_sort=sort_by,
                                 current_user=current_user,
                                 habits=habits,
                                 month_days=month_days,
                                 month=month,
                                 year=year,
                                 entries=entries,
                                 current_datetime=current_datetime,
                                 today_iso=today_iso)
        except Exception as e:
            flash(f'Error loading tasks: {str(e)}', 'error')
            return render_template('index.html', tasks=[], stats={'total': 0, 'complete': 0, 'incomplete': 0}, current_user=get_current_user(user_model))
    
    @app.route('/add', methods=['GET', 'POST'])
    @login_required
    def add_task():
        """Add a new task."""
        current_user = get_current_user(user_model)
        user_id = current_user['id'] if current_user else None
        
        if request.method == 'POST':
            try:
                title = request.form.get('title', '').strip()
                description = request.form.get('description', '').strip()
                is_shared = request.form.get('is_shared') == 'on'
                due_date = request.form.get('due_date', '').strip() or None
                priority = request.form.get('priority', 'medium').strip()
                is_recurring = request.form.get('is_recurring') == 'on'
                recurring_type = request.form.get('recurring_type', '').strip() or None if is_recurring else None
                recurring_time = request.form.get('recurring_time', '').strip() or None
                recurring_end_date = request.form.get('recurring_end_date', '').strip() or None
                
                # Validation
                if not title:
                    flash('Task title is required!', 'error')
                    return render_template('add_task.html', current_user=current_user)
                
                if len(title) > 200:
                    flash('Task title must be less than 200 characters!', 'error')
                    return render_template('add_task.html', current_user=current_user)
                
                if len(description) > 1000:
                    flash('Task description must be less than 1000 characters!', 'error')
                    return render_template('add_task.html', current_user=current_user)
                
                # Validate priority
                if priority not in ['low', 'medium', 'high']:
                    priority = 'medium'
                
                # If recurring but no type selected, don't make it recurring
                if is_recurring and not recurring_type:
                    recurring_type = None
                    recurring_time = None
                    recurring_end_date = None
                
                # Create task
                task_id = task_model.create_task(
                    title, description, user_id=user_id, is_shared=is_shared,
                    due_date=due_date, recurring_type=recurring_type,
                    recurring_time=recurring_time, recurring_end_date=recurring_end_date,
                    priority=priority
                )
                flash('Task added successfully!', 'success')
                return redirect(url_for('index'))
                
            except ValueError as e:
                flash(str(e), 'error')
                return render_template('add_task.html', current_user=current_user)
            except Exception as e:
                flash(f'Error adding task: {str(e)}', 'error')
                return render_template('add_task.html', current_user=current_user)
        
        # Handle quick action for "Add Task for Today"
        quick_action = request.args.get('quick')
        quick_date = None
        if quick_action == 'today':
            from datetime import date
            quick_date = date.today().isoformat()
        
        return render_template('add_task.html', current_user=current_user, quick_date=quick_date)
    
    @app.route('/update/<int:task_id>', methods=['POST'])
    @login_required
    def update_task_status(task_id):
        """Update task status (toggle complete/incomplete)."""
        current_user = get_current_user(user_model)
        user_id = current_user['id'] if current_user else None
        
        try:
            status = request.form.get('status', 'complete')
            
            if status not in ['complete', 'incomplete']:
                flash('Invalid status!', 'error')
                return redirect(url_for('index'))
            
            success = task_model.update_task_status(task_id, status, user_id=user_id)
            
            if success:
                flash('Task status updated successfully!', 'success')
            else:
                flash('Task not found or you do not have permission!', 'error')
                
        except Exception as e:
            flash(f'Error updating task: {str(e)}', 'error')
        
        return redirect(url_for('index'))
    
    @app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
    @login_required
    def edit_task(task_id):
        """Edit task title and description."""
        current_user = get_current_user(user_model)
        user_id = current_user['id'] if current_user else None
        
        task = task_model.get_task_by_id(task_id, user_id=user_id)
        
        if not task:
            flash('Task not found or you do not have permission!', 'error')
            return redirect(url_for('index'))
        
        if request.method == 'POST':
            try:
                title = request.form.get('title', '').strip()
                description = request.form.get('description', '').strip()
                is_shared = request.form.get('is_shared') == 'on'
                due_date = request.form.get('due_date', '').strip() or None
                priority = request.form.get('priority', 'medium').strip()
                is_recurring = request.form.get('is_recurring') == 'on'
                recurring_type = request.form.get('recurring_type', '').strip() or None if is_recurring else None
                recurring_time = request.form.get('recurring_time', '').strip() or None
                recurring_end_date = request.form.get('recurring_end_date', '').strip() or None
                
                # Validation
                if not title:
                    flash('Task title is required!', 'error')
                    return render_template('edit_task.html', task=task, current_user=current_user)
                
                if len(title) > 200:
                    flash('Task title must be less than 200 characters!', 'error')
                    return render_template('edit_task.html', task=task, current_user=current_user)
                
                if len(description) > 1000:
                    flash('Task description must be less than 1000 characters!', 'error')
                    return render_template('edit_task.html', task=task, current_user=current_user)
                
                # Validate priority
                if priority not in ['low', 'medium', 'high']:
                    priority = 'medium'
                
                # If recurring but no type selected, don't make it recurring
                if is_recurring and not recurring_type:
                    recurring_type = None
                    recurring_time = None
                    recurring_end_date = None
                
                # Update task
                success = task_model.update_task(
                    task_id, title, description, user_id=user_id,
                    due_date=due_date, recurring_type=recurring_type,
                    recurring_time=recurring_time, recurring_end_date=recurring_end_date,
                    priority=priority
                )
                
                # Update sharing status if user is the owner
                if success and task.get('user_id') == user_id:
                    task_model.share_task(task_id, is_shared, user_id=user_id)
                
                if success:
                    flash('Task updated successfully!', 'success')
                    return redirect(url_for('index'))
                else:
                    flash('Error updating task!', 'error')
                    
            except ValueError as e:
                flash(str(e), 'error')
            except Exception as e:
                flash(f'Error updating task: {str(e)}', 'error')
        
        return render_template('edit_task.html', task=task, current_user=current_user)
    
    @app.route('/delete/<int:task_id>', methods=['POST'])
    @login_required
    def delete_task(task_id):
        """Delete a task."""
        current_user = get_current_user(user_model)
        user_id = current_user['id'] if current_user else None
        
        try:
            success = task_model.delete_task(task_id, user_id=user_id)
            
            if success:
                flash('Task deleted successfully!', 'success')
            else:
                flash('Task not found or you do not have permission!', 'error')
                
        except Exception as e:
            flash(f'Error deleting task: {str(e)}', 'error')
        
        return redirect(url_for('index'))
    
    # ========== Admin Routes ==========
    
    @app.route('/admin/users', methods=['GET', 'POST'])
    @login_required
    def admin_users():
        """Admin user management page."""
        current_user = get_current_user(user_model)
        
        # Check if user is admin
        if not current_user or not session.get('is_admin', False):
            flash('Admin privileges required.', 'error')
            return redirect(url_for('index'))
        
        if request.method == 'POST':
            # Create new user
            try:
                username = request.form.get('username', '').strip()
                password = request.form.get('password', '')
                is_admin = request.form.get('is_admin') == 'on'
                
                if not username or not password:
                    flash('Username and password are required!', 'error')
                else:
                    user_id = user_model.create_user(username, password, is_admin=is_admin)
                    flash(f'User "{username}" created successfully!', 'success')
                    return redirect(url_for('admin_users'))
                    
            except ValueError as e:
                flash(str(e), 'error')
            except Exception as e:
                flash(f'Error creating user: {str(e)}', 'error')
        
        # Get all users
        users = user_model.get_all_users()
        return render_template('admin_users.html', users=users, current_user=current_user)
    
    @app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
    @login_required
    def admin_delete_user(user_id):
        """Delete a user (admin only)."""
        current_user = get_current_user(user_model)
        
        # Check if user is admin
        if not current_user or not session.get('is_admin', False):
            flash('Admin privileges required.', 'error')
            return redirect(url_for('index'))
        
        # Prevent deleting yourself
        if user_id == current_user['id']:
            flash('You cannot delete your own account!', 'error')
            return redirect(url_for('admin_users'))
        
        try:
            success = user_model.delete_user(user_id)
            if success:
                flash('User deleted successfully!', 'success')
            else:
                flash('User not found!', 'error')
        except Exception as e:
            flash(f'Error deleting user: {str(e)}', 'error')
        
        return redirect(url_for('admin_users'))
    
    # ========== RESTful API Endpoints ==========
    
    @app.route('/api/tasks', methods=['GET'])
    @login_required
    def api_get_all_tasks():
        """Get all tasks in JSON format."""
        try:
            current_user = get_current_user(user_model)
            user_id = current_user['id'] if current_user else None
            
            status_filter = request.args.get('status', None)
            sort_by = request.args.get('sort', 'created_at')
            
            tasks = task_model.get_all_tasks(status=status_filter, sort_by=sort_by, user_id=user_id)
            stats = task_model.get_task_count(user_id=user_id)
            
            return jsonify({
                'success': True,
                'data': tasks,
                'stats': stats
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/task/<int:task_id>', methods=['GET'])
    @login_required
    def api_get_task(task_id):
        """Get a specific task by ID."""
        try:
            current_user = get_current_user(user_model)
            user_id = current_user['id'] if current_user else None
            
            task = task_model.get_task_by_id(task_id, user_id=user_id)
            
            if task:
                return jsonify({
                    'success': True,
                    'data': task
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': 'Task not found or access denied'
                }), 404
                
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/task', methods=['POST'])
    @login_required
    def api_create_task():
        """Create a new task via API."""
        try:
            current_user = get_current_user(user_model)
            user_id = current_user['id'] if current_user else None
            
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'No JSON data provided'
                }), 400
            
            title = data.get('title', '').strip()
            description = data.get('description', '').strip()
            is_shared = data.get('is_shared', False)
            
            # Validation
            if not title:
                return jsonify({
                    'success': False,
                    'error': 'Task title is required'
                }), 400
            
            if len(title) > 200:
                return jsonify({
                    'success': False,
                    'error': 'Task title must be less than 200 characters'
                }), 400
            
            if len(description) > 1000:
                return jsonify({
                    'success': False,
                    'error': 'Task description must be less than 1000 characters'
                }), 400
            
            # Create task
            task_id = task_model.create_task(title, description, user_id=user_id, is_shared=is_shared)
            task = task_model.get_task_by_id(task_id, user_id=user_id)
            
            return jsonify({
                'success': True,
                'data': task,
                'message': 'Task created successfully'
            }), 201
            
        except ValueError as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 400
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/task/<int:task_id>', methods=['PUT'])
    @login_required
    def api_update_task(task_id):
        """Update a task via API."""
        try:
            current_user = get_current_user(user_model)
            user_id = current_user['id'] if current_user else None
            
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'No JSON data provided'
                }), 400
            
            # Check if task exists and user has access
            task = task_model.get_task_by_id(task_id, user_id=user_id)
            if not task:
                return jsonify({
                    'success': False,
                    'error': 'Task not found or access denied'
                }), 404
            
            # Update fields if provided
            title = data.get('title', task['title']).strip()
            description = data.get('description', task.get('description', '')).strip()
            status = data.get('status', task['status'])
            is_shared = data.get('is_shared', task.get('is_shared', False))
            
            # Validation
            if not title:
                return jsonify({
                    'success': False,
                    'error': 'Task title is required'
                }), 400
            
            if len(title) > 200:
                return jsonify({
                    'success': False,
                    'error': 'Task title must be less than 200 characters'
                }), 400
            
            if len(description) > 1000:
                return jsonify({
                    'success': False,
                    'error': 'Task description must be less than 1000 characters'
                }), 400
            
            if status not in ['complete', 'incomplete']:
                return jsonify({
                    'success': False,
                    'error': "Status must be 'complete' or 'incomplete'"
                }), 400
            
            # Update task
            task_model.update_task(task_id, title, description, user_id=user_id)
            task_model.update_task_status(task_id, status, user_id=user_id)
            
            # Update sharing status if user is the owner
            if task.get('user_id') == user_id:
                task_model.share_task(task_id, is_shared, user_id=user_id)
            
            updated_task = task_model.get_task_by_id(task_id, user_id=user_id)
            
            return jsonify({
                'success': True,
                'data': updated_task,
                'message': 'Task updated successfully'
            }), 200
            
        except ValueError as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 400
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/task/<int:task_id>', methods=['DELETE'])
    @login_required
    def api_delete_task(task_id):
        """Delete a task via API."""
        try:
            current_user = get_current_user(user_model)
            user_id = current_user['id'] if current_user else None
            
            # Check if task exists and user has access
            task = task_model.get_task_by_id(task_id, user_id=user_id)
            if not task:
                return jsonify({
                    'success': False,
                    'error': 'Task not found or access denied'
                }), 404
            
            # Delete task
            success = task_model.delete_task(task_id, user_id=user_id)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': 'Task deleted successfully'
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': 'Failed to delete task'
                }), 500
                
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

