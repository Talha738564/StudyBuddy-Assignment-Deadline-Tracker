import json
from planner import Planner
with open("assignment.json","w") as f:
    all_data=[]
    all_data=[a.to_dict() for a in Planner.view_all_assignments()]
    json.dump(all_data,f)
with open("subject.json","w") as f:
    json.dump(Planner.subjects,f)







