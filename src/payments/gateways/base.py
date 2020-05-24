from abc import ABC, abstractmethod
from collections import namedtuple
from decimal import Decimal


class GatewayError(RuntimeError):
    """
    Generic exception to propagate any PSP-related errors occurred.
    """


SaleResult = namedtuple('SaleResult', ('id', 'status'))
"""
Represents successful sale request. Contains PSP data about sale.
"""


class BaseGateway(ABC):
    """
    Base abstract class for gateways (implementations of integration with PSP).
    """

    @abstractmethod
    def tokenize_card(self, card_number: str, expiry_date: str) -> str:
        """
        Abstract method that should be implemented on concrete gateway class in
        order to tokenize provided card details on PSP.
        :return: token generated for provided card details
        """

    @abstractmethod
    def sale_by_token(self, token: str,
                      transaction_amount: Decimal) -> SaleResult:
        """
        Abstract method that should be implemented on concrete gateway class in
        order to request sale on PSP for provided token with specified amount.
        :param token:
        :param transaction_amount:
        :return: transaction data
        """
