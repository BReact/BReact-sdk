class BReactError(Exception):
    """Base exception for all BReact SDK errors."""
    pass

class BReactClientError(BReactError):
    """Raised when there's a client configuration error."""
    pass

class ServiceExecutionError(BReactError):
    """Raised when a service execution fails."""
    pass

class ServiceNotFoundError(BReactError):
    """Raised when attempting to use a non-existent service."""
    pass