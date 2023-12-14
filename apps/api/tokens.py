import os
import ast

from rest_framework_simplejwt.tokens import AccessToken


class CustomAccessToken(AccessToken):
    def get_token(self, user):
        token = super().get_token(user)

        cookie_options = {
            'httponly': ast.literal_eval(os.getenv('COOKIE_HTTPONLY')),
            'secure': ast.literal_eval(os.getenv('COOKIE_SECURE')),
            'samesite': ast.literal_eval(os.getenv('COOKIE_SAMESITE')),
            'max-age': int(os.getenv('COOKIE_MAX_AGE')),
        }

        cookie_name = os.getenv('COOKIE_NAME')

        token_value = str(token)

        token.set_cookie(cookie_name, token_value, **cookie_options)
        
        return token
