class StudyBuddyError(Exception):
    pass
class AssignmentNotExistError(StudyBuddyError):
        pass
class SubjectNotFound(StudyBuddyError):
    pass
class WrongDeadlineError(StudyBuddyError):
    pass
class InvalidWeight(StudyBuddyError):
    pass


