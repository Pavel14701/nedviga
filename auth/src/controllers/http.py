from litestar import post, Request, Response
from dishka.integrations.base import FromDishka as Depends
from dishka.integrations.litestar import inject
from litestar.exceptions import HTTPException
from litestar.params import Body
from litestar.status_codes import HTTP_401_UNAUTHORIZED, HTTP_400_BAD_REQUEST


from src.application import interactors
from src.application import dto
from src.domain.entities import AuthForm
from src.controllers.schemas import TokenResponse

@post("/token", response_model=TokenResponse)
@inject
async def login_for_access_token(
    get_user_data_interactor: Depends[interactors.GetUserDataInteractor],
    hash_password_interactor: Depends[interactors.HashPasswordInteractor],
    create_access_token_interactor: Depends[interactors.CreateAccessTokenInteractor],
    create_refresh_token_interactor: Depends[interactors.CreateRefreshTokenInteractor],
    form_data: AuthForm = Body()
) -> dict[str, str]:
    user = await get_user_data_interactor(form_data)
    data_password = dto.HashPasswordDTO(
        password=form_data.password,
        salt=user.salt
    )
    if not user or await hash_password_interactor(data_password) != user.hashed_password:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Email not confirmed")
    data_token_dto = dto.AccessRefreshTokenDTO(
        data={"sub": user.username}
    )
    access_token = await create_access_token_interactor(data_token_dto)
    refresh_token = await create_refresh_token_interactor(data_token_dto)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@post("/token", response_model=TokenResponse)
@inject
async def login_for_access_token(
    get_user_data_interactor: Depends[interactors.GetUserDataInteractor],
    hash_password_interactor: Depends[interactors.HashPasswordInteractor],
    create_access_token_interactor: Depends[interactors.CreateAccessTokenInteractor],
    create_refresh_token_interactor: Depends[interactors.CreateRefreshTokenInteractor],
    form_data: AuthForm = Body()
) -> dict[str, str]:
    user = await get_user_data_interactor(form_data)
    data_password = dto.HashPasswordDTO(
        password=form_data.password,
        salt=user.salt
    )
    if not user or await hash_password_interactor(data_password) != user.hashed_password:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Email not confirmed")
    data_token_dto = dto.AccessRefreshTokenDTO(
        data={"sub": user.username}
    )
    access_token = await create_access_token_interactor(data_token_dto)
    refresh_token = await create_refresh_token_interactor(data_token_dto)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
