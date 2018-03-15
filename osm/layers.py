from __future__ import division

from shapely import geometry, ops
import math
import util
from settings import HIGHWAY_WEIGHTS, LANE_WIDTH_M

def roads(geoms):
    lookup = {}
    for g in geoms:
        highway = g.tags.get('highway')
        if highway not in HIGHWAY_WEIGHTS:
            continue
        lookup.setdefault(HIGHWAY_WEIGHTS[highway], []).append(g)
    result = []
    for weight, gs in lookup.items():
        g = geometry.collection.GeometryCollection(gs)
        if weight > 0:
            g = g.buffer(weight * LANE_WIDTH_M / 1000)
        result.append(g)
    return ops.cascaded_union(result)

def railroads(geoms, decorated_rails=False):
    # Subways are included in railroads
    gs = []
    # gs = [g for g in geoms if 'railway' in g.tags and g.tags.get('railway') != 'subway']
    for g in geoms:
        if 'railway' in g.tags:
            if g.tags.get('railway') == 'subway':
                continue
            if g.tags.get('railway') == 'dismantled':
                continue
            gs.append(g)
    if decorated_rails:
        paths = []
        for g in gs:
            if isinstance(g, geometry.LineString):
                s = 3 / 1000
                for x, y, a in util.interpolated_points(g, 18 / 1000):
                    x1 = x + math.cos(a + math.pi / 2) * s
                    y1 = y + math.sin(a + math.pi / 2) * s
                    x2 = x + math.cos(a - math.pi / 2) * s
                    y2 = y + math.sin(a - math.pi / 2) * s
                    paths.append([(x1, y1), (x2, y2)])
        gs.append(geometry.MultiLineString(paths))
    return geometry.collection.GeometryCollection(gs)

def subway(geoms):
    # Subways are included in railroads
    gs = [g for g in geoms if g.tags.get('railway') == 'subway']
    return geometry.collection.GeometryCollection(gs)

def buildings(geoms):
    gs = [g for g in geoms if 'building' in g.tags]
    return geometry.collection.GeometryCollection(gs)

def riverbank(geoms):
    gs = [g for g in geoms if g.tags.get('waterway') == 'riverbank']
    return geometry.collection.GeometryCollection(gs)

def water(geoms, roads, draw_waves=False):
    s = 1
    gs = [g for g in geoms if g.tags.get('natural') == 'water']
    gs += [g for g in geoms if 'water' in g.tags]
    gs += [g for g in geoms if g.tags.get('natural') == 'coastline']
    gs = [g.difference(roads) for g in gs]
    g = ops.cascaded_union(gs)
    if draw_waves:
        waves = []
        for i, g in enumerate(gs):
            if isinstance(g, geometry.collection.GeometryCollection):
                continue
            waves.append(util.waves(g, 3 / 1000 * s, 18 / 1000 * s, 12 / 1000 * s))
        # gs += [g for g in geoms if 'waterway' in g.tags]
        # g = ops.cascaded_union(gs)
        return geometry.collection.GeometryCollection([g] + waves)
    return geometry.collection.GeometryCollection(g)
