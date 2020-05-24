from decimal import Decimal

import pytest

from payments.gateways.base import GatewayError, SaleResult
from payments.service import PaymentService, PaymentServiceError


@pytest.fixture
def gateway_mock(mocker):
    return mocker.patch('payments.service.PaymentService.gateway')


def test_tokenize_properly_delegated(make_random_str, gateway_mock):
    card_number = make_random_str(16, digits=True)
    expiry_date = '12/2020'
    token = make_random_str()
    tokenize_card_mock = gateway_mock.tokenize_card
    tokenize_card_mock.return_value = token

    returned_value = PaymentService.tokenize(card_number, expiry_date)

    assert returned_value == token
    tokenize_card_mock.assert_called_once_with(card_number, expiry_date)


def test_tokenize_gateway_error(make_random_str, gateway_mock):
    card_number = make_random_str(16, digits=True)
    expiry_date = '12/2020'
    gateway_mock.tokenize_card.side_effect = GatewayError('Error')

    with pytest.raises(PaymentServiceError, match='Error'):
        PaymentService.tokenize(card_number, expiry_date)


def test_sale_properly_delegated(make_random_str, gateway_mock):
    token = make_random_str(16, digits=True)
    transaction_amount = Decimal(100)
    sale_id, sale_status = make_random_str(4), make_random_str(4)
    sale_by_token_mock = gateway_mock.sale_by_token
    sale_by_token_mock.return_value = SaleResult(sale_id, sale_status)

    returned_value = PaymentService.sale(token, transaction_amount)

    assert returned_value == SaleResult(sale_id, sale_status)
    sale_by_token_mock.assert_called_once_with(token, transaction_amount)


def test_sale_gateway_error(make_random_str, gateway_mock):
    token = make_random_str(16, digits=True)
    transaction_amount = Decimal(100)
    gateway_mock.sale_by_token.side_effect = GatewayError('Error')

    with pytest.raises(PaymentServiceError, match='Error'):
        PaymentService.sale(token, transaction_amount)
