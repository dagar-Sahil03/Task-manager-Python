"""
Database models and CRUD operations for Task Tracker application.
Uses SQLite for data persistence.
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional


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
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT NOT NULL DEFAULT 'incomplete',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def create_task(self, title: str, description: str = "") -> int:
        """
        Create a new task.
        
        Args:
            title: Task title (required)
            description: Task description (optional)
            
        Returns:
            ID of the created task
        """
        if not title or not title.strip():
            raise ValueError("Task title is required")
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO tasks (title, description, status)
            VALUES (?, ?, 'incomplete')
        """, (title.strip(), description.strip()))
        
        task_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return task_id
    
    def get_all_tasks(self, status: Optional[str] = None, sort_by: str = "created_at") -> List[Dict]:
        """
        Retrieve all tasks, optionally filtered by status.
        
        Args:
            status: Filter by status ('complete' or 'incomplete'), None for all
            sort_by: Field to sort by ('created_at', 'updated_at', 'title')
            
        Returns:
            List of task dictionaries
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM tasks"
        params = []
        
        if status:
            query += " WHERE status = ?"
            params.append(status)
        
        # Validate sort_by to prevent SQL injection
        valid_sort_fields = ["created_at", "updated_at", "title", "status"]
        if sort_by not in valid_sort_fields:
            sort_by = "created_at"
        
        query += f" ORDER BY {sort_by} DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_task_by_id(self, task_id: int) -> Optional[Dict]:
        """
        Retrieve a task by its ID.
        
        Args:
            task_id: Task ID
            
        Returns:
            Task dictionary or None if not found
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def update_task_status(self, task_id: int, status: str) -> bool:
        """
        Update task status.
        
        Args:
            task_id: Task ID
            status: New status ('complete' or 'incomplete')
            
        Returns:
            True if update successful, False otherwise
        """
        if status not in ['complete', 'incomplete']:
            raise ValueError("Status must be 'complete' or 'incomplete'")
        
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
    
    def update_task(self, task_id: int, title: str, description: str = "") -> bool:
        """
        Update task title and description.
        
        Args:
            task_id: Task ID
            title: New title
            description: New description
            
        Returns:
            True if update successful, False otherwise
        """
        if not title or not title.strip():
            raise ValueError("Task title is required")
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE tasks 
            SET title = ?, description = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (title.strip(), description.strip(), task_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def delete_task(self, task_id: int) -> bool:
        """
        Delete a task by ID.
        
        Args:
            task_id: Task ID
            
        Returns:
            True if deletion successful, False otherwise
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def get_task_count(self) -> Dict[str, int]:
        """
        Get count of tasks by status.
        
        Returns:
            Dictionary with 'total', 'complete', and 'incomplete' counts
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
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

