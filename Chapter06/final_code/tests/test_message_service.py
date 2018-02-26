from mock import patch
from time import sleep

import pytest
from nameko.testing.services import entrypoint_hook

from temp_messenger.dependencies.messages import MessageError
from temp_messenger.message_service import sort_messages_by_expiry


@pytest.fixture
def message_lifetime():
    with patch(
        'temp_messenger.dependencies.messages.MESSAGE_LIFETIME',
        100
    ) as lifetime:
        yield lifetime


def test_gets_message(message_svc, fake_strict_redis):
    fake_strict_redis().hmset(
        'message-1', {
            'email': 'foo@example.com',
            'message': 'Test message here!',
        }
    )

    with entrypoint_hook(message_svc, 'get_message') as get_message:
        message = get_message('message-1')

    assert message == 'Test message here!'


def test_raises_error_if_message_does_not_exist(
    message_svc, fake_strict_redis
):
    with entrypoint_hook(message_svc, 'get_message') as get_message:
        with pytest.raises(MessageError) as err:
            get_message('message-x')

    err.match(r'Message not found: message-x')


def test_saves_new_message(message_svc, fake_strict_redis, uuid4):
    uuid4.return_value.hex = 'abcdef123456'

    with entrypoint_hook(message_svc, 'save_message') as save_message:
        message_id = save_message('a@b.com', 'Test message here!')

    assert message_id == 'abcdef123456'
    # Writing point:
    # When first running this, it will fail since the message is
    # in bytes. fake_strict_redis is not set up to
    # decode_responses. decode() is needed
    message = fake_strict_redis().hgetall('abcdef123456')
    assert message == {
        b'email': b'a@b.com',
        b'message': b'Test message here!',
    }


def test_gets_all_messages(message_svc, fake_strict_redis):
    fake_strict_redis().hmset(
        'message-1', {'message': 'Hello', 'email': 'a@b.com'}
    )
    fake_strict_redis().hmset(
        'abcdef123456', {'message': 'Howdy', 'email': 'b@a.com'}
    )
    fake_strict_redis().hmset(
        'xyz789', {'message': 'I Love Python', 'email': 'a@b.com'}
    )
    fake_strict_redis().hmset(
        'aaaabbbb', {'message': 'So do I!', 'email': 'b@a.com'}
    )

    with entrypoint_hook(
        message_svc, 'get_all_messages'
    ) as get_all_messages:
        messages = get_all_messages()

    assert messages == [
        {
            'id': 'message-1',
            'email': 'a@b.com',
            'message': 'Hello',
            'expires_in': -1
        },
        {
            'id': 'abcdef123456',
            'email': 'b@a.com',
            'message': 'Howdy',
            'expires_in': -1,
        },
        {
            'id': 'xyz789',
            'email': 'a@b.com',
            'message': 'I Love Python',
            'expires_in': -1
        },
        {
            'id': 'aaaabbbb',
            'email': 'b@a.com',
            'message': 'So do I!',
            'expires_in': -1
        },
    ]


def test_returns_empty_list_if_no_messages(message_svc):
    # Writing point:
    # This test will fail at first since redis is not cleared
    # after each test. Explain the tear down
    with entrypoint_hook(
        message_svc, 'get_all_messages'
    ) as get_all_messages:
        messages = get_all_messages()

    assert messages == []


def test_save_message_expiry(
    message_svc, fake_strict_redis, uuid4, message_lifetime
):
    uuid4.return_value.hex = 'abcdef123456'

    with entrypoint_hook(
        message_svc, 'save_message'
    ) as save_message:
        save_message('foo@example.com', 'Test message here!')

    message = fake_strict_redis().hgetall('abcdef123456')
    assert message == {
        b'email': b'foo@example.com',
        b'message': b'Test message here!',
    }

    sleep(0.1)

    message = fake_strict_redis().get('abcdef123456')
    assert message is None


def test_sort_message_by_expiry():
    messages = [
        {'message': 'So do I!', 'expires_in': 4},
        {'message': 'Hello', 'expires_in': 1},
        {'message': 'I Love Python', 'expires_in': 3},
        {'message': 'Howdy', 'expires_in': 2},
    ]

    sorted_messages = sort_messages_by_expiry(messages)

    assert sorted_messages == [
        {'message': 'Hello', 'expires_in': 1},
        {'message': 'Howdy', 'expires_in': 2},
        {'message': 'I Love Python', 'expires_in': 3},
        {'message': 'So do I!', 'expires_in': 4},
    ]


def test_sort_message_by_expiry_reversed():
    messages = [
        {'message': 'So do I!', 'expires_in': 4},
        {'message': 'Hello', 'expires_in': 1},
        {'message': 'I Love Python', 'expires_in': 3},
        {'message': 'Howdy', 'expires_in': 2},
    ]

    sorted_messages = sort_messages_by_expiry(
        messages, reverse=True
    )

    assert sorted_messages == [
        {'message': 'So do I!', 'expires_in': 4},
        {'message': 'I Love Python', 'expires_in': 3},
        {'message': 'Howdy', 'expires_in': 2},
        {'message': 'Hello', 'expires_in': 1},
    ]
