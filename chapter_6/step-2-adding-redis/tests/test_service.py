from mock import patch

import pytest
from fakeredis import FakeStrictRedis
from nameko.containers import ServiceContainer
from nameko.testing.services import entrypoint_hook, worker_factory

from temp_messenger.dependencies.redis import RedisError
from temp_messenger.service import MessageService, WebServer


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


def test_konnichiwa():
    service = worker_factory(MessageService)

    result = service.konnichiwa()

    assert result == 'Konnichiwa!'


def test_get_message_http(
    web_session, config, container_factory, fake_strict_redis
):
    fake_strict_redis().set('message-1', 'Test message here!')
    message_svc = container_factory(MessageService, config)
    web_server = container_factory(WebServer, config)
    message_svc.start()
    web_server.start()

    result = web_session.get('/message-1')

    assert result.text == 'Test message here!'


def test_gets_message(fake_strict_redis, config):
    fake_strict_redis().set('message-1', 'Test message here!')
    fake_strict_redis().set('message-2', '(╯°□°）╯︵ ┻━┻)')

    container = ServiceContainer(MessageService, config)
    container.start()

    with entrypoint_hook(container, 'get_message') as get_message:
        message_1 = get_message('message-1')
        message_2 = get_message('message-2')

    assert message_1 == 'Test message here!'
    assert message_2 == '(╯°□°）╯︵ ┻━┻)'


def test_raises_error_if_message_does_not_exist(
    fake_strict_redis, config
):
    container = ServiceContainer(MessageService, config)
    container.start()

    with entrypoint_hook(container, 'get_message') as get_message:
        with pytest.raises(RedisError) as err:
            get_message('message-x')

    err.match(r'Message not found: message-x')
