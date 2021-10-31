from rest_framework import exceptions, status

class EmailTokenNotValid(exceptions.APIException):
    status_code = 400
    default_detail = 'Email token is invalid or expired'
    default_code = 'email_token_not_valid'

