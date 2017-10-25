import sys
import bpy
import bgl
from mathutils import Matrix, Vector
from bmesh.types import BMVert
from mathutils.geometry import intersect_line_plane
from ..lib.classes.profiler.profiler import profiler
from ..common.decorators import stats_wrapper, stats_report


'''
The types below wrap the mathutils.Vector class, distinguishing among the
different types of geometric entities that are typically represented using
a vanilla Vector.
'''


float_inf = float('inf')


class Entity2D:
    def is_2D(self): return True
    def is_3D(self): return False

class Entity3D:
    def is_2D(self): return False
    def is_3D(self): return True


class Vec2D(Vector, Entity2D):
    @stats_wrapper
    def __init__(self, *args, **kwargs):
        Vector.__init__(*args, **kwargs)
    def __str__(self):
        return '<Vec2D (%0.4f, %0.4f)>' % (self.x,self.y)
    def __repr__(self): return self.__str__()
    def as_vector(self): return Vector(self)
    def from_vector(self, v): self.x,self.y = v


class Vec(Vector, Entity3D):
    @stats_wrapper
    def __init__(self, *args, **kwargs):
        Vector.__init__(*args, **kwargs)
    def __str__(self):
        return '<Vec (%0.4f, %0.4f, %0.4f)>' % (self.x,self.y,self.z)
    def __repr__(self): return self.__str__()
    def normalize(self):
        super().normalize()
        return self
    def cross(self, other):
        t = type(other)
        if t is Vector: return Vec(super().cross(other))
        if t is Vec or t is Direction or t is Normal:
            return Vec(super().cross(Vector(other)))
        assert False, 'unhandled type of other: %s (%s)' % (str(other), str(t))
    def as_vector(self): return Vector(self)
    def from_vector(self, v): self.x,self.y,self.z = v


class Point2D(Vector, Entity2D):
    @stats_wrapper
    def __init__(self, *args, **kwargs):
        Vector.__init__(*args, **kwargs)
    def __str__(self):
        return '<Point2D (%0.4f, %0.4f)>' % (self.x,self.y)
    def __repr__(self): return self.__str__()
    def __add__(self, other):
        t = type(other)
        if t is Direction2D:
            return Point2D((self.x+other.x,self.y+other.y))
        if t is Vector or t is Vec2D:
            return Point2D((self.x+other.x,self.y+other.y))
        assert False, "unhandled type of other: %s (%s)" % (str(other), str(t))
    def __radd__(self, other):
        return self.__add__(other)
    def __sub__(self, other):
        t = type(other)
        if t is Vector or t is Vec2D:
            return Point2D((self.x-other.x,self.y-other.y))
        elif t is Point2D:
            return Vec2D((self.x-other.x, self.y-other.y))
        assert False, "unhandled type of other: %s (%s)" % (str(other), str(t))
    def as_vector(self): return Vector(self)
    def from_vector(self, v): self.x,self.y = v


class Point(Vector, Entity3D):
    @stats_wrapper
    def __init__(self, *args, **kwargs):
        Vector.__init__(*args, **kwargs)
    def __str__(self):
        return '<Point (%0.4f, %0.4f, %0.4f)>' % (self.x,self.y,self.z)
    def __repr__(self): return self.__str__()
    def __add__(self, other):
        t = type(other)
        if t is Direction:
            return Point((self.x+other.x,self.y+other.y,self.z+other.z))
        if t is Vector or t is Vec:
            return Point((self.x+other.x,self.y+other.y,self.z+other.z))
        assert False, "unhandled type of other: %s (%s)" % (str(other), str(t))
    def __radd__(self, other):
        return self.__add__(other)
    def __sub__(self, other):
        t = type(other)
        if t is Vector or t is Vec:
            return Point((self.x-other.x,self.y-other.y,self.z-other.z))
        elif t is Point:
            return Vec((self.x-other.x, self.y-other.y, self.z-other.z))
        assert False, "unhandled type of other: %s (%s)" % (str(other), str(t))
    def as_vector(self): return Vector(self)
    def from_vector(self, v): self.x,self.y,self.z = v
    
    @staticmethod
    def average(points):
        x,y,z,c = 0,0,0,0
        for p in points:
            x += p.x
            y += p.y
            z += p.z
            c += 1
        if c == 0: return Point((0,0,0))
        return Point((x/c, y/c, z/c))


class Direction2D(Vector, Entity2D):
    @stats_wrapper
    def __init__(self, t=None):
        if t is not None: self.from_vector(t)
    def __str__(self):
        return '<Direction2D (%0.4f, %0.4f)>' % (self.x,self.y)
    def __repr__(self): return self.__str__()
    def __mul__(self, other):
        t = type(other)
        if t is float or t is int:
            return Vec2D((other * self.x, other * self.y))
        assert False, "unhandled type of other: %s (%s)" % (str(other), str(t))
    def __rmul__(self, other):
        return self.__mul__(other)
    def normalize(self):
        super().normalize()
        return self
    def as_vector(self): return Vector(self)
    def from_vector(self, v):
        self.x,self.y = v
        self.normalize()


class Direction(Vector, Entity3D):
    @stats_wrapper
    def __init__(self, t=None):
        if t is not None: self.from_vector(t)
    def __str__(self):
        return '<Direction (%0.4f, %0.4f, %0.4f)>' % (self.x,self.y,self.z)
    def __repr__(self): return self.__str__()
    def __mul__(self, other):
        t = type(other)
        if t is float or t is int:
            return Vector((other * self.x, other * self.y, other * self.z))
        assert False, "unhandled type of other: %s (%s)" % (str(other), str(t))
    def __rmul__(self, other):
        return self.__mul__(other)
    def normalize(self):
        super().normalize()
        return self
    def cross(self, other):
        t = type(other)
        if t is Vector: return Vec(super().cross(other))
        if t is Vec or t is Direction or t is Normal:
            return Vec(super().cross(Vector(other)))
        assert False, 'unhandled type of other: %s (%s)' % (str(other), str(t))

    def as_vector(self): return Vector(self)
    def from_vector(self, v):
        self.x,self.y,self.z = v
        self.normalize()


class Normal(Vector, Entity3D):
    @stats_wrapper
    def __init__(self, t=None):
        if t is not None: self.from_vector(t)
    def __str__(self):
        return '<Normal (%0.4f, %0.4f, %0.4f)>' % (self.x,self.y,self.z)
    def __repr__(self): return self.__str__()
    def __mul__(self, other):
        t = type(other)
        if t is float or t is int:
            return Vector((other * self.x, other * self.y, other * self.z))
        assert False, "unhandled type of other: %s (%s)" % (str(other), str(t))
    def __rmul__(self, other):
        return self.__mul__(other)
    def normalize(self):
        super().normalize()
        return self
    def cross(self, other):
        t = type(other)
        if t is Vector: return Vec(super().cross(other))
        if t is Vec or t is Direction or t is Normal:
            return Vec(super().cross(Vector(other)))
        assert False, 'unhandled type of other: %s (%s)' % (str(other), str(t))
    def as_vector(self): return Vector(self)
    def from_vector(self, v):
        self.x,self.y,self.z = v
        self.normalize()


class Ray(Entity3D):
    @stats_wrapper
    def __init__(self, o:Point, d:Direction, min_dist:float=0.0, max_dist:float=float_inf):   # sys.float_info.max
        o,d = Point(o),Direction(d)
        self.o = o + min_dist * d
        self.d = d
        if max_dist == float_inf:
            self.max = max_dist
        else:
            om = o + max_dist * d
            self.max = (self.o - om).length

    def __str__(self):
        return '<Ray (%0.4f, %0.4f, %0.4f)->(%0.4f, %0.4f, %0.4f)>' % (self.o.x,self.o.y,self.o.z,self.d.x,self.d.y,self.d.z)

    def __repr__(self): return self.__str__()

    def eval(self, t:float):
        return self.o + max(self.min, min(self.max, t)) * self.d

    @classmethod
    def from_screenspace(cls, pos:Vector):
        # convert pos in screenspace to ray
        pass


class Plane(Entity3D):
    @classmethod
    def from_points(cls, p0:Point, p1:Point, p2:Point):
        o = Point(((p0.x+p1.x+p2.x)/3, (p0.y+p1.y+p2.y)/3, (p0.z+p1.z+p2.z)/3))
        n = Normal((p1-p0).cross(p2-p0)).normalize()
        return cls(o, n)
    
    def __init__(self, o:Point, n:Normal):
        self.o = o
        self.n = n

    def __str__(self):
        return '<Plane (%0.4f, %0.4f, %0.4f), (%0.4f, %0.4f, %0.4f)>' % (self.o.x,self.o.y,self.o.z, self.n.x,self.n.y,self.n.z)

    def __repr__(self): return self.__str__()

    def side(self, p:Point):
        d = (p - self.o).dot(self.n)
        if abs(d) < 0.000001: return 0
        return -1 if d < 0 else 1

    def distance_to(self, p:Point):
        return abs((p - self.o).dot(self.n))
    def signed_distance_to(self, p:Point):
        return (p - self.o).dot(self.n)

    def project(self, p:Point):
        return p + self.n * (self.o - p).dot(self.n)

    def polygon_intersects(self, points):
        return abs(sum(self.side(p) for p in points)) != len(points)
        
    @stats_wrapper
    def triangle_intersect(self, points):
        return abs(sum(self.side(p) for p in points)) != 3

    @profiler.profile
    def triangle_intersection(self, points):
        s0,s1,s2 = map(self.side, points)
        if abs(s0+s1+s2) == 3: return []    # all points on same side of plane
        p0,p1,p2 = map(Point, points)
        if s0 == 0 or s1 == 0 or s2 == 0:   # at least one point on plane
            # handle if all points in plane
            if s0 == 0 and s1 == 0 and s2 == 0: return [(p0,p1), (p1,p2), (p2,p0)]
            # handle if two points in plane
            if s0 == 0 and s1 == 0: return [(p0,p1)]
            if s1 == 0 and s2 == 0: return [(p1,p2)]
            if s2 == 0 and s0 == 0: return [(p2,p0)]
            # one point on plane, two on same side
            if s0 == 0 and s1 == s2: return [(p0,p0)]
            if s1 == 0 and s2 == s0: return [(p1,p1)]
            if s2 == 0 and s0 == s1: return [(p2,p2)]
        # two points on one side, one point on the other
        p01 = intersect_line_plane(p0, p1, self.o, self.n)
        p12 = intersect_line_plane(p1, p2, self.o, self.n)
        p20 = intersect_line_plane(p2, p0, self.o, self.n)
        if s0 == 0: return [(p0, p12)]
        if s1 == 0: return [(p1, p20)]
        if s2 == 0: return [(p2, p01)]
        if s0 != s1 and s0 != s2 and p01 and p20: return [(p01, p20)]
        if s1 != s0 and s1 != s2 and p01 and p12: return [(p01, p12)]
        if s2 != s0 and s2 != s1 and p12 and p20: return [(p12, p20)]
        print('%s %s %s' % (str(p0), str(p1), str(p2)))
        print('%s %s %s' % (str(s0), str(s1), str(s2)))
        print('%s %s %s' % (str(p01), str(p12), str(p20)))
        assert False

    @stats_wrapper
    def edge_intersect(self, points):
        return abs(sum(self.side(p) for p in points)) != 2

    @profiler.profile
    def edge_intersection(self, points):
        s0,s1 = map(self.side, points)
        if abs(s0 + s1) == 2: return []   # points on same side
        p0,p1 = map(Point, points)
        if s0 == 0 and s1 == 0: return [(p0, p1)]
        if s0 == 0: return [(p0, p0)]
        if s1 == 0: return [(p1, p1)]
        p01 = Point(intersect_line_plane(p0, p1, self.o, self.n))
        return [(p01, p01)]

    def edge_crosses(self, points):
        p0,p1 = points
        return self.side(p0) != self.side(p1)

    def edge_coplanar(self, points):
        p0,p1 = points
        return self.side(p0) == 0 and self.side(p1) == 0

class Frame:
    @staticmethod
    def from_plane(plane:Plane, x:Direction=None, y:Direction=None):
        return Frame(plane.o, x=x, y=y, z=Direction(plane.n))

    @stats_wrapper
    def __init__(self, o:Point, x:Direction=None, y:Direction=None, z:Direction=None):
        c = (1 if x else 0) + (1 if y else 0) + (1 if z else 0)
        assert c!=0, "Must specify at least one direction"
        if c == 1:
            if x:
                y = Direction((-x.x + 3.14, x.y + 42, x.z - 1.61))
                z = Direction(x.cross(y))
                y = Direction(z.cross(x))
            elif y:
                x = Direction((-y.x + 3.14, y.y + 42, y.z - 1.61))
                z = Direction(x.cross(y))
                x = Direction(y.cross(z))
            else:
                x = Direction((-z.x + 3.14, z.y + 42, z.z - 1.61))
                y = Direction(-x.cross(z))
                x = Direction(y.cross(z))
        elif c >= 2:
            if x and y:
                z = Direction(x.cross(y))
                y = Direction(z.cross(x))
                x = Direction(y.cross(z))
            elif x and z:
                y = Direction(z.cross(x))
                x = Direction(y.cross(z))
                z = Direction(x.cross(y))
            else:
                x = Direction(y.cross(z))
                y = Direction(z.cross(x))
                z = Direction(z)

        self.o = Point(o)
        self.x = x
        self.y = y
        self.z = z

        self.fn_l2w_typed = {
            Point:      self.l2w_point,
            Direction:  self.l2w_direction,
            Normal:     self.l2w_normal,
            Vec:        self.l2w_vector,
            Vector:     self.l2w_vector,
            # Ray:        self.l2w_ray,
            # Plane:      self.l2w_plane,
            # BMVert:     self.l2w_bmvert,
        }
        self.fn_w2l_typed = {
            Point:      self.w2l_point,
            Direction:  self.w2l_direction,
            Normal:     self.w2l_normal,
            Vec:        self.w2l_vector,
            Vector:     self.w2l_vector,
            # Ray:        self.w2l_ray,
            # Plane:      self.w2l_plane,
            # BMVert:     self.w2l_bmvert,
        }

    def __str__(self):
        return '<Frame (%0.4f, %0.4f, %0.4f), (%0.4f, %0.4f, %0.4f), (%0.4f, %0.4f, %0.4f), (%0.4f, %0.4f, %0.4f)>' % (
            self.o.x,self.o.y,self.o.z,
            self.x.x,self.x.y,self.x.z,
            self.y.x,self.y.y,self.y.z,
            self.z.x,self.z.y,self.z.z,
            )

    def _dot_fns(self): return self.x.dot,self.y.dot,self.z.dot
    def _dots(self, v): return (self.x.dot(v), self.y.dot(v), self.z.dot(v))
    def _mults(self, v): return self.x*v.x + self.y*v.y + self.z*v.z

    def l2w_typed(self, data):
        ''' dispatched conversion '''
        t = type(data)
        assert t in self.fn_l2w_typed, "unhandled type of data: %s (%s)" % (str(data), str(type(data)))
        return self.fn_l2w_typed[t](data)
    def w2l_typed(self, data):
        ''' dispatched conversion '''
        t = type(data)
        assert t in self.fn_w2l_typed, "unhandled type of data: %s (%s)" % (str(data), str(type(data)))
        return self.fn_w2l_typed[t](data)

    def w2l_point(self, p:Point)->Point: return Point(self._dots(p - self.o))
    def l2w_point(self, p:Point)->Point: return Point(self.o + self._mults(p))

    def w2l_vector(self, v:Vector)->Vec: return Vec(self._dots(v))
    def l2w_vector(self, v:Vector)->Vec: return Vec(self._mults(v))

    def w2l_direction(self, d:Direction)->Direction: return Direction(self._dots(d)).normalize()
    def l2w_direction(self, d:Direction)->Direction: return Direction(self._mults(d)).normalize()

    def w2l_normal(self, n:Normal)->Normal: return Normal(self._dots(n)).normalize()
    def l2w_normal(self, n:Normal)->Normal: return Normal(self._mults(n)).normalize()

    def rotate_about_z(self, radians:float):
        c,s = math.cos(radians),math.sin(radians)
        x,y = self.x,self.y
        self.x = x*c + y*s
        self.y = -x*s + y*c


class XForm:
    @staticmethod
    def get_mats(mx:Matrix):
        smat,d = str(mx),XForm.get_mats.__dict__
        if smat not in d:
            m = {
                'mx_p': None, 'imx_p': None,
                'mx_d': None, 'imx_d': None,
                'mx_n': None, 'imx_n': None
            }
            m['mx_p']  = Matrix(mx)
            m['mx_t']  = mx.transposed()
            m['imx_p'] = mx.inverted()
            m['mx_d']  = mx.to_3x3()
            m['imx_d'] = m['mx_d'].inverted()
            m['mx_n']  = m['imx_d'].transposed()
            m['imx_n'] = m['mx_d'].transposed()
            d[smat] = m
        return d[smat]

    @stats_wrapper
    def __init__(self, mx:Matrix=None):
        if mx is None: mx = Matrix()
        self.assign(mx)

    def assign(self, mx):
        if type(mx) is XForm: return self.assign(mx.mx_p)

        mats = XForm.get_mats(mx)
        self.mx_p,self.imx_p = mats['mx_p'],mats['imx_p']
        self.mx_d,self.imx_d = mats['mx_d'],mats['imx_d']
        self.mx_n,self.imx_n = mats['mx_n'],mats['imx_n']
        self.mx_t = mats['mx_t']

        self.fn_l2w_typed = {
            Point:      lambda x: self.l2w_point(x),
            Direction:  lambda x: self.l2w_direction(x),
            Normal:     lambda x: self.l2w_normal(x),
            Vec:        lambda x: self.l2w_vector(x),
            Vector:     lambda x: self.l2w_vector(x),
            Ray:        lambda x: self.l2w_ray(x),
            Plane:      lambda x: self.l2w_plane(x),
            BMVert:     lambda x: self.l2w_bmvert(x),
        }
        self.fn_w2l_typed = {
            Point:      lambda x: self.w2l_point(x),
            Direction:  lambda x: self.w2l_direction(x),
            Normal:     lambda x: self.w2l_normal(x),
            Vec:        lambda x: self.w2l_vector(x),
            Vector:     lambda x: self.w2l_vector(x),
            Ray:        lambda x: self.w2l_ray(x),
            Plane:      lambda x: self.w2l_plane(x),
            BMVert:     lambda x: self.w2l_bmvert(x),
        }
        return self

    def __str__(self):
        v = tuple(x for r in self.mx_p for x in r)
        return '<XForm (%0.4f, %0.4f, %0.4f, %0.4f)\n' \
               '       (%0.4f, %0.4f, %0.4f, %0.4f)\n' \
               '       (%0.4f, %0.4f, %0.4f, %0.4f)\n' \
               '       (%0.4f, %0.4f, %0.4f, %0.4f)>' % v

    def __repr__(self): return self.__str__()

    def __mul__(self, other):
        t = type(other)
        if t is XForm:  return XForm(self.mx_p * other.mx_p)
        if t is Matrix: return XForm(self.mx_p * other)
        return self.l2w_typed(other)

    def __imul__(self, other):
        self.assign(self.mx_p * (other.mx_p if type(other) is XForm else other))

    def __truediv__(self, other):
        return self.w2l_typed(other)

    def __iter__(self):
        for v in self.mx_p: yield v


    def l2w_typed(self, data):
        ''' dispatched conversion '''
        t = type(data)
        assert t in self.fn_l2w_typed, "unhandled type of data: %s (%s)" % (str(data), str(type(data)))
        return self.fn_l2w_typed[t](data)
    def w2l_typed(self, data):
        ''' dispatched conversion '''
        t = type(data)
        assert t in self.fn_w2l_typed, "unhandled type of data: %s (%s)" % (str(data), str(type(data)))
        return self.fn_w2l_typed[t](data)

    def l2w_point(self, p:Point)->Point: return Point(self.mx_p * p)
    def w2l_point(self, p:Point)->Point: return Point(self.imx_p * p)

    def l2w_direction(self, d:Direction)->Direction: return Direction(self.mx_d * d)
    def w2l_direction(self, d:Direction)->Direction: return Direction(self.imx_d * d)

    def l2w_normal(self, n:Normal)->Normal: return Normal(self.mx_n * n)
    def w2l_normal(self, n:Normal)->Normal: return Normal(self.imx_n * n)

    def l2w_vector(self, v:Vector)->Vec: return Vec(self.mx_d * v)
    def w2l_vector(self, v:Vector)->Vec: return Vec(self.imx_d * v)

    def l2w_ray(self, ray:Ray)->Ray:
        o = self.l2w_point(ray.o)
        d = self.l2w_direction(ray.d)
        if ray.max == float('inf'):
            l1 = ray.max
        else:
            l1 = (o - self.l2w_point(ray.o + ray.max * ray.d)).length
        return Ray(o=o0, d=d, max_dist=l1)
    def w2l_ray(self, ray:Ray)->Ray:
        o = self.w2l_point(ray.o)
        d = self.w2l_direction(ray.d)
        if ray.max == float('inf'):
            l1 = ray.max
        else:
            l1 = (o - self.w2l_point(ray.o + ray.max * ray.d)).length
        return Ray(o=o, d=d, max_dist=l1)

    def l2w_plane(self, plane:Plane)->Plane:
        return Plane(o=self.l2w_point(plane.o), n=self.l2w_normal(plane.n))
    def w2l_plane(self, plane:Plane)->Plane:
        return Plane(o=self.w2l_point(plane.o), n=self.w2l_normal(plane.n))

    def l2w_bmvert(self, bmv:BMVert)->Point: return Point(self.mx_p * bmv.co)
    def w2l_bmevrt(self, bmv:BMVert)->Point: return Point(self.imx_p * bmv.co)

    def to_bglMatrix(self):
        bglMatrix = bgl.Buffer(bgl.GL_FLOAT, [16])
        for i,v in enumerate([v for r in self.mx_t for v in r]):
            bglMatrix[i] = v
        return bglMatrix


class BBox:
    @stats_wrapper
    def __init__(self, from_bmverts=None, from_coords=None):
        assert from_bmverts or from_coords
        if from_bmverts: from_coords = [bmv.co for bmv in from_bmverts]
        else: from_coords = list(from_coords)
        mx,my,mz = from_coords[0]
        Mx,My,Mz = mx,my,mz
        for x,y,z in from_coords:
            mx,my,mz = min(mx,x),min(my,y),min(mz,z)
            Mx,My,Mz = max(Mx,x),max(My,y),max(Mz,z)
        self.min = Point((mx, my, mz))
        self.max = Point((Mx, My, Mz))
        self.mx,self.my,self.mz = mx,my,mz
        self.Mx,self.My,self.Mz = Mx,My,Mz

    def __str__(self):
        return '<BBox (%0.4f, %0.4f, %0.4f) (%0.4f, %0.4f, %0.4f)>' % (self.mx, self.my, self.mz, self.Mx, self.My, self.Mz)

    def __repr__(self): return self.__str__()

    def Point_within(self, point:Point, margin=0):
        return all(m-margin <= v and v <= M+margin for v,m,M in zip(point,self.min,self.max))

# https://rosettacode.org/wiki/Determine_if_two_triangles_overlap#C.2B.2B
def triangle2D_det(p0, p1, p2):
    return p0.x * (p1.y - p2.y) + p1.x * (p2.y - p0.y) + p2.x * (p0.y - p1.y)
def triangle2D_boundary_collision_check(p0, p1, p2, eps):
    return triangle2D_det(p0, p1, p2) < eps
def triangle2D_collision_check(p0, p1, p2, eps):
    return triangle2D_det(p0, p1, p2) <= eps
def triangle2D_overlap(triangle0, triangle1, eps=0.0):
    _chk = triangle2D_collision_check
    def chk(e0, e1, p0, p1, p2): return _chk(e0,e1,p0,eps) and _chk(e0,e1,p1,eps) and _chk(e0,e1,p2,eps)
    a0,a1,a2 = triangle0
    b0,b1,b2 = triangle1
    if chk(a0, a1, b0, b1, b2) or chk(a1, a2, b0, b1, b2) or chk(a2, a0, b0, b1, b2): return False
    if chk(b0, b1, a0, a1, a2) or chk(b1, b2, a0, a1, a2) or chk(b2, b0, a0, a1, a2): return False
    return True

def triangle2D_area(p0, p1, p2):
    a = Vector((p0.x, p0.y, 0.0))
    b = Vector((p1.x, p1.y, 0.0))
    c = Vector((p2.x, p2.y, 0.0))
    return (b-a).cross(c-a).length / 2

def segment2D_intersection(a0,a1, b0,b1):
    # get distance from b0 to a0---a1
    dir_a0a1 = a1 - a0
    dist_a0a1 = max(0.00000001, dir_a0a1.length)
    dir_a0a1 /= dist_a0a1
    vec_a0b0 = b0 - a0
    closest_b0_a0a1 = a0 + dir_a0a1 * dir_a0a1.dot(vec_a0b0)
    pdir_a0a1_b0 = b0 - closest_b0_a0a1
    dist_a0a1_b0 = pdir_a0a1_b0.length
    if dist_a0a1_b0 == 0:
        # b0 is on a0-a1 line
        return b0
    pdir_a0a1_b0 /= dist_a0a1_b0
    dir_b0b1 = b1 - b0
    dist_b0b1 = max(0.00000001, dir_b0b1.length)
    dir_b0b1 /= dist_b0b1
    dot = dir_b0b1.dot(pdir_a0a1_b0)
    if abs(dot) <= 0.0000001:
        # a0-a1 and b0-b1 are nearly parallel
        return None
    dist_intersection_b0b1 = dist_a0a1_b0 / dot
    if dist_intersection_b0b1 < 0 or dist_intersection_b0b1 > dist_b0b1: return None
    intersection = b0 + dir_b0b1 * dist_intersection_b0b1
    # dist_intersection_a0a1 = dir_a0a1.dot(intersection - a0)
    # if dist_intersection_a0a1 < 0 or dist_intersection_a0a1 > dist_a0a1: return None
    return intersection
    


if __name__ == '__main__':
    # run tests
    p0 = Point((1,2,3))
    p1 = Point((0,0,1))
    v0 = Vec((1,0,0))
    r = Ray(p0, v0)
    mxt = XForm(Matrix.Translation((1,2,3)))
    mxr = XForm(Matrix.Rotation(0.1, 4, Vector((0,0,1))))
    mxtr = mxt * mxr

    print('')

    print(p1 - p0)
    print(p0 + v0)
    print(p0*2) # should be able to do this??
    print(p0.copy())
    print(r)

    print("%s => %s" % (v0, mxt * v0))
    print("%s => %s" % (p0, mxt * p0))

    print("%s => %s" % (v0, mxr * v0))
    print("%s => %s" % (p0, mxr * p0))

    print('%s => %s => %s' % (r, mxtr * r, mxtr / (mxtr * r)))

    print(mxr)
    print(mxr.mx_p)
