from typing import Annotated

from litestar import post, get, Controller
from dishka.integrations.base import FromDishka as Depends
from dishka.integrations.litestar import inject
from litestar.exceptions import HTTPException
from litestar.params import Body
from litestar.status_codes import HTTP_401_UNAUTHORIZED

from auth.src.application.interactors import (
    ConfirmSignupInteractor, 
    LoginInteractor,
    RefreshTokenInteractor, 
    SignupInteractor, 
    VerifyTokenInteractor
)
from auth.src.application.dto import (
    LoginDTO, 
    SignupDTO, 
    TokensDTO
)
from auth.src.controllers.schemas import (
    TokenResponse,
    TokensForm,
    UserAuthResponse, 
    UserSignupRequest, 
    UserSignupResponse, 
    AuthForm
)


class AuthController(Controller):
    path = "/auth"

    @post(
        path="/signup",
        operation_id="user_signup",
        summary="User Registration",
        description="Endpoint for registering a new user.",
        response_class=UserSignupResponse
    )
    @inject
    async def signup(
        self,
        body: Annotated[UserSignupRequest, Body(description="User registration data.")],
        interactor: Depends[SignupInteractor]
    ) -> UserSignupResponse:
        signup_dto = SignupDTO(
            username=body.username,
            email=body.email,
            password=body.password
        )
        new_user_dm = await interactor(signup_dto)
        return UserSignupResponse(
            id=new_user_dm.uuid,
            username=new_user_dm.username,
        )

    @get(
        path="/signup/{user_uuid}",
        operation_id="confirm_signup",
        summary="Registration Confirmation",
        description="Endpoint for confirming user registration by UUID",
        response_class=TokenResponse
    )
    @inject
    async def confirm_signup(
        user_uuid: str,
        interactor: Depends[ConfirmSignupInteractor],
    ) -> TokenResponse:
        tokens_dm = await interactor(user_uuid=user_uuid)
        return TokenResponse(
            access_token=tokens_dm.access_token,
            refresh_token=tokens_dm.refresh_token
        )

    @post(
        path="/login",
        operation_id="user_login",
        summary="User Login",
        description="Endpoint for user authentication. Accepts credentials and \
            returns an authentication token.",
        response_class=TokenResponse
    )
    @inject
    async def login_for_access_token(
        self,
        body: Annotated[AuthForm, Body(description="User registration data.")],
        interactor: Depends[LoginInteractor]
    ) -> TokenResponse:
        params = LoginDTO(
            username=body.username,
            phone=body.phone,
            password=body.password
        )
        tokens_dm = await interactor(params)
        if not tokens_dm:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password or user is not activated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return TokenResponse(**tokens_dm)


    @post(
        path="/refresh",
        operation_id="refresh_access_token",
        summary="Refresh Access Token",
        description="Endpoint for refreshing authentication tokens. \
            Accepts an access token and a refresh token, validates them, \
            and returns new authentication tokens.",
        response_model=TokenResponse
    )
    @inject
    async def refresh_access_token(
        body: Annotated[TokensForm, Body(description="User tokens for authentification.")],
        interactor: Depends[RefreshTokenInteractor]
    ) -> TokenResponse:
        tokens = TokensDTO(access_token=body.access_token, refresh_token=body.refresh_token)
        if tokens_dm := await interactor(tokens):
            return TokenResponse(**tokens_dm)
        raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Incorrect refresh token or user is not activated",
                headers={"WWW-Authenticate": "Bearer"},
            )

    @post(
        path="/logout",
        operation_id="user_logout",
        summary="User Logout",
        description="Endpoint for logging out a user. Invalidates the user's access \
            and refresh tokens, preventing further use of these tokens."
    )
    @inject
    async def logout(
        self,
        body: Annotated[TokensForm, Body(description="User tokens for authentification.")],
        interactor: Depends[LoginInteractor]
    ) -> bool:
        params = TokensDTO(
            access_token=body.access_token,
            refresh_token=body.refresh_token
        )
        result = await interactor(params)
        if not result:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Incorrect tokens",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return result

    @post(
        path="/verify",
        operation_id="user_verify",
        summary="User Verify",
        description="Endpoint for logging out a user. Invalidates the user's access \
            and refresh tokens, preventing further use of these tokens.",
        response_class=UserAuthResponse
    )
    @inject
    async def verify_token(
        self,
        token: Annotated[str, Body(description="User access token for authentification.")],
        interactor: Depends[VerifyTokenInteractor]
    ) -> UserAuthResponse:
        user_dm = await interactor(token)
        if not user_dm:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Incorrect access token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return UserAuthResponse(**user_dm)