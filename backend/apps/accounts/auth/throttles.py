from config.throttles import EmailThrottle, IPThrottle, UserThrottle


class RegisterThrottle(IPThrottle):
    scope = "register"


class LoginThrottle(IPThrottle):
    scope = "login"


class RefreshThrottle(IPThrottle):
    scope = "refresh"


class PasswordForgotIPThrottle(IPThrottle):
    scope = "password_forgot_ip"


class PasswordForgotEmailThrottle(EmailThrottle):
    scope = "password_forgot_email"


class VerificationResendThrottle(UserThrottle):
    scope = "verification_resend"


class EmailChangeThrottle(UserThrottle):
    scope = "email_change"


class PasswordChangeThrottle(UserThrottle):
    scope = "password_change"
