"""
Route handlers for Task Tracker application.
Handles both web routes and RESTful API endpoints.
"""

from flask import render_template, request, redirect, url_for, flash, jsonify
from typing import Dict, Any


def register_routes(app, task_model):
    """Register all routes with the Flask app."""
    
    @app.route('/')
    def index():
        """Homepage displaying all tasks."""
        try:
            # Get filter and sort parameters
            status_filter = request.args.get('status', None)
            sort_by = request.args.get('sort', 'created_at')
            
            # Get tasks from database
            tasks = task_model.get_all_tasks(status=status_filter, sort_by=sort_by)
            
            # Get task statistics
            stats = task_model.get_task_count()
            
            return render_template('index.html', 
                                 tasks=tasks, 
                                 stats=stats,
                                 current_filter=status_filter,
                                 current_sort=sort_by)
        except Exception as e:
            flash(f'Error loading tasks: {str(e)}', 'error')
            return render_template('index.html', tasks=[], stats={'total': 0, 'complete': 0, 'incomplete': 0})
    
    @app.route('/add', methods=['GET', 'POST'])
    def add_task():
        """Add a new task."""
        if request.method == 'POST':
            try:
                title = request.form.get('title', '').strip()
                description = request.form.get('description', '').strip()
                
                # Validation
                if not title:
                    flash('Task title is required!', 'error')
                    return render_template('add_task.html')
                
                if len(title) > 200:
                    flash('Task title must be less than 200 characters!', 'error')
                    return render_template('add_task.html')
                
                if len(description) > 1000:
                    flash('Task description must be less than 1000 characters!', 'error')
                    return render_template('add_task.html')
                
                # Create task
                task_id = task_model.create_task(title, description)
                flash('Task added successfully!', 'success')
                return redirect(url_for('index'))
                
            except ValueError as e:
                flash(str(e), 'error')
                return render_template('add_task.html')
            except Exception as e:
                flash(f'Error adding task: {str(e)}', 'error')
                return render_template('add_task.html')
        
        return render_template('add_task.html')
    
    @app.route('/update/<int:task_id>', methods=['POST'])
    def update_task_status(task_id):
        """Update task status (toggle complete/incomplete)."""
        try:
            status = request.form.get('status', 'complete')
            
            if status not in ['complete', 'incomplete']:
                flash('Invalid status!', 'error')
                return redirect(url_for('index'))
            
            success = task_model.update_task_status(task_id, status)
            
            if success:
                flash('Task status updated successfully!', 'success')
            else:
                flash('Task not found!', 'error')
                
        except Exception as e:
            flash(f'Error updating task: {str(e)}', 'error')
        
        return redirect(url_for('index'))
    
    @app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
    def edit_task(task_id):
        """Edit task title and description."""
        task = task_model.get_task_by_id(task_id)
        
        if not task:
            flash('Task not found!', 'error')
            return redirect(url_for('index'))
        
        if request.method == 'POST':
            try:
                title = request.form.get('title', '').strip()
                description = request.form.get('description', '').strip()
                
                # Validation
                if not title:
                    flash('Task title is required!', 'error')
                    return render_template('edit_task.html', task=task)
                
                if len(title) > 200:
                    flash('Task title must be less than 200 characters!', 'error')
                    return render_template('edit_task.html', task=task)
                
                if len(description) > 1000:
                    flash('Task description must be less than 1000 characters!', 'error')
                    return render_template('edit_task.html', task=task)
                
                # Update task
                success = task_model.update_task(task_id, title, description)
                
                if success:
                    flash('Task updated successfully!', 'success')
                    return redirect(url_for('index'))
                else:
                    flash('Error updating task!', 'error')
                    
            except ValueError as e:
                flash(str(e), 'error')
            except Exception as e:
                flash(f'Error updating task: {str(e)}', 'error')
        
        return render_template('edit_task.html', task=task)
    
    @app.route('/delete/<int:task_id>', methods=['POST'])
    def delete_task(task_id):
        """Delete a task."""
        try:
            success = task_model.delete_task(task_id)
            
            if success:
                flash('Task deleted successfully!', 'success')
            else:
                flash('Task not found!', 'error')
                
        except Exception as e:
            flash(f'Error deleting task: {str(e)}', 'error')
        
        return redirect(url_for('index'))
    
    # ========== RESTful API Endpoints ==========
    
    @app.route('/api/tasks', methods=['GET'])
    def api_get_all_tasks():
        """Get all tasks in JSON format."""
        try:
            status_filter = request.args.get('status', None)
            sort_by = request.args.get('sort', 'created_at')
            
            tasks = task_model.get_all_tasks(status=status_filter, sort_by=sort_by)
            stats = task_model.get_task_count()
            
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
    def api_get_task(task_id):
        """Get a specific task by ID."""
        try:
            task = task_model.get_task_by_id(task_id)
            
            if task:
                return jsonify({
                    'success': True,
                    'data': task
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': 'Task not found'
                }), 404
                
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/task', methods=['POST'])
    def api_create_task():
        """Create a new task via API."""
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'No JSON data provided'
                }), 400
            
            title = data.get('title', '').strip()
            description = data.get('description', '').strip()
            
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
            task_id = task_model.create_task(title, description)
            task = task_model.get_task_by_id(task_id)
            
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
    def api_update_task(task_id):
        """Update a task via API."""
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'No JSON data provided'
                }), 400
            
            # Check if task exists
            task = task_model.get_task_by_id(task_id)
            if not task:
                return jsonify({
                    'success': False,
                    'error': 'Task not found'
                }), 404
            
            # Update fields if provided
            title = data.get('title', task['title']).strip()
            description = data.get('description', task.get('description', '')).strip()
            status = data.get('status', task['status'])
            
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
            task_model.update_task(task_id, title, description)
            task_model.update_task_status(task_id, status)
            
            updated_task = task_model.get_task_by_id(task_id)
            
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
    def api_delete_task(task_id):
        """Delete a task via API."""
        try:
            # Check if task exists
            task = task_model.get_task_by_id(task_id)
            if not task:
                return jsonify({
                    'success': False,
                    'error': 'Task not found'
                }), 404
            
            # Delete task
            success = task_model.delete_task(task_id)
            
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

