from pyproj import CRS
import json
import pathlib

path = pathlib.Path(__file__)

crs_defaults = {
    "proj": "tmerc",
    "vunits": "m",
    "units": "m",
    "axis": "neu",
    "ellps": "WGS84"
}

with open(path.parent.joinpath('data', 'theater_crs.json')) as file:

    crs_definitions = json.load(file)

crs = {}
for key, value in crs_definitions.items():

    proj = {}
    proj.update(crs_defaults)
    proj.update(value)

    crs[key] = CRS.from_dict(proj)

crs['wgs84'] = CRS('WGS84')
