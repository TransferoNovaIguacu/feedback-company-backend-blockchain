# Isso é apenas um teste
from rest_framework.views import exception_handler
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, (AuthenticationFailed, NotAuthenticated)):
        return Response(
            {"Error": "Você não é um usuário verificado"},
            status=status.HTTP_401_UNAUTHORIZED,
        )
    
    return response
