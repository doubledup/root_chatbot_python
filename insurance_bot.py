from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response
from root import insurance
from os import environ as env
import json

client = insurance.Client()

policy_holder = {
            "id":            {"number": "6801015800084", "type": "id", "country": "ZA"},
            "first_name":    "John",
            "last_name":     "Smith",
            "date_of_birth": "19950101",
            "email":         "john.smith@root.co.za",
            "cellphone":     {"country": "ZA", "number": "0718822882"}
}

application = {
            "quote_package_id": "2c9a2297-5532-4f35-bbd1-48762934602f",
            "monthly_premium":  12340,
            "serial_number":    "1234567789"
}


def get_phone_brands(request):
    phone_brands = client.gadgets.list_phone_brands()
    return response_object(' '.join(phone_brands))


def response_object(speech, context=[]):
    resp = {
        "speech": speech,
        "displayText": "This text probably won't appear anywhere",
        "context": context
    }
    return Response(body=json.dumps(resp))


def get_quote(request):
    # create quote
    model_name = request.json_body.get('result', {})[0].get('parameters', {}).get('model_name')
    quotes = client.quotes.create({"type": "root_gadgets", "model_name": model_name})
    quote_ids = [{"quote_id": quote.get("quote_package_id")} for quote in quotes]

    quote_vars = [{"name": quote.get("package_name"), "premium": quote.get("suggested_premium")/100} for quote in quotes]
    result_string = "You have a couple of options:\n %s" \
                    % "\n".join(["%(name)s: R%(premium)s" % data for data in quote_vars])

    return response_object(result_string, quote_ids)


def create_policy(request):

    quote_ids = request.json_body.get('contexts', [])[0].get('parameters', [])

    # create polocy holder
    policyholder = client.policyholders.create(policy_holder.get("id"), policy_holder.get("first_name"),
                                               policy_holder.get("last_name"), policy_holder.get("email"),
                                               policy_holder.get("date_of_birth"), policy_holder.get("cellphone"))

    # create application
    result = client.applications.create(policyholder.get("policyholder_id"), quote_id,
                                        application.get("monthly_premium"), application.get("serial_number"))

    # issue policy
    issued_policy = client.policies.issue(result.get("application_id"))

    print(issued_policy)
    result_string = issued_policy.get("status")
    return response_object(result_string)


def compute_base_request(request):
    if 'application/json' in request.headers["Content-Type"]:
        intent = request.json_body.get('result', {}).get('metadata', {}).get('intentName')
        if intent == 'phone_brand':
            return get_phone_brands(request)
        elif intent == 'create_policy':
            return create_policy(request)
        elif intent == 'get_quote':
            return get_quote(request)
        else:
            return response_object('No intent given')
    return response_object('No body present')

if __name__ == '__main__':
    with Configurator() as config:
        config.add_route('base_request', '/')
        config.add_view(compute_base_request, route_name='base_request')

        app = config.make_wsgi_app()
    port = env.get('PORT')
    port = int(port) if port else False
    server = make_server('0.0.0.0', (port if port else 8080), app)
    print('Server Started')
    server.serve_forever()
