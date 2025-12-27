import pygame
from message_manager import MessageManager, Flags, Message
import time

class Player:
  SPEED = 256
  def __init__(self, id, x, y):
    self.id = id
    self.previous_update_time = time.monotonic()
    self.position = pygame.Vector2(x, y)
    self.previous_position = self.position.copy()
    self.velocity = pygame.Vector2(0, 0)  
  
  
  def __repr__(self):
    return f"<{self.id}, [{self.position.x}, {self.position.y}]>"
