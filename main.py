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

class polygon:
  all = []
  
  def __init__(self, *corners):
    if len(corners) == 1:
      corners = corners[0]
      self.corners = [vector(corners[:2]) for i in range(4)]
      self.corners[1] += corners[2], 0
      self.corners[2] += corners[2:]
      self.corners[3] += 0, corners[3]
    else:
      self.corners = corners
    self.corners = [*map(vector, self.corners)]
    polygon.all.append(self)
  
  def __str__(self):
    return str([*map(lambda c:(c.x,c.y), self.corners)])
  
  def append(self, item):
    self.corners.append(vector(item))
  
  def lines(self):
    return zip(self.corners, self.corners[-1:]+self.corners[:-1])
  
  def draw(self, color):
    update_rects.append(pygame.draw.polygon(screen, color, [*map(intVector, self.corners)]))

class camera:
  def __init__(self, pos, angle, fov=90, viewRange=1000):
    self.pos, self.angle, self.fov, self.viewRange = vector(pos), vector(1,0).rotate(angle), fov, viewRange
  
  def rays(self, n=screen_rect.w):
    return [self.angle.rotate(self.fov*(i - 0.5*(n-1))/n)*self.viewRange for i in range(n)]
  
  def draw(self, color):
    update_rects.append(pygame.draw.circle(screen, color, intVector(self.pos), 10))

#gets the intersection point of two lines
#line1 and line2 both take a list of 2 vectors
#returns vector for intersection point or None if there is no intersection
def intersection(line1, line2):
  line1, line2 = [*map(vector, line1)], [*map(vector, line2)]
  try:
    slope1 = (line1[1].y-line1[0].y)/(line1[1].x-line1[0].x)
  except ZeroDivisionError:
    slope1 = float("inf")
  intercept1 = line1[0].y - slope1*line1[0].x
  try:
    slope2 = (line2[1].y-line2[0].y)/(line2[1].x-line2[0].x)
  except ZeroDivisionError:
    slope2 = float("inf")
  intercept2 = line2[0].y - slope2*line2[0].x
  print(slope1, intercept1)
  print(slope2, intercept2)
  if slope1 == slope2:
    if intercept1 == intercept2:
      if intercept1 not in [float("inf"), float("-inf")]:
        #if y-intercepts are equal: lines are the same
        #test for lines touching eachother using ranges of x and y
        return vector() #placeholder
      elif line1[0].x == line2[0].x:
        #if both lines are vertical and equal
        #mabye combine with if above
        return vector() #placeholder
  else:
    if slope1 in [float("inf"), float("-inf"), 0] or slope2 in [float("inf"), float("-inf"), 0]:
      pass
    x = (intercept2-intercept1)/(slope1-slope2)
    y = slope1*x + intercept1
    return vector(x, y)

screen.fill(background)
pygame.display.flip()

Camera = camera((400,400), -90)
polygon((350, 150, 100, 100))

for wall in polygon.all:
  print(wall)
  for edge in wall.lines():
    for ray in Camera.rays(1):
      print([Camera.pos, ray+Camera.pos], edge)
      print(intersection([Camera.pos, ray+Camera.pos], edge))

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
  for wall in polygon.all:
    wall.draw(foreground)
  
  screen.blit(font.render(str(int(fps)), 0, foreground), (0,0))
  update_rects.append(pygame.rect.Rect((0,0), font.size(str(int(fps)))))
  pygame.display.update(update_rects[0]+update_rects[1:])
pygame.quit()
