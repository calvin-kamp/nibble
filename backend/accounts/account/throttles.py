from config.throttles import UserThrottle


class AccountDeletionThrottle(UserThrottle):
    scope = "account_deletion"


class AccountExportThrottle(UserThrottle):
    scope = "account_export"
