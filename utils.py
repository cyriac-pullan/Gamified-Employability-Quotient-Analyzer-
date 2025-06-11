import json
import os
from models import Badge, Challenge, UserBadge, Activity, Assessment, db
from datetime import datetime
import PyPDF2
import textstat
import re

def calculate_employability_score(user):
    """Calculate overall employability score based on various factors"""
    score = 0
    total_weight = 0
    
    # CGPA component (20% weight)
    if user.cgpa > 0:
        cgpa_score = min(user.cgpa / 4.0 * 100, 100)  # Assuming 4.0 scale
        score += cgpa_score * 0.2
        total_weight += 0.2
    
    # Assessment scores (40% weight)
    assessments = Assessment.query.filter_by(user_id=user.id).all()
    if assessments:
        assessment_scores = []
        for assessment in assessments:
            assessment_scores.append(assessment.get_percentage())
        
        avg_assessment_score = sum(assessment_scores) / len(assessment_scores)
        score += avg_assessment_score * 0.4
        total_weight += 0.4
    
    # Resume quality (20% weight)
    if hasattr(user, 'resumes') and user.resumes:
        latest_resume = user.resumes[-1]
        if latest_resume.analysis_data:
            analysis = json.loads(latest_resume.analysis_data)
            resume_score = analysis.get('overall_score', 50)
            score += resume_score * 0.2
            total_weight += 0.2
    
    # Experience/Activities (20% weight)
    activity_count = len(user.activities)
    activity_score = min(activity_count * 5, 100)  # 5 points per activity, max 100
    score += activity_score * 0.2
    total_weight += 0.2
    
    # Normalize the score
    if total_weight > 0:
        final_score = score / total_weight
    else:
        final_score = 0
    
    return round(final_score, 1)

def analyze_resume(file_path):
    """Analyze uploaded resume and return insights"""
    analysis = {
        'word_count': 0,
        'readability_score': 0,
        'sections_found': [],
        'skills_mentioned': [],
        'overall_score': 0,
        'suggestions': []
    }
    
    try:
        # Extract text from PDF
        text = ""
        if file_path.lower().endswith('.pdf'):
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text()
        else:
            # For DOC/DOCX files, we'll just return basic analysis
            text = "Sample resume text for analysis"
        
        # Basic analysis
        analysis['word_count'] = len(text.split())
        
        # Check for common resume sections
        sections = ['experience', 'education', 'skills', 'projects', 'certifications']
        for section in sections:
            if section.lower() in text.lower():
                analysis['sections_found'].append(section.title())
        
        # Look for technical skills
        skills = ['python', 'java', 'javascript', 'sql', 'html', 'css', 'react', 'angular', 'node.js']
        for skill in skills:
            if skill.lower() in text.lower():
                analysis['skills_mentioned'].append(skill)
        
        # Calculate overall score
        score = 50  # Base score
        
        if analysis['word_count'] >= 200:
            score += 10
        if analysis['word_count'] >= 400:
            score += 10
        
        score += len(analysis['sections_found']) * 5
        score += len(analysis['skills_mentioned']) * 3
        
        analysis['overall_score'] = min(score, 100)
        
        # Generate suggestions
        if analysis['word_count'] < 200:
            analysis['suggestions'].append("Consider adding more details to reach 200+ words")
        if 'Experience' not in analysis['sections_found']:
            analysis['suggestions'].append("Add an Experience or Work History section")
        if len(analysis['skills_mentioned']) < 3:
            analysis['suggestions'].append("Include more technical skills relevant to your field")
        
    except Exception as e:
        print(f"Error analyzing resume: {e}")
        analysis['suggestions'].append("Unable to fully analyze resume file")
    
    return analysis

def get_assessment_questions(assessment_type):
    """Return questions for different assessment types"""
    questions = {
        'aptitude': [
            {
                'id': 1,
                'question': 'If 3x + 7 = 22, what is the value of x?',
                'options': ['3', '5', '7', '9'],
                'correct': '5'
            },
            {
                'id': 2,
                'question': 'What comes next in the sequence: 2, 6, 12, 20, 30, ?',
                'options': ['40', '42', '44', '46'],
                'correct': '42'
            },
            {
                'id': 3,
                'question': 'A train travels 180 km in 3 hours. What is its average speed?',
                'options': ['50 km/h', '60 km/h', '65 km/h', '70 km/h'],
                'correct': '60 km/h'
            },
            {
                'id': 4,
                'question': 'Which number is the odd one out: 8, 27, 64, 125, 216?',
                'options': ['8', '27', '64', '125'],
                'correct': '8'
            },
            {
                'id': 5,
                'question': 'If COMPUTER is coded as RFUVQNFS, how is MONITOR coded?',
                'options': ['MNITQOP', 'NLMJUPM', 'NPOQMJI', 'NQOJUQM'],
                'correct': 'NQOJUQM'
            }
        ],
        'technical': [
            {
                'id': 1,
                'question': 'Which of the following is NOT a programming language?',
                'options': ['Python', 'Java', 'HTML', 'C++'],
                'correct': 'HTML'
            },
            {
                'id': 2,
                'question': 'What does SQL stand for?',
                'options': ['Structured Query Language', 'Simple Query Language', 'Standard Query Language', 'System Query Language'],
                'correct': 'Structured Query Language'
            },
            {
                'id': 3,
                'question': 'Which data structure follows LIFO (Last In First Out) principle?',
                'options': ['Queue', 'Stack', 'Array', 'Linked List'],
                'correct': 'Stack'
            },
            {
                'id': 4,
                'question': 'What is the time complexity of binary search?',
                'options': ['O(n)', 'O(log n)', 'O(n²)', 'O(1)'],
                'correct': 'O(log n)'
            },
            {
                'id': 5,
                'question': 'Which HTTP method is used to update a resource?',
                'options': ['GET', 'POST', 'PUT', 'DELETE'],
                'correct': 'PUT'
            }
        ],
        'soft_skills': [
            {
                'id': 1,
                'question': 'When working in a team, what is the most important factor for success?',
                'options': ['Individual brilliance', 'Clear communication', 'Competition among members', 'Working independently'],
                'correct': 'Clear communication'
            },
            {
                'id': 2,
                'question': 'How should you handle constructive criticism?',
                'options': ['Ignore it', 'Get defensive', 'Listen and learn from it', 'Argue back'],
                'correct': 'Listen and learn from it'
            },
            {
                'id': 3,
                'question': 'What is the best way to manage your time effectively?',
                'options': ['Multitask everything', 'Prioritize tasks', 'Work on easy tasks first', 'Avoid planning'],
                'correct': 'Prioritize tasks'
            },
            {
                'id': 4,
                'question': 'In a professional setting, how should you communicate bad news?',
                'options': ['Via email only', 'Be direct and honest', 'Avoid mentioning it', 'Blame others'],
                'correct': 'Be direct and honest'
            },
            {
                'id': 5,
                'question': 'What demonstrates good leadership skills?',
                'options': ['Making all decisions alone', 'Empowering team members', 'Avoiding responsibility', 'Taking all credit'],
                'correct': 'Empowering team members'
            }
        ]
    }
    
    return questions.get(assessment_type, [])

def grade_assessment(assessment_type, answers):
    """Grade the assessment and return score, max_score, and feedback"""
    questions = get_assessment_questions(assessment_type)
    correct_answers = 0
    total_questions = len(questions)
    feedback = []
    
    for question in questions:
        question_id = str(question['id'])
        if question_id in answers:
            if answers[question_id] == question['correct']:
                correct_answers += 1
            else:
                feedback.append(f"Question {question_id}: Correct answer is {question['correct']}")
    
    return correct_answers, total_questions, feedback

def get_mock_interview_questions():
    """Return mock interview questions"""
    return [
        "Tell me about yourself and your background.",
        "Why are you interested in this field/position?",
        "What are your greatest strengths?",
        "Describe a challenging situation you faced and how you handled it.",
        "Where do you see yourself in 5 years?",
        "Why should we hire you?",
        "What questions do you have for us?"
    ]

def award_badges(user, activity_type, score=None):
    """Award badges based on user activities and achievements"""
    badges_to_award = []
    
    # Assessment-based badges
    if activity_type == 'aptitude' and score and score >= 80:
        badges_to_award.append('Aptitude Pro')
    elif activity_type == 'technical' and score and score >= 80:
        badges_to_award.append('Tech Wizard')
    elif activity_type == 'soft_skills' and score and score >= 80:
        badges_to_award.append('Soft Skills Hero')
    elif activity_type == 'resume':
        badges_to_award.append('Resume Ready')
    
    # XP-based badges
    if user.total_xp >= 100 and user.total_xp < 200:
        badges_to_award.append('Rising Star')
    elif user.total_xp >= 500:
        badges_to_award.append('High Achiever')
    
    # Award badges that user doesn't already have
    for badge_name in badges_to_award:
        badge = Badge.query.filter_by(name=badge_name).first()
        if badge:
            existing_user_badge = UserBadge.query.filter_by(
                user_id=user.id, 
                badge_id=badge.id
            ).first()
            
            if not existing_user_badge:
                user_badge = UserBadge(user_id=user.id, badge_id=badge.id)
                db.session.add(user_badge)
                
                # Award XP for earning badge
                user.add_xp(badge.xp_reward)
                
                # Create activity
                activity = Activity(
                    user_id=user.id,
                    activity_type='badge_earned',
                    description=f'Earned "{badge.name}" badge!',
                    xp_earned=badge.xp_reward
                )
                db.session.add(activity)

def create_default_badges():
    """Create default badges for the system"""
    default_badges = [
        {
            'name': 'Welcome Aboard',
            'description': 'Successfully registered and joined the platform',
            'icon': 'fas fa-star',
            'color': 'gold',
            'xp_reward': 25
        },
        {
            'name': 'Aptitude Pro',
            'description': 'Scored 80% or higher on an aptitude test',
            'icon': 'fas fa-brain',
            'color': 'purple',
            'xp_reward': 50
        },
        {
            'name': 'Tech Wizard',
            'description': 'Excelled in technical assessments',
            'icon': 'fas fa-code',
            'color': 'blue',
            'xp_reward': 50
        },
        {
            'name': 'Soft Skills Hero',
            'description': 'Demonstrated excellent soft skills',
            'icon': 'fas fa-handshake',
            'color': 'green',
            'xp_reward': 50
        },
        {
            'name': 'Resume Ready',
            'description': 'Uploaded and optimized resume',
            'icon': 'fas fa-file-alt',
            'color': 'orange',
            'xp_reward': 30
        },
        {
            'name': 'Rising Star',
            'description': 'Earned 100+ XP points',
            'icon': 'fas fa-rocket',
            'color': 'red',
            'xp_reward': 25
        },
        {
            'name': 'High Achiever',
            'description': 'Earned 500+ XP points',
            'icon': 'fas fa-trophy',
            'color': 'gold',
            'xp_reward': 100
        }
    ]
    
    for badge_data in default_badges:
        badge = Badge(**badge_data)
        db.session.add(badge)
    
    db.session.commit()

def create_default_challenges():
    """Create default challenges for users"""
    default_challenges = [
        {
            'title': 'Assessment Champion',
            'description': 'Complete any assessment today',
            'challenge_type': 'daily',
            'target_value': 1,
            'xp_reward': 25,
            'points_reward': 15
        },
        {
            'title': 'Profile Perfectionist',
            'description': 'Update your profile information',
            'challenge_type': 'daily',
            'target_value': 1,
            'xp_reward': 15,
            'points_reward': 10
        },
        {
            'title': 'Weekly Warrior',
            'description': 'Complete 3 assessments this week',
            'challenge_type': 'weekly',
            'target_value': 3,
            'xp_reward': 75,
            'points_reward': 50
        },
        {
            'title': 'Resume Master',
            'description': 'Upload your resume this week',
            'challenge_type': 'weekly',
            'target_value': 1,
            'xp_reward': 40,
            'points_reward': 25
        }
    ]
    
    for challenge_data in default_challenges:
        challenge = Challenge(**challenge_data)
        db.session.add(challenge)
    
    db.session.commit()
