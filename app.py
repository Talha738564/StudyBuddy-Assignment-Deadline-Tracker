import os
from flask import Flask, request, jsonify, send_file, render_template
from planner import Planner
from file_manager import FileManager
from models.assignment import HomeworkAssignment, ProjectAssignment, ExamPrep
from exceptions import (
    StudyBuddyError, AssignmentNotFound, SubjectNotFound, WrongDeadlineError,
    InvalidPriority, InvalidHour, InvalidProgress, InvalidType, TitleError
)

# Ensure required directories exist before file operations
os.makedirs('data', exist_ok=True)
os.makedirs('reports', exist_ok=True)

app = Flask(__name__)
planner = Planner()

# Load initial data into planner memory
loaded_assignments = FileManager.load_assignments()
for a in loaded_assignments:
    planner.add_assignment(a.subject, a)

def save_data():
    FileManager.save_assignments(planner.view_all_assignments())

def format_assignment(a):
    data = a.to_dict()
    urgency = a.calculate_urgency()
    
    # Handle Infinity for JSON compatibility
    if urgency == float('inf'):
        data['urgency'] = None
        data['is_overdue'] = True
    else:
        data['urgency'] = urgency
        data['is_overdue'] = False
        
    data['days_left'] = a.day_left()
    return data

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/assignments', methods=['GET'])
def get_assignments():
    assignments = planner.view_all_assignments()
    return jsonify([format_assignment(a) for a in assignments])

@app.route('/api/assignments', methods=['POST'])
def add_assignment():
    data = request.json
    try:
        a_type = data.get('type')
        title = data.get('title')
        subject = data.get('subject')
        deadline = data.get('deadline')
        priority_weight = int(data.get('priority_weight', 1))
        estimated_hours = int(data.get('estimated_hours', 1))
        progress = int(data.get('progress', 0))

        if a_type == 'homework':
            new_assignment = HomeworkAssignment(title, subject, deadline, priority_weight, estimated_hours, progress, data.get('submission_type', ''))
        elif a_type == 'project':
            milestones = data.get('milestones', '').split(',') if data.get('milestones') else []
            team = data.get('team_members', '').split(',') if data.get('team_members') else []
            new_assignment = ProjectAssignment(title, subject, deadline, priority_weight, estimated_hours, progress, milestones, team)
        elif a_type == 'exam':
            topics = data.get('important_topics', '').split(',') if data.get('important_topics') else []
            new_assignment = ExamPrep(title, subject, deadline, priority_weight, estimated_hours, progress, topics)
        else:
            return jsonify({"error": "Invalid assignment type"}), 400

        planner.add_assignment(subject, new_assignment)
        save_data()
        return jsonify({"message": "Assignment added successfully"}), 201

    except (TitleError, WrongDeadlineError, InvalidPriority, InvalidHour, InvalidProgress, SubjectNotFound, InvalidType) as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred: " + str(e)}), 400

@app.route('/api/assignments/<subject>/<title>', methods=['PUT'])
def update_assignment(subject, title):
    data = request.json
    try:
        planner.update_assignment(
            subject, title,
            deadline=data.get('deadline') or None,
            priority_weight=data.get('priority_weight') or None,
            estimated_hours=data.get('estimated_hours') or None,
            progress=data.get('progress') or None
        )
        save_data()
        return jsonify({"message": "Assignment updated successfully"})
    except (SubjectNotFound, AssignmentNotFound, InvalidProgress, InvalidHour, InvalidPriority, WrongDeadlineError) as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/assignments/<subject>/<title>', methods=['DELETE'])
def delete_assignment(subject, title):
    try:
        planner.remove_assignment(subject, title)
        save_data()
        return jsonify({"message": "Assignment deleted successfully"})
    except (SubjectNotFound, AssignmentNotFound) as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/focus', methods=['GET'])
def get_focus():
    assignments = planner.focus_list()
    return jsonify([format_assignment(a) for a in assignments])

@app.route('/api/reminders', methods=['GET'])
def get_reminders():
    days = int(request.args.get('days', 2))
    assignments = planner.get_reminder(days_left=days)
    return jsonify([format_assignment(a) for a in assignments])

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    stats = planner.get_statistics()
    return jsonify(stats)

@app.route('/api/export', methods=['GET'])
def export_report():
    planner.export_report()
    return send_file('reports/study_report.txt', as_attachment=True)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)