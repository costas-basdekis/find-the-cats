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
		self.load_connections_from_json_file(connections_filename)

	def load_stations_from_json_file(self, stations_filename):
		with open(stations_filename, 'rb') as f:
			raw_stations = json.load(f)

		for _id, name in raw_stations:
			self.create_station(_id, name)

	def load_connections_from_json_file(self, connections_filename):
		with open(connections_filename, 'rb') as f:
			raw_connections = json.load(f)

		for first_id, second_id in raw_connections:
			first_station = self.stations_by_id[first_id]
			second_station = self.stations_by_id[second_id]

			first_station.connect_with(second_station)


class Station(object):
	def __init__(self, _id, name, stations):
		self._id = _id
		self.name = name
		self.stations = stations
		self.stations.add_station(self)
		self.connections_by_id = {}

	def connect_with(self, station):
		if station._id in self.connections_by_id:
			return

		self.connections_by_id[station._id] = station
		station.connect_with(self)


def main():
	stations = Stations()
	stations.load_from_json_files("./tfl_stations.json", "./tfl_connections.json")
	print 'Loaded', len(stations.stations_by_name), "stations, with ", sum(len(station.connections_by_id) for station in stations.stations_by_name.itervalues()), "total connections"

if __name__ == '__main__':
	main()
