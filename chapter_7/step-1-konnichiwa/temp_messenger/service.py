from nameko.rpc import rpc, RpcProxy
from nameko.web.handlers import http


class KonnichiwaService:

    name = 'konnichiwa_service'

    @rpc
    def konnichiwa(self):
        return 'Konnichiwa!'


class WebServer:

    name = 'web_server'
    konnichiwa_service = RpcProxy('konnichiwa_service')

    @http('GET', '/')
    def root(self, request):
        return self.konnichiwa_service.konnichiwa()
