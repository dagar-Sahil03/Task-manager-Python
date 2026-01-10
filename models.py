"""
Database models and CRUD operations for Task Tracker application.
Uses SQLite for data persistence.
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional
from werkzeug.security import generate_password_hash, check_password_hash


class TaskModel:
    """Handles all database operations for tasks."""
    
    def __init__(self, db_path: str = "database/tasks.db"):
        """
        Initialize the database connection.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self._ensure_database_directory()
        self._init_database()
    
    def _ensure_database_directory(self):
        """Ensure the database directory exists."""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
    
    def _get_connection(self):
        """Get a database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        return conn
    
    def _init_database(self):
        """Initialize the database schema if it doesn't exist."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Create tasks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT NOT NULL DEFAULT 'incomplete',
                user_id INTEGER,
                is_shared INTEGER NOT NULL DEFAULT 0,
                due_date DATE,
                recurring_type TEXT,
                recurring_time TIME,
                recurring_end_date DATE,
                priority TEXT NOT NULL DEFAULT 'medium',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Add user_id column if it doesn't exist (for existing databases)
        try:
            cursor.execute("ALTER TABLE tasks ADD COLUMN user_id INTEGER")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        # Add is_shared column if it doesn't exist (for existing databases)
        try:
            cursor.execute("ALTER TABLE tasks ADD COLUMN is_shared INTEGER NOT NULL DEFAULT 0")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        # Add due_date column if it doesn't exist
        try:
            cursor.execute("ALTER TABLE tasks ADD COLUMN due_date DATE")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        # Add recurring_type column if it doesn't exist
        try:
            cursor.execute("ALTER TABLE tasks ADD COLUMN recurring_type TEXT")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        # Add recurring_time column if it doesn't exist
        try:
            cursor.execute("ALTER TABLE tasks ADD COLUMN recurring_time TIME")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        # Add recurring_end_date column if it doesn't exist
        try:
            cursor.execute("ALTER TABLE tasks ADD COLUMN recurring_end_date DATE")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        # Add priority column if it doesn't exist
        try:
            cursor.execute("ALTER TABLE tasks ADD COLUMN priority TEXT NOT NULL DEFAULT 'medium'")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        conn.commit()
        conn.close()
    
    def create_task(self, title: str, description: str = "", user_id: Optional[int] = None, is_shared: bool = False, 
                    due_date: Optional[str] = None, recurring_type: Optional[str] = None, 
                    recurring_time: Optional[str] = None, recurring_end_date: Optional[str] = None,
                    priority: str = "medium") -> int:
        """
        Create a new task.
        
        Args:
            title: Task title (required)
            description: Task description (optional)
            user_id: ID of the user who owns the task
            is_shared: Whether the task is shared with other users
            due_date: Due date in YYYY-MM-DD format (optional)
            recurring_type: Type of recurrence ('daily', 'weekly', 'monthly', None)
            recurring_time: Time for recurring tasks in HH:MM format (optional)
            recurring_end_date: End date for recurring tasks in YYYY-MM-DD format (optional)
            priority: Task priority ('low', 'medium', 'high')
            
        Returns:
            ID of the created task
        """
        if not title or not title.strip():
            raise ValueError("Task title is required")
        
        if priority not in ['low', 'medium', 'high']:
            priority = 'medium'
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO tasks (title, description, status, user_id, is_shared, due_date, 
                             recurring_type, recurring_time, recurring_end_date, priority)
            VALUES (?, ?, 'incomplete', ?, ?, ?, ?, ?, ?, ?)
        """, (title.strip(), description.strip(), user_id, 1 if is_shared else 0,
              due_date, recurring_type, recurring_time, recurring_end_date, priority))
        
        task_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return task_id
    
    def get_all_tasks(self, status: Optional[str] = None, sort_by: str = "created_at", user_id: Optional[int] = None,
                     date_filter: Optional[str] = None, priority_filter: Optional[str] = None) -> List[Dict]:
        """
        Retrieve tasks for a specific user, including shared tasks.
        
        Args:
            status: Filter by status ('complete' or 'incomplete'), None for all
            sort_by: Field to sort by ('created_at', 'updated_at', 'title', 'status', 'due_date', 'priority')
            user_id: ID of the user (if None, returns all tasks - for admin use)
            date_filter: Filter by date in YYYY-MM-DD format (optional)
            priority_filter: Filter by priority ('low', 'medium', 'high', None)
            
        Returns:
            List of task dictionaries
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM tasks"
        params = []
        conditions = []
        
        # Filter by user: show user's own tasks and shared tasks
        if user_id is not None:
            conditions.append("(user_id = ? OR is_shared = 1)")
            params.append(user_id)
        
        # Filter by status
        if status:
            conditions.append("status = ?")
            params.append(status)
        
        # Filter by date
        if date_filter:
            conditions.append("(due_date = ? OR (recurring_type IS NOT NULL AND (recurring_end_date IS NULL OR recurring_end_date >= ?)))")
            params.append(date_filter)
            params.append(date_filter)
        
        # Filter by priority
        if priority_filter:
            conditions.append("priority = ?")
            params.append(priority_filter)
        
        # Add WHERE clause if we have conditions
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        # Validate sort_by to prevent SQL injection
        valid_sort_fields = ["created_at", "updated_at", "title", "status", "due_date", "priority"]
        if sort_by not in valid_sort_fields:
            sort_by = "due_date" if date_filter else "created_at"
        
        # Special sorting for priority
        if sort_by == "priority":
            query += " ORDER BY CASE priority WHEN 'high' THEN 1 WHEN 'medium' THEN 2 WHEN 'low' THEN 3 END, due_date ASC"
        else:
            query += f" ORDER BY {sort_by} {'ASC' if sort_by == 'due_date' else 'DESC'}"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        tasks = []
        for row in rows:
            task = dict(row)
            task['is_shared'] = bool(task.get('is_shared', 0))
            tasks.append(task)
        
        return tasks
    
    def get_task_by_id(self, task_id: int, user_id: Optional[int] = None) -> Optional[Dict]:
        """
        Retrieve a task by its ID.
        
        Args:
            task_id: Task ID
            user_id: ID of the user requesting the task (for ownership check)
            
        Returns:
            Task dictionary or None if not found or user doesn't have access
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        task = dict(row)
        task['is_shared'] = bool(task.get('is_shared', 0))
        
        # Check ownership if user_id is provided
        if user_id is not None:
            task_user_id = task.get('user_id')
            if task_user_id != user_id and not task['is_shared']:
                return None  # User doesn't own this task and it's not shared
        
        return task
    
    def update_task_status(self, task_id: int, status: str, user_id: Optional[int] = None) -> bool:
        """
        Update task status.
        
        Args:
            task_id: Task ID
            status: New status ('complete' or 'incomplete')
            user_id: ID of the user making the update (for ownership check)
            
        Returns:
            True if update successful, False otherwise
        """
        if status not in ['complete', 'incomplete']:
            raise ValueError("Status must be 'complete' or 'incomplete'")
        
        # Check ownership if user_id is provided
        if user_id is not None:
            task = self.get_task_by_id(task_id, user_id)
            if not task:
                return False
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE tasks 
            SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (status, task_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def update_task(self, task_id: int, title: str, description: str = "", user_id: Optional[int] = None,
                   due_date: Optional[str] = None, recurring_type: Optional[str] = None,
                   recurring_time: Optional[str] = None, recurring_end_date: Optional[str] = None,
                   priority: Optional[str] = None) -> bool:
        """
        Update task title and description.
        
        Args:
            task_id: Task ID
            title: New title
            description: New description
            user_id: ID of the user making the update (for ownership check)
            due_date: Due date in YYYY-MM-DD format (optional)
            recurring_type: Type of recurrence ('daily', 'weekly', 'monthly', None)
            recurring_time: Time for recurring tasks in HH:MM format (optional)
            recurring_end_date: End date for recurring tasks in YYYY-MM-DD format (optional)
            priority: Task priority ('low', 'medium', 'high')
            
        Returns:
            True if update successful, False otherwise
        """
        if not title or not title.strip():
            raise ValueError("Task title is required")
        
        # Check ownership if user_id is provided
        if user_id is not None:
            task = self.get_task_by_id(task_id, user_id)
            if not task:
                return False
        
        # Get current task to preserve fields not being updated
        current_task = self.get_task_by_id(task_id)
        if not current_task:
            return False
        
        # Use provided values or keep existing ones
        final_due_date = due_date if due_date is not None else current_task.get('due_date')
        final_recurring_type = recurring_type if recurring_type is not None else current_task.get('recurring_type')
        final_recurring_time = recurring_time if recurring_time is not None else current_task.get('recurring_time')
        final_recurring_end_date = recurring_end_date if recurring_end_date is not None else current_task.get('recurring_end_date')
        final_priority = priority if priority is not None else current_task.get('priority', 'medium')
        
        if final_priority not in ['low', 'medium', 'high']:
            final_priority = 'medium'
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE tasks 
            SET title = ?, description = ?, due_date = ?, recurring_type = ?, 
                recurring_time = ?, recurring_end_date = ?, priority = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (title.strip(), description.strip(), final_due_date, final_recurring_type,
              final_recurring_time, final_recurring_end_date, final_priority, task_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def delete_task(self, task_id: int, user_id: Optional[int] = None) -> bool:
        """
        Delete a task by ID.
        
        Args:
            task_id: Task ID
            user_id: ID of the user making the deletion (for ownership check)
            
        Returns:
            True if deletion successful, False otherwise
        """
        # Check ownership if user_id is provided
        if user_id is not None:
            task = self.get_task_by_id(task_id, user_id)
            if not task:
                return False
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def share_task(self, task_id: int, is_shared: bool = True, user_id: Optional[int] = None) -> bool:
        """
        Share or unshare a task.
        
        Args:
            task_id: Task ID
            is_shared: Whether to share (True) or unshare (False) the task
            user_id: ID of the user making the change (must be task owner)
            
        Returns:
            True if update successful, False otherwise
        """
        # Check ownership - only owner can share/unshare
        if user_id is not None:
            task = self.get_task_by_id(task_id)
            if not task or task.get('user_id') != user_id:
                return False
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE tasks 
            SET is_shared = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (1 if is_shared else 0, task_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def get_task_count(self, user_id: Optional[int] = None) -> Dict[str, int]:
        """
        Get count of tasks by status for a specific user.
        
        Args:
            user_id: ID of the user (if None, counts all tasks - for admin use)
            
        Returns:
            Dictionary with 'total', 'complete', and 'incomplete' counts
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if user_id is not None:
            # Count user's own tasks and shared tasks
            cursor.execute("""
                SELECT COUNT(*) as total 
                FROM tasks 
                WHERE user_id = ? OR is_shared = 1
            """, (user_id,))
            total = cursor.fetchone()['total']
            
            cursor.execute("""
                SELECT COUNT(*) as complete 
                FROM tasks 
                WHERE (user_id = ? OR is_shared = 1) AND status = 'complete'
            """, (user_id,))
            complete = cursor.fetchone()['complete']
        else:
            # Count all tasks (admin view)
            cursor.execute("SELECT COUNT(*) as total FROM tasks")
            total = cursor.fetchone()['total']
            
            cursor.execute("SELECT COUNT(*) as complete FROM tasks WHERE status = 'complete'")
            complete = cursor.fetchone()['complete']
        
        incomplete = total - complete
        
        conn.close()
        
        return {
            'total': total,
            'complete': complete,
            'incomplete': incomplete
        }
    
    def get_tasks_by_date_range(self, start_date: str, end_date: str, user_id: Optional[int] = None) -> List[Dict]:
        """
        Get tasks within a date range, including recurring tasks.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            user_id: ID of the user (if None, returns all tasks)
            
        Returns:
            List of task dictionaries with date information
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        conditions = []
        params = []
        
        # Filter by user
        if user_id is not None:
            conditions.append("(user_id = ? OR is_shared = 1)")
            params.append(user_id)
        
        # Filter by date range: tasks with due_date in range OR recurring tasks
        date_condition = """(
            (due_date IS NOT NULL AND due_date >= ? AND due_date <= ?) OR
            (recurring_type IS NOT NULL AND (recurring_end_date IS NULL OR recurring_end_date >= ?))
        )"""
        conditions.append(date_condition)
        params.extend([start_date, end_date, start_date])
        
        query = "SELECT * FROM tasks"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY due_date ASC, priority ASC, created_at ASC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        tasks = []
        for row in rows:
            task = dict(row)
            task['is_shared'] = bool(task.get('is_shared', 0))
            tasks.append(task)
        
        return tasks
    
    def get_tasks_for_date(self, date: str, user_id: Optional[int] = None) -> List[Dict]:
        """
        Get tasks for a specific date, including recurring tasks that occur on that date.
        
        Args:
            date: Date in YYYY-MM-DD format
            user_id: ID of the user (if None, returns all tasks)
            
        Returns:
            List of task dictionaries
        """
        return self.get_all_tasks(status=None, sort_by='due_date', user_id=user_id, date_filter=date)
    
    def get_tasks_for_today(self, user_id: Optional[int] = None) -> List[Dict]:
        """
        Get tasks for today.
        
        Args:
            user_id: ID of the user (if None, returns all tasks)
            
        Returns:
            List of task dictionaries
        """
        from datetime import date
        today = date.today().isoformat()
        return self.get_tasks_for_date(today, user_id)


class UserModel:
    """Handles all database operations for users."""
    
    def __init__(self, db_path: str = "database/tasks.db"):
        """
        Initialize the database connection.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self._ensure_database_directory()
        self._init_database()
    
    def _ensure_database_directory(self):
        """Ensure the database directory exists."""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
    
    def _get_connection(self):
        """Get a database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        return conn
    
    def _init_database(self):
        """Initialize the users table if it doesn't exist."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Create users table with extended profile fields
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                is_admin INTEGER NOT NULL DEFAULT 0,
                full_name TEXT,
                avatar_url TEXT,
                occupation TEXT,
                timezone TEXT,
                preferred_hours TEXT,
                location TEXT,
                theme_pref TEXT,
                birthday DATE,
                bio TEXT,
                interests TEXT,
                skills TEXT,
                strengths_weaknesses TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Ensure existing databases get new profile columns (safe ALTERs)
        profile_columns = {
            'full_name': 'TEXT',
            'avatar_url': 'TEXT',
            'occupation': 'TEXT',
            'timezone': 'TEXT',
            'preferred_hours': 'TEXT',
            'location': 'TEXT',
            'theme_pref': 'TEXT',
            'birthday': 'DATE',
            'bio': 'TEXT',
            'interests': 'TEXT',
            'skills': 'TEXT',
            'strengths_weaknesses': 'TEXT'
        }

        for col, coltype in profile_columns.items():
            try:
                cursor.execute(f"ALTER TABLE users ADD COLUMN {col} {coltype}")
            except sqlite3.OperationalError:
                # Column probably exists
                pass

        # Create goals table to store user goals (short-term, long-term, etc.)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                category TEXT NOT NULL DEFAULT 'short_term',
                custom_category TEXT,
                target_date DATE,
                is_completed INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        conn.commit()
        conn.close()

    # ---------- User profile methods ----------
    def update_user_profile(self, user_id: int, **fields) -> bool:
        """
        Update user profile fields.

        Accepts keyword args for profile columns (see _init_database). Returns True if updated.
        """
        allowed = ['full_name', 'avatar_url', 'occupation', 'timezone', 'preferred_hours',
                   'location', 'theme_pref', 'birthday', 'bio', 'interests', 'skills', 'strengths_weaknesses']
        updates = {k: v for k, v in fields.items() if k in allowed}
        if not updates:
            return False

        set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
        params = list(updates.values())
        params.append(user_id)

        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(f"UPDATE users SET {set_clause} WHERE id = ?", params)
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success

    # ---------- Goals methods ----------
    def create_goal(self, user_id: int, title: str, description: str = '', category: str = 'short_term', custom_category: str = None, target_date: Optional[str] = None) -> int:
        if not title or not title.strip():
            raise ValueError('Goal title is required')
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO goals (user_id, title, description, category, custom_category, target_date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, title.strip(), description.strip(), category, custom_category, target_date))
        goal_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return goal_id

    def get_goals(self, user_id: int) -> List[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM goals WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
        rows = cursor.fetchall()
        conn.close()
        goals = [dict(r) for r in rows]
        for g in goals:
            g['is_completed'] = bool(g.get('is_completed', 0))
        return goals

    def get_goal_by_id(self, goal_id: int, user_id: Optional[int] = None) -> Optional[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM goals WHERE id = ?", (goal_id,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        goal = dict(row)
        if user_id is not None and goal.get('user_id') != user_id:
            return None
        goal['is_completed'] = bool(goal.get('is_completed', 0))
        return goal

    def update_goal(self, goal_id: int, user_id: int, **fields) -> bool:
        allowed = ['title', 'description', 'category', 'custom_category', 'target_date', 'is_completed']
        updates = {k: v for k, v in fields.items() if k in allowed}
        if not updates:
            return False
        # Ensure ownership
        goal = self.get_goal_by_id(goal_id)
        if not goal or goal.get('user_id') != user_id:
            return False

        set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
        params = list(updates.values())
        params.append(goal_id)
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(f"UPDATE goals SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?", params)
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success

    def delete_goal(self, goal_id: int, user_id: int) -> bool:
        # Ensure ownership
        goal = self.get_goal_by_id(goal_id)
        if not goal or goal.get('user_id') != user_id:
            return False
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM goals WHERE id = ?", (goal_id,))
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
    
    def create_user(self, username: str, password: str, is_admin: bool = False) -> int:
        """
        Create a new user.
        
        Args:
            username: Username (must be unique)
            password: Plain text password (will be hashed)
            is_admin: Whether user is an admin
            
        Returns:
            ID of the created user
            
        Raises:
            ValueError: If username is empty or already exists
        """
        if not username or not username.strip():
            raise ValueError("Username is required")
        
        if not password or not password.strip():
            raise ValueError("Password is required")
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Check if username already exists
        cursor.execute("SELECT id FROM users WHERE username = ?", (username.strip(),))
        if cursor.fetchone():
            conn.close()
            raise ValueError("Username already exists")
        
        # Hash password
        password_hash = generate_password_hash(password)
        
        cursor.execute("""
            INSERT INTO users (username, password_hash, is_admin)
            VALUES (?, ?, ?)
        """, (username.strip(), password_hash, 1 if is_admin else 0))
        
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return user_id
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """
        Authenticate a user by username and password.
        
        Args:
            username: Username
            password: Plain text password
            
        Returns:
            User dictionary if authentication successful, None otherwise
        """
        if not username or not password:
            return None
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE username = ?", (username.strip(),))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        user = dict(row)
        
        # Check password
        if check_password_hash(user['password_hash'], password):
            # Remove password_hash from returned dict
            user.pop('password_hash', None)
            user['is_admin'] = bool(user['is_admin'])
            return user
        
        return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """
        Retrieve a user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User dictionary or None if not found
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, username, is_admin, created_at FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            user = dict(row)
            user['is_admin'] = bool(user['is_admin'])
            return user
        return None
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """
        Retrieve a user by username.
        
        Args:
            username: Username
            
        Returns:
            User dictionary or None if not found
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, username, is_admin, created_at FROM users WHERE username = ?", (username.strip(),))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            user = dict(row)
            user['is_admin'] = bool(user['is_admin'])
            return user
        return None
    
    def get_all_users(self) -> List[Dict]:
        """
        Retrieve all users.
        
        Returns:
            List of user dictionaries (without password hashes)
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, username, is_admin, created_at FROM users ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        
        users = []
        for row in rows:
            user = dict(row)
            user['is_admin'] = bool(user['is_admin'])
            users.append(user)
        
        return users
    
    def delete_user(self, user_id: int) -> bool:
        """
        Delete a user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            True if deletion successful, False otherwise
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success

