from __future__ import division

from shapely import geometry

import axi
import overpass
import layers
import parser
import projections
import sys
import os
import util
import settings
import time

# TODO: Implement better argument parsing
def crop_geom(g, w, h):
    tags = g.tags
    if not g.is_valid:
        g = g.buffer(0)
    if g.is_empty:
        return None
    g = util.centered_crop(g, w, h)
    if g.is_empty:
        return None
    g.tags = tags
    return g

def main():
    start = time.time()
    if settings.VERBOSE:
        print("{} Starting point".format(util.timestamp()))
    if len(sys.argv) > 1:
        args = sys.argv[1:]
        filename = args[0]
    else:
        filename = os.path.join(settings.TEMP_DIRECTORY, settings.TEMP_FILENAME)
    if not settings.DEBUG_MODE:
        print('WARNING: Debug mode OFF')
        print('YOU ARE DOWNLOADING DATA')
        print("Be a good guy, don't do this ofter")
        raw_input('Press ENTER to continue!')
        print('Requesting data from Overpass...')
        if os.path.exists(settings.TEMP_DIRECTORY):
            raise IOError('Dir already exists')
        os.makedirs(settings.TEMP_DIRECTORY)
        overpass_api = overpass.API()
        # * unpacks variable and gives it as 4 separate arguments
        map_query = overpass.MapQuery(*util.relevant_area_bounds())
        response = overpass_api.Get(map_query, responseformat='xml')
        with open(os.path.join(settings.TEMP_DIRECTORY, settings.TEMP_FILENAME), 'w') as file:
            file.write(response.encode('utf-8'))

    proj = projections.LambertAzimuthalEqualArea(settings.LNG, settings.LAT, settings.ROTATION_DEGREES)
    _, filename_extension = os.path.splitext(filename)
    geoms = parser.parse(filename, transform=proj.project, extension=filename_extension)
    if settings.VERBOSE:
        print("{} geometries.".format(len(geoms)))
    w = settings.MAP_WIDTH_KM
    h = w / settings.ASPECT_RATIO
    geoms = filter(None, [crop_geom(g, w + 0.1, h + 0.1) for g in geoms])
    if settings.VERBOSE:
        print("{} geometries.".format(len(geoms)))
    # g = geometry.collection.GeometryCollection(geoms)
    # TODO: Organize this and add default setups
    roads = layers.roads(geoms)
    # railroads = layers.railroads(geoms)
    # buildings = layers.buildings(geoms)
    water = layers.water(geoms, roads)
    subway = layers.subway(geoms)
    river = layers.riverbank(geoms)
    g = geometry.collection.GeometryCollection([
        roads,
        subway,
        # railroads,
        # buildings,
        water,
        river,
    ])

    # TODO: Implemente plotting different layers with different colors
    paths = util.shapely_to_paths(g)
    paths.append(util.centered_rectangle(w, h))

    title = 'Chicago'
    d = axi.Drawing(axi.text(title, axi.FUTURAL))
    d = d.scale_to_fit(8.5, 12 - 1)
    # d = d.rotate(-90)
    d = d.move(12, 8.5 / 2, 1, 0.5)
    print(d.bounds)
    paths.extend(d.paths)

    d = axi.Drawing(paths)
    d = d.translate(w / 2, h / 2)
    d = d.scale(settings.PAGE_WIDTH_IN / w)
    d = d.crop_paths(0, 0, settings.PAGE_WIDTH_IN, settings.PAGE_HEIGHT_IN)
    d = d.remove_paths_outside(settings.PAGE_WIDTH_IN, settings.PAGE_HEIGHT_IN)
    d = d.sort_paths().join_paths(0.002).simplify_paths(0.002)
    # d.dump_svg('out.svg')
    im = d.render(line_width=0.25 / 25.4)
    im.write_to_png('out.png')
    took = (time.time() - start) / 60
    if settings.VERBOSE:
        print("Took {} minutes.".format(took))
    # raw_input('Press ENTER to continue!')
    # axi.draw(d)

if __name__ == '__main__':
    main()
