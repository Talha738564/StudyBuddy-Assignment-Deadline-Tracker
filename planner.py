from models.subject import Subject 
from exceptions import  SubjectNotFound


class Planner:
    def __init__(self):
        self.subjects={}
        
    def add_assignment(self,subject_name,assignment):
        if subject_name not in self.subjects:
            self.subjects[subject_name]=Subject(subject_name)
        self.subjects[subject_name].add_assignment(assignment)
    def view_all_assignments(self):
        all_assignments=[]
        for subject in self.subjects.values():
            all_assignments.extend(subject.assignments)
        return sorted(all_assignments,key=lambda a:a.calculate_urgency(), reverse=True)
    def remove_assignment(self,subject_name,assignment):
        subject = self.subjects.get(subject_name)
        if subject is None:
            raise SubjectNotFound(f"No subject named '{subject_name}'")
        return subject.remove_assignment(assignment) 
    def update_assignment(self, subject_name, title, deadline=None, priority_weight=None, estimated_hours=None, progress=None):
        subject = self.subjects.get(subject_name)
        if subject is None:
            raise SubjectNotFound(f"No subject named '{subject_name}'")
        return subject.update_assignment(title, deadline, priority_weight, estimated_hours, progress) 
    def focus_list(self,n=5):
        all_sorted=self.view_all_assignments()
        return all_sorted[:n]
    def get_remainder(self,days_left=2):
        remainders=[]
        for assignment in self.view_all_assignments:
            if assignment.day_left<=days_left:
                remainders.append(assignment)
        return remainders
    def get_statistics(self):
        all_assignments=self.view_all_assignments()
        completed=[assignment for assignment in all_assignments if assignment.progress==100 ]
        pending=[assignment for assignment in all_assignments if assignment.progress<100 ]
        completion_times = [(a.completed_date - a.created_date).days for a in completed]

        if completion_times:
            avg_completion_time = sum(completion_times) / len(completion_times)
        else:
            avg_completion_time = 0   # or None — your call, see note below

        return {
            "total": len(all_assignments),
            "completed": len(completed),
            "pending": len(pending),
            "avg_completion_time_days": avg_completion_time,
        }



    


        




            


    
    
    
    
    
    
    






        


        
    
        



