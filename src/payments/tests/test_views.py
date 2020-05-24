import pytest

from payments.gateways.base import SaleResult
from payments.service import PaymentServiceError


@pytest.fixture
def payment_service_mock(mocker):
    return mocker.patch('payments.serializers.PaymentService')


def test_tokenize_view_ok(api, make_random_str, payment_service_mock):
    token = make_random_str()
    payment_service_mock.tokenize.return_value = token
    data = {
        'card_number': make_random_str(16, digits=True),
        'expiry_date': '12/2020',
    }

    response = api.post('/tokenise', data=data, format='json')

    assert response.status_code == 200, response.rendered_content
    assert response.data == {'token': token}


def test_tokenize_view_payment_service_error(api, make_random_str, payment_service_mock):
    payment_service_mock.tokenize.side_effect = PaymentServiceError('Something wrong')
    data = {
        'card_number': make_random_str(16, digits=True),
        'expiry_date': '12/2020',
    }

    response = api.post('/tokenise', data=data, format='json')

    assert response.status_code == 400
    assert response.data == {'error': 'Something wrong'}


def test_sale_view_ok(api, make_random_str, payment_service_mock):
    sale_id, sale_status = make_random_str(4), make_random_str(4)
    payment_service_mock.sale.return_value = SaleResult(sale_id, sale_status)
    data = {
        'token': make_random_str(),
        'transaction_amount': '100',
    }

    response = api.post('/sale', data=data, format='json')

    assert response.status_code == 200, response.rendered_content
    assert response.data == {'id': sale_id, 'status': sale_status}


def test_sale_view_payment_service_error(api, make_random_str, payment_service_mock):
    payment_service_mock.sale.side_effect = PaymentServiceError('Something wrong')
    data = {
        'token': make_random_str(),
        'transaction_amount': '100',
    }

    response = api.post('/sale', data=data, format='json')

    assert response.status_code == 400
    assert response.data == {'error': 'Something wrong'}
