class DomainError(Exception):
    """Base class for business errors. Routes never build HTTP errors by hand;
    main.py maps these to HTTP responses."""

    status_code = 400

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class NotFoundError(DomainError):
    status_code = 404


class ConflictError(DomainError):
    status_code = 409


class BusinessRuleError(DomainError):
    status_code = 422


class LedgerImmutableError(DomainError):
    status_code = 500
