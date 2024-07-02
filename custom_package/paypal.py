import json

DETAILS = """{
  "detail": {
    "invoice_number": "{invoice_number}",
    "reference": "deal-ref",
    "invoice_date": "2018-11-12",
    "currency_code": "{currency_code}",
    "note": "Thank you for your business.",
    "term": "No refunds after 30 days.",
    "memo": "This is a long contract",
    "payment_term": {
      "term_type": "NET_10",
      "due_date": "2018-11-22"
    }
  },
  "invoicer": {
    "name": {
      "given_name": "Unfold",
      "surname": "Agile Loop"
    },
    "address": {
      "address_line_1": "1234 First Street",
      "address_line_2": "337673 Hillside Court",
      "admin_area_2": "Anytown",
      "admin_area_1": "CA",
      "postal_code": "98765",
      "country_code": "US"
    },
    "email_address": "unfold@agileloop.com",
    "phones": [
      {
        "country_code": "001",
        "national_number": "4085551234",
        "phone_type": "MOBILE"
      }
    ],
    "website": "https://agileloop.ai/",
    "tax_id": "ABcNkWSfb5ICTt73nD3QON1fnnpgNKBy- Jb5SeuGj185MNNw6g",
    "logo_url": "https://mintlify.s3-us-west-1.amazonaws.com/agileloop/logo/light.svg",
    "additional_notes": "2-4"
  },
  "primary_recipients": [
    {
      "billing_info": {
        "name": {
          "given_name": "{recipient_firstname}",
          "surname": "{recipient_surname}"
        },
        "address": {
          "address_line_1": "1234 Main Street",
          "admin_area_2": "Anytown",
          "admin_area_1": "CA",
          "postal_code": "98765",
          "country_code": "US"
        },
        "email_address": "{recipient_email_address}",
        "phones": [
          {
            "country_code": "001",
            "national_number": "4884551234",
            "phone_type": "HOME"
          }
        ],
        "additional_info_value": "add-info"
      },
      "shipping_info": {
        "name": {
          "given_name": "{recipient_firstname}",
          "surname": "{recipient_surname}"
        },
        "address": {
          "address_line_1": "1234 Main Street",
          "admin_area_2": "Anytown",
          "admin_area_1": "CA",
          "postal_code": "98765",
          "country_code": "US"
        }
      }
    }
  ],
  "items": [
    {
      "name": "{item_name}",
      "description": "...",
      "quantity": "{item_quantity}",
      "unit_amount": {
        "currency_code": "{currency_code}",
        "value": "{item_unit_amount}"
      },
      "tax": {
        "name": "Sales Tax",
        "percent": "7.25"
      },
      "discount": {
        "percent": "5"
      },
      "unit_of_measure": "QUANTITY"
    }
  ],
  "amount": {
    "breakdown": {
      "custom": {
        "label": "Packing Charges",
        "amount": {
          "currency_code": "{currency_code}",
          "value": "10.00"
        }
      },
      "shipping": {
        "amount": {
          "currency_code": "{currency_code}",
          "value": "10.00"
        },
        "tax": {
          "name": "Sales Tax",
          "percent": "7.25"
        }
      },
      "discount": {
        "invoice_discount": {
          "percent": "5"
        }
      }
    }
  }
}"""

# data = {
#     "invoice_number": "Invoice-12345",
#     "recipient_email_address": "bill-me@example.com",
#     "recipient_firstname": "Stephanie",
#     "recipient_surname": "Meyers",
#     "currency_code": "USD",
#     "item_name": "Mug",
#     "item_quantity": "3",
#     "item_unit_amount": "9.9",
# }


def paypal_add_required_fields_to_default_draft_invoice(data: dict) -> dict:
    details = DETAILS
    for key in data.keys():
        details = details.replace("{" + key + "}", str(data[key]))

    return details  # json.loads(details)
