"""
Script to create an initial admin user for the Task Tracker application.
Run this script to bootstrap the first admin user.
"""

import os
import sys
from models import UserModel

def create_admin_user():
    """Create an admin user interactively."""
    print("=" * 50)
    print("Task Tracker - Admin User Creation")
    print("=" * 50)
    print()
    
    # Get database path from environment or use default
    db_path = os.getenv('DATABASE_PATH', 'database/tasks.db')
    user_model = UserModel(db_path=db_path)
    
    # Check if admin users already exist
    existing_users = user_model.get_all_users()
    admin_users = [u for u in existing_users if u.get('is_admin')]
    
    if admin_users:
        print(f"Warning: {len(admin_users)} admin user(s) already exist(s).")
        response = input("Do you want to create another admin user? (y/n): ").strip().lower()
        if response != 'y':
            print("Operation cancelled.")
            return
    
    # Get username
    while True:
        username = input("Enter username: ").strip()
        if username:
            # Check if username already exists
            existing_user = user_model.get_user_by_username(username)
            if existing_user:
                print(f"Error: Username '{username}' already exists. Please choose a different username.")
                continue
            break
        else:
            print("Username cannot be empty. Please try again.")
    
    # Get password
    while True:
        password = input("Enter password: ").strip()
        if len(password) < 4:
            print("Error: Password must be at least 4 characters long.")
            continue
        confirm_password = input("Confirm password: ").strip()
        if password == confirm_password:
            break
        else:
            print("Error: Passwords do not match. Please try again.")
    
    # Create admin user
    try:
        user_id = user_model.create_user(username, password, is_admin=True)
        print()
        print("=" * 50)
        print("✓ Admin user created successfully!")
        print(f"  Username: {username}")
        print(f"  User ID: {user_id}")
        print("=" * 50)
        print()
        print("You can now log in to the application using these credentials.")
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    try:
        create_admin_user()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(0)

