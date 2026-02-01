🎯 Gamified Employability Quotient Analyzer

The Gamified Employability Quotient Analyzer (GEQA) is a web-based application that evaluates an individual’s employability using a data-driven scoring system combined with gamification.

The system supports both User and Admin roles, enabling structured assessment, monitoring, and improvement of employability metrics in an engaging way.

🚀 Key Features
👤 User Features

🧠 Employability Quotient (EQ) calculation

🎮 Gamified assessment experience

📊 Skill & attribute evaluation

📈 Visual feedback and improvement suggestions

🌐 Simple and interactive web interface

🛠️ Admin Features

🔐 Admin login & access control

👥 View and manage user records

📊 Monitor employability scores and trends

🧩 Control assessment parameters & logic

📁 Manage uploaded data and inputs

📈 Analyze overall employability insights

🛠️ Tech Stack

Backend: Python (Flask)

Frontend: HTML, CSS, JavaScript

Data Processing: Python logic / ML-ready structure

Deployment: Render / Heroku

Version Control: Git & GitHub

📂 Project Structure
Gamified-Employability-Quotient-Analyzer/
├── .github/                # GitHub workflows (if any)
├── instance/               # App instance / database files
├── static/                 # CSS, JS, images
├── templates/              # HTML templates (user & admin pages)
├── uploads/                # Uploaded files / user inputs
├── app.py                  # Main Flask application
├── main.py                 # Optional runner
├── models.py               # Employability scoring & logic
├── routes.py               # User & admin routes
├── utils.py                # Helper / utility functions
├── requirements.txt        # Python dependencies
├── Procfile                # Deployment config
├── render.yaml             # Render deployment config
└── README.md               # Project documentation

🧠 How It Works
User Flow

User accesses the application.

User submits details related to skills, education, and employability factors.

Backend processes data using logic in models.py.

An Employability Quotient (EQ) score is calculated.

Results are displayed with gamified feedback.

Admin Flow

Admin logs in through the admin interface.

Admin views user data and employability scores.

Admin monitors trends and performance analytics.

Admin manages assessment logic and system data.

⚙️ Installation & Setup
Prerequisites

Python 3.9+

pip package manager

Step 1: Clone the Repository
git clone https://github.com/cyriac-pullan/Gamified-Employability-Quotient-Analyzer-.git
cd Gamified-Employability-Quotient-Analyzer-

Step 2: Create Virtual Environment
python -m venv venv


Activate it:

Windows

venv\Scripts\activate


macOS / Linux

source venv/bin/activate

Step 3: Install Dependencies
pip install -r requirements.txt

▶️ Running the Application
python app.py


The application will run at:

http://127.0.0.1:5000/


User interface → /

Admin interface → /admin (if configured in routes)

☁️ Deployment

The project supports cloud deployment:

Procfile → Heroku

render.yaml → Render

Render Deployment

Push the repository to GitHub

Connect GitHub repo to Render

Select Python environment

Deploy 🚀

🎯 Use Cases

Students assessing employability readiness

Colleges tracking student skill development

Placement & training departments

Hackathons and academic evaluations

Skill development & career platforms

🔐 Roles Summary
Role	Capabilities
User	Take assessments, view EQ score, get feedback
Admin	Manage users, analyze scores, monitor trends
🤝 Contributing

Contributions are welcome!

Fork the repository

Create a new branch

Commit your changes

Open a Pull Request

📄 License

No license specified currently.
You may add MIT / Apache 2.0 if open-source usage is intended.

👤 Author

Cyriac Paul Pullan
B.Tech – Artificial Intelligence & Data Science
GitHub: https://github.com/cyriac-pullan

⭐ Support

If you like this project, give it a ⭐ on GitHub!
