class InvalidArgumentError(Exception):
    def __init__(self, argument_name):
        message = f'The argument {argument_name} is invalid'
        super().__init__(message)


class OrderAlreadyCompletedError(Exception):
    def __init__(self, order):
        message = f'The order with ID: {order.id} is already completed.'
        super().__init__(message)


class OrderAlreadyCancelledError(Exception):
    def __init__(self, order):
        message = f'The order with ID: {order.id} is already cancelled.'
        super().__init__(message)


class OrderCancellationError(Exception):
    pass


class OrderNotFoundError(Exception):
    pass
