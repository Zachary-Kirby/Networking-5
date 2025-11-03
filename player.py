import pygame
from message_manager import MessageManager, Flags, Message

class Player:
  def __init__(self, x, y, id):
    self.id = id
    self.position = pygame.Vector2(x, y)
    self.velocity = pygame.Vector2(0, 0)  
  def update(self, message_manager: MessageManager):
    inputs = [False]*8
    flags = [False,False,False,False,False,False,False,False]
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]: self.position.x -= 4; flags[0]=True
    if keys[pygame.K_d]: self.position.x += 4; flags[1]=True
    if keys[pygame.K_w]: self.position.y -= 4; flags[2]=True
    if keys[pygame.K_s]: self.position.y += 4; flags[3]=True
    message_manager.emit(PlayerMove(Flags([flags])))
  def __repr__(self):
    return f"<{self.id}, [{self.position.x}, {self.position.y}]>"

class PlayerMove(Message):
  
  def __init__(self, data: Flags):
    self.data = data
    
  def to_bytes(self) -> bytes:
    return self.data.to_bytes()