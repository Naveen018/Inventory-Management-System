from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        logger.error(f"Error occurred: {str(exc)}")
        custom_response_data = {
            "error": True,
            "message": str(exc),
            "status_code": response.status_code
        }
        response.data = custom_response_data

    return response