from models import assignment

class Subject():                                        
    assignment=[]
    def __init__(self,name):
        self.name=name


    def add_assignment(self,assignment):
        self.assignments.append(assignment)

    def view_all_assignments(self):
        for assignment in self.assignments:
            print(f"Assignment Title :{self.title} \n Assignmnet Subject: {self.subject} \n Assignment Deadline: {self.deadline} ")
    def delete_assignment(self,title):
        del_ass=(assignment  for assignment in self.assignments if assignment.title ==title)
        # This assignment needs to be deleted 




