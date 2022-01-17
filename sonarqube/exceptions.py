from requests.exceptions import HTTPError, RequestException

def raise_for_status(res):
    try:
        res.raise_for_status()
    except HTTPError as e:
        if res.status_code == 400:
            # Validation error
            msg = ', '.join(e['msg'] for e in res.json()['errors'])
            raise ValidationError(e, msg)

        elif res.status_code in (401, 403):
            # Auth error
            raise AuthError(e)

        elif res.status_code < 500:
            # Other 4xx, generic client error
            raise ClientError(e)

        else:
            # 5xx is server error
            raise ServerError(e)

class SonarQubeApiException(RequestException):
    def __init__(self, http_error, *args, **kwargs):
        super().__init__(response = http_error.response, request = http_error.request, *args, **kwargs)
    
class ClientError(SonarQubeApiException):
    pass

class ServerError(SonarQubeApiException):
    pass

class AuthError(SonarQubeApiException):
    pass

class ValidationError(SonarQubeApiException):
    pass

class CliException(Exception):
    pass