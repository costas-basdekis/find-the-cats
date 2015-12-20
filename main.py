import json
from random import randint


class Stations(object):
	def __init__(self):
		self.stations_by_id = {}
		self.stations_by_name = {}

	@property
	def stations_count(self):
		return len(self.stations_by_id)

	@property
	def iterate_stations(self):
	    return self.stations_by_id.itervalues()

	@property
	def stations_id_range(self):
	    return min(self.stations_by_id), max(self.stations_by_id)

	def by_id(self, _id):
	    return self.stations_by_id[_id]

	@property
	def bidi_connections_count(self):
	    return sum(
	    	len(station.connections_by_id)
	    	for station
	    	in self.iterate_stations
	    )

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

		for _id_str, name in raw_stations:
			_id = int(_id_str)
			self.create_station(_id, name)

	def load_connections_from_json_file(self, connections_filename):
		with open(connections_filename, 'rb') as f:
			raw_connections = json.load(f)

		for first_id_str, second_id_str in raw_connections:
			first_id, second_id = int(first_id_str), int(second_id_str)
			first_station = self.by_id(first_id)
			second_station = self.by_id(second_id)

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


class FindTheCatGame(object):
	def __init__(self, stations):
		self.stations = stations

	def start(self, pairs_count):
		self.initialise_game_stations()
		self.put_pairs_on_map(pairs_count)

	def initialise_game_stations(self):
		self.game_stations = {
			station._id: GameStation(self, station)
			for station in self.stations.iterate_stations
		}

	def by_id(self, _id):
		return self.game_stations[_id]

	def put_pairs_on_map(self, pairs_count):
		min_station_id, max_station_id = self.stations.stations_id_range
		for pair_id in xrange(pairs_count):
			cat_station_id = randint(min_station_id, max_station_id)
			owner_station_id = cat_station_id
			while owner_station_id == cat_station_id:
				owner_station_id = randint(min_station_id, max_station_id)

			cat_station = self.by_id(cat_station_id)
			cat_station.put_cat(pair_id)

			owner_station = self.by_id(owner_station_id)
			owner_station.put_owner(pair_id)


class GameStation(object):
	"""
	We are using a differnt class for GameStation, because so that we can have
	more than one instances of FindTheCatGame at any point. The reason we want
	that, is separation of concerns.
	"""
	def __init__(self, game, station):
		self.game = game
		self.station = station
		self.is_open = True
		self.cats = set()
		self.owners = set()

	def put_cat(self, pair_id):
		self.cats.add(pair_id)

	def put_owner(self, pair_id):
		self.owners.add(pair_id)


def main():
	stations = Stations()
	stations.load_from_json_files("./tfl_stations.json", "./tfl_connections.json")
	print 'Loaded', stations.stations_count, "stations, with ", stations.bidi_connections_count, "total connections"

	pairs_count = 10
	game = FindTheCatGame(stations)
	game.start(pairs_count)
	print 'Started a game with', pairs_count, "pairs"

if __name__ == '__main__':
	main()
