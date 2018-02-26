from nameko.rpc import rpc

from .dependencies.users import UserStore


class UserService:

    name = 'user_service'

    user_store = UserStore()

    @rpc
    def create_user(self, first_name, last_name, email, password):
        self.user_store.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
        )

    @rpc
    def authenticate_user(self, email, password):
        self.user_store.authenticate(email, password)
