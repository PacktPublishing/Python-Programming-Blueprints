from mock import patch

import pytest
from fakeredis import FakeStrictRedis
from nameko.containers import ServiceContainer
from nameko.testing.services import entrypoint_hook, worker_factory

from temp_messenger.dependencies.redis import RedisError
from temp_messenger.service import MessageService


@pytest.fixture
def fake_strict_redis():
    with patch('temp_messenger.dependencies.redis.StrictRedis', FakeStrictRedis) as r:
        yield r


@pytest.fixture
def config(web_config):
    return dict(
        AMQP_URI='pyamqp://guest:guest@localhost',
        REDIS_URL='redis://redis:6379/0',
        **web_config
    )


@pytest.fixture
def uuid4():
    with patch('temp_messenger.dependencies.redis.uuid4') as uuid4:
        yield uuid4


def test_gets_message(fake_strict_redis, config):
    fake_strict_redis().set('message-1', 'Test message here!')

    container = ServiceContainer(MessageService, config)
    container.start()

    with entrypoint_hook(container, 'get_message') as get_message:
        message = get_message('message-1')

    assert message == 'Test message here!'


def test_raises_error_if_message_does_not_exist(
    fake_strict_redis, config
):
    container = ServiceContainer(MessageService, config)
    container.start()

    with entrypoint_hook(container, 'get_message') as get_message:
        with pytest.raises(RedisError) as err:
            get_message('message-x')

    err.match(r'Message not found: message-x')


def test_saves_new_message(fake_strict_redis, config, uuid4):
    uuid4.return_value.hex = 'abcdef123456'
    container = ServiceContainer(MessageService, config)
    container.start()

    with entrypoint_hook(
        container, 'save_message'
    ) as save_message:
        message_id = save_message('Test message here!')

    assert message_id == 'abcdef123456'
    # Writing point:
    # When first running this, it will fail since the message is
    # in bytes. fake_strict_redis is not set up to
    # decode_responses. decode() is needed
    message = fake_strict_redis().get('abcdef123456').decode()
    assert message == 'Test message here!'
