"""
Connection handling for SOCKS5 proxy
Handles SOCKS5 protocol, connection establishment, and data forwarding
"""

import socket
import asyncio
import logging
from typing import Optional, Tuple, Any
from .config_manager import ProxyConfig


class ConnectionHandler:
    """Handles SOCKS5 connections and data forwarding"""
    
    def __init__(self, config: ProxyConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    async def create_connection_with_local_ipv6(
        self, 
        dest_addr: str, 
        dest_port: int, 
        local_ipv6: str
    ) -> Tuple[asyncio.StreamReader, asyncio.StreamWriter]:
        """
        Create a connection bound to a specific local IPv6 address
        
        Args:
            dest_addr: Destination address
            dest_port: Destination port
            local_ipv6: Local IPv6 address to bind to
            
        Returns:
            Tuple of (reader, writer) for the connection
        """
        loop = asyncio.get_running_loop()
        sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        sock.setblocking(False)
        
        try:
            sock.bind((local_ipv6, 0))
            await loop.sock_connect(sock, (dest_addr, dest_port))
            return await asyncio.open_connection(sock=sock)
        except Exception as e:
            sock.close()
            raise e
    
    async def handle_socks_connection(
        self, 
        reader: asyncio.StreamReader, 
        writer: asyncio.StreamWriter
    ) -> None:
        """
        Handle SOCKS5 connection protocol
        
        Args:
            reader: Stream reader for incoming data
            writer: Stream writer for outgoing data
        """
        try:
            # SOCKS5 handshake
            if not await self._handle_socks_handshake(reader, writer):
                return
            
            # Parse SOCKS5 request
            dest_addr, dest_port = await self._parse_socks_request(reader, writer)
            if dest_addr is None:
                return
            
            # Get local IPv6 address
            local_ipv6 = self.config.get_current_address()
            if not local_ipv6:
                self.logger.error("No IPv6 address available")
                await self._send_socks_error(writer, 0x05)  # Connection refused
                return
            
            self.logger.info(f"Request: {dest_addr}:{dest_port} using IPv6: {local_ipv6}")
            
            # Establish connection
            try:
                remote_reader, remote_writer = await self.create_connection_with_local_ipv6(
                    dest_addr, dest_port, local_ipv6
                )
            except Exception as e:
                self.logger.error(f"Failed to establish connection: {e}")
                await self._send_socks_error(writer, 0x05)  # Connection refused
                return
            
            # Send SOCKS5 reply
            await self._send_socks_reply(writer, local_ipv6)
            
            # Start data forwarding
            await self._forward_data(reader, writer, remote_reader, remote_writer)
            
        except Exception as e:
            self.logger.error(f"SOCKS connection error: {e}")
        finally:
            await self._close_connection(writer)
    
    async def _handle_socks_handshake(
        self, 
        reader: asyncio.StreamReader, 
        writer: asyncio.StreamWriter
    ) -> bool:
        """Handle SOCKS5 handshake"""
        try:
            # Read handshake header
            header = await reader.readexactly(2)
            if len(header) != 2:
                return False
            
            version, nmethods = header
            if version != 5:
                return False
            
            # Read authentication methods
            methods = await reader.readexactly(nmethods)
            if 0x00 not in methods:  # No authentication
                writer.write(b"\x05\xFF")
                await writer.drain()
                return False
            
            # Send response (no authentication)
            writer.write(b"\x05\x00")
            await writer.drain()
            return True
            
        except Exception as e:
            self.logger.error(f"Handshake error: {e}")
            return False
    
    async def _parse_socks_request(
        self, 
        reader: asyncio.StreamReader, 
        writer: asyncio.StreamWriter
    ) -> Tuple[Optional[str], Optional[int]]:
        """Parse SOCKS5 request"""
        try:
            # Read request header
            req = await reader.readexactly(4)
            if len(req) != 4:
                await self._send_socks_error(writer, 0x07)  # Command not supported
                return None, None
            
            ver, cmd, _, atyp = req
            
            if ver != 5 or cmd != 1:  # Only CONNECT command supported
                await self._send_socks_error(writer, 0x07)  # Command not supported
                return None, None
            
            # Parse destination address
            if atyp == 1:  # IPv4
                addr_bytes = await reader.readexactly(4)
                dest_addr = socket.inet_ntoa(addr_bytes)
            elif atyp == 3:  # Domain name
                addr_len = (await reader.readexactly(1))[0]
                dest_addr = (await reader.readexactly(addr_len)).decode()
            elif atyp == 4:  # IPv6
                addr_bytes = await reader.readexactly(16)
                dest_addr = socket.inet_ntop(socket.AF_INET6, addr_bytes)
            else:
                await self._send_socks_error(writer, 0x08)  # Address type not supported
                return None, None
            
            # Read destination port
            port_bytes = await reader.readexactly(2)
            dest_port = int.from_bytes(port_bytes, "big")
            
            return dest_addr, dest_port
            
        except Exception as e:
            self.logger.error(f"Request parsing error: {e}")
            await self._send_socks_error(writer, 0x01)  # General failure
            return None, None
    
    async def _send_socks_reply(
        self, 
        writer: asyncio.StreamWriter, 
        local_ipv6: str
    ) -> None:
        """Send SOCKS5 reply"""
        try:
            reply = (
                b"\x05\x00\x00\x04" +  # Version, success, reserved, IPv6
                socket.inet_pton(socket.AF_INET6, local_ipv6) +  # IPv6 address
                (0).to_bytes(2, "big")  # Port (0 for SOCKS5)
            )
            writer.write(reply)
            await writer.drain()
        except Exception as e:
            self.logger.error(f"Failed to send SOCKS reply: {e}")
    
    async def _send_socks_error(
        self, 
        writer: asyncio.StreamWriter, 
        error_code: int
    ) -> None:
        """Send SOCKS5 error reply"""
        try:
            error_reply = b"\x05" + error_code.to_bytes(1, "big") + b"\x00\x01" + b'\x00' * 6
            writer.write(error_reply)
            await writer.drain()
        except Exception as e:
            self.logger.error(f"Failed to send SOCKS error: {e}")
    
    async def _forward_data(
        self,
        client_reader: asyncio.StreamReader,
        client_writer: asyncio.StreamWriter,
        remote_reader: asyncio.StreamReader,
        remote_writer: asyncio.StreamWriter
    ) -> None:
        """Forward data between client and remote connection"""
        
        async def pipe_data(src: asyncio.StreamReader, dst: asyncio.StreamWriter, name: str):
            """Pipe data from source to destination"""
            try:
                while True:
                    data = await src.read(4096)
                    if not data:
                        break
                    dst.write(data)
                    await dst.drain()
            except Exception as e:
                self.logger.debug(f"Data pipe {name} closed: {e}")
            finally:
                try:
                    dst.close()
                    await dst.wait_closed()
                except Exception:
                    pass
        
        # Start bidirectional data forwarding
        await asyncio.gather(
            pipe_data(client_reader, remote_writer, "client->remote"),
            pipe_data(remote_reader, client_writer, "remote->client"),
            return_exceptions=True
        )
    
    async def _close_connection(self, writer: asyncio.StreamWriter) -> None:
        """Close connection gracefully"""
        try:
            writer.close()
            await writer.wait_closed()
        except Exception as e:
            self.logger.debug(f"Error closing connection: {e}")
    
    async def handle_control_connection(
        self, 
        reader: asyncio.StreamReader, 
        writer: asyncio.StreamWriter
    ) -> None:
        """
        Handle control connection for normal mode
        
        Args:
            reader: Stream reader for incoming commands
            writer: Stream writer for responses
        """
        try:
            data = await reader.readline()
            if not data:
                return
            
            command = data.decode().strip()
            response = await self._process_control_command(command)
            
            writer.write(response.encode("utf-8"))
            await writer.drain()
            
        except Exception as e:
            self.logger.error(f"Control connection error: {e}")
            try:
                writer.write(f"Error: {e}\n".encode("utf-8"))
                await writer.drain()
            except Exception:
                pass
        finally:
            await self._close_connection(writer)
    
    async def _process_control_command(self, command: str) -> str:
        """Process control command"""
        if not command.startswith("switch"):
            return "Unknown command\n"
        
        parts = command.split()
        if len(parts) != 2:
            return "Usage: switch <index>\n"
        
        try:
            index = int(parts[1])
            if self.config.set_address_by_index(index):
                current_addr = self.config.get_current_address()
                self.logger.info(f"Switched to IPv6 address: {current_addr}")
                return f"Switched to {current_addr}\n"
            else:
                return "Invalid index\n"
        except ValueError:
            return "Invalid index format\n"
        except Exception as e:
            return f"Error: {e}\n"
