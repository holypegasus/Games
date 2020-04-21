import functools

import p5
import numpy as np
from p5 import (
  Vector,circle,triangle
  ,push_matrix,pop_matrix,begin_shape,end_shape
  ,vertex,translate,rotate
  ,size,background,stroke,run
  )

## UTIL
def rand_vect(shift=-0.5,scale=1.): # (x, y)
  return (np.random.rand(2) + shift) * scale
## OBJ
class VecTorus(Vector):
  def __new__(cls,x,y,x_max,y_max):
    new = super().__new__(cls,x,y)
    new.x_max = x_max
    new.y_max = y_max
    return new
  def __init__(self,x,y,x_max,y_max):
    super().__init__(x,y)
    self.x_max = x_max
    self.y_max = y_max
  def __add__(self,other):
    x = (self.x + other.x) % self.x_max
    y = (self.y + other.y) % self.y_max
    return VecTorus(x,y,self.x_max,self.y_max)
  def __sub__(self,other): # Vector
    return Vector(self.x,self.y) - Vector(other.x,other.y)
  def __mul__(self,scalar):
    if isinstance(scalar, (int,float)):
        x, y, z = scalar * self._array
        return self.__class__(x, y, self.x_max, self.y_max)
    raise TypeError("Can't multiply/divide a point by a non-numeric.")
  def __repr__(self):
    return '{}({:0.0f}, {:0.0f})'.format(self.__class__.__name__,self.x,self.y)
  __str__ = __repr__
class Boid:
  _id = 0
  def __init__(self,x,y,width,height,size,sight,speeds,force_max,ks):
    self.id = Boid._id
    Boid._id += 1
    self.width = width
    self.height = height
    self.size = size
    self.sight = sight
    self.speed_min,self.speed_max = speeds
    self.force_max = force_max
    self.ks = ks
    self.pos = VecTorus(x,y,width,height)
    self.vel = Vector(*rand_vect(shift=-0.5,scale=self.speed_max))
    self.acc = Vector(*rand_vect(shift=-0.5,scale=force_max))
  def __eq__(self, other):
    return self.id==other.id
  def show(self):
    r = self.size
    stroke(255) # color white
    circle(self.pos, radius=r)
    # x,y,z = self.pos
    # x_max,y_max = self.pos.x_max,self.pos.y_max
    # push_matrix()
    # translate(*self.pos)
    # rotate(self.velo.angle)
    # vects3 = [ # 0-radian-pointing triangle 
    #   VecTorus(r,0,x_max,y_max),
    #   VecTorus(-r,r/2,x_max,y_max),
    #   VecTorus(-r,-r/2,x_max,y_max),
    #   ]
    # tri = triangle(*vects3)
    # # begin_shape()
    # # vs = [vertex(*v) for v in vects3]
    # # end_shape()
    # pop_matrix()
    # print(repr(self))
  def __str__(self):
    return '%s(%s)'%(self.__class__.__name__, self.id)
  def __repr__(self):
    return '%s @%s >(%s, %s) +%s'%(str(self), self.pos, self.velo, self.velo.angle, self.acc)
  ## TODO World.classmethods
  def nearby(self, boids):
    return [boid for boid in boids
      if boid != self
      and (boid.pos-self.pos).magnitude <= self.sight]
  def avg_pos(self, poses, default):
    x_max, y_max = self.pos.x_max, self.pos.y_max
    pos_base = VecTorus(0,0,x_max,y_max)
    if poses:
      return sum(poses,pos_base) / len(poses)
    else:
      return default
  def avg_vel(self, vels, default):
    vel_base = Vector(0,0)
    if vels:
      return sum(vels,vel_base) / len(vels)
    else:
      return default
  @staticmethod
  def norm(vect, scale, norm_max=None):
    # print('{} -N> {}'.format(vect, vect / vect.magnitude * norm_max))
    if norm_max is None or vect.magnitude > norm_max:
      return vect / vect.magnitude * scale
    else:
      return vect
  ## Boid behaviors
  def align(self, boids): # acc align
    # delta vel -> acc
    vel_avg = self.avg_vel([boid.vel for boid in boids],self.vel)
    return Boid.norm(vel_avg, self.speed_max) - self.vel
  def cohere(self, boids): # acc cohere
    # delta pos -> vel
    pos_avg = self.avg_pos([boid.pos for boid in boids],self.pos)
    velo2pos_avg = Boid.norm(pos_avg-self.pos, self.speed_max, 0.)
    # delta vel -> acc
    return Boid.norm(velo2pos_avg-self.vel, self.force_max, self.force_max)
  def repel(self, boids, k=1.): # acc repel
    # delta pos -> vel
    vels_away = [self.pos-boid.pos for boid in boids]
    vels_inverse = [v / (v.magnitude-self.size)**2 for v in vels_away]
    vel_avg = self.avg_vel(vels_inverse,self.vel)
    vel_avg = Boid.norm(vel_avg, self.speed_max, self.vel)
    # delta vel -> acc
    return Boid.norm(vel_avg-self.vel, self.force_max, self.force_max)
  def show_accs(self, accs):
    sum_accs = sum(accs,Vector(0,0))
    print('%s: %s x %s => %s'%(
      self,
      list(map(
        lambda acc:(
          round(acc.angle,1)
          ,round(acc.magnitude,1))
        ,accs)),
      self.ks,
      (
        round(sum_accs.angle,1)
        ,round(sum_accs.magnitude,1))))
  def react(self,boids): # reactive traits
    boids_nearby = self.nearby(boids)
    accs = (
      self.align(boids_nearby) * self.ks.get('k_align',0),
      self.cohere(boids_nearby) * self.ks.get('k_cohere',0),
      self.repel(boids_nearby) * self.ks.get('k_repel',0),
      )
    self.acc += sum(accs,Vector(0,0))
    # self.show_accs(accs)
  def inhere(self): # inherent traits
    self.pos += self.vel
    self.vel = Boid.norm(self.vel+self.acc, self.speed_max, self.speed_min)
## VIZ
# once at start
def setup():  size(W,H)
# repeated every time-step
def draw():
  background(30,30,47) # color
  for boid in BOIDS:
    boid.show()
    boid.react(BOIDS)
    boid.inhere()

## MAIN
W = H = 700
N = 10
BOIDS = [Boid(*rand_vect(scale=W), W, H,
  size=5,
  sight=(W+H)/N,
  speeds=(2,10),
  force_max=1.,
  ks = dict(
    k_align=1.,
    k_cohere=1.,
    k_repel=1.,
    )
  )
  for _ in range(N)]
if __name__=='__main__':
  # test VecTorus
  # vt_p = VecTorus(*rand_vect(W),W,H)
  # vt_v = VecTorus(*rand_vect(W),W,H)
  # print((vt_p, vt_v))
  # print(vt_p+vt_v)

  run()
