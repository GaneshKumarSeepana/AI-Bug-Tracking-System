# AI-Powered Bug Tracking System

A modern bug tracking system with AI-powered bug prioritization and classification.

## Features

- **AI-Powered Analysis**: Automatically classifies and prioritizes bugs using machine learning
- **Role-Based Access Control**: Separate dashboards for Admins, Managers, and Developers
- **Modern UI**: Dark theme with glassmorphism effects and smooth animations
- **Real-time Analytics**: Charts and statistics for bug trends and team performance

## Tech Stack

### Backend
- Flask (Python web framework)
- MongoDB (Database)
- Scikit-learn (Machine learning)
- PyMongo (MongoDB driver)

### Frontend
- HTML5/CSS3
- Vanilla JavaScript
- Chart.js (Analytics visualization)
- Font Awesome (Icons)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/GaneshKumarSeepana/AI-Bug-Tracking-System.git
cd AI-Bug-Tracking-System
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r backend/requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory:
```
SECRET_KEY=your-secret-key-here
MONGO_URI=mongodb://localhost:27017/bug_tracker_db
```

5. Install and start MongoDB:
- Download MongoDB Community Server from https://www.mongodb.com/try/download/community
- Start MongoDB service

6. Run the application:
```bash
python backend/app.py
```

7. Access the application:
- Main app: http://127.0.0.1:5000
- Admin login: http://127.0.0.1:5000/admin/login

## Default Admin Credentials

For first-time setup, visit: http://127.0.0.1:5000/create-admin

This will create an admin user. **Change the default credentials in `backend/app.py` before deploying to production.**

## Project Structure

```
AI_Bug_Tracking_System/
├── backend/
│   ├── app.py              # Main Flask application
│   ├── config.py           # Configuration
│   └── requirements.txt    # Python dependencies
├── templates/              # HTML templates
├── static/                 # CSS, JS, and static assets
├── m1/                     # Machine learning models
└── .env                    # Environment variables (not in repo)
```

## Security Notes

- Never commit `.env` file to version control
- Change default admin credentials before production deployment
- Use strong SECRET_KEY in production
- Enable SSL/TLS for MongoDB connections in production

## License

MIT License

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
