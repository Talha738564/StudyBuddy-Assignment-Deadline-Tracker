from abc import ABC,abstractmethod
from exceptions import (
    InvalidPriority,
    WrongDeadlineError,
    InvalidHour,
    InvalidProgress,
    InvalidType,
    TitleError,
    SubjectNotFound
)
from datetime import  date, datetime 

class Assignment(ABC):
    def __init__(self,title,subject,deadline,priority_weight,estimated_hours,progress): 
        self.title=title
        self.subject=subject
        self.estimated_hours=estimated_hours
        self.priority_weight=priority_weight
        self.progress=progress
        self.deadline=deadline




    @property
    def subject(self):
        return self.subject
    @subject.setter
    def subject(self,value):
        if not isinstance(value, str):
            raise InvalidType(f"Subject  must be a string , got {type(value).__name__}")
        elif value=="":
            raise SubjectNotFound("Subject name must be Entered")
        self._subject=value
    @property
    def title(self):
        return self.title
    @title.setter
    def title(self,value):
        if not isinstance(value, str):
            raise InvalidType(f"Title  must be a string , got {type(value).__name__}")
        elif value=="":
            raise TitleError("Title Must be Entered")
        self._title=value

    @property
    def deadline(self):
        return self._deadline
    @deadline.setter
    def deadline(self,value):
            if not isinstance(value, str) or value=="":
                raise InvalidType(f"deadline  must be a string , got {type(value).__name__}")
            try:
                deadline_str=value 
                deadline=datetime.strptime(deadline_str,"%Y-%m-%d").date()
                self._deadline=deadline
            except ValueError:
                try: 
                    deadline=datetime.strptime(deadline_str,"%d-%m-%Y").date()
                    self._deadline=deadline
                except ValueError :
                    raise WrongDeadlineError(f"Invalid Format: {deadline_str}") from None
                
        


 
    @property
    def priority_weight(self):
        return self._priority_weight

    @priority_weight.setter
    def priority_weight(self, value):
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise InvalidType(f"priority_weight must be a number, got {type(value).__name__}")
        if value < 0 or value > 100:
            raise InvalidPriority("Priority cannot be negative or greater than 100")
        self._priority_weight= value



    @property
    def estimated_hours(self):
        return self._estimated_hours    

    @estimated_hours.setter
    def estimated_hours(self, value):
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise InvalidType(f"estimated_hours must be a number, got {type(value).__name__}")
        if value <= 0:
            raise InvalidHour("Estimated Hours for Assignment Cannot be Zero or Negative")
        self._estimated_hours =value
    @property
    def progress(self):
        return self._progress

    @progress.setter
    def progress(self, value):
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise InvalidType(f"progress must be a number, got {type(value).__name__}")
        if value < 0 or value > 100:
            raise InvalidProgress("Progress cannot be negative or greater than 100")
        self._progress=value

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
                urgency= self.priority_weight+(1/days_left)**2
            return urgency



a1=ExamAssignment("Problem Solving and Algorithums","DSA","27-7-2026",70,5,10)
print(a1.calculate_urgency())
            
    

    





        
        








    