from abc import ABC,abstractmethod
from exceptions import (
    InvalidPriority,
    WrongDeadlineError,
    InvalidHour,
    InvalidProgress,
    InvalidType,
    TitleError,
    SubjectNotFound,
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
        return self._subject
    @subject.setter
    def subject(self,value):
        if not isinstance(value, str):
            raise InvalidType(f"Subject  must be a string , got {type(value).__name__}")
        elif value=="":
            raise SubjectNotFound("Subject name must be Entered")
        self._subject=value
    @property
    def title(self):
        return self._title
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
                deadline_str=value.strip() 
                deadline=datetime.strptime(deadline_str,"%Y-%m-%d").date()
            except ValueError as e:
                try: 
                    deadline=datetime.strptime(deadline_str,"%d-%m-%Y").date()
                except ValueError as e2 :
                    raise WrongDeadlineError( f"Invalid deadline '{value}'. Use YYYY-MM-DD or DD-MM-YYYY.") from e2
            if deadline.year<1000:
                raise WrongDeadlineError(f"Year must be a four digit: {value}")
            self._deadline=deadline
            # for fmt in ("%Y-%m-%d", "%d-%m-%Y"):
            # try:
            #     self._deadline = datetime.strptime(value, fmt).date()
            #     return
            # except ValueError:
            #     pass

            # raise WrongDeadlineError(
            #     f"Invalid deadline '{value}'. Use YYYY-MM-DD or DD-MM-YYYY."
            # )
                                    
        


    def day_left(self):
        return (self.deadline - date.today()).days
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
    def deadline_status(self):
           days_left=self.day_left()
           if days_left<0:
               return f"OverDue by {-days_left} days"
           elif days_left==0:
               return f"Due Today"
           else:
               return f"due in {days_left} days"
       
    def dispaly_summary(self):
        pass
    def display_detail(self):
        return (f"Title: {self.title}\n" 
            f"Subject: {self.subject}\n"
            f"Type: {type(self).__name__}\n"
            f"Deadline: {self.deadline}({self.deadline_status()})\n"
            f"Urgency: {self.calculate_urgency()}\n"
            f"Progress: {self.progress}% \n")



class HomeworkAssignment(Assignment):
    def __init__(self,title,subject,deadline,priority_weight,estimated_hours,progress,submission_type):
        super().__init__(title,subject,deadline,priority_weight,estimated_hours,progress)
        self._submission_type=submission_type
    @property
    def submission_type(self):
        return self._submission_type
    @submission_type.setter
    def submission_type(self,value):
        if not isinstance(value, str):
            raise InvalidType(f"Subject  must be a string , got {type(value).__name__}")       
        self._submission_type=value 
    def calculate_urgency(self):
            
            days_left=self.day_left()
            if days_left<=0:
                urgency=float('inf')
            else:
                work_remaining=100-self.progress
                urgency= self.priority_weight+(work_remaining/days_left)
            return urgency
    
    
    def display_summary(self):
        return (f"[{self.subject}] {self.title} | {self.submission_type} | {self.deadline_status()}  | Urgency :{self.calculate_urgency()} | {self.progress}% Done")
    def display_detail(self):
        base=super().display_detail()
        return base +f"Submission Type: {self.submission_type}"
    


        
        

    
class ProjectAssignment(Assignment):
    def __init__(self,title,subject,deadline,priority_weight,estimated_hours,progress,milestones,team_members):
        super().__init__(title,subject,deadline,priority_weight,estimated_hours,progress)
        self._milestones=milestones
        self._team_members=team_members
    def calculate_urgency(self):
            days_left=self.day_left()
            if days_left<=0:
                urgency=float('inf')
            else:
                work_remaining=100-self.progress
                urgency= self.priority_weight+(work_remaining/days_left)*(self.estimated_hours/days_left)
            return urgency
    def display_summary(self):
        return (f"[{self.subject}] {self.title} |  {self.deadline_status()}  | Urgency :{self.calculate_urgency()} | {self.progress}% Done | Members: {len(self.team_members)}"  )
    def display_detail(self):
        base=super().display_detail()
        return base+f"Milestones Achieved: {','.join(self.milestones)}\n"+f"Team Members:{",".join(self.team_members)} "
        
        






class ExamPrep(Assignment):
    def __init__(self,title,subject,deadline,priority_weight,estimated_hours,progress,important_topics):
        super().__init__(title,subject,deadline,priority_weight,estimated_hours,progress)
        self._important_topics=important_topics
    def calculate_urgency(self):
            days_left=self.day_left()
            if days_left<=0:
                urgency=float('inf')
            else:
                urgency= self.priority_weight+(1/days_left)**2
            return urgency
    def display_summary(self):
        return (f"[{self.subject}] {self.title} | {self.deadline_status()} | Urgency :{self.calculate_urgency()} | {self.progress}% Done |  Important Topics: {len(self.important_topics)}"  )
    def display_detail(self):
        base=super().display_detail()
        return base+f"Important Topics: {','.join(self.important_topics)}"
        
    
    
    



    

    





        
        








    