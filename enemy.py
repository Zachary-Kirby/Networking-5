import pygame
from typing import Optional

class RedEnemy:
  def __init__(self, id, x, y):
    self.id = id
    self.position = pygame.Vector2(x, y)
    self.velocity = pygame.Vector2(0, 0)
    self.target: Optional[pygame.Vector2] = None
  def update(self):
    self.position += self.velocity
    if self.target:
      self.velocity += (self.target - self.position) * 0.1
    self.velocity *= 0.9
  def draw(self, window: pygame.Surface):
    draw_rect = pygame.Rect(self.position.x-2, self.position.y-2, 4, 4)
    pygame.draw.rect(window, (0xff,0x44,0x44), draw_rect)