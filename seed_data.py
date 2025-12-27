"""
Database seeding script for Task Tracker.
Creates sample tasks for testing and demonstration.
"""

from models import TaskModel
import sys


def seed_database():
    """Seed the database with sample tasks."""
    print("Seeding database with sample tasks...")
    
    # Initialize database model
    task_model = TaskModel()
    
    # Sample tasks
    sample_tasks = [
        {
            'title': 'Complete Flask project assignment',
            'description': 'Finish the Task Tracker web application with all required features including CRUD operations, API endpoints, and deployment configuration.',
            'status': 'complete'
        },
        {
            'title': 'Write project documentation',
            'description': 'Create comprehensive README.md and DESIGN.md files with architecture diagrams and setup instructions.',
            'status': 'complete'
        },
        {
            'title': 'Test all API endpoints',
            'description': 'Verify that all RESTful API endpoints (GET, POST, PUT, DELETE) are working correctly with proper JSON responses.',
            'status': 'incomplete'
        },
        {
            'title': 'Deploy application to Linux server',
            'description': 'Set up Gunicorn WSGI server and deploy the application following the deployment documentation.',
            'status': 'incomplete'
        },
        {
            'title': 'Review code for PEP 8 compliance',
            'description': 'Ensure all Python code follows PEP 8 style guidelines and add proper comments where needed.',
            'status': 'incomplete'
        },
        {
            'title': 'Add task filtering and sorting',
            'description': 'Implement optional enhancement features for filtering tasks by status and sorting by different criteria.',
            'status': 'incomplete'
        },
        {
            'title': 'Create user authentication system',
            'description': 'Future enhancement: Add user registration and login functionality to support multiple users.',
            'status': 'incomplete'
        },
        {
            'title': 'Implement task categories',
            'description': 'Future enhancement: Allow users to organize tasks into categories or projects for better management.',
            'status': 'incomplete'
        }
    ]
    
    # Create tasks
    created_count = 0
    for task_data in sample_tasks:
        try:
            task_id = task_model.create_task(
                title=task_data['title'],
                description=task_data['description']
            )
            
            # Update status if not default
            if task_data['status'] == 'complete':
                task_model.update_task_status(task_id, 'complete')
            
            created_count += 1
            print(f"  ✓ Created task: {task_data['title']}")
            
        except Exception as e:
            print(f"  ✗ Error creating task '{task_data['title']}': {str(e)}")
    
    print(f"\nDatabase seeding completed! Created {created_count} sample tasks.")
    
    # Display statistics
    stats = task_model.get_task_count()
    print(f"\nDatabase Statistics:")
    print(f"  Total tasks: {stats['total']}")
    print(f"  Completed: {stats['complete']}")
    print(f"  Incomplete: {stats['incomplete']}")


if __name__ == '__main__':
    try:
        seed_database()
    except KeyboardInterrupt:
        print("\n\nSeeding interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError during seeding: {str(e)}")
        sys.exit(1)

