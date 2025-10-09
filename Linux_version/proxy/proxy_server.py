"""
Main proxy server implementation
Coordinates network management, connection handling, and server lifecycle
"""

import asyncio
import logging
import atexit
import sys
from typing import Optional, List
from .config_manager import ProxyConfig, ProxyMode
from .network_manager import NetworkManager
from .connection_handler import ConnectionHandler


class ProxyServer:
    """Main proxy server class"""
    
    def __init__(self, config: Optional[ProxyConfig] = None):
        self.config = config or ProxyConfig()
        self.network_manager = NetworkManager(self.config)
        self.connection_handler = ConnectionHandler(self.config)
        self.logger = logging.getLogger(__name__)
        
        self._socks_server: Optional[asyncio.Server] = None
        self._control_server: Optional[asyncio.Server] = None
        self._running = False
        
        # Register cleanup on exit
        atexit.register(self.cleanup)
    
    async def start(self) -> bool:
        """
        Start the proxy server
        
        Returns:
            True if started successfully, False otherwise
        """
        try:
            self.logger.info("Starting proxy server...")
            
            # Create network interfaces
            self.logger.info("Creating network interfaces...")
            interfaces = self.network_manager.create_interfaces()
            
            if not interfaces:
                self.logger.error("Failed to create any network interfaces")
                return False
            
            # Wait for IPv6 address assignment
            self.logger.info("Waiting for IPv6 address assignment...")
            if not self.network_manager.wait_for_ipv6_assignment():
                self.logger.error("Failed to get enough IPv6 addresses")
                return False
            
            # Update configuration with actual addresses
            addresses = self.network_manager.get_existing_interfaces()
            self.config.update_interface_addresses(addresses)
            
            # Log available interfaces
            self.logger.info("Available IPv6 interfaces:")
            for i, (iface, ip) in enumerate(addresses.items()):
                self.logger.info(f"  {i}: {iface} -> {ip}")
            
            # Start SOCKS5 server
            self._socks_server = await asyncio.start_server(
                self.connection_handler.handle_socks_connection,
                self.config.bind_address,
                self.config.port
            )
            
            self.logger.info(
                f"SOCKS5 proxy running on {self.config.bind_address}:{self.config.port}, "
                f"mode: {self.config.mode.value}"
            )
            
            # Start control server for normal mode
            if self.config.mode == ProxyMode.NORMAL:
                self._control_server = await asyncio.start_server(
                    self.connection_handler.handle_control_connection,
                    self.config.control_bind,
                    self.config.control_port
                )
                self.logger.info(
                    f"Control interface running on {self.config.control_bind}:{self.config.control_port}"
                )
            else:
                self.logger.info("Random mode: control interface disabled")
            
            self._running = True
            self.logger.info("Proxy server started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start proxy server: {e}")
            await self.stop()
            return False
    
    async def stop(self) -> None:
        """Stop the proxy server"""
        try:
            self.logger.info("Stopping proxy server...")
            self._running = False
            
            # Stop servers
            if self._socks_server:
                self._socks_server.close()
                await self._socks_server.wait_closed()
                self._socks_server = None
            
            if self._control_server:
                self._control_server.close()
                await self._control_server.wait_closed()
                self._control_server = None
            
            self.logger.info("Proxy server stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping proxy server: {e}")
    
    async def run(self) -> None:
        """Run the proxy server (blocking)"""
        if not await self.start():
            raise RuntimeError("Failed to start proxy server")
        
        try:
            # Create tasks for both servers
            tasks = [self._socks_server.serve_forever()]
            if self._control_server:
                tasks.append(self._control_server.serve_forever())
            
            # Wait for all tasks
            await asyncio.gather(*tasks)
            
        except asyncio.CancelledError:
            self.logger.info("Proxy server cancelled")
        except Exception as e:
            self.logger.error(f"Proxy server error: {e}")
        finally:
            await self.stop()
    
    def cleanup(self) -> None:
        """Cleanup resources (called on exit)"""
        try:
            if self._running:
                self.logger.info("Cleaning up proxy server resources...")
                
                # Delete network interfaces
                self.network_manager.delete_interfaces()
                
                self.logger.info("Cleanup completed")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    def switch_proxy_server(self) -> Optional[str]:
        """
        Switch to next proxy server (for normal mode)
        
        Returns:
            Current IPv6 address if switched, None otherwise
        """
        if self.config.mode != ProxyMode.NORMAL:
            self.logger.warning("Cannot switch proxy server in random mode")
            return None
        
        new_address = self.config.switch_to_next_address()
        if new_address:
            self.logger.info(f"Switched to IPv6 address: {new_address}")
        else:
            self.logger.warning("Failed to switch proxy server")
        
        return new_address
    
    def get_status(self) -> dict:
        """
        Get current server status
        
        Returns:
            Dictionary with status information
        """
        return {
            'running': self._running,
            'mode': self.config.mode.value,
            'current_address': self.config.get_current_address(),
            'available_addresses': self.config.get_ipv6_addresses(),
            'interface_status': self.network_manager.get_interface_status(),
            'socks_port': self.config.port,
            'control_port': self.config.control_port if self.config.mode == ProxyMode.NORMAL else None
        }
    
    def validate_setup(self) -> tuple[bool, List[str]]:
        """
        Validate the proxy setup
        
        Returns:
            Tuple of (is_valid, error_messages)
        """
        return self.network_manager.validate_network_setup()


# Convenience functions for backward compatibility
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
    
    server = ProxyServer(config)
    
    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        print("Received interrupt signal, exiting...")
        sys.exit(0)


def switch_proxy_server() -> None:
    """Switch proxy server (backward compatibility)"""
    # This is a global function for backward compatibility
    # In practice, you should use the ProxyServer instance method
    print("Warning: switch_proxy_server() called without server instance")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="IPv6 SOCKS5 Proxy Server")
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
