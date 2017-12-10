from mock import Mock, patch, call

import pytest

from temp_messenger.dependencies.redis import Redis


@pytest.fixture
def mock_strict_redis():
    with patch('temp_messenger.dependencies.redis.StrictRedis') as redis:
        yield redis


@pytest.fixture
def test_redis():
    test_redis = Redis()
    test_redis.container = Mock()
    test_redis.container.config = {'REDIS_URL': 'redis://redis/0'}

    return test_redis


def test_sets_up_redis_dependency(mock_strict_redis, test_redis):
    test_redis.setup()

    assert test_redis.redis_url == 'redis://redis/0'
    assert mock_strict_redis.from_url.call_args_list == [
        call('redis://redis/0', decode_responses=True)
    ]


def test_stop(mock_strict_redis, test_redis):
    test_redis.setup()
    test_redis.stop()

    with pytest.raises(AttributeError):
        test_redis.client


def test_get_dependency(mock_strict_redis, test_redis):
    test_redis.setup()

    worker_ctx = Mock()
    assert test_redis.get_dependency(worker_ctx) == test_redis.client
