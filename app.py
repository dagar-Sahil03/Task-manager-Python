"""
Main Flask application for Task Tracker.
Initializes Flask app, database connection, and registers routes.
"""

from flask import Flask
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Flask application
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['DATABASE_PATH'] = os.getenv('DATABASE_PATH', 'database/tasks.db')

# Initialize database model
from models import TaskModel
task_model = TaskModel(db_path=app.config['DATABASE_PATH'])

# Register routes
from routes import register_routes
register_routes(app, task_model)


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return {'error': 'Not found'}, 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return {'error': 'Internal server error'}, 500


if __name__ == '__main__':
    # Development server
    app.run(debug=True, host='0.0.0.0', port=5000)

