from mock import Mock, patch, call

import pytest

from temp_messenger.dependencies.redis import MessageStore


@pytest.fixture
def mock_strict_redis():
    with patch('temp_messenger.dependencies.redis.StrictRedis') as redis:
        yield redis


@pytest.fixture
def message_store():
    message_store = MessageStore()
    message_store.container = Mock()
    message_store.container.config = {'REDIS_URL': 'redis://redis/0'}

    return message_store


def test_sets_up_redis_dependency(mock_strict_redis, message_store):
    message_store.setup()

    assert mock_strict_redis.from_url.call_args_list == [
        call('redis://redis/0', decode_responses=True, charset='utf-8')
    ]


def test_stop(mock_strict_redis, message_store):
    message_store.setup()
    message_store.stop()

    with pytest.raises(AttributeError):
        message_store.client


def test_get_dependency(mock_strict_redis, message_store):
    message_store.setup()

    worker_ctx = Mock()
    assert message_store.get_dependency(worker_ctx) == message_store.client
