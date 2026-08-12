import json
from models.assignment import HomeworkAssignment,ProjectAssignment,ExamPrep
Type_name={
    "HomeworkAssignment":HomeworkAssignment,
    "ProjectAssignment":ProjectAssignment,
    "ExamPrep":ExamPrep
}
class FileManager:
    @staticmethod
    def save_assignments(data):
       with open("data/assignments.json","w") as f:
            all_data=[]
            all_data=[a.to_dict() for a in data]
            json.dump(all_data,f,indent=2)
    @staticmethod
    def load_assignments(filepath="data/assignments.json"):
        try:
            with open(filepath,"r") as f:
                raw_data=json.load(f)
        except json.JSONDecodeError:
            raise ValueError(f"{filepath} is corrupted")
        except FileNotFoundError:
            return []
        assignments=[]
        for item in raw_data:
            cls=Type_name.get(raw_data["type"])
            if cls:
                assignments.append(cls.from_dict(item))
        return assignments                            


            
 







