from mock import patch

import pytest
from fakeredis import FakeStrictRedis
from nameko.containers import ServiceContainer

from temp_messenger.dependencies.users import Base
from temp_messenger.message_service import MessageService
from temp_messenger.user_service import UserService


TEST_DB_URI = (
    'postgresql+psycopg2://postgres:secret@localhost:'
    '5433/users?client_encoding=utf8'
)


@pytest.fixture()
def hashed_password():
    with patch(
        'temp_messenger.dependencies.users.bcrypt.hashpw'
    ) as hashpw:
        hashpw.return_value = b'hashed_password'
        yield hashpw


@pytest.fixture
def test_config(web_config):
    config = {
        'AMQP_URI': 'pyamqp://guest:guest@localhost',
        'REDIS_URL': 'redis://redis:6379/0',
        'DB_URIS': {
            "user_service:Base": TEST_DB_URI
        }
    }
    config.update(**web_config)
    return config


@pytest.fixture
def fake_strict_redis():
    with patch(
        'temp_messenger.dependencies.messages.StrictRedis',
        FakeStrictRedis
    ) as fake_strict_redis:
        yield fake_strict_redis
        fake_strict_redis().flushall()


@pytest.fixture
def message_svc(test_config, fake_strict_redis):
    message_svc = ServiceContainer(MessageService, test_config)
    message_svc.start()

    return message_svc


@pytest.fixture
def user_svc(test_config):
    user_service = ServiceContainer(UserService, test_config)
    user_service.start()

    return user_service


@pytest.fixture(scope='session')
def db_url():
    return TEST_DB_URI


@pytest.fixture(scope='session')
def model_base():
    return Base


@pytest.fixture(scope='session')
def db_engine_options():
    return dict(
        client_encoding='utf8',
        connect_args={'client_encoding': 'utf8'}
    )


@pytest.fixture
def uuid4():
    with patch(
        'temp_messenger.dependencies.messages.uuid4'
    ) as uuid4:
        yield uuid4
