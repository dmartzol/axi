from __future__ import division

import overpass
import parser
import projections
import sys
import os
import util
import settings
import time
import setups

# TODO: Implement better argument parsing


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
    geoms = filter(None, [util.crop_geom(g, w + 0.1, h + 0.1) for g in geoms])
    if settings.VERBOSE:
        print("{} geometries.".format(len(geoms)))

    setups.chicago_large(geoms)

    took = (time.time() - start) / 60
    if settings.VERBOSE:
        print("Took {} minutes.".format(took))

if __name__ == '__main__':
    main()
