from mock import Mock, patch

import pytest

from temp_messenger.dependencies.users import (
    CreateUserError,
    AuthenticationError,
    UserNotFound,
    UserStore,
    UserWrapper,
)


class TestUserStore:

    def test_user_store(self, test_config):
        user_store = UserStore()
        user_store.container = Mock()
        user_store.container.service_name = 'user_service'
        user_store.container.config = test_config
        user_store.setup()

        dependency = user_store.get_dependency(Mock())

        assert isinstance(dependency, UserWrapper)


class TestUserWrapper:

    @pytest.fixture
    def hash_work_factor(self):
        with patch(
            'temp_messenger.dependencies.users.HASH_WORK_FACTOR', 4
        ) as hash_work_factor:
            yield hash_work_factor

    @pytest.fixture
    def user_wrapper(self, db_session):
        return UserWrapper(db_session)

    def test_creates_user(self, user_wrapper, hashed_password):
        user_wrapper.create(
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            password='super-secret',
        )
        user = user_wrapper.get('john.doe@example.com')

        assert user.first_name == 'John'
        assert user.last_name == 'Doe'
        assert user.email == 'john.doe@example.com'
        assert user.password == b'hashed_password'

    def test_user_exists(self, user_wrapper, hashed_password):
        user_wrapper.create(
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            password='super-secret',
        )

        with pytest.raises(CreateUserError) as err:
            user_wrapper.create(
                first_name='John',
                last_name='Doe',
                email='john.doe@example.com',
                password='super-secret',
            )

        err.match('john.doe@example.com')

    def test_gets_user(self, user_wrapper, hashed_password):
        user_wrapper.create(
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            password='super-secret',
        )

        user = user_wrapper.get('john.doe@example.com')

        assert user.first_name == 'John'
        assert user.last_name == 'Doe'
        assert user.email == 'john.doe@example.com'
        assert user.password == b'hashed_password'

    def test_user_not_found(self, user_wrapper):
        with pytest.raises(UserNotFound) as err:
            user_wrapper.get('i_dont_exist@example.com')

        err.match('i_dont_exist@example.com')

    def test_authenticates_valid_password(
        self, user_wrapper, hash_work_factor
    ):
        user_wrapper.create(
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            password='super-secret',
        )

        user = user_wrapper.authenticate(
            'john.doe@example.com', 'super-secret'
        )

        assert user.first_name == 'John'
        assert user.last_name == 'Doe'
        assert user.email == 'john.doe@example.com'

    def test_invalid_password(self, user_wrapper, hash_work_factor):
        user_wrapper.create(
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            password='super-secret',
        )

        with pytest.raises(AuthenticationError) as err:
            user_wrapper.authenticate(
                'john.doe@example.com', 'wrong-password'
            )

        err.match(r'Incorrect password for john.doe@example.com')

    def test_authenticate_non_existing_user(self, user_wrapper):
        with pytest.raises(UserNotFound) as err:
            user_wrapper.authenticate(
                'i_dont_exist@example.com', 'wrong-password'
            )

        err.match('i_dont_exist@example.com')
