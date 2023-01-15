from typing import Tuple
from flask import Response
from flask import jsonify

from core.libs.exceptions import FyleError
from marshmallow.exceptions import ValidationError
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import HTTPException


class ErrorHandler:
    """
    Base error handler, Different implementation of _get_status_code, _get_message can be provided
    in child classes to provide handling for specific exception classes
    """
    error_title = "Error"
    default_status_code = 500
    default_error_message = "Unknown error occurred"

    def _get_status_code(self, exception: Exception) -> int:
        return self.default_status_code

    def _get_message(self, exception: Exception) -> str:
        return self.default_error_message

    def get_error_response(self, exception: Exception) -> Tuple[Response, int]:
        """
        Return error response after formatting exception for message and status code
        """
        return jsonify(
            error=self.error_title, message=self._get_message(exception)
        ), self._get_status_code(exception)


class FyleErrorHandler(ErrorHandler):
    error_title = FyleError.__name__

    def _get_status_code(self, exception: FyleError) -> int:
        return exception.status_code

    def _get_message(self, exception: FyleError) -> str:
        return exception.message


class ValidationErrorHandler(ErrorHandler):
    error_title = ValidationError.__name__
    default_status_code = 400

    def _get_message(self, exception: ValidationError) -> str:
        # TODO: Convert message into string
        return exception.messages


class IntegrityErrorHandler(ErrorHandler):
    error_title = IntegrityError.__name__
    default_status_code = 400

    def _get_message(self, exception: IntegrityError) -> str:
        return str(exception.orig)


class HTTPExceptionHandler(ErrorHandler):
    error_title = HTTPException.__name__

    def _get_status_code(self, exception: HTTPException) -> int:
        return exception.code

    def _get_message(self, exception: HTTPException) -> str:
        return str(exception)


DEFAULT_ERROR_HANDLER = ErrorHandler()
ERROR_HANDLERS = {
    FyleError: FyleErrorHandler(),
    ValidationError: ValidationErrorHandler(),
    IntegrityError: IntegrityErrorHandler(),
    HTTPException: HTTPExceptionHandler(),
}
