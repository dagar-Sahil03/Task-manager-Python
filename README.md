# Task Tracker: Web-Based Task Management System

A comprehensive web-based task management application built with Flask, featuring CRUD operations, RESTful API endpoints, and a responsive Bootstrap UI.

## 📋 Project Overview

Task Tracker is a full-featured web application that enables users to efficiently manage tasks, track progress, and maintain productivity. The application provides an intuitive interface for creating, reading, updating, and deleting tasks, with persistent data storage using SQLite.

### Key Features

- ✅ **Complete CRUD Operations**: Create, read, update, and delete tasks
- 📊 **Task Statistics**: View total, completed, and incomplete task counts
- 🔍 **Filtering & Sorting**: Filter tasks by status and sort by various criteria
- 🎨 **Responsive Design**: Mobile-friendly UI built with Bootstrap 5
- 🔌 **RESTful API**: Complete API endpoints for programmatic access
- 💾 **Data Persistence**: SQLite database for reliable data storage
- 🚀 **Production Ready**: Gunicorn WSGI server configuration included

## 🛠️ Technology Stack

### Backend
- **Flask 3.0.0**: Web framework for Python
- **SQLite3**: Lightweight relational database
- **Gunicorn**: Production WSGI HTTP server
- **python-dotenv**: Environment variable management

### Frontend
- **Bootstrap 5.3.0**: Responsive CSS framework
- **Bootstrap Icons**: Icon library
- **Jinja2**: Template engine
- **JavaScript (ES6)**: Client-side interactions

### Development Tools
- **Python 3.8+**: Programming language
- **Git**: Version control
- **Virtual Environment**: Dependency isolation

## 📁 System Architecture and Folder Structure

```
task-tracker/
├── app.py                 # Main Flask application entry point
├── models.py              # Database models and CRUD operations
├── routes.py              # Route handlers (web and API)
├── wsgi.py                # WSGI entry point for Gunicorn
├── gunicorn_config.py     # Gunicorn server configuration
├── seed_data.py           # Database seeding script
├── requirements.txt       # Python dependencies
├── .gitignore            # Git ignore patterns
├── .env                  # Environment variables (create from template)
├── README.md             # This file
├── DESIGN.md             # Architecture and design documentation
├── templates/            # Jinja2 HTML templates
│   ├── base.html        # Base template with navigation
│   ├── index.html       # Homepage (task list)
│   ├── add_task.html    # Add task form
│   └── edit_task.html   # Edit task form
├── static/              # Static files
│   ├── css/
│   │   └── style.css    # Custom CSS styles
│   └── js/
│       └── main.js      # JavaScript for interactions
├── database/            # Database files
│   └── tasks.db         # SQLite database (created automatically)
├── scripts/             # Deployment scripts
│   ├── setup.sh         # Linux setup script
│   └── deploy.sh        # Deployment script
└── tests/               # Test files (optional)
```

## 🚀 Installation and Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git (for version control)
- Linux environment (for deployment)

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd task-tracker
```

### Step 2: Set Up Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a `.env` file in the project root:

```env
# Flask Configuration
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
FLASK_DEBUG=True

# Database Configuration
DATABASE_PATH=database/tasks.db

# Gunicorn Configuration (optional)
GUNICORN_BIND=0.0.0.0:8000
GUNICORN_WORKERS=4
GUNICORN_LOG_LEVEL=info
```

Generate a secure secret key:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### Step 5: Initialize Database

The database will be created automatically on first run. To seed with sample data:

```bash
python3 seed_data.py
```

### Step 6: Run the Application

**Development Mode:**
```bash
python3 app.py
```

The application will be available at `http://localhost:5000`

**Production Mode (Linux):**
```bash
# Run setup script first
chmod +x scripts/setup.sh
./scripts/setup.sh

# Deploy with Gunicorn
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

The application will be available at `http://localhost:8000` (or configured port)

## 📖 Usage Guide

### Web Interface

1. **View All Tasks**: Navigate to the homepage to see all tasks with their status
2. **Add Task**: Click "Add New Task" button, fill in title and description, then submit
3. **Update Status**: Click "Mark Complete" or "Mark Incomplete" buttons on task cards
4. **Edit Task**: Click "Edit" button to modify task title and description
5. **Delete Task**: Click "Delete" button (confirmation required)
6. **Filter Tasks**: Use the filter dropdown to show only completed or incomplete tasks
7. **Sort Tasks**: Use the sort dropdown to organize tasks by date, title, or status

### RESTful API

The application provides RESTful API endpoints for programmatic access:

#### Get All Tasks
```bash
GET /api/tasks
GET /api/tasks?status=complete
GET /api/tasks?sort=created_at
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "title": "Task Title",
      "description": "Task Description",
      "status": "incomplete",
      "created_at": "2024-01-01 12:00:00",
      "updated_at": "2024-01-01 12:00:00"
    }
  ],
  "stats": {
    "total": 10,
    "complete": 5,
    "incomplete": 5
  }
}
```

#### Get Specific Task
```bash
GET /api/task/<id>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "title": "Task Title",
    "description": "Task Description",
    "status": "incomplete",
    "created_at": "2024-01-01 12:00:00",
    "updated_at": "2024-01-01 12:00:00"
  }
}
```

#### Create Task
```bash
POST /api/task
Content-Type: application/json

{
  "title": "New Task",
  "description": "Task description"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 2,
    "title": "New Task",
    "description": "Task description",
    "status": "incomplete",
    "created_at": "2024-01-01 12:00:00",
    "updated_at": "2024-01-01 12:00:00"
  },
  "message": "Task created successfully"
}
```

#### Update Task
```bash
PUT /api/task/<id>
Content-Type: application/json

{
  "title": "Updated Task",
  "description": "Updated description",
  "status": "complete"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "title": "Updated Task",
    "description": "Updated description",
    "status": "complete",
    "created_at": "2024-01-01 12:00:00",
    "updated_at": "2024-01-01 13:00:00"
  },
  "message": "Task updated successfully"
}
```

#### Delete Task
```bash
DELETE /api/task/<id>
```

**Response:**
```json
{
  "success": true,
  "message": "Task deleted successfully"
}
```

### Example API Usage with cURL

```bash
# Get all tasks
curl http://localhost:5000/api/tasks

# Get specific task
curl http://localhost:5000/api/task/1

# Create task
curl -X POST http://localhost:5000/api/task \
  -H "Content-Type: application/json" \
  -d '{"title": "New Task", "description": "Description"}'

# Update task
curl -X PUT http://localhost:5000/api/task/1 \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated", "status": "complete"}'

# Delete task
curl -X DELETE http://localhost:5000/api/task/1
```

## 🧪 Testing Procedures

### Manual Testing Checklist

- [ ] Create a new task with title and description
- [ ] Create a task with only title (description optional)
- [ ] View all tasks on homepage
- [ ] Filter tasks by status (complete/incomplete)
- [ ] Sort tasks by different criteria
- [ ] Update task status (complete ↔ incomplete)
- [ ] Edit task title and description
- [ ] Delete task (verify confirmation dialog)
- [ ] Test form validation (empty title, long text)
- [ ] Test API endpoints with cURL or Postman
- [ ] Verify responsive design on mobile devices
- [ ] Test error handling (invalid task ID, etc.)

### Database Testing

```bash
# Test database operations
python3 -c "from models import TaskModel; tm = TaskModel(); print(tm.get_task_count())"
```

### API Testing

Use the provided cURL examples or tools like Postman to test all API endpoints.

## 🐛 Known Issues and Limitations

1. **No User Authentication**: The application currently doesn't support multiple users. All tasks are shared.
2. **No Task Categories**: Tasks cannot be organized into categories or projects.
3. **No Due Dates**: Tasks don't have due date or reminder functionality.
4. **No File Attachments**: Tasks cannot have file attachments.
5. **Limited Search**: No full-text search capability for tasks.
6. **No Export Functionality**: Tasks cannot be exported to CSV or other formats.

## 🔮 Future Enhancement Roadmap

### Short-term Enhancements
- [ ] User authentication and authorization
- [ ] Task categories and tags
- [ ] Due dates and reminders
- [ ] Task priority levels
- [ ] Full-text search functionality

### Medium-term Enhancements
- [ ] Task comments and notes
- [ ] File attachments
- [ ] Task templates
- [ ] Recurring tasks
- [ ] Task dependencies
- [ ] Export/import functionality (CSV, JSON)

### Long-term Enhancements
- [ ] Multi-user collaboration
- [ ] Real-time updates (WebSocket)
- [ ] Mobile app (React Native)
- [ ] Calendar view
- [ ] Analytics and reporting
- [ ] Integration with external services (Google Calendar, etc.)

## 👥 Contributors and Acknowledgments

### Development
- Built as part of the Eduwise Solutions Mini Project Assignment
- Follows Flask best practices and PEP 8 coding standards

### Technologies and Resources
- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [Bootstrap Framework](https://getbootstrap.com/)
- [Bootstrap Icons](https://icons.getbootstrap.com/)
- [Jinja2 Template Designer](https://jinja.palletsprojects.com/)

## 📄 License

This project is developed for educational purposes as part of the Eduwise Solutions assignment.

## 📞 Support

For issues, questions, or contributions, please refer to the project repository or contact the development team.

---

**Note**: This application is designed to run on a fresh Linux installation following the provided documentation. Ensure all dependencies are installed and environment variables are properly configured before deployment.

