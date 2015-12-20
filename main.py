import json


class Stations(object):
	def __init__(self):
		self.stations_by_id = {}
		self.stations_by_name = {}

	def create_station(self, _id, name):
		Station(_id, name, self)

	def add_station(self, station):
		self.stations_by_id[station._id] = station
		self.stations_by_name[station.name] = station

	def load_from_json_files(self, stations_filename, connections_filename):
		self.load_stations_from_json_file(stations_filename)

	def load_stations_from_json_file(self, stations_filename):
		with open(stations_filename, 'rb') as f:
			raw_stations = json.load(f)

		for _id, name in raw_stations:
			self.create_station(_id, name)


class Station(object):
	def __init__(self, _id, name, stations):
		self._id = _id
		self.name = name
		self.stations = stations
		self.stations.add_station(self)
