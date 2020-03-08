import logging
from abc import ABC, abstractmethod
from collections import OrderedDict
from functools import wraps

"""
  P0 World
    Pos: abstract position
    Loc: location w/ content
    Player
      pos
      radius
        zone_of_control
      dribble
        velo 1
      pass
        velo 1~5
      catch
        passive
    Ball(Player)
      pos
      radius
      velo
    Field
      discrete cells
      dims
      repr
  P1 Pass
    Player -Ball> Player|Pos
    Ball ->
    Field
    Turn
  P2 Catch
    GOAL
      ball retention vs other team
  P3 Expose
    Field
      continuous
    Lane
  """

### UTILS
def get_logger(lvl=logging.INFO):
  logger = logging.getLogger(__name__)
  logger.setLevel(lvl)
  hdlr = logging.StreamHandler()
  # hdlr.setFormatter(
  #   logging.Formatter(
  #     '%(asctime)s <%(module)s.%(funcName)s:%(lineno)d> %(message)s', '%Y%m%d %H:%M:%S'))
  logger.addHandler(hdlr)
  return logger
logf = get_logger().info
mapl = lambda f, xs: list(map(f, xs))
get_class_name = lambda obj: obj.__class__.__name__
def check_type(obj, *types):
  # assert isinstance(obj, types), '%s:%s !in %s'%(obj,type(obj),types)
  assert isinstance(obj, types), '%s:%s !in %s'%(
    obj, get_class_name(obj), {t.__name__ for t in types})
def check_not_type(obj, *types):
  assert not isinstance(obj, types), '%s:%s !in %s'%(obj,type(obj),types)
#@ TODO decorate class: get param-type from annotation to auto-check parma-type
def auto_check_type(*types_all):
  def wrap_func(f):
    @wraps(f)
    def wrap_args(self,*args,**kwargs):
      args = list(args) + list(kwargs.values())
      nonlocal types_all
      for arg, types_1 in zip(args, types_all):
        if types_1:
          check_type(arg, types_1)
      return f(self,*args,**kwargs)
    return wrap_args
  return wrap_func
#@ TODO check property/method
def auto_check_trait(*traits):
  pass
# class AutoMemo: # TODO decorate class to memoize created-instances
def show(obj,mode='*',funcs=[repr],f=None):
  name_func = f.__name__ if f else ''
  draft = '  &&  '.join(f(obj) for f in funcs)
  # logf('~~~ %s %s: %s'%(mode, get_class_name(obj), draft))
  logf('~~~ %s %s %s'%(mode, name_func, draft))
def show_change(*funcs): #@ show state post change
  def wrap_func(f):
    @wraps(f)
    def wrap_args(self,*args,**kwargs):
      res = f(self,*args,**kwargs)
      mode = '+' if f.__name__=='__init__' else '*'
      show(self,mode,funcs or [repr],f)
      return res
    return wrap_args
  return wrap_func
def add_show(names_method): #@ TODO wrap-class: auto show_change for methods
  def wrap_class(cls):
  # def __init__(self,*args,**kwargs):
  #   self.show(self)
    setattr(cls, 'show', show)
    return cls
  return wrap_class
### Abstract templates (to enable auto_check_type)
class Positional(ABC):  pass
class Actor(ABC):  pass
class Expanse(ABC):  pass
### POSITIONALS
class Pos(Positional): # abstract-position/coordinates
  # @show_change()
  @auto_check_type(int,int)
  def __init__(self, x, y):
    assert x>=0, x
    assert y>=0, y
    self.x, self.y = x, y
  @auto_check_type(Positional)
  def __eq__(self, other):
    return self.x==other.x and self.y==other.y
  def __repr__(self):
    return '@%s'%((self.x, self.y),)
#? TODO class null instance
class NullPos(Positional):
  def __init__(self): pass
  def __repr__(self):
    return '@%s'%(get_class_name(self))
  def __bool__(self): return False
class Loc(Pos): # positional-container: Loc:>Player
  # @show_change()
  @auto_check_type(Pos, (type(None),Actor))
  def __init__(self, pos, obj=None): # obj: None|Player
    self.pos = pos
    self.obj = obj
  def get_obj(self):
    return self.obj
  @show_change()
  @auto_check_type(Actor)
  def set_obj(self, obj):
    if self.get_obj():
      self.obj.possess(obj)
    else:
      self.obj = obj
  @show_change()
  @auto_check_type(Actor)
  def del_obj(self):
    obj = self.obj
    self.obj = None
    return obj
  @auto_check_type(Positional)
  def __eq__(self, other):
    return self.pos==other.pos
  def __repr__(self):
    return '%s%s: %s'%(
      get_class_name(self),
      self.pos,
      repr(self.obj) if self.obj else '+')
  def __str__(self):
    return str(self.obj) if self.obj else ' + '
### ACTORS
class Player(Actor):  # Player:>Ball
  @show_change()
  @auto_check_type(int,None,str)
  def __init__(self, i, field=None, team=' '):
    self.i = i
    # self.team = team
    # assert field is None or check_type(field, Field)
    self.field = field
    self.pos = NullPos()
    self._ball = None
  @show_change()
  def move(self, pos):
    check_type(pos, Pos)
    self.field.move(self,pos)
  @show_change()
  def set_pos(self, pos):
    check_type(pos, Pos)
    self.field.move(self,pos)
    self.pos = pos
    return self
  @show_change()
  def possess(self, obj):
    if self!=obj:
      check_type(obj, Ball)
      self.set_obj(obj)
  @show_change()
  def set_obj(self, ball):
    self._ball = ball
  def __repr__(self):
    return '%s_%s %s'%(get_class_name(self), self.i, self.pos)
  def __str__(self):
    return ' %s%s'%(str(self.i), "'" if self._ball else ' ')
class Ball(Player):
  def __init__(self, field=None):
    super().__init__(0,field)

if __name__=='__main__':
  d = OrderedDict()
  check_type(d, dict)
  pos = Pos(2, 1)
  # Pos(0, -1)
  loc = Loc(pos)
  # loc.set_obj(pos)
  player = Player(7)
  loc.set_obj(player)
  ball = Ball()
  player.set_obj(ball)

