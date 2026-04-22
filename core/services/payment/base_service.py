from abc import ABC, abstractmethod


class BasePaymentService(ABC):

    @abstractmethod
    def initialize_payment(self, booking, user):
        pass

    @abstractmethod
    def verify_payment(self, reference):
        pass

