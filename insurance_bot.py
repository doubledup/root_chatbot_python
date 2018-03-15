from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response
from root import insurance
from os import environ as env
import json

client = insurance.Client()


def get_phone_brands(request):
    phone_brands = client.gadgets.list_phone_brands()
    return response_object(' '.join(phone_brands))


def response_object(speech):
    resp = {
        "speech": speech,
        "displayText": "This text probably won't appear anywhere",
    }
    return Response(body=json.dumps(resp))


def check_phone_brand(request):
    phone_brands = client.gadgets.list_phone_brands()
    return response_object(' '.join(phone_brands))


def compute_base_request(request):
    print(request.json_body.get('result').get('metadata').get('intentName'))
    intent = request.json_body.get('result', {}).get('metadata', {}).get('intentName')
    if intent == 'phone_brand':
        get_phone_brands(request)
    else:
        response_object('No intent given')

if __name__ == '__main__':
    with Configurator() as config:
        config.add_route('phone_brands', '/phone_brands')
        config.add_view(get_phone_brands, route_name='phone_brands')

        config.add_route('base_request', '/')
        config.add_view(compute_base_request, route_name='base_request')

        app = config.make_wsgi_app()
    port = env.get('PORT')
    port = int(port) if port else False
    server = make_server('0.0.0.0', (port if port else 8080), app)
    print('Server Started')
    server.serve_forever()
