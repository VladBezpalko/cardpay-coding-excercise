import logging
from decimal import Decimal

from payments.gateways.base import GatewayError, SaleResult
from payments.gateways.braintree import BraintreeGateway


logger = logging.getLogger(__name__)


class PaymentServiceError(RuntimeError):
    """
    An exception to propagate any errors that occurred
    in processing payments logic.
    """


class PaymentService:
    """
    Service that holds all payment-related logic.
    An entry point for code that performs payment activity.
    """
    gateway = BraintreeGateway()

    @classmethod
    def tokenize(cls, card_number: str, expiry_date: str) -> str:
        """
        Holds a logic of card tokenizing.
        For now it's just delegating call to the corresponding gateway.
        :return: token generated by PSP for provided card details
        """
        try:
            token = cls.gateway.tokenize_card(card_number, expiry_date)
        except GatewayError as exception:
            raise PaymentServiceError(exception)

        return token

    @classmethod
    def sale(cls, token: str, transaction_amount: Decimal) -> SaleResult:
        """
        Holds a logic of processing sale by provided token.
        For now it's just delegating call to the corresponding gateway.
        :return: result of sale request from PSP
        """
        try:
            sale_result = cls.gateway.sale_by_token(token, transaction_amount)
        except GatewayError as exception:
            raise PaymentServiceError(exception)

        logger.info(
            'Sale with id=%s requested successfully and has status=%s',
            sale_result.id, sale_result.status,
        )

        return sale_result
