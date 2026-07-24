from abc import ABC,abstractmethod
from datetime import  date

class Assignment(ABC):
    def __init__(self,title,subject,deadline,priority_weight,estimated_hours,progress):
        self.title=title
        self.subject=subject
        self.deadline=deadline
        self.priority_weight=priority_weight
        self.estimated_hours=estimated_hours
        self.progress=progress
    @abstractmethod
    def calculate_urgency(self):
        pass
class HomeworkAssignment(Assignment):
    def __init__(self,title,subject,deadline,priority_weight,estimated_hours,progress):
        super().__init__(title,subject,deadline,priority_weight,estimated_hours,progress)
    def calculate_urgency(self):
        


        try:

            days_left=(self.deadline - date.today()).days
            work_remaining=100-self.progress
            return self.priority_weight*(work_remaining/days_left)
        except ZeroDivisionError as e:

            print("[Error]: Days left cannot be Zero")
            







class ProjectAssignment(Assignment):
    def __init__(self,title,subject,deadline,priority_weight,estimated_hours,progress):
        super().__init__(title,subject,deadline,priority_weight,estimated_hours,progress)
    def calculate_urgency(self):
        pass






class ExamAssignment(Assignment):
    def __init__(self,title,subject,deadline,priority_weight,estimated_hours,progress):
        super().__init__(title,subject,deadline,priority_weight,estimated_hours,progress)
    def calculate_urgency(self):
        
        








    