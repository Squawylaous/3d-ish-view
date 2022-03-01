import pygame
from pygame.locals import *
from pygame.math import Vector2 as vector
from itertools import starmap

pygame.init()

clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 25)
background = Color(161, 161, 161)
foreground = Color(255, 255, 255)
screen = pygame.display.set_mode((0, 0), FULLSCREEN)
screen_rect = screen.get_rect()
pygame.key.set_repeat(1, 10)

update_rects = [[]]
fps = 0

def intVector(v):
  return int(v.x), int(v.y)

def lineRect(line):
  rect = pygame.rect.Rect(*map(intVector, [line[0], line[1]-line[0]]))
  rect.normalize()
  return rect

def colorMerge(*colorList):
  colors = []
  percents = []
  for i in range(1, len(colorList), 2):
    if type(colorList[i]) is not float:
      break
    colors.append(colorList[i-1])
    percents.append(colorList[i])
  colorList = colorList[len(colors)*2:]
  if colorList:
    colors += colorList
    percents += [(1-sum(percents))/len(colorList)]*len(colorList)
  percents = [i/sum(percents) for i in percents]
  colors = starmap(pygame.Color, colors)
  return [[i*percent for i in color] for color, percent in zip(colors, percents)]

print(colorMerge(background, foreground))
print(colorMerge(background, 0.25, foreground))
print(colorMerge(background, 0.25, foreground, 0.5))
print(colorMerge(background, 0.25, foreground, 0.5, [208, 208, 0]))

#gets the intersection point of two lines
#line1 and line2 both take a list of 2 vectors
#returns vector for intersection point or None if there is no intersection
def intersection(line1, line2):
  line1, line2 = [*map(vector, line1)], [*map(vector, line2)]
  try:
    slope1 = (line1[1].y-line1[0].y)/(line1[1].x-line1[0].x)
  except ZeroDivisionError:
    slope1 = float("inf")
    intercept1 = -slope1
  else:
    intercept1 = line1[0].y - slope1*line1[0].x
  
  try:
    slope2 = (line2[1].y-line2[0].y)/(line2[1].x-line2[0].x)
  except ZeroDivisionError:
    slope2 = float("inf")
    intercept2 = -slope2
  else:
    intercept2 = line2[0].y - slope2*line2[0].x
  
  if slope1 == slope2:
    if intercept1 == intercept2:
      if intercept1 != float("-inf"):
        #if y-intercepts are equal: lines are the same
        #test for lines touching eachother using ranges of x and y
        x, y = 0, 0 #placeholder
      elif line1[0].x == line2[0].x:
        #if both lines are vertical and equal
        #mabye combine with if above
        x, y = 0, 0 #placeholder
      else:
        return None
  elif slope1 == float("inf"):
    x = line1[0].x
    y = slope2*x + intercept2
  elif slope2 == float("inf"):
    x = line2[0].x
    y = slope1*x + intercept1
  else:
    x = (intercept2-intercept1)/(slope1-slope2)
    y = slope1*x + intercept1
  
  x, y = round(x, 10), round(y, 10)
  
  # tests to see if current x and y values are within bounds of lines
  if max(min(line1[0].x, line1[1].x), min(line2[0].x, line2[1].x)) <=\
  x <= min(max(line1[0].x, line1[1].x), max(line2[0].x, line2[1].x)) and\
  max(min(line1[0].y, line1[1].y), min(line2[0].y, line2[1].y)) <=\
  y <= min(max(line1[0].y, line1[1].y), max(line2[0].y, line2[1].y)):
    return vector(x, y)

def polygon(*points, color=foreground, colors=[]):
  if len(points) == 1:
    points = [vector(points[0][:2])+i for i in [(0,0), (points[0][2],0), points[0][2:], (0,points[0][3])]]
  corners = [*map(vector, points)]
  lines = [*zip(corners, corners[-1:]+corners[:-1])]
  Colors = [color]*(len(lines))
  Colors[:len(colors)] = colors
  for line, color in zip(lines, Colors):
    Wall(line, color)

class Wall:
  all = []
  
  def __init__(self, line, color=foreground):
    self.line, self.color = [*map(vector, line)], color
    Wall.all.append(self)
  
  def __str__(self):
    return str([*map(lambda c:(c.x,c.y), self.line), "color:"+str(self.color)])

  def draw(self):
    update_rects.append(pygame.draw.line(screen, self.color, *map(intVector, self.line), 5))

class camera:
  def __init__(self, pos, angle, fov=90, viewRange=500, fidelity=screen_rect.w):
    self.pos, self.angle = vector(pos), vector(1,0).rotate(angle)
    self.fov, self.viewRange, self.fidelity = fov, viewRange, fidelity
    self.comp = True
  
  def rays(self, n=screen_rect.w):
    return [self.angle.rotate(self.fov*(i - 0.5*(n-1))/n)*self.viewRange for i in range(n)]
  
  def draw(self):
    inters = [None for i in range(self.fidelity)]
    rays = self.rays(self.fidelity)
    for i in range(self.fidelity):
      ray = rays[i]
      for wall in Wall.all:
        point = intersection([self.pos, ray+self.pos], wall.line)
        if point is not None:
          if self.comp:
            percent = ((point-self.pos)*self.angle)/self.viewRange
          else:
            percent = (point-self.pos).length()/self.viewRange
          if inters[i] is None or inters[i]["%"] > percent:
            inters[i] = {"i":i, "%":percent, "color":wall.color}
    
    buffer = 0.9
    for ray in inters:
      if ray is not None:
        rect = pygame.rect.Rect(ray["i"]*screen_rect.w/self.fidelity, 0,
          screen_rect.w/self.fidelity, screen_rect.h*(1-ray["%"])*buffer)
        rect.centery = screen_rect.h/2
        update_rects.append(pygame.draw.rect(screen, ray["color"], rect))
  
  def dot(self, color):
    update_rects.append(pygame.draw.circle(screen, color, intVector(self.pos), 10))

screen.fill(background)
pygame.display.flip()

viewMode = True
Camera = camera((400,400), -90, fidelity=80)
polygon((250, 100, 300, 100))
polygon((350, 200, 100, 100))

while True:
  clock.tick(-1)
  fps = clock.get_fps()
  update_rects = [update_rects[1:]]
  
  if pygame.event.get(QUIT):
    break
  for event in pygame.event.get():
    if event.type == KEYDOWN:
      if event.key == K_w:
        Camera.pos.y -= 1
      elif event.key == K_s:
        Camera.pos.y += 1
      elif event.key == K_a:
        Camera.pos.x -= 1
      elif event.key == K_d:
        Camera.pos.x += 1
    elif event.type == KEYUP:
      if event.key == K_RETURN:
        viewMode = not viewMode
      elif event.key == K_SPACE:
        Camera.comp = not Camera.comp
      elif event.key == K_ESCAPE:
        pygame.event.post(pygame.event.Event(QUIT))
  
  screen.fill(background)
  if viewMode:
    Camera.draw()
  else:
    Camera.dot(foreground)
    for wall in Wall.all:
      wall.draw()
  
  screen.blit(font.render(str(int(fps)), 0, foreground), (0,0))
  update_rects.append(pygame.rect.Rect((0,0), font.size(str(int(fps)))))
  pygame.display.update(update_rects[0]+update_rects[1:])
pygame.quit()
