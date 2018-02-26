from mock import Mock, patch, call

import pytest

from temp_messenger.dependencies.messages import MessageStore


@pytest.fixture
def mock_strict_redis():
    with patch(
        'temp_messenger.dependencies.messages.StrictRedis'
    ) as redis:
        yield redis


@pytest.fixture
def test_message_store():
    test_message_store = MessageStore()
    test_message_store.container = Mock()
    test_message_store.container.config = {
        'REDIS_URL': 'redis://redis/0'
    }

    return test_message_store


def test_sets_up_redis_dependency(
    mock_strict_redis, test_message_store
):
    test_message_store.setup()

    assert test_message_store.redis_url == 'redis://redis/0'
    assert mock_strict_redis.from_url.call_args_list == [
        call(
            'redis://redis/0',
            decode_responses=True,
            charset='utf-8'
        )
    ]


def test_stop(mock_strict_redis, test_message_store):
    test_message_store.setup()
    test_message_store.stop()

    with pytest.raises(AttributeError):
        test_message_store.client


def test_get_dependency(mock_strict_redis, test_message_store):
    test_message_store.setup()

    worker_ctx = Mock()
    assert test_message_store.get_dependency(
        worker_ctx
    ) == test_message_store.client
