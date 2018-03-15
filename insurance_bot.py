from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response
from root import insurance
from os import environ as env
import json

client = insurance.Client()


def get_phone_brands(request):
    phone_brands = client.gadgets.list_phone_brands()
    phone_brands = {brand: brand for brand in phone_brands}
    return Response(body=json.dumps(phone_brands))


def hello_world(request):
    return Response('hello world!')

if __name__ == '__main__':
    with Configurator() as config:
        config.add_route('phone_brands', '/phone_brands')
        config.add_view(get_phone_brands, route_name='phone_brands')

        config.add_route('hello_world', '/')
        config.add_view(hello_world, route_name='hello_world')

        app = config.make_wsgi_app()
    port = int(env.get('PORT'))
    server = make_server('0.0.0.0', (port if port else 8080), app)
    print('Server Started')
    server.serve_forever()
