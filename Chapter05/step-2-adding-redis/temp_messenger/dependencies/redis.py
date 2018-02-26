from nameko.extensions import DependencyProvider
from redis import StrictRedis


class Redis(DependencyProvider):

    def setup(self):
        self.redis_url = self.container.config['REDIS_URL']
        self.client = RedisClient(self.redis_url)

    def stop(self):
        del self.client

    def get_dependency(self, worker_ctx):
        return self.client


class RedisClient:

    def __init__(self, url):
        self.redis = StrictRedis.from_url(
            url, decode_responses=True
        )

    def get_message(self, message_id):
        message = self.redis.get(message_id)

        if message is None:
            raise RedisError(
                'Message not found: {}'.format(message_id)
            )

        return message


class RedisError(Exception):
    pass
