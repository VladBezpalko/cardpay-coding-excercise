import logging
from decimal import Decimal
from operator import itemgetter
from typing import Optional

import requests

from django.conf import settings

from payments.gateways.base import BaseGateway, GatewayError, SaleResult


logger = logging.getLogger(__name__)


class BraintreeGateway(BaseGateway):
    """
    Integration with Braintree GraphQL API.
    """
    API_REQUEST_TIMEOUT = 25
    API_VERSION = '2020-05-24'

    def tokenize_card(self, card_number: str, expiry_date: str) -> str:
        exp_month, exp_year = expiry_date.split('/')
        query = """
        mutation tokenizeCreditCard($input: TokenizeCreditCardInput!) {
          tokenizeCreditCard(input: $input) {paymentMethod {id}}
        }
        """
        input_data = {
            'creditCard': {
                'number': card_number,
                'expirationMonth': exp_month,
                'expirationYear': exp_year,
            },
        }

        response_data = self._perform_query(query, {'input': input_data})
        query_result = self._extract_query_result(
            response_data, 'tokenizeCreditCard',
        )

        try:
            token = query_result['paymentMethod']['id']
        except (KeyError, TypeError):
            raise GatewayError('Braintree misbehavior: data is missing')

        return token

    def sale_by_token(self, token: str,
                      transaction_amount: Decimal) -> SaleResult:
        query = """
        mutation chargePaymentMethod($input: ChargePaymentMethodInput!) {
          chargePaymentMethod(input: $input) {
            transaction {
              id
              amount { value currencyIsoCode }
              status
            }
          }
        }
        """
        input_data = {
            'paymentMethodId': token,
            'transaction': {'amount': str(transaction_amount)},
        }

        response_data = self._perform_query(query, {'input': input_data})
        query_result = self._extract_query_result(
            response_data, 'chargePaymentMethod',
        )

        try:
            transaction = query_result['transaction']
        except KeyError:
            raise GatewayError('Braintree misbehavior: data is missing')

        return SaleResult(transaction.get('id'), transaction.get('status'))

    def _perform_query(self, query: str, variables: dict) -> dict:
        """
        Holds logic of performing requests to Braintree GraphQL API.
        :param query: GraphQL query
        :param variables: variables for GraphQL query
        :raise GatewayError: if any issue during processing of request occurred
        :return: response json parsed as dict
        """
        url = settings.BRAINTREE_API_URL
        try:
            response = requests.post(
                url, json={'query': query, 'variables': variables},
                headers=self._prepare_headers(),
                timeout=self.API_REQUEST_TIMEOUT,
            )
        except (requests.ConnectionError, requests.Timeout):
            log_msg = 'Connection issues for request to Braintree API'
            self._log_request(logging.ERROR, log_msg, url=url)
            raise GatewayError('Connection issues')

        try:
            response_data = response.json()
        except ValueError:
            log_msg = 'Could not extract json data from Braintree response'
            self._log_request(logging.ERROR, log_msg, response)
            raise GatewayError('Unexpected data format')

        if {'data', 'errors'} & response_data.keys():
            # if any of these keys included in response body
            request_id = response_data.get('extensions', {}).get('requestId')
            self._log_request(
                logging.INFO, 'Request to Braintree executed', response,
                request_id=request_id,
            )
        else:
            log_msg = 'Response form Braintree missing informative keys'
            self._log_request(logging.ERROR, log_msg, response)
            raise GatewayError('Braintree misbehavior')

        return response_data

    def _prepare_headers(self) -> dict:
        return {
            'Authorization': f'Basic {settings.BRAINTREE_API_KEY}',
            'Braintree-Version': self.API_VERSION,
        }

    def _extract_query_result(self, resp_data: dict, query_name: str) -> dict:
        """
        Defining common logic for extracting query/mutation result data
        from response.
        Ensuring extra safety from Braintree misbehavior (missing keys)
        with `get`.
        Should be revisited in case of introducing requests with more
        than one query/mutation.
        :raise GatewayError: if there's no data for query_name, but errors
        :return: query result extracted from response data
        """
        query_result = resp_data.get('data', {}).get(query_name)
        if not query_result:
            msg = ' '.join(map(itemgetter('message'), resp_data['errors']))
            raise GatewayError(msg)

        return query_result

    def _log_request(
            self, level: int, message: str,
            response: Optional[requests.Response] = None,
            **kwargs) -> None:
        """
        Shortcut to log communication with API that gather extra data from
        response/request objects.
        :param level: level constant from `logging` module
        :param message: text for log
        :param response: object that represents response
        :param kwargs: additional keys that will be passed to log extra
        """
        if response is not None:
            request = response.request
            extra = {
                'url': request.url,
                'status_code': response.status_code,
            }
            extra.update(kwargs)
        else:
            extra = kwargs

        logger.log(level, message, extra=extra)
