
CARY = 35.787196, -78.783337
BOSTON = 42.3583, -71.0610
BUDAPEST = 47.498206, 19.052509
SONG_SPARROW = 36.1143248, -79.9575
NEW_ORLEANS = 29.9432062, -90.1002717
FRENCH_QUARTER = 29.9588, -90.0641
ROME = 41.89306, 12.48308
# ROME = 41.90813, 12.47330
ANNECY = 45.89917, 6.12471
ANNECY = 45.89885, 6.12796
# CHICAGO = 41.919017, -87.706786
# CHICAGO = 41.875188, -87.6783875
# CHICAGO = 41.895248, -87.700898
CHICAGO = 41.889302, -87.686563
PADERBORN = 51.718973, 8.755517

LAT, LNG = CHICAGO

VERBOSE = True
DEBUG_MODE = True
TEMP_DIRECTORY = 'temp'
TEMP_FILENAME = 'overpass_request.xml'
# View dimensions
ROTATION_DEGREES = 0
MAP_WIDTH_KM = 17

# Page dimensions
PAGE_WIDTH_IN = 12
PAGE_HEIGHT_IN = 8.5
ASPECT_RATIO = PAGE_WIDTH_IN / PAGE_HEIGHT_IN


# LANE_WIDTH_M = 3.7/2
LANE_WIDTH_M = 12

HIGHWAY_WEIGHTS = {
    'motorway': 2,
    'motorway_link': 2,
    'trunk_link': 2,
    'trunk': 2,
    'primary_link': 1.75,
    'primary': 1.75,
    'secondary': 1.5,
    'secondary_link': 1.5,
    'tertiary_link': 1.25,
    'tertiary': 1.25,
    'living_street': 1,
    'unclassified': 1,
    'residential': 1,
    # 'service': 0.1,
    'pedestrian': 0.5,
    # 'footway': 0.1,
    'turning_circle': 3,
}