"""
Proxy module for IPv6 SOCKS5 proxy server
Refactored version with improved modularity and maintainability
"""

from .config_manager import ProxyConfig, ProxyMode
from .network_manager import NetworkManager
from .proxy_server import ProxyServer
from .connection_handler import ConnectionHandler

__all__ = [
    'ProxyConfig',
    'ProxyMode',
    'NetworkManager', 
    'ProxyServer',
    'ConnectionHandler'
]

__version__ = '2.0.0'
