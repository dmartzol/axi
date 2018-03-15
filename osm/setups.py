from __future__ import division
import layers
import axi
from shapely import geometry
import util
import settings
import os

def chicago_large(geoms):
    roads = layers.roads(geoms)
    railroads = layers.railroads(geoms)
    subway = layers.subway(geoms)
    river = layers.riverbank(geoms)
    water = layers.water(geoms, roads)

    if not os.path.exists('layers'):
        os.makedirs('layers')
    draw_layers([water], 'water')
    draw_layers([roads], 'roads', frame=True)
    draw_layers([railroads], 'rail')
    draw_layers([subway], 'subway')
    draw_layers([river], 'river')
    draw_text('Chicago Metropolitan Area')

def draw_layers(layers_list, layer_name, frame=False, svg_output=True, axi_draw=False):
    w = settings.MAP_WIDTH_KM
    h = w / settings.ASPECT_RATIO
    g = geometry.collection.GeometryCollection(layers_list)
    paths = util.shapely_to_paths(g)
    if frame:
        paths.append(util.centered_rectangle(w, h))

    d = axi.Drawing(paths)
    d = d.translate(w / 2, h / 2)
    d = d.scale(settings.PAGE_WIDTH_IN / w)
    d = d.crop_paths(0, 0, settings.PAGE_WIDTH_IN, settings.PAGE_HEIGHT_IN)
    d = d.remove_paths_outside(settings.PAGE_WIDTH_IN, settings.PAGE_HEIGHT_IN)
    if axi_draw:
        d = d.sort_paths()
    d = d.join_paths(0.002).simplify_paths(0.002)
    im = d.render(line_width=0.25 / 25.4)
    im.write_to_png(os.path.join('layers', layer_name + '.png'))
    if svg_output:
        d.dump_svg(os.path.join('layers', layer_name + '.svg'))
    if axi_draw:
        raw_input('Drawing {}. Press ENTER to continue!'.format(layer_name))
        axi.draw(d)

def draw_text(title, axi_draw=False, svg_output=True):
    w = settings.MAP_WIDTH_KM
    h = w / settings.ASPECT_RATIO
    d = axi.Drawing(axi.text(title, axi.FUTURAL))
    d = d.scale_to_fit(5, 3)
    d = d.rotate(-90)
    d = d.translate(w / 2, h / 2)
    d = d.center(0, 0)
    if axi_draw:
        d = d.sort_paths()
    d = d.join_paths(0.002).simplify_paths(0.002)
    im = d.render(line_width=0.25 / 25.4)
    im.write_to_png(os.path.join('layers', 'text.png'))
    if svg_output:
        d.dump_svg(os.path.join('layers', 'text.svg'))
    if axi_draw:
        raw_input('Writing text. Press ENTER to continue!')
        axi.draw(d)

def default(geoms):
    w = settings.MAP_WIDTH_KM
    h = w / settings.ASPECT_RATIO
    roads = layers.roads(geoms)
    railroads = layers.railroads(geoms)
    buildings = layers.buildings(geoms)
    # water = layers.water(geoms, roads)
    subway = layers.subway(geoms)
    river = layers.riverbank(geoms)
    g = geometry.collection.GeometryCollection([
        roads,
        # subway,
        # railroads,
        # buildings,
        # water,
        # river,
    ])
    paths = util.shapely_to_paths(g)
    paths.append(util.centered_rectangle(w, h))
    d = axi.Drawing(paths)
    d = d.translate(w / 2, h / 2)
    d = d.scale(settings.PAGE_WIDTH_IN / w)
    d = d.crop_paths(0, 0, settings.PAGE_WIDTH_IN, settings.PAGE_HEIGHT_IN)
    d = d.remove_paths_outside(settings.PAGE_WIDTH_IN, settings.PAGE_HEIGHT_IN)
    d = d.sort_paths().join_paths(0.002).simplify_paths(0.002)
    im = d.render(line_width=0.25 / 25.4)
    im.write_to_png('out.png')
    # raw_input('Press ENTER to continue!')
    # axi.draw(d)
