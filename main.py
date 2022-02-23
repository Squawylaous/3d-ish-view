import pygame
from pygame.locals import *
from pygame.math import Vector2 as vector

pygame.init()

clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 25)
background = Color(161, 161, 161)
foreground = Color(255, 255, 255)
screen = pygame.display.set_mode((0, 0), FULLSCREEN)
screen_rect = screen.get_rect()

update_rects = [[]]
fps = 0

def intVector(v):
  return int(v.x), int(v.y)

class camera:
  def __init__(self, pos, looking_at):
    self.pos, self.looking_at = vector(pos), vector(looking_at)
  
  def draw(self, color):
    update_rects.append(pygame.draw.circle(screen, color, intVector(self.pos), 10))

screen.fill(background)
pygame.display.flip()

Camera = camera((200,200), (0,0))

while True:
  clock.tick(-1)
  fps = clock.get_fps()
  update_rects = [update_rects[1:]]
  
  if pygame.event.get(QUIT):
    break
  for event in pygame.event.get():
    if event.type == KEYDOWN:
      if event.key == K_ESCAPE:
        pygame.event.post(pygame.event.Event(QUIT))
  
  screen.fill(background)
  
  Camera.draw(foreground)
  
  screen.blit(font.render(str(int(fps)), 0, foreground), (0,0))
  update_rects.append(pygame.rect.Rect((0,0), font.size(str(int(fps)))))
  pygame.display.update(update_rects[0]+update_rects[1:])
pygame.quit()
