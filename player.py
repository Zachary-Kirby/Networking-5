import pygame
from message_manager import MessageManager, Flags, Message

class Player:
  def __init__(self, id, x, y):
    self.id = id
    self.position = pygame.Vector2(x, y)
    self.velocity = pygame.Vector2(0, 0)  
  
  
  def __repr__(self):
    return f"<{self.id}, [{self.position.x}, {self.position.y}]>"
