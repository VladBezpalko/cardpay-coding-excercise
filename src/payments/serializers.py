from rest_framework import serializers

from payments.service import PaymentService, PaymentServiceError


EXPIRY_DATE_REGEX = r'^(0[1-9]|1[0-2])\/?([0-9]{4}|[0-9]{2})$'
EXPIRY_DATE_INVALID_MESSAGE = 'This value does not match the required pattern.'


class TokenizeSerializer(serializers.Serializer):
    card_number = serializers.CharField(min_length=12, max_length=19)
    expiry_date = serializers.RegexField(
        regex=EXPIRY_DATE_REGEX,
        error_messages={'invalid': EXPIRY_DATE_INVALID_MESSAGE},
    )

    def validate_card_number(self, value: str) -> str:
        """
        Check if card_number value contains only digits.
        """
        if not all([c.isdigit() for c in value]):
            raise serializers.ValidationError(
                detail='This field should contain only digits.', code='invalid',
            )

        return value

    def create(self, validated_data: dict) -> dict:
        try:
            token = PaymentService.tokenize(
                card_number=validated_data['card_number'],
                expiry_date=validated_data['expiry_date'],
            )
        except PaymentServiceError as exception:
            raise serializers.ValidationError({'error': str(exception)})

        self._data = {'token': token}
        return self._data


class SaleSerializer(serializers.Serializer):
    token = serializers.CharField()
    transaction_amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    def create(self, validated_data: dict) -> dict:
        try:
            sale_result = PaymentService.sale(
                token=validated_data['token'],
                transaction_amount=validated_data['transaction_amount'],
            )
        except PaymentServiceError as exception:
            raise serializers.ValidationError({'error': str(exception)})

        self._data = {'id': sale_result.id, 'status': sale_result.status}
        return self._data
