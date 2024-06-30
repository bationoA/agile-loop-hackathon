import base64
import json

import requests

from custom_package import get_trello_board_identifier_prompt, include_board_id_in_query
from custom_package.paypal import paypal_add_required_fields_to_default_draft_invoice


#
# def generate_access_token() -> str:
#     # Replace these with your actual client ID and secret
#     client_id = 'AbMsGGszl86i-5a6Rn434Ws2YM-z-A3_3D3zPZ_IhdNqkIpFAqaqyH8I_QvpjDV-At0FrXwjCs_72DEF'
#     client_secret = 'EAdATSveoNBnULMgXVOopDESvm0-RRLv4F9cryoW3X4UO_02Wu_TQ0y4CvmL1VIuJ8XepVDHiOOLfiIf'
#
#     # Encode the client ID and secret in Base64
#     credentials = f"{client_id}:{client_secret}"
#     encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
#
#     # Define the headers and data for the request
#     headers = {
#         "Authorization": f"Basic {encoded_credentials}",
#         "Content-Type": "application/x-www-form-urlencoded"
#     }
#
#     data = {
#         "grant_type": "client_credentials"
#     }
#
#     # Make the POST request
#     response = requests.post(
#         "https://api-m.sandbox.paypal.com/v1/oauth2/token",
#         headers=headers,
#         data=data
#     )
#
#     response_json = response.json()
#
#     print(f"response_json: {response_json}")
#
#     return response_json["access_token"]
#
#
# def create_draft_invoice(data: dict, encoded_credentials: str):
#     # Define the headers and data for the request
#     headers = {
#         "Authorization": f"Bearer {encoded_credentials}",
#         "Content-Type": "application/json",
#         "Prefer": "return=representation"
#     }
#
#     data = paypal_add_required_fields_to_default_draft_invoice(data=data)
#
#     # Make the POST request
#     response = requests.post(
#         "https://api-m.paypal.com/v2/invoicing/invoices",
#         headers=headers,
#         data=data
#     )
#
#     return response


def main():
    # prompt = get_trello_board_identifier_prompt()
    #
    # print(f"get_trello_board_identifier_prompt: {prompt}")
    #
    # while 1:
    #     query = input("Enter query: ")
    #     new_query = include_board_id_in_query(query)
    #
    #     print(f"new_query: {new_query}")

    workspace_id = "667eeaee004df9127d441c4c"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        'x-api-key': 'ZmMwNTRiOWEtNTA2YS00NzRlLThmZmQtYWJjOWRlYjdhY2Rj',
    }

    body = {
        "address": "Ground Floor, ABC Bldg., Palo Alto, California, USA 94020",
        "email": "amosb.dev1@gmail.com",
        "name": "Client X1"
    }
    url = "https://api.clockify.me/api/v1/workspaces/{}/clients"
    try:
        response = requests.post(url=url.format(workspace_id), headers=headers, data=json.dumps(body))

        print(f"response.status: {response.status_code}")
        print(f"response.reason: {response.reason}")
        print(f"response.json: {response.json()}")
    except BaseException as e:
        print(f"ERROR: {str(e)}")


print(main())
