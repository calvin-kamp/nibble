from config.throttles import UserThrottle


class UsernameAvailabilityThrottle(UserThrottle):
    scope = "username_availability"
