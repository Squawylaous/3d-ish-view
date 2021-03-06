import numpy as np
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
pygame.key.set_repeat(1, 50)

update_rects = [[]]
fps = 0

def intVector(v):
  return (*map(int, map(round, v)),)

def roundVector(v, n=0):
  return vector(*map(round, v, [n,n]))

def lineRect(line):
  line = [*map(vector, line)]
  rect = pygame.rect.Rect(*map(intVector, [line[0], line[1]-line[0]]))
  rect.normalize()
  return rect

def colorMerge(*colorList):
  if len(colorList) < 2:
    colorList = (foreground,) + colorList + (background,)
  colors = []
  percents = []
  for i in range(1, len(colorList), 2):
    if type(colorList[i]) is not float:
      break
    colors.append(colorList[i-1])
    percents.append(colorList[i])
  
  colorList = colorList[len(colors)*2:]
  if colorList:
    colors.append(map(np.average, zip(*colorList)))
    percents.append(max(1-sum(percents), 0))
  return pygame.Color(*[int(round(np.average(i, weights=percents))) for i in zip(*colors)])

#pygame's draw functions tend to return rects slightly smaller than they should be if you set a width,
#so this should (hopefully) fix that
def draw_shape(name, surface, color, *args, width=None):
  if width is not None:
    args += (width,)
  rect = getattr(pygame.draw, name)(surface, color, *args)
  if width is not None:
    rect = map(sum, zip(rect, [-width//2,-width//2,width,width]))
  rect = pygame.rect.Rect(*map(sum, zip(rect, [-1,-1,2,2])))
  update_rects.append(rect)
  return rect

#gets the intersection point of two lines
#line1 and line2 both take a list of 2 vectors
#returns vector for intersection point or None if there is no intersection
def intersection(line1, line2, or_eq=True):
  line1, line2 = [*map(roundVector, line1, [10]*2)], [*map(roundVector, line2, [10]*2)]
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
        return vector(np.average([i.x for i in line1+line2]), np.average([i.y for i in line1+line2])) #placeholder?
      elif line1[0].x == line2[0].x:
        #if both lines are vertical and equal
        #mabye combine with if above
        return vector(np.average([i.x for i in line1+line2]), np.average([i.y for i in line1+line2])) #placeholder
      else:
        return None
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
  min_x = max(min(line1[0].x, line1[1].x), min(line2[0].x, line2[1].x))
  max_x = min(max(line1[0].x, line1[1].x), max(line2[0].x, line2[1].x))
  min_y = max(min(line1[0].y, line1[1].y), min(line2[0].y, line2[1].y))
  max_y = min(max(line1[0].y, line1[1].y), max(line2[0].y, line2[1].y))
  if min_x <= x <= max_x and min_y <= y <= max_y:
    if not or_eq:
      if sum(map(lambda point:point.x == x and point.y == y, line1+line2)):
        return None
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
  
  @property
  def center(self):
    return (self.line[0]+self.line[1])/2

  def draw(self):
    draw_shape("line", screen, self.color, *map(intVector, self.line), width=5)

class Camera:
  def __init__(self, player, *, fov, viewRange, fidelity=screen_rect.w):
    self.player, self.fov, self.viewRange, self.fidelity = player, fov, viewRange, fidelity
    self.viewMode, self.comp, self.extend = True, False, False
  
  @property
  def pos(self):
    return self.player.pos
  
  @pos.setter
  def pos(self, value):
    self.player.pos = value
  
  @property
  def angle(self):
    return self.player.angle
  
  @angle.setter
  def angle(self, value):
    self.player.angle = value
  
  def rays(self, n):
    return [self.angle.rotate(self.fov*(i - 0.5*(n-1))/n)*self.viewRange for i in range(n)]
  
  def draw(self):
    buffer = 0.9
    if self.viewMode == 1:
      visible = []
      for wall in Wall.all:
        #remake thing to check if wall is in range
        line = [intersection(wall.line, [self.pos, self.pos+self.angle.rotate(ray*self.fov/2)*self.viewRange]) for ray in [-1,1]]
        angles = [(self.angle.angle_to(i-self.pos)+180)%360-180 for i in wall.line]
        line += [wall.line[i] for i in range(len(angles)) if abs(angles[i])<=self.fov/2]
        line = [*map(vector, {(*i,) for i in line if i is not None})]
        if len(line)==2:
          visible.append({"wall":wall, "line":wall.line if self.extend else line, "inters":[]})
      for i in range(len(visible)):
        wall = visible[i]
        for other in visible[i+1:]:
          inter = intersection(wall["line"], other["line"], or_eq=False)
          if inter is not None:
            wall["inters"].append(inter)
            other["inters"].append(inter)
        wall["inters"] = sorted(wall["line"]+wall["inters"], key=wall["line"][0].distance_squared_to)
      visible = [{"wall":wall["wall"], "line":wall["inters"][i-1:i+1]} for wall in visible for i in range(1, len(wall["inters"]))]
      for i in range(len(visible)):
        wall = visible[i]
        wall["i"] = i
        wall["angles"] = [(round(self.angle.angle_to(i-self.pos), 10)+180)%360-180 for i in wall["line"]]
      visibleOrdered = [[] for i in visible]
      for i in range(len(visible)):
        wall = visible[i]
        for other in visible[i+1:]:
          if min(other["angles"]) < wall["angles"][0] < max(other["angles"]):
            if intersection(other["line"], [self.pos, wall["line"][0]], or_eq=False) is None:
              visibleOrdered[wall["i"]].append(other["i"])
            else:
              visibleOrdered[other["i"]].append(wall["i"])
          elif min(other["angles"]) < wall["angles"][1] < max(other["angles"]):
            if intersection(other["line"], [self.pos, wall["line"][1]], or_eq=False) is None:
              visibleOrdered[wall["i"]].append(other["i"])
            else:
              visibleOrdered[other["i"]].append(wall["i"])
          elif min(wall["angles"]) < other["angles"][0] < max(wall["angles"]):
            if intersection(wall["line"], [self.pos, other["line"][0]], or_eq=False) is None:
              visibleOrdered[other["i"]].append(wall["i"])
            else:
              visibleOrdered[wall["i"]].append(other["i"])
          elif min(wall["angles"]) < other["angles"][1] < max(wall["angles"]):
            if intersection(wall["line"], [self.pos, other["line"][1]], or_eq=False) is None:
              visibleOrdered[other["i"]].append(wall["i"])
            else:
              visibleOrdered[wall["i"]].append(other["i"])
      newVisibleOrdered = []
      while True:
        for i in range(len(visibleOrdered)):
          if not len(visibleOrdered[i]) and i not in newVisibleOrdered:
            newVisibleOrdered.append(i)
        for i in range(len(visibleOrdered)):
          visibleOrdered[i] = [i for i in visibleOrdered[i] if i not in newVisibleOrdered]
        if len(newVisibleOrdered) >= len(visibleOrdered):
          break
      visible = [visible[i] for i in newVisibleOrdered]
      for wall in visible:
        x_values = [(i/self.fov+0.5)*screen_rect.w for i in wall["angles"]]
        y_values = [(min(self.pos.distance_to(i)/self.viewRange, 1)-1)*buffer for i in wall["line"]]
        y_values = [(i+1)*screen_rect.h/2 for i in y_values+[-ii for ii in y_values]]
        polygon = [*map(intVector, zip(x_values*2, y_values))]
        polygon = [polygon[i] for i in [0, 2, 3, 1]]
        draw_shape("polygon", screen, wall["wall"].color, polygon)
        draw_shape("polygon", screen, [0]*3, polygon, width=1)
      
    else:
      inters = [None for i in range(self.fidelity)]
      rays = self.rays(self.fidelity)
      for i in range(self.fidelity):
        ray = rays[i]
        for wall in Wall.all:
          point = intersection([self.pos, ray+self.pos], wall.line)
          if point is not None:
            if self.comp:
              percent = (point-self.pos)*self.angle
            else:
              percent = (point-self.pos).length()
            percent = 1-percent/self.viewRange
            if inters[i] is None or inters[i]["%"] < percent:
              inters[i] = {"i":i, "%":percent, "color":wall.color}
      
      for ray in inters:
        if ray is not None:
          rect = pygame.rect.Rect(screen_rect.w/self.fidelity*ray["i"], screen_rect.h/2*(1-ray["%"]*buffer),
            screen_rect.w/self.fidelity, screen_rect.h*ray["%"]*buffer)
          draw_shape("rect", screen, ray["color"], rect)
  
  def dot(self, color):
    draw_shape("line", screen, color, *map(intVector, [self.pos, self.pos+self.angle.rotate(-self.fov/2)*self.viewRange]), width=3)
    draw_shape("line", screen, color, *map(intVector, [self.pos, self.pos+self.angle.rotate(self.fov/2)*self.viewRange]), width=3)
    draw_shape("circle", screen, color, intVector(self.pos), 10)

class Player:
  def __init__(self, pos, angle):
    self.pos, self.angle = vector(pos), vector(1,0).rotate(angle)
    self.speed, self.rotate_speed = 12.5, 2.5
    self.camera = Camera(self, fov=90, viewRange=1000)
  
  @property
  def velocity(self):
    return self.angle * self.speed

screen.fill(background)
pygame.display.flip()

player = Player((400,400), -90)
player.camera.fidelity = 80
polygon((250, 100, 300, 100))
polygon((350, 175, 100, 150), color=colorMerge(.75))
polygon((0, 0, 1000, 1000), color=colorMerge(.5))

while True:
  clock.tick(-1)
  fps = clock.get_fps()
  update_rects = [update_rects[1:]]
  screen.fill(background)
  
  if pygame.event.get(QUIT):
    break
  for event in pygame.event.get():
    if event.type == KEYDOWN:
      if event.key == K_w:
        player.pos += player.velocity
      elif event.key == K_s:
        player.pos -= player.velocity
      elif event.key == K_a:
        player.pos -= player.velocity.rotate(90)
      elif event.key == K_d:
        player.pos += player.velocity.rotate(90)
      elif event.key == K_LEFT:
        player.angle.rotate_ip(-player.rotate_speed)
      elif event.key == K_RIGHT:
        player.angle.rotate_ip(player.rotate_speed)
    elif event.type == KEYUP:
      if event.key == K_RETURN:
        player.camera.viewMode = (player.camera.viewMode+1)%3
      elif event.key == K_SPACE:
        player.camera.comp = not player.camera.comp
      elif event.key == K_e:
        player.camera.extend = not player.camera.extend
      elif event.key == K_ESCAPE:
        pygame.event.post(pygame.event.Event(QUIT))
  
  if player.camera.viewMode:
    player.camera.draw()
  else:
    player.camera.dot(foreground)
    for wall in Wall.all:
      wall.draw()
  
  screen.blit(font.render(str(int(fps)), 0, foreground), (0,0))
  update_rects.append(pygame.rect.Rect((0,0), font.size(str(int(fps)))))
  pygame.display.update(update_rects[0]+update_rects[1:])
pygame.quit()
