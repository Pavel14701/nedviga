from mail.src.application.interfaces import GetTemplates
from mail.src.config import AppConfig

class TemplatesGateway(GetTemplates):
    def __init__(self, config: AppConfig):
        self._config = config

    def registration_template(self, uuid: str) -> str:
        return  """
        <html>
            <body>
                <h1>Добро пожаловать!</h1>
                <p>Спасибо за регистрацию в нашем сервисе. Для подтверждения аккаунта, \
                    пожалуйста, перейдите по ссылке ниже:</p>
                <a href="{path}/{uuid}">Подтвердить аккаунт</a>
                <p>Если ссылка не работает, скопируйте и вставьте её в браузер:</p>
                <p>{path}{uuid}</p>
                <br>
                <p>С наилучшими пожеланиями,</p>
                <p>Команда поддержки</p>
            </body>
        </html>
        """.format(
            path=self._config.confirm_path,
            uuid=uuid
        )