from chats.src.application.dto import SendMessageDTO
from chats.src.application.interfaces import DBSession, UUIDGenerator, SendMessage, AuthService
from chats.src.domain.entities import MessageDM

class SendMessageInteractor:
    def __init__(
        self, 
        session: DBSession, 
        uuid_generator: UUIDGenerator,
        auth: AuthService,
        gateway: SendMessage,
    ) -> None:
        self._session = session
        self._uuid_generator = uuid_generator
        self._auth = auth
        self._gateway = gateway

    async def __call__(self, dto: SendMessageDTO) -> MessageDM:
        