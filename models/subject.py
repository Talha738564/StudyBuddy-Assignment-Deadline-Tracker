from models import assignment
from exceptions import AssignmentNotFound

class Subject:                                        
    def __init__(self,name):
        self.name=name
        self.assignments=[]



    def add_assignment(self,assignment):
        self.assignments.append(assignment)
        return

    def remove_assignment(self,title):
        for assignment in self.assignments:
            if assignment.title==title:
                self.assignments.remove(assignment)
                return assignment
        raise AssignmentNotFound(f"No assignment Titled:' {title} ' Found!")             
    def view_all_assignments(self):
        for assignment in self.assignments:
            print(assignment.display_detail())
    def get_pending(self):
        pendings=[assignment.display_detail() for assignment in self.assignments if assignment.progress<100]            
        for pending in pendings:
            print(pending)
        return            
    def get_completed(self):
        completed=[assignment.display_detail() for assignment in self.assignments if assignment.progress==100]            
        for c in completed:
            print(c)
        return completed                    
    def update_assignment(self,title,deadline=None,priority_weight=None,estimated_hours=None,progress=None):
        assignment=next((assignment  for assignment in self.assignments if assignment.title == title),None)
        if assignment is None:
            raise AssignmentNotFound(f"No assignment Titled:' {title} ' Found!")             
        if deadline is not None:
            assignment.deadline=deadline
        if priority_weight is not None:
            assignment.priority_weight=priority_weight
        if estimated_hours is not None:
            assignment.estimated_hours=estimated_hours
        if progress is not None:
            assignment.progress=progress
        return assignment   
             
    

        
        







