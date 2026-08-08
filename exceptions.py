class StudyBuddyError(Exception):
    pass
class AssignmentNotFound(StudyBuddyError):
        pass
class SubjectNotFound(StudyBuddyError):
    pass
class WrongDeadlineError(StudyBuddyError):
    pass
class InvalidPriority(StudyBuddyError):
    pass
class InvalidHour(StudyBuddyError):
    pass
class InvalidProgress(StudyBuddyError):
    pass
class InvalidType(Exception):
    pass
class TitleError(Exception):
     pass
class DuplicateAssignmentError:
     pass


