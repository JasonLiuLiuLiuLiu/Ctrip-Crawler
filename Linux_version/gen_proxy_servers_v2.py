#!/usr/bin/env python3
"""
Refactored IPv6 SOCKS5 Proxy Server
Backward compatible replacement for gen_proxy_servers.py
"""

import sys
import logging
from proxy import ProxyServer, ProxyConfig, ProxyMode

# Global server instance for backward compatibility
_global_server: ProxyServer = None


def run_proxy(
    mode: str = "random",
    port: int = 1080,
    bind_address: str = "0.0.0.0",
    base_interface: str = "eth0",
    num_interfaces: int = 3,
    delete_iface: bool = False,
    control_port: int = 1081,
    control_bind: str = "127.0.0.1"
) -> None:
    """
    Start proxy server with specified parameters (backward compatibility)
    
    Args:
        mode: Proxy mode ("random" or "normal")
        port: SOCKS5 proxy port
        bind_address: Bind address for SOCKS5 server
        base_interface: Base network interface
        num_interfaces: Number of interfaces to create
        delete_iface: Whether to delete existing interfaces
        control_port: Control interface port
        control_bind: Control interface bind address
    """
    global _global_server
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create configuration
    config = ProxyConfig(
        mode=ProxyMode(mode),
        port=port,
        bind_address=bind_address,
        base_interface=base_interface,
        num_interfaces=num_interfaces,
        delete_interface=delete_iface,
        control_port=control_port,
        control_bind=control_bind
    )
    
    # Create and run server
    _global_server = ProxyServer(config)
    
    try:
        import asyncio
        asyncio.run(_global_server.run())
    except KeyboardInterrupt:
        print("Received interrupt signal, exiting...")
        sys.exit(0)


def switch_proxy_server() -> None:
    """
    Switch to next proxy server (for normal mode)
    Backward compatibility function
    """
    global _global_server
    
    if _global_server is None:
        print("Proxy server not running")
        return
    
    result = _global_server.switch_proxy_server()
    if result:
        print(f"Switched to IPv6 address: {result}")
    else:
        print("Failed to switch proxy server or not in normal mode")


# Backward compatibility: expose the old interface
def is_root():
    """Check if running as root"""
    import os
    return os.geteuid() == 0


def interface_usable(interface_name, test_addr='2400:3200::1', max_retries=3):
    """Test if interface is usable (backward compatibility)"""
    from proxy.network_manager import NetworkManager
    from proxy.config_manager import ProxyConfig
    
    config = ProxyConfig(test_address=test_addr, max_retries=max_retries)
    manager = NetworkManager(config)
    return manager.interface_usable(interface_name)


def get_existing_interfaces(base_interface='eth0'):
    """Get existing interfaces (backward compatibility)"""
    from proxy.network_manager import NetworkManager
    from proxy.config_manager import ProxyConfig
    
    config = ProxyConfig(base_interface=base_interface)
    manager = NetworkManager(config)
    return manager.get_existing_interfaces()


def create_ipv6_addresses(n, base_interface='eth0', delete_interface=True):
    """Create IPv6 addresses (backward compatibility)"""
    from proxy.network_manager import NetworkManager
    from proxy.config_manager import ProxyConfig
    
    config = ProxyConfig(
        base_interface=base_interface,
        num_interfaces=n,
        delete_interface=delete_interface
    )
    manager = NetworkManager(config)
    return manager.create_interfaces()


def delete_ipv6_addresses(base_interface='eth0'):
    """Delete IPv6 addresses (backward compatibility)"""
    from proxy.network_manager import NetworkManager
    from proxy.config_manager import ProxyConfig
    
    config = ProxyConfig(base_interface=base_interface)
    manager = NetworkManager(config)
    manager.delete_interfaces()


def select_ipv6_address():
    """Select IPv6 address (backward compatibility)"""
    global _global_server
    
    if _global_server is None:
        raise Exception("Proxy server not running")
    
    return _global_server.config.get_current_address()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="IPv6 SOCKS5 Proxy Server (Refactored)")
    parser.add_argument("--mode", choices=["random", "normal"], default="random", 
                       help="Proxy mode: random or normal")
    parser.add_argument("--port", type=int, default=1080, 
                       help="SOCKS5 proxy port")
    parser.add_argument("--bind-address", type=str, default="0.0.0.0", 
                       help="SOCKS5 proxy bind address")
    parser.add_argument("--control-port", type=int, default=1081, 
                       help="Control interface port (normal mode only)")
    parser.add_argument("--control-bind", type=str, default="127.0.0.1", 
                       help="Control interface bind address")
    parser.add_argument("--base-interface", type=str, default="eth0", 
                       help="Base network interface")
    parser.add_argument("--num-interfaces", type=int, default=3, 
                       help="Number of interfaces to create")
    parser.add_argument("--delete-iface", action="store_true", 
                       help="Delete existing interfaces before starting")
    
    args = parser.parse_args()
    
    run_proxy(
        mode=args.mode,
        port=args.port,
        bind_address=args.bind_address,
        base_interface=args.base_interface,
        num_interfaces=args.num_interfaces,
        delete_iface=args.delete_iface,
        control_port=args.control_port,
        control_bind=args.control_bind
    )
