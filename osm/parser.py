from imposm.parser import OSMParser
from shapely import geometry, ops
from util import timestamp
import util
import settings

class Handler(object):
    def __init__(self, transform=None):
        self.transform = transform
        self.coords = []
        self.nodes = []
        self.ways = []
        self.relations = []
        self.coords_by_id = {}
        self.nodes_by_id = {}
        self.ways_by_id = {}
        self.relations_by_id = {}
    def on_coords(self, coords):
        self.coords.extend(coords)
    def on_nodes(self, nodes):
        self.nodes.extend(nodes)
    def on_ways(self, ways):
        self.ways.extend(ways)
    def on_relations(self, relations):
        self.relations.extend(relations)
    def transform_point(self, lng, lat):
        if self.transform:
            return self.transform(lng, lat)
        return lng, lat
    def create_geometries(self):
        if settings.VERBOSE:
            print("Creating lookup tables")
            print("{} Nodes dictionary".format(timestamp()))
        # create lookup tables
        # Saving coordinates in dictionary coords_by_id
        bounds = util.relevant_area_bounds()
        for osmid, lng, lat in self.coords:
            if util.coords_in_bounds(lat, lng, bounds):
                lng, lat = self.transform_point(lng, lat)
                self.coords_by_id[osmid] = (lng, lat)
        for osmid, tags, (lng, lat) in self.nodes:
            if util.coords_in_bounds(lat, lng, bounds):
                lng, lat = self.transform_point(lng, lat)
                self.nodes_by_id[osmid] = (lng, lat, tags)
        # deleting the nodes for which we don't have coordinates
        # (because are out of the requested area)
        if settings.VERBOSE:
            print("{} Ways dictionary".format(timestamp()))
        filtered_ways = []
        for osmid, tags, refs in self.ways:
            known_nodes = self.discard_unknown_nodes_from_ways(refs)
            if len(known_nodes) > 1:  # Avoinding ways with no nodes or only one node
                refs = known_nodes
                self.ways_by_id[osmid] = (tags, refs)
                filtered_ways.append((osmid, tags, refs))
        self.ways = filtered_ways

        # Saving relations in dictionary by id
        # deleting the nodes for which we don't have info
        # deleting the ways for which we don't have info
        # (because they are out of the requested area)
        if settings.VERBOSE:
            print("{} Relations dictionary".format(timestamp()))
        for osmid, tags, relation_members in self.relations:
            known_members = []
            for member in relation_members:
                member_id, member_type, member_role = member
                if member_type == 'node':
                    if self.node_is_known(member_id):
                        known_members.append(member)
                if member_type == 'way':
                    if self.way_is_known(member_id):
                        known_members.append(member)
                if member_type == 'relation':
                    pass
                    # TODO: do this one day
                    # print("I didn't save this member yet {}".format(member))  # TODO: do this one day
            self.relations_by_id[osmid] = (tags, known_members)

        # create geometries
        if settings.VERBOSE:
            print("Creating geometries")
        geoms = []
        way_geoms_by_id = {}
        if settings.VERBOSE:
            print("{} Points from nodes".format(timestamp()))
        for osmid, tags, (lng, lat) in self.nodes:
            lng, lat = self.transform_point(lng, lat)
            g = geometry.Point(lng, lat)
            g.tags = tags
            geoms.append(g)
        if settings.VERBOSE:
            print("{} Polygons and LineStrings from ways".format(timestamp()))
        for osmid, tags, refs in self.ways:
            coords = [self.coords_by_id[x] for x in refs]
            closed = refs[0] == refs[-1]
            if 'highway' in tags or 'barrier' in tags:
                closed = False
            if tags.get('area') == 'yes':
                closed = True
            if len(coords) < 3:
                closed = False
            if closed:
                g = geometry.Polygon(coords)
                if not g.is_valid:
                    #TODO: Save invalid polygons in a file
                    continue
            else:
                g = geometry.LineString(coords)
                if not g.is_valid:
                    #TODO: Save invalid linestrings in a file
                    continue
            g.tags = tags
            way_geoms_by_id[osmid] = g
            geoms.append(g)
        if settings.VERBOSE:
            print("{} Others from relations".format(timestamp()))
        for osmid, tags, members in self.relations:
            if tags.get('type') == 'multipolygon':
                outers = []
                inners = []
                outer_lines = []
                inner_lines = []
                for refid, reftype, role in members:
                    if reftype != 'way':
                        continue
                    if refid not in way_geoms_by_id:
                        continue
                    way = way_geoms_by_id[refid]
                    if role == 'outer':
                        if isinstance(way, geometry.Polygon):
                            outers.append(way)
                        else:
                            outer_lines.append(way)
                    elif role == 'inner':
                        if isinstance(way, geometry.Polygon):
                            inners.append(way)
                        else:
                            inner_lines.append(way)
                if outer_lines:
                    outers.extend(list(ops.polygonize(outer_lines)))
                if inner_lines:
                    inners.extend(list(ops.polygonize(inner_lines)))
                g = ops.cascaded_union(outers)
                if inners:
                    g = g.difference(ops.cascaded_union(inners))
                g.tags = tags
                geoms.append(g)
        return geoms

    def discard_unknown_nodes_from_ways(self, nodes_ids):
        """
        Iterates over the nodes of the way and discards the ones without known coordinates
        input way element out of imposm.Parser
        outputs a list of the known nodes
        """
        known_nodes = []
        for node_id in nodes_ids:
            if self.node_is_known(node_id):
                known_nodes.append(node_id)
            else:
                return known_nodes  # if one node is not known then the way stops here
        return known_nodes

    def node_is_known(self, node_id):
        """
        returns True if the node id is in the list of coords_by_id.
        Returns False otherwise
        """
        if node_id in self.coords_by_id:
            return True
        return False

    def way_is_known(self, way_id):
        """
        returns True if the way id is in the list of ways_by_id.
        Returns False otherwise
        """
        if way_id in self.ways_by_id:
            return True
        return False

def parse(filename, transform=None, extension='.pbf'):
    handler = Handler(transform)
    p = OSMParser(
        concurrency=1,
        coords_callback=handler.on_coords,
        nodes_callback=handler.on_nodes,
        ways_callback=handler.on_ways,
        relations_callback=handler.on_relations)
    if extension == '.xml':
        if settings.VERBOSE:
            print("{} Parsing from xml file".format(timestamp()))
        p.parse_xml_file(filename)
    else:
        if settings.VERBOSE:
            print("{} Parsing from pbf file".format(timestamp()))
        p.parse(filename)
        if settings.VERBOSE:
            print("{} Done parsing".format(timestamp()))
    return handler.create_geometries()
