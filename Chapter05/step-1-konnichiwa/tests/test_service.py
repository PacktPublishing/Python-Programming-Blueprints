from nameko.testing.services import worker_factory

from temp_messenger.service import KonnichiwaService, WebServer


def test_konnichiwa():
    service = worker_factory(KonnichiwaService)

    result = service.konnichiwa()

    assert result == 'Konnichiwa!'


def test_root_http(web_session, web_config, container_factory):
    web_config['AMQP_URI'] = 'pyamqp://guest:guest@localhost'
    web_server = container_factory(WebServer, web_config)
    konnichiwa = container_factory(KonnichiwaService, web_config)
    web_server.start()
    konnichiwa.start()

    result = web_session.get('/')

    assert result.text == 'Konnichiwa!'
