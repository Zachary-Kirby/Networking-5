import socket
from io import BytesIO
import struct

PORT = 59277
PACKET_SIZE = 512

class UDPLayer:
  def __init__(self, is_server = False, connections: list[tuple[str, int]] = []):
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.socket.setblocking(False)
    self.is_server = is_server
    if is_server:
      self.socket.bind(("0.0.0.0", PORT))
    self.connections = connections
    self.message_count = 0
  
  def close(self):
    self.socket.close()
  
  def send(self, data: bytes, retries = 0):
    """
    retries will re-attempt sending the message if it fails to be recieved
    """
    self.message_count += 1
    for connection in self.connections:
      self.socket.sendto(data, connection)
  
  def recieve(self) -> BytesIO | None:
    try:
      data, address = self.socket.recvfrom(PACKET_SIZE)
      if self.is_server:
        if address not in self.connections and data.startswith(b"connect!"):
          self.connections.append(address)
      stream = BytesIO(data)
      return stream
    except BlockingIOError:
      return None