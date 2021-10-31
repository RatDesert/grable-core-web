from rest_framework import throttling


class RefreshThrottle(throttling.AnonRateThrottle):
    rate = '1/second'
    scope = "token"


class LoginThrottle(throttling.AnonRateThrottle):
    rate = '1/second'
    scope = "login"
