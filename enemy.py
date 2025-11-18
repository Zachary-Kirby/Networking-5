import pygame
from typing import Optional

class RedEnemy:
  def __init__(self, id, x, y):
    self.id = id
    self.position = pygame.Vector2(x, y)
    self.velocity = pygame.Vector2(0, 0)
    self.target: Optional[pygame.Vector2] = None
    self.enemies: Optional[list["RedEnemy"]] = None
  
  def update(self):
    self.position += self.velocity
    if self.enemies:
      for enemy in self.enemies:
        dif = (enemy.position - self.position)
        l = dif.dot(dif)
        if l != 0:
          self.velocity -= dif / l * 16
    if self.target:
      dif = (self.target - self.position)
      l = dif.dot(dif)
      self.velocity += dif * 0.1
      if l != 0:
        self.velocity -= (self.target - self.position) / l * 1000
    self.velocity *= 0.9
  
  def draw(self, window: pygame.Surface):
    draw_rect = pygame.Rect(self.position.x-2, self.position.y-2, 4, 4)
    pygame.draw.rect(window, (0xff,0x44,0x44), draw_rect)