from util import (
  mapl
  ,get_class_name, check_type, check_not_type, auto_check_type
  ,show, show_change
  ,Positional, Actor, Expanse
  ,Pos, Loc, Player, Ball
  )

class Field(Expanse):
  @show_change()
  def __init__(self, width, height):
    self.width, self.height = width, height
    self._loc_matrix = [[Loc(Pos(x,y))
      for x in range(self.width)]
      for y in range(self.height)]
  def __getitem__(self, pos_able):
    if not isinstance(pos_able, Pos):
      assert hasattr(pos_able, 'pos'), pos_able
      pos = pos_able.pos
    else:
      check_type(pos_able, Pos)
      pos = pos_able
    return self._loc_matrix[pos.y][pos.x]
  # don't allow co-locate same type
  @show_change(repr)
  @auto_check_type(Actor, (Positional,Actor))
  def move(self, source, target): # [Player,Ball] -> [Pos,Player,Ball]
    # check_type(source, Player,Ball)
    # check_type(target, Pos,Player,Ball)
    check_not_type(self[target].get_obj(), type(source))
    if getattr(source, 'pos') and source.pos:
      obj = self[source].del_obj()
    else:
      obj = source
    self[target].set_obj(obj)
  def __repr__(self):
    return '%s\n%s'%(
        get_class_name(self),
        '\n'.join(
          ' '.join(mapl(str,locs))
          for locs in self._loc_matrix)
        )
  def __str__(self):
    return '%s [w: %s; h: %s]'%(get_class_name(self), self.width, self.height)

class Turns:
  pass

# Init Field
field = Field(width=10,height=6)
# Add & move Player
p0 = Player(7,field)
p0.set_pos(Pos(2,1))
p0.move(Pos(3,2))
# Add Ball & moved by Player
ball = Ball(field)
ball.set_pos(Pos(3,2))


