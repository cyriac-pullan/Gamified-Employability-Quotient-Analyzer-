from flask import render_template, request, redirect, url_for, session, flash, jsonify, current_app
from app import app, db
from models import User, Assessment, Badge, UserBadge, Activity, Resume, Challenge, UserChallenge, MockInterview
from utils import calculate_employability_score, analyze_resume, create_default_badges, create_default_challenges, get_assessment_questions, grade_assessment, award_badges, get_mock_interview_questions
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        full_name = request.form['full_name']
        cgpa = float(request.form.get('cgpa', 0.0))
        year_of_study = request.form['year_of_study']
        major = request.form['major']
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('register.html')
        
        # Create new user
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            cgpa=cgpa,
            year_of_study=year_of_study,
            major=major
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Create welcome activity
        activity = Activity(
            user_id=user.id,
            activity_type='registration',
            description='Welcome to Employability Game!',
            points_earned=50,
            xp_earned=25
        )
        db.session.add(activity)
        
        user.total_points += 50
        user.add_xp(25)
        
        flash('Registration successful! Welcome to the game!', 'success')
        session['user_id'] = user.id
        return redirect(url_for('dashboard'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user:
        return redirect(url_for('logout'))
    
    # Get recent activities
    recent_activities = Activity.query.filter_by(user_id=user.id).order_by(Activity.created_at.desc()).limit(5).all()
    
    # Get user badges
    user_badges = UserBadge.query.filter_by(user_id=user.id).join(Badge).all()
    
    # Get active challenges
    active_challenges = UserChallenge.query.filter_by(
        user_id=user.id, 
        completed=False
    ).join(Challenge).limit(3).all()
    
    # Calculate employability score
    user.employability_score = calculate_employability_score(user)
    db.session.commit()
    
    return render_template('dashboard.html', 
                         user=user, 
                         activities=recent_activities,
                         badges=user_badges,
                         challenges=active_challenges)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user:
        return redirect(url_for('logout'))
    
    if request.method == 'POST':
        user.full_name = request.form['full_name']
        user.cgpa = float(request.form.get('cgpa', user.cgpa))
        user.year_of_study = request.form['year_of_study']
        user.major = request.form['major']
        user.show_on_leaderboard = 'show_on_leaderboard' in request.form
        
        db.session.commit()
        
        # Award points for profile update
        activity = Activity(
            user_id=user.id,
            activity_type='profile_update',
            description='Updated profile information',
            points_earned=10,
            xp_earned=5
        )
        db.session.add(activity)
        user.total_points += 10
        user.add_xp(5)
        
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
    
    return render_template('profile.html', user=user)

@app.route('/assessments')
def assessments():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    user_assessments = Assessment.query.filter_by(user_id=user.id).order_by(Assessment.completed_at.desc()).all()
    
    # Group assessments by type
    assessment_summary = {}
    for assessment in user_assessments:
        if assessment.assessment_type not in assessment_summary:
            assessment_summary[assessment.assessment_type] = []
        assessment_summary[assessment.assessment_type].append(assessment)
    
    return render_template('assessments.html', 
                         user=user, 
                         assessment_summary=assessment_summary)

@app.route('/assessment/<assessment_type>')
def take_assessment(assessment_type):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if assessment_type not in ['aptitude', 'technical', 'soft_skills']:
        flash('Invalid assessment type', 'error')
        return redirect(url_for('assessments'))
    
    questions = get_assessment_questions(assessment_type)
    return render_template('assessment_quiz.html', 
                         assessment_type=assessment_type,
                         questions=questions)

@app.route('/submit_assessment', methods=['POST'])
def submit_assessment():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    assessment_type = request.form['assessment_type']
    answers = {}
    
    # Collect answers
    for key, value in request.form.items():
        if key.startswith('question_'):
            question_id = key.replace('question_', '')
            answers[question_id] = value
    
    # Grade the assessment
    score, max_score, feedback = grade_assessment(assessment_type, answers)
    
    # Save assessment
    assessment = Assessment(
        user_id=user.id,
        assessment_type=assessment_type,
        score=score,
        max_score=max_score,
        questions_data=json.dumps(answers)
    )
    db.session.add(assessment)
    
    # Award points and XP
    percentage = (score / max_score) * 100
    base_points = 50
    base_xp = 30
    
    if percentage >= 90:
        points = base_points + 30
        xp = base_xp + 20
    elif percentage >= 80:
        points = base_points + 20
        xp = base_xp + 15
    elif percentage >= 70:
        points = base_points + 10
        xp = base_xp + 10
    else:
        points = base_points
        xp = base_xp
    
    activity = Activity(
        user_id=user.id,
        activity_type='assessment',
        description=f'Completed {assessment_type.replace("_", " ").title()} Assessment ({percentage:.1f}%)',
        points_earned=points,
        xp_earned=xp
    )
    db.session.add(activity)
    
    user.total_points += points
    user.add_xp(xp)
    
    # Check for badges
    award_badges(user, assessment_type, percentage)
    
    db.session.commit()
    
    flash(f'Assessment completed! Score: {percentage:.1f}% (+{points} points, +{xp} XP)', 'success')
    return redirect(url_for('assessments'))

@app.route('/resume', methods=['GET', 'POST'])
def resume():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    user_resume = Resume.query.filter_by(user_id=user.id).order_by(Resume.uploaded_at.desc()).first()
    
    if request.method == 'POST':
        if 'resume_file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['resume_file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file and file.filename.lower().endswith(('.pdf', '.doc', '.docx')):
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
            unique_filename = timestamp + filename
            
            # Ensure upload directory exists
            os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)
            
            # Analyze resume
            analysis = analyze_resume(file_path)
            
            # Save resume record
            resume_record = Resume(
                user_id=user.id,
                filename=unique_filename,
                original_filename=file.filename,
                file_path=file_path,
                analysis_data=json.dumps(analysis)
            )
            db.session.add(resume_record)
            
            # Award points for resume upload
            activity = Activity(
                user_id=user.id,
                activity_type='resume_upload',
                description='Uploaded and analyzed resume',
                points_earned=40,
                xp_earned=25
            )
            db.session.add(activity)
            
            user.total_points += 40
            user.add_xp(25)
            
            # Check for resume-related badges
            award_badges(user, 'resume', 100)
            
            db.session.commit()
            
            flash('Resume uploaded and analyzed successfully! (+40 points, +25 XP)', 'success')
            return redirect(url_for('resume'))
        else:
            flash('Please upload a PDF, DOC, or DOCX file', 'error')
    
    analysis_data = None
    if user_resume and user_resume.analysis_data:
        analysis_data = json.loads(user_resume.analysis_data)
    
    return render_template('resume.html', 
                         user=user, 
                         resume=user_resume,
                         analysis=analysis_data)

@app.route('/mock_interview', methods=['GET', 'POST'])
def mock_interview():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        responses = {}
        for key, value in request.form.items():
            if key.startswith('response_'):
                question_id = key.replace('response_', '')
                responses[question_id] = value
        
        # Simple scoring based on response length and keywords
        total_score = 0
        feedback_items = []
        
        for response in responses.values():
            score = min(len(response.split()) / 50 * 100, 100)  # Basic scoring
            total_score += score
            if len(response.split()) < 10:
                feedback_items.append("Try to provide more detailed responses")
        
        average_score = total_score / len(responses) if responses else 0
        
        # Save mock interview
        mock_interview_record = MockInterview(
            user_id=user.id,
            questions_data=json.dumps(responses),
            overall_score=average_score,
            feedback=json.dumps(feedback_items)
        )
        db.session.add(mock_interview_record)
        
        # Award points
        points = int(average_score / 2)
        xp = int(average_score / 3)
        
        activity = Activity(
            user_id=user.id,
            activity_type='mock_interview',
            description=f'Completed mock interview (Score: {average_score:.1f}%)',
            points_earned=points,
            xp_earned=xp
        )
        db.session.add(activity)
        
        user.total_points += points
        user.add_xp(xp)
        
        db.session.commit()
        
        flash(f'Mock interview completed! Score: {average_score:.1f}% (+{points} points, +{xp} XP)', 'success')
        return redirect(url_for('mock_interview'))
    
    questions = get_mock_interview_questions()
    previous_interviews = MockInterview.query.filter_by(user_id=user.id).order_by(MockInterview.completed_at.desc()).limit(3).all()
    
    return render_template('mock_interview.html', 
                         user=user, 
                         questions=questions,
                         previous_interviews=previous_interviews)

@app.route('/analytics')
def analytics():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    # Get assessment data for charts
    assessments = Assessment.query.filter_by(user_id=user.id).all()
    
    # Prepare data for charts
    skill_data = {}
    progress_data = []
    
    for assessment in assessments:
        assessment_type = assessment.assessment_type.replace('_', ' ').title()
        percentage = assessment.get_percentage()
        
        if assessment_type not in skill_data:
            skill_data[assessment_type] = []
        skill_data[assessment_type].append({
            'date': assessment.completed_at.strftime('%Y-%m-%d'),
            'score': percentage
        })
    
    # Get recent activities for timeline
    activities = Activity.query.filter_by(user_id=user.id).order_by(Activity.created_at.desc()).limit(10).all()
    
    return render_template('analytics.html', 
                         user=user,
                         skill_data=json.dumps(skill_data),
                         activities=activities)

@app.route('/leaderboard')
def leaderboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    current_user = User.query.get(session['user_id'])
    
    # Get top users (only those who opted to show on leaderboard)
    top_users = User.query.filter_by(show_on_leaderboard=True)\
                         .order_by(User.total_xp.desc())\
                         .limit(20).all()
    
    # Find current user's rank
    user_rank = None
    if current_user.show_on_leaderboard:
        higher_xp_count = User.query.filter(
            User.total_xp > current_user.total_xp,
            User.show_on_leaderboard == True
        ).count()
        user_rank = higher_xp_count + 1
    
    return render_template('leaderboard.html', 
                         current_user=current_user,
                         top_users=top_users,
                         user_rank=user_rank)

@app.route('/challenges')
def challenges():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    # Get user's challenges
    user_challenges = UserChallenge.query.filter_by(user_id=user.id)\
                                        .join(Challenge)\
                                        .order_by(UserChallenge.completed.asc(), UserChallenge.assigned_at.desc())\
                                        .all()
    
    return render_template('challenges.html', 
                         user=user,
                         user_challenges=user_challenges)

# Initialize default data on app startup
def initialize_default_data():
    with app.app_context():
        # Create default badges if they don't exist
        if Badge.query.count() == 0:
            create_default_badges()
        
        # Create default challenges if they don't exist
        if Challenge.query.count() == 0:
            create_default_challenges()

# Call initialization function
initialize_default_data()
