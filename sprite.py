#Pyjsdl - Copyright (C) 2013 James Garnon

from rect import Rect
import mask

__docformat__ = 'restructuredtext'


def id(sprite):
    return sprite._identity


class Sprite(object):
    """
    **pyjsdl.sprite.Sprite**
    
    * Sprite.add
    * Sprite.remove
    * Sprite.kill
    * Sprite.alive
    * Sprite.groups
    * Sprite.update
    """

    _identity = 0

    def __init__(self, *groups):
        """
        Return Sprite.
        Optional argument inludes group(s) to place sprite.
        Sprite can have image and rect attributes.
        """
        self._identity = Sprite._identity
        Sprite._identity += 1
        self._rect_pre = Rect(0,0,0,0)
        self.x = None
        self.y = None
        self.image = None
        self.rect = None
        for group in groups:
            if self not in group:
                group.add(self)

    def __repr__(self):
        """
        Return string representation of Sprite object.
        """
        return "%s(in %d groups)" % (self.__class__, len(self.groups()))

    def add(self, *groups):
        """
        Add sprite to group(s).
        """
        for group in groups:
            if self not in group:
                group.add(self)
        return None

    def remove(self, *groups):
        """
        Remove sprite from group(s).
        """
        for group in groups:
            if self in group:
                group.remove(self)
        return None

    def kill(self):
        """
        Remove sprite from all member groups.
        """
        for group in Group._groups:
            if self in group:
                group.remove(self)
        return None

    def alive(self):
        """
        Return True if sprite is member of any groups.
        """
        for group in Group._groups:
            if self in group:
                return True
        return False

    def groups(self):
        """
        Return list of groups that sprite is a member.
        """
        return [group for group in Group._groups if self in group]

    def update(self, *args):
        """
        Method to place sprite update statements that is called by group update.
        """
        pass


class DirtySprite(Sprite):
    """
    **pyjsdl.sprite.Sprite**
    
    * Sprite subclass
    * subclass not implemented
    """

    def __init__(self, *groups):
        """
        Return Sprite.
        """
        Sprite.__init__(self, *groups)


class Group(object):
    """
    **pyjsdl.sprite.Group**
    
    * Group.sprites
    * Group.copy
    * Group.add
    * Group.remove
    * Group.has
    * Group.draw
    * Group.clear
    * Group.empty
    * Group.update
    """

    _groups = []

    def __init__(self, *sprites):
        """
        Return Group.
        Can optionally be called with sprite(s) to add.
        """
        Group._groups.append(self)
        self._sprites = {}
        if sprites:
            for sprite in sprites:
                self._sprites[id(sprite)] = sprite
        self._surface_blits = []
        self._clear_active = False
        self._sprites_drawn = {}
        self._rects = []

    def __repr__(self):
        """
        Return string representation of Group object.
        """
        return "%s(%d sprites)" % (self.__class__, len(self._sprites))

    def __iter__(self):
        """
        Provides iterator to sprites in Group.
        """
        return self._sprites.itervalues()

    def __contains__(self, sprite):
        """
        Provides check if sprite is in Group.
        """
        return id(sprite) in self._sprites
#        return id(sprite) in self._sprites.iterkeys()   #pyjs: iterkeys - AttributeError __contain__ is not a function

    def __len__(self):
        """
        Provides count of sprites in Group.
        """
        return len(self._sprites)

    def sprites(self):
        """
        Return list of sprites in the group.
        """
        return self._sprites.values()

    def copy(self):
        """
        Return copy of group.
        """
        newgroup = self.__class__()
        newgroup._sprites = self._sprites.copy()
        return newgroup

    def add(self, *sprites):
        """
        Add sprite(s) to group.
        """
        for sprite in sprites:
            self._sprites[id(sprite)] = sprite
        return None

    def remove(self, *sprites):
        """
        Remove sprite(s) from group.
        """
        for sprite in sprites:
            try:
                del self._sprites[id(sprite)]
            except KeyError:
                pass
        return None

    def has(self, *sprites):
        """
        Check if all sprite(s) in group.
        """
        try:
            if not isinstance(sprites[0], Sprite):
                sprites = sprites[0]
        except IndexError:
            return False
        for sprite in sprites:
            if id(sprite) not in self._sprites.iterkeys():
                return False
        return True

    def draw(self, surface):
        """
        Draw sprite on surface.
        """
        self._surface_blits[:] = [(sprite.image,sprite.rect) for sprite in self._sprites.itervalues()]
        surface.blits(self._surface_blits)
        if self._clear_active:
            self._rects.extend(self._sprites_drawn.itervalues())
            self._sprites_drawn.clear()
            for sprite in self._sprites:
                self._sprites_drawn[sprite] = self._get_rect(self._sprites[sprite].rect)
        return None

    def clear(self, surface, background):
        """
        Clear previous sprite draw to surface using a background surface.
        The background argument can be a callback function.
        """
        self._clear_active = True
        if hasattr(background, 'width'):
            surface._blit_clear(background, self._sprites_drawn.itervalues())
        else:
            for sprite in self._sprites_drawn:
                background(surface, self._sprites_drawn[sprite])

    def _get_rect(self, r):
        try:
            rect = self._rects.pop()
            rect.x, rect.y, rect.width, rect.height = r.x, r.y, r.width, r.height
        except IndexError:
            rect = Rect(r.x, r.y, r.width, r.height)
        return rect

    def empty(self):
        """
        Empty group.
        """
        self._sprites.clear()
        return None

    def update(self, *args):
        """
        Update sprites in group by calling sprite.update.
        """
        for sprite in self._sprites.values():
            sprite.update(*args)
        return None


class GroupSingle(Group):
    """
    **pyjsdl.sprite.GroupSingle**
    
    * Group subclass
    """

    def __init__(self, sprite=None):
        """
        Return GroupSingle, a Group subclass that holds a single sprite.
        Can optionally be called with sprite to add.
        """
        if sprite:
            Group.__init__(self, sprite)
        else:
            Group.__init__(self)

    def __getattr__(self, attr):
        """
        Get Group.sprite.
        """
        if attr == 'sprite':
            try:
                return self._sprites.values()[0]
            except:
                return None

    def add(self, sprite):
        """
        Add sprite to group, replacing existing sprite.
        """
        self._sprites.clear()
        self._sprites[id(sprite)] = sprite
        return None

    def update(self, *args):
        """
        Update sprite by calling Sprite.update.
        """
        self._sprites.values()[0].update(*args)
        return None


class RenderUpdates(Group):
    """
    **pyjsdl.sprite.RenderUpdates**
    
    * Group subclass
    """

    def __init__(self, *sprites):
        """
        Return RenderUpdates, a Group subsclass that provides dirty draw functions.
        Can optionally be called with sprite(s) to add.
        """
        Group.__init__(self, *sprites)
        self.changed_areas = []

    def draw(self, surface):
        """
        Draw sprite on surface.
        Returns list of Rect of sprites updated, which can be passed to display.update.
        """
        self._surface_blits[:] = [(sprite.image,sprite.rect) for sprite in self._sprites.itervalues()]
        surface.blits(self._surface_blits)
        if self._clear_active:
            self._rects.extend(self.changed_areas)
            self.changed_areas[:] = []
            for sprite in self._sprites:
                try:
                    if self._sprites_drawn[sprite].intersects(self._sprites[sprite].rect):
                        self._sprites_drawn[sprite].union_ip(self._sprites[sprite].rect)
                    else:
                        self.changed_areas.append(self._get_rect(self._sprites[sprite].rect))
                except KeyError:
                    self.changed_areas.append(self._get_rect(self._sprites[sprite].rect))
            self.changed_areas.extend(self._sprites_drawn.itervalues())
            self._sprites_drawn.clear()
            for sprite in self._sprites:
                self._sprites_drawn[sprite] = self._get_rect(self._sprites[sprite].rect)
        else:
            self._rects.extend(self.changed_areas)
            self.changed_areas[:] = []
            self.changed_areas.extend([self._get_rect(sprite.rect) for sprite in self._sprites.itervalues()])
        return self.changed_areas


class OrderedUpdates(RenderUpdates):
    """
    **pyjsdl.sprite.OrderedUpdates**
    
    * RenderUpdates subclass
    """

    def __init__(self, *sprites):
        """
        Return OrderedUpdates, a RenderUpdates subclass that maintains order of sprites.
        Can optionally be called with sprite(s) to add.
        """
        self.order = {}
        self.place = {}
        self.range = 1000
        self.index = iter(xrange(self.range))
        self.sort = None
        for sprite in sprites:
            if sprite not in self._sprites:
                spriteID = id(sprite)
                index = self.index.next()
                self.order[index] = spriteID
                self.place[spriteID] = index
        RenderUpdates.__init__(self, *sprites)

    def __iter__(self):
        """
        Provides iterator to sprites in Group.
        """
        try:
            order_sprite = iter(self.sort)
        except TypeError:
            keys = self.order.keys()
            keys.sort()
            self.sort = [self._sprites[self.order[key]] for key in keys]
            order_sprite = iter(self.sort)
        return order_sprite

    def sprites(self):
        """
        Return ordered list of sprites in the group.
        """
        try:
            order_sprite = self.sort[:]
        except TypeError:
            keys = self.order.keys()
            keys.sort()
            self.sort = [self._sprites[self.order[key]] for key in keys]
            order_sprite = self.sort[:]
        return order_sprite

    def copy(self):
        """
        Return copy of group.
        """
        newgroup = RenderUpdates.copy(self)
        newgroup.order = self.order.copy()
        newgroup.place = self.place.copy()
        newgroup.range = self.range
        newgroup.index = iter(xrange(max(self.order.keys())+1,self.range))
        return newgroup

    def add(self, *sprites):
        """
        Add sprite(s) to group, maintaining order of addition.
        """
        for sprite in sprites:
            if sprite not in self._sprites:
                try:
                    index = self.index.next()
                    spriteID = id(sprite)
                    self.order[index] = spriteID
                    self.place[spriteID] = index
                except StopIteration:
                    keys = self.order.keys()
                    keys.sort()
                    if len(keys)*2 > self.range:
                        self.range = len(keys)*2
                    self.index = iter(xrange(self.range))
                    order = self.order
                    self.order = {}
                    self.place = {}
                    for key in keys:
                        index = self.index.next()
                        self.order[index] = order[key]
                        self.place[order[key]] = index
                    index = self.index.next()
                    spriteID = id(sprite)
                    self.order[index] = spriteID
                    self.place[spriteID] = index
        self.sort = None
        RenderUpdates.add(self, *sprites)
        return None

    def remove(self, *sprites):
        """
        Remove sprite(s) from group.
        """
        for sprite in sprites:
            try:
                spriteID = id(sprite)
                del self.order[self.place[spriteID]]
                del self.place[spriteID]
            except KeyError:
                continue
        self.sort = None
        RenderUpdates.remove(self, *sprites)
        return None

    def empty(self):
        """
        Empty group.
        """
        self.order = {}
        self.place = {}
        self.index = iter(xrange(self.range))
        self.sort = None
        RenderUpdates.empty(self)

    def draw(self, surface):
        """
        Draw sprite on surface in order of addition.
        """
        try:
            order_sprite = iter(self.sort)
        except TypeError:
            keys = self.order.keys()
            keys.sort()
            self.sort = [self._sprites[self.order[key]] for key in keys]
            order_sprite = iter(self.sort)
        self._surface_blits = [(sprite.image,sprite.rect) for sprite in order_sprite]
        surface.blits(self._surface_blits)
        if self._clear_active:
            self._rects.extend(self.changed_areas)
            self.changed_areas[:] = []
            for sprite in self._sprites:
                try:
                    if self._sprites_drawn[sprite].intersects(self._sprites[sprite].rect):
                        self._sprites_drawn[sprite].union_ip(self._sprites[sprite].rect)
                    else:
                        self.changed_areas.append(self._get_rect(self._sprites[sprite].rect))
                except KeyError:
                    self.changed_areas.append(self._get_rect(self._sprites[sprite].rect))
            self.changed_areas.extend(self._sprites_drawn.itervalues())
            self._sprites_drawn.clear()
            for sprite in self._sprites:
                self._sprites_drawn[sprite] = self._get_rect(self._sprites[sprite].rect)
        else:
            self._rects.extend(self.changed_areas)
            self.changed_areas[:] = []
            self.changed_areas.extend([self._get_rect(sprite.rect) for sprite in self._sprites.itervalues()])
        return self.changed_areas


class LayeredUpdates(OrderedUpdates):
    """
    **pyjsdl.sprite.LayeredUpdates**
    
    * OrderedUpdates subclass
    * subclass not implemented
    """

    def __init__(self, *sprites):
        """
        Return OrderedUpdates - subclass not implemented.
        """
        OrderedUpdates(self, *sprites)


class LayeredDirty(LayeredUpdates):
    """
    **pyjsdl.sprite.LayeredDirty**
    
    * LayeredUpdates subclass
    * subclass not implemented
    """

    def __init__(self, *sprites):
        """
        Return LayeredUpdates - subclass not implemented.
        """
        LayeredUpdates(self, *sprites)


def spritecollide(sprite, group, dokill, collided=None):
    """
    **pyjsdl.sprite.spritecollide**
    
    Return list of sprites in group that intersect with sprite.
    The dokill argument is bool, True removes sprite from group.
    An optional collided argument is a callback function (ie. collide_mask).
    """
    collide = []
    for sprites in group:
        if sprite.rect.intersects(sprites.rect):
            if collided:
                if not collided(sprite,sprites):
                    continue
            collide.append(sprites)
            if dokill:
                group.remove(sprites)
    return collide


def collide_rect(sprite1, sprite2):
    """
    **pyjsdl.sprite.collide_rect**
    
    Check if the rects of the two sprites intersect.
    """
    return sprite1.rect.intersects(sprite2.rect)


def groupcollide(group1, group2, dokill1, dokill2):
    """
    **pyjsdl.sprite.groupcollide**
    
    Return list of sprites in group that intersect with sprite.
    The dokill argument is bool, True removes sprite from group.
    """
    collide = {}
    for sprite1 in group1:
        collide[sprite1] = []
        for sprite2 in group2:
            if sprite1.rect.intersects(sprite2.rect):
                collide[sprite1].append(sprite2)
    for sprite1 in collide:
        if collide[sprite1]:
            if dokill1:
                group1.remove(sprite1)
            if dokill2:
                for sprite2 in collide[sprite1]:
                    group2.remove(sprite2)


def spritecollideany(sprite, group):
    """
    **pyjsdl.sprite.spritecollideany**
    
    Check if sprite intersect with any sprites in group.
    """
    for sprites in group:
        if sprite.rect.intersects(sprites.rect):
            return True
    return False


def collide_mask(sprite1, sprite2):
    """
    **pyjsdl.sprite.collide_mask**
    
    Check if mask of sprites intersect.
    """
    clip = sprite1.rect.createIntersection(sprite2.rect)
    if clip.width < 1 or clip.height < 1:
        return False
    x1,y1 = clip.x-sprite1.rect.x, clip.y-sprite1.rect.y
    x2,y2 = clip.x-sprite2.rect.x, clip.y-sprite2.rect.y
    masks = []
    for sprite in (sprite1, sprite2):
        try:
            masks.append(sprite.mask)
        except AttributeError:
            masks.append(mask.from_surface(sprite.image))
    for y in range(clip.height):
        try:
            if masks[0].bit[y1+y].get(x1, x1+clip.width).intersects(masks[1].bit[y2+y].get(x2, x2+clip.width)):
                return True
        except IndexError:
            continue
    return False

