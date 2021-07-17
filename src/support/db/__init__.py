from .users import users
from .chats import chats
from .recipes import recipes
from .audios import audios
from .reactions import reactions

from .base import metadata, engine

metadata.create_all(bind=engine)


from support.models.user import User
from support.repositories.users import UserRepository

class User_db(User, UserRepository):
    pass


class Chat_db():
    pass