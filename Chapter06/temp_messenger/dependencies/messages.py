from uuid import uuid4

from nameko.extensions import DependencyProvider
from redis import StrictRedis


MESSAGE_LIFETIME = 10000


class MessageError(Exception):
    pass


class MessageStore(DependencyProvider):

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
            url, decode_responses=True, charset='utf-8'
        )

    def get_message(self, message_id):
        message = self.redis.hget(message_id, 'message')

        if message is None:
            raise MessageError(
                'Message not found: {}'.format(message_id)
            )

        return message

    def save_message(self, email, message):
        message_id = uuid4().hex
        payload = {
            'email': email,
            'message': message,
        }
        self.redis.hmset(message_id, payload)
        self.redis.pexpire(message_id, MESSAGE_LIFETIME)

        return message_id

    # def get_all_messages(self):
    #     message_ids = self.redis.keys()
    #     messages = []

    #     for message_id in message_ids:
    #         message = self.redis.get(message_id)
    #         messages.append(
    #             {
    #                 'id': message_id,
    #                 'message': self.redis.get(message_id),
    #                 'expires_in': self.redis.pttl(message_id),
    #             }
    #         )

    #     return messages

    def get_all_messages(self):
        return [
            {
                'id': message_id,
                'email': self.redis.hget(message_id, 'email'),
                'message': self.redis.hget(message_id, 'message'),
                'expires_in': self.redis.pttl(message_id),
            }
            for message_id in self.redis.keys()
        ]
