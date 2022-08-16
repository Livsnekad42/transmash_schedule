from typing import Dict, Union
import asyncio
import ssl
from datetime import datetime

from django.conf import settings

from zeep import Settings, AsyncClient, Client
from zeep.transports import AsyncTransport, Transport
import httpx
import requests


DATE_FORMAT = "%d.%M.%Y %H:%M:%S"

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
ctx.options ^= ssl.OP_NO_TLSv1_1

LoanTypes = Union["loan", "credit"]


async def astart_transaction(data: Dict[str, Union[int, str]], loan_types: LoanTypes = "loan") \
        -> Dict[str, Union[int, str]]:

    if loan_types == "loan":
        endpoint = settings.PAYMENT_PROCESSING_LOAN

    else:
        #TODO: endpoint = settings.PAYMENT_PROCESSING_CREDIT
        raise Exception("Not fount endpoint from type loans")

    today = datetime.today()

    transaction = {
        "merchantId": settings.MID,
        "currencyCode": "398",
        "languageCode": "ru",
        "terminalId": "",
        "merchantLocalDateTime": today.strftime(DATE_FORMAT),
        "orderId": data['orderId'],
        "totalAmount": int(data['amount'] * 100),
        "customerReference": data['customerReference'],
        "returnURL": data["returnURL"],
    }

    async with httpx.AsyncClient(verify=False) as client:
        transport = AsyncTransport(client=client)
        client = AsyncClient(endpoint, transport=transport)
        client.service._binding_options['address'] = endpoint
        return await client.service.startTransaction(transaction)


async def astatus_transaction(customer_ref: Union[int, str], loan_types: LoanTypes = "loan") -> \
        Dict[str, Union[int, str]]:

    if loan_types == "loan":
        endpoint = settings.PAYMENT_PROCESSING_LOAN

    else:
        # TODO: endpoint = settings.PAYMENT_PROCESSING_CREDIT
        raise Exception("Not fount endpoint from type loans")

    data = {
        "merchantId": settings.MID,
        "referenceNr": customer_ref,
    }

    async with httpx.AsyncClient(verify=False) as client:
        transport = AsyncTransport(client=client)
        client = AsyncClient(endpoint, transport=transport)
        client.service._binding_options['address'] = endpoint
        response_processing = await client.service.getTransactionStatusCode(**data)
        return response_processing


def start_transaction(data: Dict[str, Union[int, str]], endpoint: str) -> Dict[str, Union[int, str]]:
    today = datetime.today()

    transaction = {
        "merchantId": settings.MID,
        "currencyCode": "398",
        "languageCode": "ru",
        "terminalId": "",
        "merchantLocalDateTime": today.strftime(DATE_FORMAT),
        "orderId": data['order'],
        "totalAmount": int(data['amount'] * 100),
        "customerReference":  data['customerReference'],
    }

    headers = {}
    proxy = {'proxy': 'https://payment.processinggmbh.ch/CNPMerchantWebServices/services/CNPMerchantWebService3'}

    session = requests.Session()
    session.verify = False
    session.stream = True

    transport = Transport(session=session)
    client = Client(endpoint, transport=transport)
    return client.service.startTransaction({"transaction": transaction})


# tests
def test():
    test_processing = "https://test.processing.kz/CNPMerchantWebServices/services/CNPMerchantWebService?wsdl"

    data = {
        "order": "17004907",
        "newPeriod": 30,
        "amount": 100,
    }

    resp = start_transaction(data, test_processing)
    return resp


def atest():
    test_processing = "https://payment.processinggmbh.ch/CNPMerchantWebServices/services/CNPMerchantWebService?wsdl"

    data = {
        "order": "17004907",
        "newPeriod": 30,
        "amount": 100,
    }

    resp = asyncio.run(astart_transaction(data))
    return resp


