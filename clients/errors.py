class ClientError(Exception):
    pass


class NotFoundError(ClientError):
    pass


class ServiceUnavailableError(ClientError):
    pass
