import pytest
from rest_framework import serializers

from payments.gateways.base import SaleResult
from payments.serializers import TokenizeSerializer, SaleSerializer
from payments.service import PaymentServiceError


@pytest.fixture
def payment_service_mock(mocker):
    return mocker.patch('payments.serializers.PaymentService')


@pytest.mark.parametrize('length,error_code', [(10, 'min_length'), (20, 'max_length')])
def test_tokenize_serializer_card_number_length_errors(length, error_code, make_random_str):
    data = {
        'card_number': make_random_str(length, digits=True),
        'expiry_date': '12/2020',
    }

    serializer = TokenizeSerializer(data=data)

    assert not serializer.is_valid()
    assert 'card_number' in serializer.errors
    assert serializer.errors['card_number'][0].code == error_code


def test_card_number_not_only_digits_error():
    data = {
        'card_number': '111122223333AAAA',
        'expiry_date': '12/2020',
    }

    serializer = TokenizeSerializer(data=data)

    assert not serializer.is_valid()
    assert 'card_number' in serializer.errors
    assert serializer.errors['card_number'][0].code == 'invalid'


@pytest.mark.parametrize('expiry_date,is_correct', [
    ('12/2020', True), ('12/20', True), ('01/20', True),
    ('20/2020', False), ('202020', False), ('wrong', False), ('1/20', False),
])
def test_tokenize_serializer_expiry_date_validation(expiry_date, is_correct, make_random_str):
    data = {
        'card_number': make_random_str(16, digits=True),
        'expiry_date': expiry_date,
    }

    serializer = TokenizeSerializer(data=data)
    is_valid = serializer.is_valid()

    if is_correct:
        assert is_valid
    else:
        assert 'expiry_date' in serializer.errors
        assert serializer.errors['expiry_date'][0].code == 'invalid'


def test_tokenize_serializer_payment_service_ok(payment_service_mock, make_random_str):
    data = {
        'card_number': make_random_str(16, digits=True),
        'expiry_date': '12/2020',
    }
    token = make_random_str()
    payment_service_mock.tokenize.return_value = token

    serializer = TokenizeSerializer(data=data)

    assert serializer.is_valid()
    serializer.save()
    assert serializer.data == {'token': token}


def test_tokenize_serializer_payment_service_error(payment_service_mock, make_random_str):
    data = {
        'card_number': make_random_str(16, digits=True),
        'expiry_date': '12/2020',
    }
    payment_service_mock.tokenize.side_effect = PaymentServiceError('Error on PSP')

    serializer = TokenizeSerializer(data=data)

    assert serializer.is_valid()
    with pytest.raises(serializers.ValidationError) as excinfo:
        serializer.save()

    assert excinfo.value.args[0] == {'error': 'Error on PSP'}


@pytest.mark.parametrize('amount,is_correct', [
    ('100', True), ('100.15', True), ('1000.1', True),
    ('not a number', False),
])
def test_sale_serializer_transaction_amount_validation(amount, is_correct, make_random_str):
    data = {
        'token': make_random_str(),
        'transaction_amount': amount,
    }

    serializer = SaleSerializer(data=data)
    is_valid = serializer.is_valid()

    if is_correct:
        assert is_valid
    else:
        assert 'transaction_amount' in serializer.errors
        assert serializer.errors['transaction_amount'][0].code == 'invalid'


def test_sale_serializer_transaction_amount_max_decimal_places(make_random_str):
    data = {
        'token': make_random_str(),
        'transaction_amount': '100.5555',
    }

    serializer = SaleSerializer(data=data)
    assert not serializer.is_valid()

    assert 'transaction_amount' in serializer.errors
    assert serializer.errors['transaction_amount'][0].code == 'max_decimal_places'


def test_sale_serializer_payment_service_ok(payment_service_mock, make_random_str):
    data = {
        'token': make_random_str(),
        'transaction_amount': '100',
    }
    sale_id, sale_status = make_random_str(4), make_random_str(4)
    payment_service_mock.sale.return_value = SaleResult(sale_id, sale_status)

    serializer = SaleSerializer(data=data)

    assert serializer.is_valid()
    serializer.save()
    assert serializer.data == {'id': sale_id, 'status': sale_status}


def test_sale_serializer_payment_service_error(payment_service_mock, make_random_str):
    data = {
        'token': make_random_str(),
        'transaction_amount': '100',
    }
    payment_service_mock.sale.side_effect = PaymentServiceError('Error on PSP')

    serializer = SaleSerializer(data=data)

    assert serializer.is_valid()
    with pytest.raises(serializers.ValidationError) as excinfo:
        serializer.save()

    assert excinfo.value.args[0] == {'error': 'Error on PSP'}
