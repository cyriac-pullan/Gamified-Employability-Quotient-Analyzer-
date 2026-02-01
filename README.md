# 🎯 Gamified Employability Quotient Analyzer (GEQA)

**GEQA** is a comprehensive, web-based platform designed to evaluate and enhance an individual's employability through a unique blend of data-driven assessment and gamification. By transforming the traditional career preparation process into an engaging game, GEQA motivates users to improve their skills while providing actionable insights.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Flask](https://img.shields.io/badge/Framework-Flask-green)
![Status](https://img.shields.io/badge/Status-Active-success)

---

## ✨ Key Features

### 👤 User Experience
*   **Comprehensive Dashboard**: View real-time stats, recent activities, and active challenges at a glance.
*   **Skill Assessments**: Take targeted quizzes in three core areas:
    *   🧠 **Aptitude**: Logic and reasoning.
    *   💻 **Technical**: Coding and domain knowledge.
    *   🤝 **Soft Skills**: Communication and interpersonal traits.
*   **Resume Analysis**: Upload your resume (PDF/DOCX) for instant AI-driven feedback and analysis.
*   **Mock Interviews**: Simulator that poses common interview questions and scores your responses based on length and keyword relevance.
*   **Analytics**: Visualize your growth with dynamic charts tracking skill progression over time.

### 🎮 Gamification Elements
GEQA uses a sophisticated reward system to keep users engaged:
*   **XP & Leveling System**:
    *   **Beginner**: < 100 XP
    *   **Learning**: 100 - 499 XP
    *   **Almost Ready**: 500 - 999 XP
    *   **Job-Ready**: 1000+ XP
*   **Badges**: Earn unique badges for milestones like perfect scores, first uploads, and streaks.
*   **Leaderboard**: Compete with peers for the top spot based on Total XP.
*   **Challenges**: Complete daily and weekly quests for bonus points.

### 🛠️ Behind the Scenes
*   **Secure Authentication**: Robust user registration and login system.
*   **Dynamic Scoring**: The Employability Quotient (EQ) is constantly recalculated based on assessment performance, profile completeness, and engagement.
*   **Admin Panel**: (Planned) manage users and content.

---

## 🏗️ Technical Architecture

This project is built using the **Flask** microframework, ensuring a lightweight yet scalable backend.

### Tech Stack
*   **Backend**: Python, Flask, SQLAlchemy (ORM)
*   **Database**: SQLite (Development) / PostgreSQL (Production)
*   **Frontend**: HTML5, CSS3, JavaScript (Jinja2 Templates)
*   **Analysis**: Custom algorithms for resume parsing and text scoring

### Project Structure
```
Gamified-Employability-Quotient-Analyzer/
├── app.py              # Application factory
├── models.py           # Database models (User, Assessment, Badge, etc.)
├── routes.py           # Endpoint definitions and view logic
├── utils.py            # Helper functions (scoring, analysis)
├── requirements.txt    # Python dependencies
├── templates/          # HTML templates
└── static/             # CSS, JS, and images
```

---

## 🚀 Getting Started

Follow these steps to set up the project locally.

### Prerequisites
*   Python 3.9 or higher
*   Git

### Installation
1.  **Clone the repository**
    ```bash
    git clone https://github.com/cyriac-pullan/Gamified-Employability-Quotient-Analyzer-.git
    cd Gamified-Employability-Quotient-Analyzer-
    ```

2.  **Create a virtual environment**
    ```bash
    # Windows
    python -m venv venv
    venv\Scripts\activate

    # macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the application**
    ```bash
    python app.py
    ```

5.  **Access the App**
    Open your browser and navigate to `http://127.0.0.1:5000/`.

---

## 📈 Roadmap

*   [ ] Integration with OpenAI/Gemini for advanced resume feedback.
*   [ ] Real-time multiplayer challenges.
*   [ ] Mobile-responsive UI improvements.
*   [ ] Corporate dashboard for recruiters.

---

## 🤝 Contributing

Contributions are welcome!
1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

## 👤 Author

**Cyriac Paul Pullan**
*   GitHub: [@cyriac-pullan](https://github.com/cyriac-pullan)
