"""
BReact OS SDK
~~~~~~~~~~~~~

BReact SDK for interacting with BReact's AI services.

:copyright: (c) 2024 by BReact OS Team.
:license: MIT, see LICENSE for more details.
"""

__version__ = "0.1.5"

from .client import create_client, AsyncBReactClient, SyncBReactClient
from .config import Configuration

__all__ = [
    "create_client",
    "AsyncBReactClient", 
    "SyncBReactClient",
    "Configuration"
] 