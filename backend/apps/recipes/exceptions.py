from config.exceptions import Conflict


class SubmissionNotPending(Conflict):
    default_code = "submission_not_pending"
    default_detail = "Diese Einreichung ist nicht mehr offen."
