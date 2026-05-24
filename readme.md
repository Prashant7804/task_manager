# Smart Task Management System

A full-stack task management web application built with Flask, PostgreSQL, WebSockets, and Pandas.

## Tech Stack

- **Backend:** Python, Flask, Flask-SQLAlchemy, Flask-Login, Flask-Bcrypt, Flask-SocketIO
- **Database:** PostgreSQL
- **Analytics:** Pandas, NumPy
- **Frontend:** HTML, CSS, Vanilla JavaScript
- **Real-time:** WebSockets via Socket.IO

## Features

- User registration and login with bcrypt password hashing
- Password reset via secure token
- Create, read, update, delete tasks
- Set task priority (low / medium / high) and status (pending / completed)
- One-click toggle to mark tasks done or undo
- Analytics dashboard — total, completed, pending, completion rate, tasks by priority
- Real-time live updates via WebSockets
- Responsive UI

## Project Structure
task_manager/
├── app/
│   ├── init.py       # App factory, extensions
│   ├── models.py         # User and Task DB models
│   ├── routes.py         # All routes and REST APIs
│   ├── sockets.py        # WebSocket events
│   ├── config.py         # Configuration
│   ├── templates/        # Jinja2 HTML templates
│   └── static/css/       # Stylesheet
├── run.py                # Entry point
├── schema.sql            # PostgreSQL schema
├── requirements.txt      # Python dependencies
└── .env                  # Environment variables (not committed)

## Setup Instructions

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd task_manager
```

### 2. Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up PostgreSQL
```bash
psql postgres
```
```sql
CREATE DATABASE task_manager;
CREATE USER task_user WITH PASSWORD 'task1234';
GRANT ALL PRIVILEGES ON DATABASE task_manager TO task_user;
GRANT ALL ON SCHEMA public TO task_user;
ALTER DATABASE task_manager OWNER TO task_user;
\q
```

### 5. Create `.env` file
DATABASE_URL=postgresql://task_user:task1234@localhost/task_manager
SECRET_KEY=supersecretkey123
### 6. Run the app
```bash
python run.py
```

Visit `http://127.0.0.1:5000`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tasks` | Get all tasks for logged-in user |
| POST | `/api/tasks` | Create a new task |
| PUT | `/api/tasks/<id>` | Update a task |
| DELETE | `/api/tasks/<id>` | Delete a task |
| GET | `/api/analytics` | Get analytics data |

## WebSocket Events

| Event | Direction | Description |
|-------|-----------|-------------|
| `connect` | Client → Server | Join user room |
| `tasks_updated` | Server → Client | Broadcast on task change |

## Demo

Register an account, add tasks with different priorities, mark them complete, and visit the Analytics page to see live stats.
