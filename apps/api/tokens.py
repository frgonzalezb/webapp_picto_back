import os

from rest_framework_simplejwt.tokens import AccessToken


class CustomAccessToken(AccessToken):
    def get_token(self, user):
        token = super().get_token(user)

        cookie_options = {
            'httponly': eval(os.environ["COOKIE_HTTPONLY"]),
            'secure': eval(os.environ["COOKIE_SECURE"]),
            'samesite': os.environ["COOKIE_SAMESITE"],
            'max-age': int(os.environ["COOKIE_MAX_AGE"]),
        }

        cookie_name = os.environ["COOKIE_NAME"]

        token_value = str(token)

        token.set_cookie(cookie_name, token_value, **cookie_options)
        
        return token
