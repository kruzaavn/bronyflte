"""core models"""

import pathlib
import luadata as lua
import zipfile
import datetime


utf = 'utf-8'


class Mission:
    """
    This class represents a DCS mission
    """

    def __init__(self,
                 name=None,
                 theater=None,
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

    def __str__(self):
        return f'{self.name}: {self.simulation_start.strftime("%x %X")}'

    def __repr__(self):
        return f'{self.name}: {self.simulation_start.strftime("%x %X")}'

    def load(self, path):
        """
        Load mission from DCS .miz file

        Parameters
        ----------
        path

        Returns
        -------

        """

        if isinstance(path, str):
            path = pathlib.Path(path)

        self.name = path.stem

        z = zipfile.ZipFile(path)

        with z.open('theatre') as file:
            self.theater = file.read().decode(utf)

        with z.open('mission') as file:
            mission = lua.unserialize(file.read().decode(utf), encoding=utf)

        date = {k.lower(): v for k, v in mission['date'].items()}

        self.simulation_start = datetime.datetime(**date) + datetime.timedelta(seconds=mission['start_time'])


    def save(self, path):
        """

        Parameters
        ----------
        path

        Returns
        -------

        """
        pass


class Flight:
    """

    """

    def __init__(self, airframe, number=1, callsign=None):
        """

        Parameters
        ----------
        airframe
        callsign
        """

        self.callsign = callsign
        self.airframe = airframe
        self.number = number
        self.flight_plan = []
