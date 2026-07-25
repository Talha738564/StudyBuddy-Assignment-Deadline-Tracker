'''
[x] HOw I came to know that which type of assignmetn need to be execute and How?
[x] Should be proficient that how to calculate the list of all assignments related
to one subject
[x] 

'''






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
            days_left=(self.deadline - date.today()).days
            if days_left<=0:
                urgency=float('inf')
            else:
                work_remaining=100-self.progress
                urgency= self.priority_weight+(work_remaining/days_left)
            return urgency
    
        
            







class ProjectAssignment(Assignment):
    def __init__(self,title,subject,deadline,priority_weight,estimated_hours,progress):
        super().__init__(title,subject,deadline,priority_weight,estimated_hours,progress)
    def calculate_urgency(self):
            days_left=(self.deadline - date.today()).days
            if days_left<=0:
                urgency=float('inf')
            else:
                work_remaining=100-self.progress
                urgency= self.priority_weight+(work_remaining/days_left)*(self.estimated_hours/days_left)
            return urgency
        






class ExamAssignment(Assignment):
    def __init__(self,title,subject,deadline,priority_weight,estimated_hours,progress):
        super().__init__(title,subject,deadline,priority_weight,estimated_hours,progress)
    def calculate_urgency(self):
            days_left=(self.deadline - date.today()).days
            if days_left<=0:
                urgency=float('inf')
            else:
                work_remaining=100-self.progress
                urgency= self.priority_weight+(1/days_left)**2
            return urgency




        
        








    