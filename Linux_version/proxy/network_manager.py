"""
Network interface management for IPv6 proxy
Handles creation, deletion, and management of macvlan interfaces
"""

import os
import re
import subprocess
import logging
from typing import Dict, List, Optional, Tuple
from .config_manager import ProxyConfig


class NetworkManager:
    """Manages network interfaces for IPv6 proxy"""
    
    def __init__(self, config: ProxyConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._sudo_cmd = ["sudo"] if not self._is_root() else []
    
    def _is_root(self) -> bool:
        """Check if running as root"""
        return os.geteuid() == 0
    
    def interface_usable(self, interface_name: str) -> bool:
        """
        Test if interface is usable by pinging a test address
        
        Args:
            interface_name: Name of the interface to test
            
        Returns:
            True if interface is usable, False otherwise
        """
        for attempt in range(self.config.max_retries):
            try:
                result = subprocess.run(
                    ["ping", "-c", "1", "-I", interface_name, self.config.test_address],
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE, 
                    timeout=self.config.timeout
                )
                if result.returncode == 0:
                    return True
            except subprocess.TimeoutExpired:
                self.logger.debug(f"[{interface_name}] Ping attempt {attempt+1} timed out, retrying...")
            except subprocess.SubprocessError as e:
                self.logger.warning(f"[{interface_name}] Error pinging: {e}")
        
        return False
    
    def get_existing_interfaces(self) -> Dict[str, str]:
        """
        Get existing macvlan interfaces and their IPv6 addresses
        
        Returns:
            Dictionary mapping interface names to IPv6 addresses
        """
        try:
            # Get all interfaces
            output = subprocess.run(
                ["ip", "addr", "show"], 
                stdout=subprocess.PIPE, 
                check=True
            ).stdout.decode()
            
            # Find matching interfaces
            iface_pattern = re.compile(re.escape(self.config.base_interface) + r'_([0-9]+)@')
            matches = iface_pattern.findall(output)
            interfaces = [f"{self.config.base_interface}_{num}" for num in matches]
            
            # Get IPv6 addresses for each interface
            iface_ipv6 = {}
            for iface in interfaces:
                try:
                    out = subprocess.run(
                        ["ip", "addr", "show", iface], 
                        stdout=subprocess.PIPE, 
                        check=True
                    ).stdout.decode()
                    
                    # Extract IPv6 addresses (excluding link-local)
                    ipv6_matches = re.findall(r"inet6\s+([0-9a-f:]+)\/\d+", out)
                    ipv6_addrs = [addr for addr in ipv6_matches if not addr.startswith("fe80")]
                    
                    if ipv6_addrs:
                        iface_ipv6[iface] = ipv6_addrs[0]
                        
                except subprocess.CalledProcessError as e:
                    self.logger.warning(f"Failed to get IPv6 address for {iface}: {e}")
                    continue
            
            return iface_ipv6
            
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            self.logger.warning(f"Failed to get existing interfaces (ip command not available): {e}")
            return {}
    
    def create_interfaces(self) -> List[str]:
        """
        Create macvlan interfaces
        
        Returns:
            List of created interface names
        """
        if self.config.delete_interface:
            self.delete_interfaces()
        
        existing_ifaces = list(self.get_existing_interfaces().keys())
        interfaces = []
        
        for i in range(1, self.config.num_interfaces + 1):
            iface = f"{self.config.base_interface}_{i}"
            
            if iface in existing_ifaces:
                if self.interface_usable(iface):
                    self.logger.info(f"[{iface}] Already exists and usable, skipping creation")
                    interfaces.append(iface)
                    continue
                else:
                    self.logger.info(f"[{iface}] Exists but not usable, recreating")
                    self._delete_interface(iface)
            
            try:
                # Create macvlan interface
                subprocess.run(
                    self._sudo_cmd + [
                        "ip", "link", "add", "link", 
                        self.config.base_interface, iface, 
                        "type", "macvlan", "mode", "bridge"
                    ],
                    check=True
                )
                
                # Bring interface up
                subprocess.run(
                    self._sudo_cmd + ["ip", "link", "set", iface, "up"],
                    check=True
                )
                
                interfaces.append(iface)
                self.logger.info(f"[{iface}] Created successfully")
                
            except subprocess.CalledProcessError as e:
                self.logger.error(f"Failed to create interface {iface}: {e}")
                continue
        
        return interfaces
    
    def delete_interfaces(self) -> None:
        """Delete all macvlan interfaces"""
        existing_ifaces = list(self.get_existing_interfaces().keys())
        
        for iface in existing_ifaces:
            self._delete_interface(iface)
    
    def _delete_interface(self, interface_name: str) -> None:
        """Delete a specific interface"""
        try:
            subprocess.run(
                self._sudo_cmd + ["ip", "link", "delete", interface_name],
                check=True
            )
            self.logger.info(f"[{interface_name}] Deleted successfully")
        except subprocess.CalledProcessError as e:
            self.logger.warning(f"Failed to delete interface {interface_name}: {e}")
    
    def wait_for_ipv6_assignment(self, max_wait: int = 10) -> bool:
        """
        Wait for IPv6 addresses to be assigned to interfaces
        
        Args:
            max_wait: Maximum seconds to wait
            
        Returns:
            True if enough addresses are assigned, False otherwise
        """
        import asyncio
        
        for _ in range(max_wait):
            addresses = self.get_existing_interfaces()
            if len(addresses) >= self.config.num_interfaces:
                self.config.update_interface_addresses(addresses)
                return True
            
            asyncio.sleep(1)
        
        self.logger.warning(f"Only got {len(addresses)} IPv6 addresses, expected {self.config.num_interfaces}")
        return False
    
    def get_interface_status(self) -> Dict[str, Dict[str, any]]:
        """
        Get detailed status of all interfaces
        
        Returns:
            Dictionary with interface status information
        """
        addresses = self.get_existing_interfaces()
        status = {}
        
        for iface, ipv6_addr in addresses.items():
            status[iface] = {
                'ipv6_address': ipv6_addr,
                'usable': self.interface_usable(iface),
                'exists': True
            }
        
        return status
    
    def validate_network_setup(self) -> Tuple[bool, List[str]]:
        """
        Validate the network setup
        
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        # Check if base interface exists
        try:
            subprocess.run(
                ["ip", "link", "show", self.config.base_interface],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            errors.append(f"Base interface {self.config.base_interface} does not exist or ip command not available")
        
        # Check if we have enough interfaces
        addresses = self.get_existing_interfaces()
        if len(addresses) < self.config.num_interfaces:
            errors.append(f"Only {len(addresses)} interfaces available, need {self.config.num_interfaces}")
        
        # Check if interfaces are usable
        unusable_interfaces = []
        for iface in addresses.keys():
            if not self.interface_usable(iface):
                unusable_interfaces.append(iface)
        
        if unusable_interfaces:
            errors.append(f"Unusable interfaces: {', '.join(unusable_interfaces)}")
        
        return len(errors) == 0, errors
