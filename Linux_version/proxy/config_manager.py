"""
Configuration management for proxy server
Handles proxy-specific configuration and validation
"""

import os
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


class ProxyMode(Enum):
    """Proxy operation modes"""
    RANDOM = "random"
    NORMAL = "normal"


@dataclass
class ProxyConfig:
    """Configuration for proxy server settings"""
    
    # Network interface settings
    base_interface: str = "eth0"
    num_interfaces: int = 3
    delete_interface: bool = False
    
    # Proxy server settings
    mode: ProxyMode = ProxyMode.RANDOM
    port: int = 1080
    bind_address: str = "0.0.0.0"
    
    # Control interface settings (for normal mode)
    control_port: int = 1081
    control_bind: str = "127.0.0.1"
    
    # Network testing settings
    test_address: str = "2400:3200::1"
    max_retries: int = 3
    timeout: int = 5
    
    # IPv6 address storage
    interface_addresses: Dict[str, str] = field(default_factory=dict)
    current_index: int = 0
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        self._validate_config()
    
    def _validate_config(self):
        """Validate configuration parameters"""
        if self.num_interfaces <= 0:
            raise ValueError("Number of interfaces must be positive")
        
        if self.port <= 0 or self.port > 65535:
            raise ValueError("Port must be between 1 and 65535")
        
        if self.control_port <= 0 or self.control_port > 65535:
            raise ValueError("Control port must be between 1 and 65535")
        
        if self.port == self.control_port:
            raise ValueError("Proxy port and control port must be different")
        
        if not self.base_interface:
            raise ValueError("Base interface name cannot be empty")
    
    def get_ipv6_addresses(self) -> List[str]:
        """Get list of available IPv6 addresses"""
        return list(self.interface_addresses.values())
    
    def get_current_address(self) -> Optional[str]:
        """Get current IPv6 address based on mode"""
        addresses = self.get_ipv6_addresses()
        if not addresses:
            return None
        
        if self.mode == ProxyMode.RANDOM:
            import random
            return random.choice(addresses)
        elif self.mode == ProxyMode.NORMAL:
            return addresses[self.current_index % len(addresses)]
        else:
            return addresses[0]
    
    def switch_to_next_address(self) -> Optional[str]:
        """Switch to next IPv6 address (normal mode only)"""
        if self.mode != ProxyMode.NORMAL:
            return None
        
        addresses = self.get_ipv6_addresses()
        if not addresses:
            return None
        
        self.current_index = (self.current_index + 1) % len(addresses)
        return self.get_current_address()
    
    def set_address_by_index(self, index: int) -> bool:
        """Set current address by index (normal mode only)"""
        if self.mode != ProxyMode.NORMAL:
            return False
        
        addresses = self.get_ipv6_addresses()
        if 0 <= index < len(addresses):
            self.current_index = index
            return True
        return False
    
    def update_interface_addresses(self, addresses: Dict[str, str]):
        """Update interface addresses mapping"""
        self.interface_addresses = addresses.copy()
        # Reset current index if it's out of bounds
        if self.current_index >= len(self.interface_addresses):
            self.current_index = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'base_interface': self.base_interface,
            'num_interfaces': self.num_interfaces,
            'delete_interface': self.delete_interface,
            'mode': self.mode.value,
            'port': self.port,
            'bind_address': self.bind_address,
            'control_port': self.control_port,
            'control_bind': self.control_bind,
            'test_address': self.test_address,
            'max_retries': self.max_retries,
            'timeout': self.timeout,
            'current_index': self.current_index
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProxyConfig':
        """Create configuration from dictionary"""
        # Handle mode conversion
        if 'mode' in data and isinstance(data['mode'], str):
            data['mode'] = ProxyMode(data['mode'])
        
        return cls(**data)
    
    @classmethod
    def from_env(cls) -> 'ProxyConfig':
        """Load configuration from environment variables"""
        config_data = {}
        
        # Map environment variables to config fields
        env_mapping = {
            'PROXY_BASE_INTERFACE': 'base_interface',
            'PROXY_NUM_INTERFACES': ('num_interfaces', int),
            'PROXY_DELETE_INTERFACE': ('delete_interface', lambda x: x.lower() == 'true'),
            'PROXY_MODE': ('mode', lambda x: ProxyMode(x)),
            'PROXY_PORT': ('port', int),
            'PROXY_BIND_ADDRESS': 'bind_address',
            'PROXY_CONTROL_PORT': ('control_port', int),
            'PROXY_CONTROL_BIND': 'control_bind',
            'PROXY_TEST_ADDRESS': 'test_address',
            'PROXY_MAX_RETRIES': ('max_retries', int),
            'PROXY_TIMEOUT': ('timeout', int)
        }
        
        for env_var, config_field in env_mapping.items():
            value = os.getenv(env_var)
            if value is not None:
                if isinstance(config_field, tuple):
                    field_name, converter = config_field
                    config_data[field_name] = converter(value)
                else:
                    config_data[config_field] = value
        
        return cls(**config_data)
