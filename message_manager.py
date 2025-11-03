from typing import Type, Callable
import struct

class Message:
  def __init__(self, data):
    self.data = data
  
  def to_bytes(self) -> bytes:
    return bytes()

class Flags:
  """
  the list orders the bits from least significant to most significant
  """
  def __init__(self, bits = [False,False,False,False, False,False,False,False]):
    self.bits:list[bool] = bits
  
  def get_flag(self, i):
    return self.bits[i]
  
  def from_bytes(self, data: bytes):
    binary = struct.unpack("B", data)[0]
    for i in range(8):
      self.bits[i] = (binary & (1 << i))>0
  
  def to_bytes(self) -> bytes:
    data = 0
    for i,v in enumerate(self.bits):
      data |= v << i
    return struct.pack("B", data)

class MessageManager:
  
  def __init__(self):
    self.messages: list[Message] = []
    self.callbacks: dict[Type[Message],list[Callable[[Message], None]]] = {}
  
  def emit(self, data: Message):
    self.messages.append(data)
  
  def register(self, message_type: Type[Message], callback: Callable):
    if message_type not in self.callbacks:
      self.callbacks[message_type] = []
    self.callbacks[message_type].append(callback)
  
  def clear(self):
    self.messages = []
  
  
  def process(self):
    for message in self.messages:
      for callback in self.callbacks[type(message)]:
        callback(message)