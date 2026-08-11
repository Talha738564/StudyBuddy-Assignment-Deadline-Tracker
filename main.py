from planner import Planner
from exceptions import (
    InvalidPriority,
    WrongDeadlineError,
    InvalidHour,
    InvalidProgress,
    InvalidType,
    TitleError,
    SubjectNotFound,
    AssignmentNotFound
)
from models.assignment import HomeworkAssignment, ProjectAssignment, ExamPrep



def print_menu():
    print("""
    1. Add Assignment
    2. View All Assignments
    3. Update Assignment
    4. Remove Assignment
    5. Today's Focus List
    6. Reminders (due soon)
    7. Statistics
    8. Export Report
    9. Exit
    """)
def handle_add(planner):
    print("1. Homework\n2. Project\n3. Exep Prep")
    user_choice=int(input("What type of Assignment: ")).strip()
    title=input("Title: ")
    subject=input("Subject: ")        
    deadline=input("Deadline: ")        
    priority_weight=int(input("Priority Weight: ") )       
    estimated_hours=int(input("Estimated Hours: ")  )      
    progress=int(input("Progress: "))
    if user_choice==1:
        submission_type=input("Submission Type: ")
        new_assignment=HomeworkAssignment(title,subject,deadline,priority_weight,estimated_hours,progress,submission_type)
    elif user_choice ==2:
        milestones = input("Milestones (comma-separated): ").split(",")
        team_members = input("Team members (comma-separated): ").split(",")
        new_assignment = ProjectAssignment(title,subject,deadline,priority_weight,estimated_hours,progress,milestones,team_members)           
    elif user_choice== 3:
        important_topics = input("Important topics (comma-separated): ").split(",")
        new_assignment = ExamPrep(title,subject,deadline,priority_weight,estimated_hours,progress,important_topics)       
    else:
        print("Invalid Choice")
        return
    planner.add_assignment(subject,new_assignment)
    print(f"Added '{title}' to {subject}.")
def handle_view_all(planner):
    assignments =planner.view_all_assignments()
    if not assignments:
        print("No assignments yet.")
        return
    for a in assignments:
        print(a.display_detail())
def handle_update(planner):
    try:
        subject_name, title = input("Enter Subject Name and Title of Assignment for Update (subject,title): ").split(",", 1)
    except ValueError:
        print("Please enter in the format: subject,title")
        return

    subject_name = subject_name.strip()
    title = title.strip()

    print("Leave blank to keep the current value.")
    deadline = input("New deadline (YYYY-MM-DD or DD-MM-YYYY): ").strip() or None

    priority_weight_input = input("New priority weight: ").strip() or None
    estimated_hours_input = input("New estimated hours: ").strip() or None
    progress_input = input("New progress percentage: ").strip() or None
    
    updated_assignment = planner.update_assignment(
        subject_name,
        title,
        deadline=deadline,
        priority_weight=priority_weight_input,
        estimated_hours=estimated_hours_input,
        progress=progress_input
    )
    print(f"Updated '{updated_assignment.title}' in '{subject_name}'.")

        

def handle_remove(planner):
    try:
        subject_name_input, title_input = input("Enter Subject Name and Title of Assignment for Deletion (subject,title): ").split(",", 1)
    except ValueError:
        print("Please enter in the format: subject,title")
        return
    subject_name=subject_name_input.strip()
    title=title_input.strip()
    removed_assignment=planner.remove_assignment(subject_name,title)
    print(f"Delete '{removed_assignment.title}' from  '{subject_name}'.")
def handle_focus_list(planner):
    for a in planner.focus_list():
        print(a.display_detail())
def handle_reminders(planner):
    for a in planner.get_reminder():
        print(a.display_detail())
    print("\n<<<<<!!! Alert !!!>>>>>\n")
    print("Complete These Assignments/Tasks as they will be Overdue in 24 or 48 hours")
def handle_statistics(planner):
    for key,value in planner.get_statistics().items():
        print(f"{key} : {value}")
def handle_report(planner):
    planner.export_report()
    print("Report saved to study_report.txt")

def main():
    planner = Planner()
    # planner = load_data()   

    while True:
        print_menu()
        choice = input("Choose an option: ").strip()

        try:
            if choice == "1":
                handle_add(planner)
            elif choice == "2":
                handle_view_all(planner)
            elif choice == "3":
                handle_update(planner)
            elif choice == "4":
                handle_remove(planner)
            elif choice == "5":
                handle_focus_list(planner)
            elif choice == "6":
                handle_reminders(planner)
            elif choice == "7":
                handle_statistics(planner)
            elif choice == "8":
                handle_report(planner)
            elif choice == "9":
                # save_data(planner)   
                print("Goodbye!")
                break
            else:
                print("Invalid option, try again.")
        except (AssignmentNotFound, SubjectNotFound, InvalidType,
                WrongDeadlineError, InvalidProgress, InvalidPriority, InvalidHour,TitleError) as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()





            

        
