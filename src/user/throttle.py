from rest_framework import throttling


class CheckUserAtributesThrottle(throttling.AnonRateThrottle):
    rate = '1/second'
    scope = "check"

class RegistrationThrottle(throttling.AnonRateThrottle):
    rate = '30/minute'
    scope = "register"

class ActivateAccountThrottle(throttling.AnonRateThrottle):
    rate = '5/hour'
    scope = "activate_account"

class ResetPasswordThrottle(throttling.AnonRateThrottle):
    rate = '3/hour'
    scope = "activate_account"