from nameko.rpc import rpc, RpcProxy
from nameko.web.handlers import http

from .dependencies.redis import Redis


class MessageService:

    name = 'message_service'
    redis = Redis()

    @rpc
    def get_message(self, message_id):
        return self.redis.get_message(message_id)

    @rpc
    def save_message(self, message):
        message_id = self.redis.save_message(message)
        return message_id

    @rpc
    def get_all_messages(self):
        messages = self.redis.get_all_messages()
        return messages


class WebServer:

    name = 'web_server'
    message_service = RpcProxy('message_service')

    @http('GET', '/<message_id>')
    def root(self, request, message_id):
        return self.message_service.get_message(message_id)
