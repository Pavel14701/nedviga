from dishka.integrations.base import FromDishka as Depends
from faststream.rabbit import RabbitRouter

from book_club.application.dto import NewBookDTO
from book_club.application.interactors import NewBookInteractor
from book_club.controllers.schemas import BookSchema

RabbitController = RabbitRouter()
