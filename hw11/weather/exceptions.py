class ResponseException(Exception):
    pass


class ResponseEmptyException(Exception):
    pass


class ServerReturnInvalidResponse(Exception):
    pass


class NoAvailableServiceError(Exception):
    pass
