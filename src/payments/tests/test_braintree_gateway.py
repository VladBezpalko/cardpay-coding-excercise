from decimal import Decimal

import requests
import pytest

from payments.gateways.base import GatewayError
from payments.gateways.braintree import BraintreeGateway


@pytest.fixture
def requests_post_mock(mocker):
    return mocker.patch('payments.gateways.braintree.requests.post')


def test_tokenize_card_success(requests_post_mock, make_random_str):
    token = make_random_str()
    card_number = make_random_str(digits=True)
    requests_post_mock.return_value.json.return_value = {
        'data': {
            'tokenizeCreditCard': {
                'paymentMethod': {'id': token},
            },
        },
    }

    result = BraintreeGateway().tokenize_card(card_number, '12/2020')

    assert requests_post_mock.called
    variables = requests_post_mock.call_args[1]['json']['variables']['input']
    cc_variable = variables['creditCard']
    assert cc_variable['number'] == card_number
    assert cc_variable['expirationMonth'] == '12'
    assert cc_variable['expirationYear'] == '2020'
    assert result == token


def test_tokenize_card_braintree_errors(requests_post_mock, make_random_str):
    requests_post_mock.return_value.json.return_value = {
        'data': {'tokenizeCreditCard': None},
        'errors': [{'message': 'Something bad happened'}],
    }

    with pytest.raises(GatewayError, match='Something bad happened'):
        BraintreeGateway().tokenize_card(make_random_str(digits=True), '12/2020')


def test_sale_by_token_success(mocker, make_random_str):
    token = make_random_str()
    transaction_id = make_random_str()
    transaction_status = make_random_str()
    requests_mock = mocker.patch('payments.gateways.braintree.requests')
    requests_post_mock = requests_mock.post
    requests_post_mock.return_value.json.return_value = {
        'data': {
            'chargePaymentMethod': {
                'transaction': {
                    'id': transaction_id,
                    'status': transaction_status,
                },
            },
        },
    }

    result = BraintreeGateway().sale_by_token(token, Decimal(100))

    assert requests_post_mock.called
    variables = requests_post_mock.call_args[1]['json']['variables']['input']
    assert variables['paymentMethodId'] == token
    assert variables['transaction']['amount'] == '100'
    assert result.id == transaction_id
    assert result.status == transaction_status


def test_sale_by_token_braintree_errors(requests_post_mock, make_random_str):
    requests_post_mock.return_value.json.return_value = {
        'data': {'chargePaymentMethod': None},
        'errors': [{'message': 'Something bad happened'}],
    }

    gateway = BraintreeGateway()
    with pytest.raises(GatewayError, match='Something bad happened'):
        gateway.sale_by_token(make_random_str(digits=True), Decimal(100))


def test_perform_query_success(requests_post_mock, make_random_str, settings, caplog):
    url = f'https://{make_random_str(10)}.com'
    api_key = make_random_str()
    settings.BRAINTREE_API_URL = url
    settings.BRAINTREE_API_KEY = api_key
    requests_post_mock.return_value.json.return_value = {
        'data': {'someMutation': {'some_var': 'zxc'}},
    }
    query = make_random_str(64)
    variables = {'some_var': 'abc'}

    gateway = BraintreeGateway()
    gateway._perform_query(query, variables)

    requests_post_mock.assert_called_once_with(
        url, json={'query': query, 'variables': variables},
        timeout=gateway.API_REQUEST_TIMEOUT,
        headers={
            'Braintree-Version': gateway.API_VERSION,
            'Authorization': f'Basic {api_key}',
        },
    )  # ensuring all parameters properly passed
    assert 'Request to Braintree executed' in caplog.messages


@pytest.mark.parametrize('exception', (requests.ConnectionError, requests.Timeout))
def test_perform_query_connection_errors(exception, make_random_str,
                                         requests_post_mock, caplog):
    requests_post_mock.side_effect = exception
    query = make_random_str(64)
    variables = {'some_var': 'abc'}

    with pytest.raises(GatewayError, match='Connection issues'):
        BraintreeGateway()._perform_query(query, variables)

    assert 'Connection issues for request to Braintree API' in caplog.messages


def test_perform_query_json_parse_errors(requests_post_mock, make_random_str,
                                         caplog):
    requests_post_mock.return_value.json.side_effect = ValueError

    with pytest.raises(GatewayError, match='Unexpected data format'):
        BraintreeGateway()._perform_query(make_random_str(64), {'some_var': 'abc'})

    expected_log_msg = 'Could not extract json data from Braintree response'
    assert expected_log_msg in caplog.messages


def test_perform_query_missing_keys(requests_post_mock, make_random_str, caplog):
    requests_post_mock.return_value.json.return_value = {
        'not_data': None, 'not_errors': None,
    }  # neither data nor errors key present in response

    with pytest.raises(GatewayError, match='Braintree misbehavior'):
        BraintreeGateway()._perform_query(make_random_str(64), {'some_var': 'abc'})

    assert 'Response form Braintree missing informative keys' in caplog.messages
