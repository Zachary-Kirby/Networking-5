import socket
from io import BytesIO
import struct
from typing import Optional, Any

PORT = 59277
PACKET_SIZE = 512

class MessageLayer:
  """
  This is a test layer just for ensuring that commands get through as expected without relying on two processes
  """
  message_layers: list["MessageLayer"] = []
  def __init__(self, is_server, id: int, test_connection_ids: list[int]):
    self.id = id
    self.is_server = is_server
    MessageLayer.message_layers.append(self)
    self.connections = test_connection_ids
    self.test_buffer: list[tuple[bytes, int]] = []
  
  def send(self, data: bytes):
    for i in self.connections:
      message_layer = MessageLayer.message_layers[i]
      message_layer.test_buffer.append((data, self.id))
  
  def send_to(self, data: bytes, address: Any):
    MessageLayer.message_layers[address].test_buffer.append((data, self.id))
  
  def close(self):
    pass
  
  def recieve(self) -> tuple[Optional[BytesIO], Optional[int]]:
    
    if len(self.test_buffer) <= 0:
      return None, None
    data, id = self.test_buffer.pop(0)
    if self.is_server:
      if id not in self.connections and data.startswith(b"connect!"):
        self.connections.append(id)
    if data == b'':
      return None, None
    stream = BytesIO(data)
    return stream, id
    
class UDPLayer():
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
  
  def send_to(self, data: bytes, address: Any, retries = 0):
    self.socket.sendto(data, address)
  
  def recieve(self) -> tuple[Optional[BytesIO], Optional[tuple[str, int]]]:
    try:
      data, address = self.socket.recvfrom(PACKET_SIZE)
      if self.is_server:
        if address not in self.connections and data.startswith(b"connect!"):
          self.connections.append(address)
      stream = BytesIO(data)
      return (stream, address)
    except BlockingIOError:
      return (None, None)
    except IOError:
      return (None, None)

