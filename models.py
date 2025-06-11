from app import db
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import json

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(100))
    cgpa = db.Column(db.Float, default=0.0)
    year_of_study = db.Column(db.String(20))
    major = db.Column(db.String(100))
    
    # Gamification fields
    total_xp = db.Column(db.Integer, default=0)
    level = db.Column(db.String(20), default='Beginner')
    total_points = db.Column(db.Integer, default=0)
    employability_score = db.Column(db.Float, default=0.0)
    
    # Profile settings
    show_on_leaderboard = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    assessments = db.relationship('Assessment', backref='user', lazy=True, cascade='all, delete-orphan')
    badges = db.relationship('UserBadge', backref='user', lazy=True, cascade='all, delete-orphan')
    activities = db.relationship('Activity', backref='user', lazy=True, cascade='all, delete-orphan')
    challenges = db.relationship('UserChallenge', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def add_xp(self, xp_points):
        self.total_xp += xp_points
        self.update_level()
        db.session.commit()
    
    def update_level(self):
        if self.total_xp < 100:
            self.level = 'Beginner'
        elif self.total_xp < 500:
            self.level = 'Learning'
        elif self.total_xp < 1000:
            self.level = 'Almost Ready'
        else:
            self.level = 'Job-Ready'
    
    def get_level_progress(self):
        level_thresholds = {
            'Beginner': 100,
            'Learning': 500,
            'Almost Ready': 1000,
            'Job-Ready': float('inf')
        }
        
        current_threshold = level_thresholds.get(self.level, 100)
        if current_threshold == float('inf'):
            return 100
        
        if self.level == 'Beginner':
            return int((self.total_xp / current_threshold) * 100)
        elif self.level == 'Learning':
            return int(((self.total_xp - 100) / (current_threshold - 100)) * 100)
        elif self.level == 'Almost Ready':
            return int(((self.total_xp - 500) / (current_threshold - 500)) * 100)
        
        return 100

class Assessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assessment_type = db.Column(db.String(50), nullable=False)  # aptitude, technical, soft_skills
    score = db.Column(db.Float, nullable=False)
    max_score = db.Column(db.Float, nullable=False)
    questions_data = db.Column(db.Text)  # JSON string of questions and answers
    time_taken = db.Column(db.Integer)  # in seconds
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_percentage(self):
        return round((self.score / self.max_score) * 100, 1)

class Badge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    icon = db.Column(db.String(50), default='fas fa-award')
    color = db.Column(db.String(20), default='gold')
    criteria = db.Column(db.Text)  # JSON string describing criteria
    xp_reward = db.Column(db.Integer, default=50)

class UserBadge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    badge_id = db.Column(db.Integer, db.ForeignKey('badge.id'), nullable=False)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    badge = db.relationship('Badge', backref='user_badges')

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    points_earned = db.Column(db.Integer, default=0)
    xp_earned = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    analysis_data = db.Column(db.Text)  # JSON string of analysis results
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='resumes')

class Challenge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    challenge_type = db.Column(db.String(20), nullable=False)  # daily, weekly
    target_value = db.Column(db.Integer, default=1)
    xp_reward = db.Column(db.Integer, default=25)
    points_reward = db.Column(db.Integer, default=10)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class UserChallenge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenge.id'), nullable=False)
    progress = db.Column(db.Integer, default=0)
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    challenge = db.relationship('Challenge', backref='user_challenges')

class MockInterview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    questions_data = db.Column(db.Text)  # JSON string of questions and responses
    overall_score = db.Column(db.Float, default=0.0)
    feedback = db.Column(db.Text)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='mock_interviews')
