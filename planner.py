from models.subject import Subject 
from exceptions import  SubjectNotFound


class Planner:
    def __init__(self):
        # map normalized subject name -> Subject instance
        self.subjects={}
    def _normalize(self, name):
        return name.strip().lower() if isinstance(name, str) else name
        
    def add_assignment(self,subject_name,assignment):
        key = self._normalize(subject_name)
        if key not in self.subjects:
            # store the original display name on Subject
            self.subjects[key]=Subject(subject_name)
        self.subjects[key].add_assignment(assignment)
    def view_all_assignments(self):
        all_assignments=[]
        for subject in self.subjects.values():
            all_assignments.extend(subject.assignments)
        return sorted(all_assignments,key=lambda a:a.calculate_urgency(), reverse=True)
    def remove_assignment(self,subject_name,assignment):
        key = self._normalize(subject_name)
        subject = self.subjects.get(key)
        if subject is None:
            raise SubjectNotFound(f"No subject named '{subject_name}'")
        return subject.remove_assignment(assignment)
    def update_assignment(self, subject_name, title, deadline=None, priority_weight=None, estimated_hours=None, progress=None):
        key = self._normalize(subject_name)
        subject = self.subjects.get(key)
        if subject is None:
            raise SubjectNotFound(f"No subject named '{subject_name}'")
        return subject.update_assignment(title, deadline, priority_weight, estimated_hours, progress)
    def focus_list(self,n=5):
        all_sorted=self.view_all_assignments()
        return all_sorted[:n]
    def get_reminder(self,days_left=2):
        reminders=[]
        for assignment in self.view_all_assignments():
            if assignment.day_left()<=days_left:
                reminders.append(assignment)
        return reminders
    
    def subject_completetion_rates(self):
        rates={}
        for name,subject in self.subjects.items():
            total=len(subject.assignments)
            if total>0:
                # Sum up the actual progress percentages of all assignments and divide by the total count
                total_progress = sum([assignment.progress for assignment in subject.assignments])
                rates[name] = total_progress / total
        return rates
    
    
                    

    def get_statistics(self):
        all_assignments=self.view_all_assignments()
        completed=[assignment for assignment in all_assignments if assignment.progress==100 ]
        pending=[assignment for assignment in all_assignments if assignment.progress<100 ]
        completion_times = [(a.completed_date - a.created_date).days for a in completed]

        if completion_times:
            avg_completion_time = sum(completion_times)/len(completion_times)
        else:
            avg_completion_time = 0
        return {
            "total": len(all_assignments),
            "completed": len(completed),
            "pending": len(pending),
            "avg_completion_time_days": avg_completion_time,
            "completion_rates": self.subject_completetion_rates(),
        }
    def export_report(self):
        from datetime import datetime # Local import to fetch the current date and time
        
        current_time = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        stats = self.get_statistics()
        
        with open("reports/study_report.txt", "w") as f:
            # ================= HEADER =================
            f.write("=" * 60 + "\n")
            f.write("                 STUDYBUDDY REPORT\n")
            f.write("=" * 60 + "\n")
            f.write(f" Generated on: {current_time}\n")
            f.write("=" * 60 + "\n\n")

            # ============= ALL ASSIGNMENTS =============
            f.write("--- [ ALL ASSIGNMENTS ] ---\n\n")
            
            assignments = self.view_all_assignments()
            if not assignments:
                f.write("  No assignments found.\n")
            else:
                for idx, assignment in enumerate(assignments, 1):
                    f.write(f" Task #{idx}\n")
                    f.write("-" * 40 + "\n")
                    
                    try:
                        f.write(assignment.display_summary() + "\n")
                    except Exception:
                        f.write(assignment.display_detail() + "\n")
                    f.write("\n") # Add a blank line between assignments
                    
            # =============== STATISTICS ===============
            f.write("\n" + "=" * 60 + "\n")
            f.write("                    STATISTICS\n")
            f.write("=" * 60 + "\n\n")
            
            # Align numbers for a clean, table-like appearance
            f.write(f"  Total Tasks         : {stats.get('total', 0)}\n")
            f.write(f"  Completed           : {stats.get('completed', 0)}\n")
            f.write(f"  Pending             : {stats.get('pending', 0)}\n")
            
            # Format average days to 1 decimal place
            avg_time = stats.get('avg_completion_time_days', 0)
            f.write(f"  Avg Days to Done    : {avg_time:.1f}\n\n")
            
            f.write("  Subject Completion Rates:\n")
            f.write("  " + "-" * 30 + "\n")
            
            rates = stats.get('completion_rates', {})
            if rates:
                for subject, rate in rates.items():
                    # Format the subject text to be 15 characters wide (aligned), and rate to 1 decimal
                    f.write(f"    - {subject.capitalize():<15} : {rate:.1f}%\n")
            else:
                f.write("    No subjects found.\n")

            # ================= FOOTER =================
            f.write("\n\n" + "=" * 60 + "\n")
            f.write("              End of StudyBuddy Report\n")
            f.write("=" * 60 + "\n")




    

    
    



    


        




            


    
    
    
    
    
    
    






        


        
    
        



