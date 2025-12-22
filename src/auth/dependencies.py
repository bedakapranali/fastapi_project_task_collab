from fastapi import Request, status, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from .utils import decode_token
from fastapi.exceptions import HTTPException
from src.db.redis import token_in_blocklist
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from .service import UserService
from typing import List, Any
from src.db.models import User

user_service = UserService()

class TokenBearer(HTTPBearer):
    def __init__(self, auto_error= True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request:Request) -> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)
        token = creds.credentials
        token_data = decode_token(token)
        if not self.token_valid(token):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={
                "error": "This TOken isinvalid or expired",
                "resolution":"Please get new token."
            })
        
        if await token_in_blocklist(token_data['jti']):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={
                "error": "This TOken has been invalid or revoked",
                "resolution":"Please get new token."
            })

        # if token_data['refresh']:
        #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Please Provide an Access Token")
        
        self.verify_token_data(token_data)
        return token_data

    def token_valid(self,token:str)->bool:
        token_data = decode_token(token)
        return True if token_data is not None else False

    
    def verify_token_data(self, token_data:dict):
        raise NotImplementedError("Please Overridde this method in child class")
    
class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data:dict)->None:
        if token_data and token_data['refresh']:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Please Provide an Access Token")

class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data:dict)->None:
        if token_data and not token_data['refresh']:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Please Provide an Refresh Token")
        

async def get_current_user(token_details : dict = Depends(AccessTokenBearer()), session:AsyncSession = Depends(get_session)):
    user_email = token_details['user']['email']
    user = await user_service.get_user_by_email(user_email, session)
    return user



class RoleChecker:
    def __init__(self, allowed_roles: List[str]) -> None:
        self.allowed_roles = allowed_roles

    async def __call__(self, current_user=Depends(get_current_user)) -> Any:
        if not current_user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please verify your account to perform this action"
            )
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not permitted to perform this action"
            )
        return True