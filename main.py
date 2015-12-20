import json
from random import sample


def random_item(_list, avoiding_item=None):
	item = avoiding_item
	while item == avoiding_item:
		# sample returns a list
		item, = sample(_list, 1)

	return item


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
	def stations_list(self):
	    return list(self.iterate_stations)

	def get_random_station(self, avoiding_station=None):
		return random_item(self.stations_list, avoiding_item=avoiding_station)

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

	@property
	def iterate_game_stations(self):
		return self.game_stations.itervalues()

	def by_id(self, _id):
		return self.game_stations[_id]

	def get_random_game_station(self, avoiding_game_station=None):
		avoiding_station = \
			avoiding_game_station.station if avoiding_game_station else None
		station = self.stations\
			.get_random_station(avoiding_station=avoiding_station)
		return self.by_id(station._id)

	def put_pairs_on_map(self, pairs_count):
		self.pairs_ids = range(pairs_count)
		self.roaming_pairs_ids = set(self.pairs_ids)

		for pair_id in self.pairs_ids:
			cat_game_station = self.get_random_game_station()
			cat_game_station.put_cat(pair_id)

			owner_game_station = self\
				.get_random_game_station(avoiding_game_station=cat_game_station)
			owner_game_station.put_owner(pair_id)

		self.cats_game_stations = {
			pair_id: game_station
			for game_station in self.iterate_game_stations
			for pair_id in game_station.cats
		}

		self.owners_game_stations = {
			pair_id: game_station
			for game_station in self.iterate_game_stations
			for pair_id in game_station.owners
		}

		self.owners_visited_game_stations = {
			pair_id: {game_station}
			for pair_id, game_station
			in self.owners_game_stations.iteritems()
		}

	def get_matched_pairs_per_station(self):
		return {
			game_station: game_station.get_matched_pairs()
			for game_station in self.iterate_game_stations
		}

	def step(self):
		self.find_and_close_stations()
		self.move_cats()
		self.move_owners()

	def find_and_close_stations(self):
		matched_pairs_per_station = self.get_matched_pairs_per_station()
		for game_station, matched_pairs in matched_pairs_per_station.iteritems():
			if not matched_pairs:
				continue

			for pair_id in matched_pairs:
				print 'Owner', pair_id, 'found cat', pair_id, '-', game_station.station.name, 'is now closed'

			game_station.close()
			self.roaming_pairs_ids -= matched_pairs

	def move_cats(self):
		for pair_id in self.roaming_pairs_ids:
			cat_game_station = self.cats_game_stations[pair_id]
			open_neighbours = cat_game_station.open_neighbours
			if not open_neighbours:
				continue

			next_game_station = random_item(open_neighbours)
			cat_game_station.move_cat_to(pair_id, next_game_station)
			self.cats_game_stations[pair_id] = next_game_station

	def move_owners(self):
		for pair_id in self.roaming_pairs_ids:
			owner_game_station = self.owners_game_stations[pair_id]
			open_neighbours = owner_game_station.open_neighbours
			if not open_neighbours:
				continue

			visited_neighbours = self.owners_visited_game_stations[pair_id]
			not_visited_open_neighbours = open_neighbours - visited_neighbours

			if not_visited_open_neighbours:
				next_game_station = random_item(not_visited_open_neighbours)
			else:
				next_game_station = random_item(open_neighbours)
			owner_game_station.move_owner_to(pair_id, next_game_station)
			self.owners_game_stations[pair_id] = next_game_station
			self.owners_visited_game_stations[pair_id].add(next_game_station)


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

	def get_matched_pairs(self):
		return self.cats & self.owners

	def close(self):
		self.is_open = False
		matched_pairs = self.get_matched_pairs()
		self.cats -= matched_pairs
		self.owners -= matched_pairs

	@property
	def open_neighbours(self):
		stations = self.station.connections_by_id.itervalues()
		neighbours = [
			self.game.game_stations[station._id]
			for station in stations
		]

		return {
			game_station
			for game_station in neighbours
			if game_station.is_open
		}

	def move_cat_to(self, pair_id, game_station):
		self.cats.remove(pair_id)
		game_station.put_cat(pair_id)

	def move_owner_to(self, pair_id, game_station):
		self.owners.remove(pair_id)
		game_station.put_owner(pair_id)

def main():
	stations = Stations()
	stations.load_from_json_files("./tfl_stations.json", "./tfl_connections.json")
	print 'Loaded', stations.stations_count, "stations, with ", stations.bidi_connections_count, "total connections"

	pairs_count = 10
	game = FindTheCatGame(stations)
	game.start(pairs_count)
	print 'Started a game with', pairs_count, "pairs"

	game.step()
	game.step()


if __name__ == '__main__':
	main()
