import logging
from abc import ABC, abstractmethod
from collections import OrderedDict
from functools import wraps

### UTILS
def get_logger(lvl=logging.INFO):
  logger = logging.getLogger(__name__)
  logger.setLevel(lvl)
  logger.addHandler(logging.StreamHandler())
  return logger
logf = get_logger().info
mapl = lambda f, xs: list(map(f, xs))
get_class_name = lambda obj: obj.__class__.__name__
def check_type(obj, *types):
  assert isinstance(obj, types), '%s:%s !in {%s}'%(
    obj, get_class_name(obj), ','.join(t.__name__ for t in types))
def check_not_type(obj, *types):
  assert not isinstance(obj, types), '%s:%s !in {%s}'%(
    obj, get_class_name(obj), ','.join(t.__name__ for t in types))
def check_func_type(*types_all): #@ auto-check_type
  def wrap_func(f):
    @wraps(f)
    def wrap_args(self,*args,**kwargs):
      nonlocal types_all
      types_all = (types_all # from decor
        or f.__annotations__.values() # from annot
        )
      args_to_check = list(args) + list(kwargs.values())
      for arg, types_1 in zip(args_to_check, types_all):
        if types_1:
          check_type(arg, types_1)
      return f(self,*args,**kwargs)
    return wrap_args
  return wrap_func
def check_class_type(cls): #@ auto-check_func_type on calling annotated-methods
  for f in [getattr(cls,name) for name in dir(cls)]: # funcs
    if callable(f) and hasattr(f,'__annotations__'): # funcs-annotated
      setattr(cls, f.__name__, check_func_type()(f))
  return cls
def auto_check_trait(*traits):  pass #@ TODO check property/method
def show(obj,mode='*',f_show=[repr],f=None):
  name_func = f.__name__ if f else ''
  draft = '  &&  '.join(f(obj) for f in f_show)
  # logf('~~~ %s %s: %s'%(mode, get_class_name(obj), draft))
  logf('~~~ %s %s %s'%(mode, name_func, draft))
def show_func_change(*f_show): #@ auto-show obj-state post-change
  def wrap_func(f):
    @wraps(f)
    def wrap_args(self,*args,**kwargs):
      res = f(self,*args,**kwargs)
      mode = '+' if f.__name__=='__init__' else '*'
      show(self,mode,f_show or [repr],f)
      return res
    return wrap_args
  return wrap_func
def show_class_change(*names_method): #@ auto-show_func_change on calling methods
  def wrap_class(cls):
    for name_method in names_method:
      func = getattr(cls, name_method)
      setattr(cls, name_method, show_func_change()(func))
    return cls
  return wrap_class

### Abstract templates to label type-req before impl
type_none = type(None)
class Positional(ABC):  pass
class Actor(ABC):  pass
class D2(ABC):  pass
### POSITIONALS TMP help test in discrete
@check_class_type
class Pos(Positional): # abstract-position/coordinates
  def __init__(self, x:int, y:int):
  # def __init__(self, x:NonNeg, y:int):
    assert x>=0, x
    assert y>=0, y
    self.x, self.y = x, y
  def __eq__(self, other:Positional):
    return self.x==other.x and self.y==other.y
  def __repr__(self):
    return '@%s'%((self.x, self.y),)
class NullPos(Positional): #1 singleton
  def __init__(self): pass
  def __repr__(self):
    return '@%s'%(get_class_name(self))
  def __bool__(self): return False
@show_class_change('set_obj','del_obj')
@check_class_type
class Loc(Pos): # positional-container: Loc:>Player
  def __init__(self, pos:Pos, obj:(type_none,Actor)=None): # obj: None|Player
    self.pos = pos
    self.obj = obj
  def get_obj(self):
    return self.obj
  def set_obj(self, obj:Actor):
    if self.get_obj():
      self.obj.possess(obj)
    else:
      self.obj = obj
  def del_obj(self):
    obj = self.obj
    self.obj = None
    return obj
  def __eq__(self, other:Positional):
    return self.pos==other.pos
  def __repr__(self):
    return '%s%s: %s'%(
      get_class_name(self),
      self.pos,
      repr(self.obj) if self.obj else '+')
  def __str__(self):
    return str(self.obj) if self.obj else ' + '
### ACTORS
@show_class_change('__init__','move','set_pos','possess')
class Player(Actor):
  def __init__(self, i:int, field:type_none=None, team:str=' '):
    self.i = i
    # self.team = team
    self.field = field
    self.pos = NullPos()
    self.ball = None
  def move(self, pos:Pos):
    self.field.move(self,pos)
  def set_pos(self, pos:Pos):
    self.field.move(self,pos)
    self.pos = pos
    return self
  def possess(self, obj:Actor):
    self.ball = obj
  def __repr__(self):
    return '%s_%s %s %s'%(
      get_class_name(self), self.i, self.pos, self.ball)
  def __str__(self):
    return ' %s%s'%(
      str(self.i), "'" if self.ball else ' ')
class Ball(Player): # involuntary Player
  def __init__(self, field=None):
    super().__init__(0,field)
  def __repr__(self):
    return '%s %s'%(
      get_class_name(self), self.pos)
  def __str__(self):
    return "'"


if __name__=='__main__':
  pos = Pos(2, 1)
  # Pos(0, -1) # should fail on positives
  loc = Loc(pos)
  # loc.set_obj(pos) # should fail on Actor
  player = Player(7)
  loc.set_obj(player)
  ball = Ball()
  player.possess(ball)

