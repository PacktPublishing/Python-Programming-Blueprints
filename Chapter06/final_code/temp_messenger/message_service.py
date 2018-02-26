from nameko.rpc import rpc
from .dependencies.messages import MessageStore


class MessageService:

    name = 'message_service'

    message_store = MessageStore()

    @rpc
    def get_message(self, message_id):
        return self.message_store.get_message(message_id)

    @rpc
    def save_message(self, email, message):
        message_id = self.message_store.save_message(
            email, message
        )
        return message_id

    @rpc
    def get_all_messages(self):
        messages = self.message_store.get_all_messages()
        sorted_messages = sort_messages_by_expiry(messages)
        return sorted_messages


def sort_messages_by_expiry(messages, reverse=False):
    return sorted(
        messages,
        key=lambda message: message['expires_in'],
        reverse=reverse
    )
