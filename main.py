class Stations(object):
	def __init__(self):
		self.stations_by_id = {}
		self.stations_by_name = {}

	def create_station(self, _id, name):
		Station(_id, name, self)

	def add_station(self, station):
		self.stations_by_id[station._id] = station
		self.stations_by_name[station.name] = station


class Station(object):
	def __init__(self, _id, name, stations):
		self._id = _id
		self.name = name
		self.stations = stations
		self.stations.add_station(self)
