from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from conf.db_conf import get_database
from crud import users
from models.users import User
from schemas.users import UserChangePasswordRequest, UserRequest, UserUpdateRequest, UserAuthResponse, UserInfoResponse
from utils.auth import get_current_user

from utils.response import success_response

router = APIRouter(prefix="/api/user", tags=["user"])


@router.post("/register")
async def register(data: UserRequest, db: AsyncSession = Depends(get_database)):
    is_exiting = await users.get_user_by_name(db, data.username)

    if is_exiting:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user already exists")

    user = await users.create_user(db, data)

    token = await users.create_token(db, user.id)
    await users.record_user_login(db, user.id)

    resp = UserAuthResponse(token=token, user_info=UserInfoResponse.model_validate(user))

    return success_response(message="success", data=resp)


@router.post("/login")
async def login(data: UserRequest, db: AsyncSession = Depends(get_database)):
    user = await users.authenticate_user(db, data.username, data.password)

    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="wrong username or password")

    token = await users.create_token(db, user.id)
    await users.record_user_login(db, user.id)
    resp = UserAuthResponse(token=token, user_info=UserInfoResponse.model_validate(user))
    return success_response(message="success", data=resp)


@router.get("/info")
async def info(user: User = Depends(get_current_user)):
    return success_response(message="获取用户信息成功", data=UserInfoResponse.model_validate(user))


@router.put("/update")
async def update_user_info(
        data: UserUpdateRequest,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_database)

):
    updated = await users.update_user(db, user.username, data)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")

    return success_response(message="success", data=UserInfoResponse.model_validate(updated))


@router.put("/password")
async def change_password(
        data: UserChangePasswordRequest,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_database)
):
    flag = await users.change_user_password(db, user, data)
    if not flag:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="wrong old password")

    return success_response(message="success")


