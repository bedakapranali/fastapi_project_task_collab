from typing import Any, Callable
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi import FastAPI, status

class TaskCollabException(Exception):
    """This is the base class for all bookly errors"""
    pass

class InvalidToken(TaskCollabException):
    """User has provided an invalid or expired token"""
    pass

class RevokedToken(TaskCollabException):
    """User has provided a token that has been revoked"""
    pass

class AccessTokenRequired(TaskCollabException):
    """User has provided a refresh token when an access token is needed"""
    pass

class RefreshTokenRequired(TaskCollabException):
    """User has provided an access token when a refresh token is needed"""
    pass

class UserAlreadyExists(TaskCollabException):
    """User has provided an email for a user who exists during sign up."""
    pass

class InvalidCredentials(TaskCollabException):
    """User has provided wrong email or password during log in."""
    pass

class InsufficientPermission(TaskCollabException):
    """User does not have the necessary permissions to perform an action."""
    pass

class TaskNotFound(TaskCollabException):
    """Task Not found"""
    pass

class UserNotFound(TaskCollabException):
    """User Not found"""
    pass

class TaskAlreadyExists(TaskCollabException):
    """Task already exists"""
    pass

class EmployeeNotFound(TaskCollabException):
    """Employee Not found"""
    pass

class AccountNotVerified(Exception):
    """Account Not yet verified"""
    pass

def create_error_handler(status_code: int, initial_detail:Any) -> Callable[[Request,Exception], JSONResponse]:
    async def exception_handler(request:Request, exc: TaskCollabException):
        return JSONResponse(
            content= initial_detail,
            status_code = status_code
        )

    return exception_handler





... # rest of the file
def register_error_handlers(app: FastAPI):
    app.add_exception_handler(
        UserAlreadyExists,
        create_error_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "User with email already exists",
                "error_code": "user_exists",
            },
        ),
    )

    app.add_exception_handler(
        EmployeeNotFound,
        create_error_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Employee not found",
                "error_code": "employee_not_found",
            },
        ),
    )
    app.add_exception_handler(
        TaskNotFound,
        create_error_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Task not found",
                "error_code": "task_not_found",
            },
        ),
    )
    app.add_exception_handler(
        InvalidCredentials,
        create_error_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail={
                "message": "Invalid Email Or Password",
                "error_code": "invalid_email_or_password",
            },
        ),
    )
    app.add_exception_handler(
        InvalidToken,
        create_error_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Token is invalid Or expired",
                "resolution": "Please get new token",
                "error_code": "invalid_token",
            },
        ),
    )
    app.add_exception_handler(
        RevokedToken,
        create_error_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Token is invalid or has been revoked",
                "resolution": "Please get new token",
                "error_code": "token_revoked",
            },
        ),
    )
    app.add_exception_handler(
        AccessTokenRequired,
        create_error_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Please provide a valid access token",
                "resolution": "Please get an access token",
                "error_code": "access_token_required",
            },
        ),
    )
    app.add_exception_handler(
        RefreshTokenRequired,
        create_error_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "Please provide a valid refresh token",
                "resolution": "Please get an refresh token",
                "error_code": "refresh_token_required",
            },
        ),
    )
    app.add_exception_handler(
        InsufficientPermission,
        create_error_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "You do not have enough permissions to perform this action",
                "error_code": "insufficient_permissions",
            },
        ),
    )
    app.add_exception_handler(
        UserNotFound,
        create_error_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={"message": "User Not Found", "error_code": "user_not_found"},
        ),
    )

    app.add_exception_handler(
    TaskAlreadyExists,
    create_error_handler(
        status_code=status.HTTP_409_CONFLICT,
        initial_detail={
            "message": "Task already exists",
            "error_code": "task_exists",
        },
    ),
)


    app.add_exception_handler(
        TaskNotFound,
        create_error_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Task Not Found",
                "error_code": "task_not_found",
            },
        ),
    )

    app.add_exception_handler(
        AccountNotVerified,
        create_error_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "Account  Not Verified",
                "error_code": "account_not_verified",
                "resolution":"Please check your email for verification detail"
            },
        ),
    )

    @app.exception_handler(500)
    async def internal_server_error(request, exc):

        return JSONResponse(
            content={
                "message": "Oops! Something went wrong",
                "error_code": "server_error",
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )