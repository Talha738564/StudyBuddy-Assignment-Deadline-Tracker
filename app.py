import os

from flask import Flask, flash, jsonify, redirect, render_template, request, send_file, url_for
from flask_login import LoginManager, UserMixin, current_user, login_required, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from werkzeug.security import check_password_hash, generate_password_hash

from exceptions import (
    AssignmentNotFound, InvalidHour, InvalidPriority, InvalidProgress, InvalidType,
    SubjectNotFound, TitleError, WrongDeadlineError,
)
from file_manager import FileManager
from models.assignment import ExamPrep, HomeworkAssignment, ProjectAssignment
from planner import Planner

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "studybuddy-dev-key-change-me")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///studybuddy.db").replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


with app.app_context():
    db.create_all()


def user_data_path():
    return os.path.join(DATA_DIR, "users", str(current_user.id), "assignments.json")


def user_report_path():
    return os.path.join(REPORTS_DIR, "users", str(current_user.id), "study_report.txt")


def get_planner():
    planner = Planner()
    for assignment in FileManager.load_assignments(filepath=user_data_path()):
        planner.add_assignment(assignment.subject, assignment)
    return planner


def save_data(planner):
    FileManager.save_assignments(planner.view_all_assignments(), filepath=user_data_path())


def format_assignment(assignment):
    data = assignment.to_dict()
    urgency = assignment.calculate_urgency()
    data["urgency"] = None if urgency == float("inf") else urgency
    data["is_overdue"] = urgency == float("inf")
    data["days_left"] = assignment.day_left()
    return data


@app.route("/")
@login_required
def index():
    return render_template("index.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    values = {"username": "", "email": ""}
    errors = {}
    if request.method == "POST":
        values = {key: request.form.get(key, "").strip() for key in values}
        password = request.form.get("password", "")
        confirmation = request.form.get("password_confirmation", "")
        if not values["username"]:
            errors["username"] = "Username is required."
        if not values["email"] or "@" not in values["email"]:
            errors["email"] = "Enter a valid email address."
        if User.query.filter(or_(User.username == values["username"], User.email == values["email"])).first():
            if User.query.filter_by(username=values["username"]).first():
                errors["username"] = "That username is already taken."
            if User.query.filter_by(email=values["email"]).first():
                errors["email"] = "That email is already registered."
        if len(password) < 8:
            errors["password"] = "Password must be at least 8 characters."
        if password != confirmation:
            errors["password_confirmation"] = "Passwords do not match."
        if not errors:
            user = User(username=values["username"], email=values["email"], password_hash=generate_password_hash(password))
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for("index"))
    return render_template("signup.html", values=values, errors=errors)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    username = ""
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        user = User.query.filter_by(username=username).first()
        if user is None or not check_password_hash(user.password_hash, request.form.get("password", "")):
            error = "Invalid username or password"
            flash(error, "error")
        else:
            login_user(user)
            return redirect(url_for("index"))
    return render_template("login.html", username=username, error=error)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/api/assignments", methods=["GET"])
@login_required
def get_assignments():
    return jsonify([format_assignment(a) for a in get_planner().view_all_assignments()])


@app.route("/api/assignments", methods=["POST"])
@login_required
def add_assignment():
    data = request.json or {}
    planner = get_planner()
    try:
        a_type = data.get("type")
        title, subject, deadline = data.get("title"), data.get("subject"), data.get("deadline")
        priority_weight = int(data.get("priority_weight", 1))
        estimated_hours = int(data.get("estimated_hours", 1))
        progress = int(data.get("progress", 0))
        if a_type == "homework":
            new_assignment = HomeworkAssignment(title, subject, deadline, priority_weight, estimated_hours, progress, data.get("submission_type", ""))
        elif a_type == "project":
            milestones = data.get("milestones", "").split(",") if data.get("milestones") else []
            team = data.get("team_members", "").split(",") if data.get("team_members") else []
            new_assignment = ProjectAssignment(title, subject, deadline, priority_weight, estimated_hours, progress, milestones, team)
        elif a_type == "exam":
            topics = data.get("important_topics", "").split(",") if data.get("important_topics") else []
            new_assignment = ExamPrep(title, subject, deadline, priority_weight, estimated_hours, progress, topics)
        else:
            return jsonify({"error": "Invalid assignment type"}), 400
        planner.add_assignment(subject, new_assignment)
        save_data(planner)
        return jsonify({"message": "Assignment added successfully"}), 201
    except (TitleError, WrongDeadlineError, InvalidPriority, InvalidHour, InvalidProgress, SubjectNotFound, InvalidType) as error:
        return jsonify({"error": str(error)}), 400
    except Exception as error:
        return jsonify({"error": "An unexpected error occurred: " + str(error)}), 400


@app.route("/api/assignments/<subject>/<title>", methods=["PUT"])
@login_required
def update_assignment(subject, title):
    planner = get_planner()
    data = request.json or {}
    try:
        planner.update_assignment(subject, title, deadline=data.get("deadline") or None, priority_weight=data.get("priority_weight") or None, estimated_hours=data.get("estimated_hours") or None, progress=data.get("progress") if data.get("progress") is not None else None)
        save_data(planner)
        return jsonify({"message": "Assignment updated successfully"})
    except (SubjectNotFound, AssignmentNotFound, InvalidProgress, InvalidHour, InvalidPriority, WrongDeadlineError) as error:
        return jsonify({"error": str(error)}), 400


@app.route("/api/assignments/<subject>/<title>", methods=["DELETE"])
@login_required
def delete_assignment(subject, title):
    planner = get_planner()
    try:
        planner.remove_assignment(subject, title)
        save_data(planner)
        return jsonify({"message": "Assignment deleted successfully"})
    except (SubjectNotFound, AssignmentNotFound) as error:
        return jsonify({"error": str(error)}), 400


@app.route("/api/focus")
@login_required
def get_focus():
    return jsonify([format_assignment(a) for a in get_planner().focus_list()])


@app.route("/api/reminders")
@login_required
def get_reminders():
    days = int(request.args.get("days", 2))
    return jsonify([format_assignment(a) for a in get_planner().get_reminder(days_left=days)])


@app.route("/api/statistics")
@login_required
def get_statistics():
    return jsonify(get_planner().get_statistics())


@app.route("/api/export")
@login_required
def export_report():
    report_path = user_report_path()
    planner = get_planner()
    planner.export_report(filepath=report_path)
    return send_file(report_path, as_attachment=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
