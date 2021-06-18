"""core models"""

import pathlib
import luadata as lua
import zipfile
import datetime
from pyproj import Transformer
from .crs import crs
import math

utf = 'utf-8'


class Waypoint:

    def __init__(self, time, latitude, longitude, altitude, type):

        """

        Parameters
        ----------
        time: datetime.Timedelta
            time since mission start
        latitude: float
            DD.D
        longitude: float
            DD.D
        altitude: float
            meters
        """

        self.time = datetime.timedelta(seconds=time)
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude
        self.type = type

    def __repr__(self):
        return f'{self.latitude} {self.longitude} {self.altitude}'

    def __str__(self):
        return self.__repr__()


class FlightPlan:

    def __init__(self):

        self.waypoints = []

    def __repr__(self):

        td = self.waypoints[-1].time - self.waypoints[0].time

        hours = math.floor(td.seconds / 3600)

        td = td - datetime.timedelta(hours=hours)

        minutes = math.floor(td.seconds / 60)

        return f'duration: {hours}:{minutes}:{td.seconds % 60}'

    @classmethod
    def from_dcs(cls, waypoints, transform):

        """

        Parameters
        ----------
        waypoints
        transform

        Returns
        -------

        """

        fp = cls()

        for waypoint in waypoints:

            lon, lat = transform.transform(waypoint['x'], waypoint['y'])

            wp = Waypoint(
                waypoint['ETA'],
                lat,
                lon,
                waypoint['alt'],
                waypoint['type'].lower()
            )

            fp.waypoints.append(wp)

        return fp


class Flight:
    """

    """

    def __init__(self, airframe, number=1, task=None, callsign=None):
        """

        Parameters
        ----------
        number
        flight_plan
        airframe
        callsign
        """

        self.callsign = callsign
        self.airframe = airframe
        self.number = number
        self.flight_plan = FlightPlan()
        self.task = task

    def __repr__(self):
        return f'{self.airframe}: {self.callsign}'

    def __str__(self):
        return self.__repr__()

    @classmethod
    def from_dcs(cls, flight, transform):

        f = cls(
            airframe=flight['units'][0]['type'],
            callsign=flight['name'],
            task=flight['task'],
            number=len(flight['units']),
        )

        f.flight_plan = FlightPlan.from_dcs(flight['route']['points'], transform)

        return f


class Mission:
    """
    This class represents a DCS mission
    """

    def __init__(self,
                 name=None,
                 theater='Caucasus',
                 simulation_start=datetime.datetime.now()):
        """

        Parameters
        ----------
        theater
        simulation_start
        name
        """

        self.name = name
        self.flights = []
        self.theater = theater
        self.simulation_start = simulation_start

        self._set_crs()

    def __str__(self):
        return f'{self.name}: {self.simulation_start.strftime("%x %X")}'

    def __repr__(self):
        return f'{self.name}: {self.simulation_start.strftime("%x %X")}'

    def _set_crs(self):

        self._crs = crs[self.theater.lower()]
        self._crs_wgs84_transform = Transformer.from_crs(self._crs, crs['wgs84'])
        self._wgs_crs_transform = Transformer.from_crs(crs['wgs84'], self._crs)

    def dcs_to_lon_lat(self, x, y):
        """

        Parameters
        ----------
        x
        y

        Returns
        -------
        longitude
        latitude
        """

        longitude, latitude = self._crs_wgs84_transform.transform(x, y)
        return longitude, latitude

    def lon_lat_to_dcs(self, lon, lat):

        """

        Parameters
        ----------
        lon
        lat

        Returns
        -------
        x
        Yields
        """

        x, y = self._wgs_crs_transform.transform(lon, lat)
        return x, y

    def load(self, path):
        """
        Load mission from DCS .miz file

        Parameters
        ----------
        path

        Returns
        -------

        """

        # check if path is a plain string or pathlib object
        if isinstance(path, str):
            path = pathlib.Path(path)

        # set name
        self.name = path.stem

        # access zipfile
        z = zipfile.ZipFile(path)

        # set the theatre
        with z.open('theatre') as file:
            self.theater = file.read().decode(utf)
            self._set_crs()

        with z.open('mission') as file:
            mission = lua.unserialize(file.read().decode(utf), encoding=utf)

        date = {k.lower(): v for k, v in mission['date'].items()}

        self.simulation_start = datetime.datetime(**date) + datetime.timedelta(seconds=mission['start_time'])

        for country in mission['coalition']['blue']['country']:
            self.flights = [
                Flight.from_dcs(flight, self._crs_wgs84_transform) for flight in
                country['plane']['group'] + country['helicopter']['group']
            ]

    def save(self, path):
        """

        Parameters
        ----------
        path

        Returns
        -------

        """
        raise NotImplemented()



