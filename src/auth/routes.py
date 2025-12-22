from fastapi import APIRouter, Depends,status
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from .schemas import CreateUserModel, UserResponseModel, UserLoginModel, EmailModel, PasswordResetModel, PasswordResetConfirmModel
from .service import UserService
from fastapi.exceptions import HTTPException
from .utils import create_access_token, decode_token, verify_password, create_url_safe_token, decode_url_safe_token, generate_password_hash
from datetime import timedelta, datetime
from fastapi.responses import JSONResponse
from .dependencies import RefreshTokenBearer, AccessTokenBearer, get_current_user, RoleChecker
from src.db.redis import add_jti_to_blocklist
from src.mail import create_message, mail
from src.core.config import config_obj
from src.db.main import get_session

user_service = UserService()
auth_router = APIRouter()
role_checker = RoleChecker(["admin", "user"])

REFRESH_TOKEN_EXPIRY = True

@auth_router.post('/send_mail')
async def send_mail(emails:EmailModel):
    emails = emails.addresses
    html = "<h1>Welcome to Task Collaboration APP</h1>"
    message = create_message(
        recipients=emails,
        subject="Welcome",
        body=html
    )
    await mail.send_message(message)
    return {
        "message":"Email Sent Successfully!"
    }


@auth_router.post('/signup', status_code=status.HTTP_201_CREATED)
async def create_user(user_data:CreateUserModel,session: AsyncSession = Depends(get_session)):
    email = user_data.email
    user_exists = await user_service.user_exists(email, session)
    if user_exists:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User with email already exists!!")
    new_user = await user_service.create_user(user_data, session)
    token = create_url_safe_token({"email":email})

    link = f"http://{config_obj.DOMAIN}/api/v1/auth/verify/{token}"


    html_msg = f"""
    <h1>Verify Your Email</h1>
    <p>Please Click this <a href="{link}">link</a> to Verify Your Email</p>
    """
    message = create_message(
        recipients=[email],
        subject="Verify Your Email",
        body=html_msg
    )
    await mail.send_message(message)
    return {
        "message":"Account Created! Check Email to Verify Your Account!",
        "user":new_user
    }

@auth_router.get('/verify/{token}')
async def verify_user_account(token:str, session:AsyncSession = Depends(get_session)):
    token_data = decode_url_safe_token(token)
    user_email = token_data.get('email')
    if user_email:
        user = await user_service.get_user_by_email(user_email, session)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")

        await user_service.update_user(user, {'is_verified':True}, session)

        return JSONResponse(
            content={
                "message":"Account verified Successfully!",

            }, status_code=status.HTTP_200_OK
        )
    return JSONResponse(
        content={
            ":message":"Error Occured during verification"
        }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )

@auth_router.post('/login')
async def login_users(login_data:UserLoginModel, session: AsyncSession = Depends(get_session)):
    email = login_data.email
    password = login_data.password
    user = await user_service.get_user_by_email(email,session)
    if user is not None:
        password_valid = verify_password(password,user.password_hash)
        if password_valid:
            access_token = create_access_token(
                user_data ={
                    'email':user.email,
                    'user_uid': str(user.uid),
                    'role':user.role
                }
            )
            refresh_token = create_access_token(
                user_data ={
                    'email':user.email,
                    'user_uid': str(user.uid)
                },
                refresh=True,
                expiry=timedelta(days=REFRESH_TOKEN_EXPIRY)
            )
            return JSONResponse(
                content={
                    "message":"Logged in successfully!!!!",
                    "access_token":access_token,
                    "refresh_token":refresh_token,
                    "user":{
                    "email":user.email,
                    "uid":str(user.uid),
                    "role":user.role
                }
                }
                
            )
        
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Email or Password")


@auth_router.get('/me')
async def get_current_user(user = Depends(get_current_user), _bool=Depends(role_checker)):
    return user


@auth_router.get('/refresh_token')
async def get_new_access_token(token_details: dict = Depends(RefreshTokenBearer())):
    expiry_timestamp = token_details['exp']
    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        new_access_token = create_access_token(
            user_data=token_details['user']
        )
        return JSONResponse(
            content = {
                "access_token" : new_access_token,   
            }
        )
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or Expired Token")
    print(expiry_timestamp)
    return {}


@auth_router.get('/logout')
async def revoke_token(token_details: dict = Depends(AccessTokenBearer())):
    jti = token_details['jti']
    await add_jti_to_blocklist(jti)
    return JSONResponse(
        content={
            "message":"Logged Out Successfully!!!"
        },
        status_code=status.HTTP_200_OK
    )

@auth_router.post('/pasword-reset')
async def password_reset_request(email_data:PasswordResetModel):
    email = email_data.email
    token = create_url_safe_token({"email":email})

    # link = f"http://{config_obj.DOMAIN}/api/v1/auth/password-reset-confirm/{token}"
    link = f"http://localhost:3000/reset-password/{token}"


    html_msg = f"""
    <h1>Reset Your Password</h1>
    <p>Please Click this <a href="{link}">link</a> to Reset Your Password/p>
    """
    message = create_message(
        recipients=[email],
        subject="Reset your Password",
        body=html_msg
    )
    await mail.send_message(message)
    return JSONResponse(
        content={ "message":"Please Check Your Email for instruction to reset your password"}, status_code=status.HTTP_200_OK
    )
       

@auth_router.post('/password-reset-confirm/{token}')
async def reset_account_password(token:str,passwords:PasswordResetConfirmModel, session:AsyncSession = Depends(get_session)):
    new_password = passwords.new_password
    confirm_password = passwords.confirm_new_password
    if new_password != confirm_password:
        raise HTTPException(
            detail="Password Do Not Match",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    token_data = decode_url_safe_token(token)
    user_email = token_data.get('email')
    if user_email:  
        user = await user_service.get_user_by_email(user_email, session)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")

        password_hash = generate_password_hash(new_password)
        await user_service.update_user(user, {'password_hash':password_hash}, session)

        return JSONResponse(
            content={
                "message":"Password Reset Successfully!",

            }, status_code=status.HTTP_200_OK
        )
    return JSONResponse(
        content={
            ":message":"Error Occured during password reset."
        }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )