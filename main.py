import sys
import json
from random import sample, choice


class Stations(object):
    @classmethod
    def from_json_files(cls, stations_filename, connections_filename):
        stations = cls()
        stations.load_from_json_files(stations_filename, connections_filename)

        return stations

    def __init__(self):
        self.stations_by_id = {}

    @property
    def stations_count(self):
        return len(self.stations_by_id)

    @property
    def iterate_stations(self):
        return self.stations_by_id.itervalues()

    @property
    def stations_list(self):
        return list(self.iterate_stations)

    def by_id(self, _id):
        return self.stations_by_id[_id]

    def create_station(self, _id, name):
        Station(_id, name, self)

    def add_station(self, station):
        self.stations_by_id[station._id] = station

    def load_from_json_files(self, stations_filename, connections_filename):
        self.load_stations_from_json_file(stations_filename)
        self.load_connections_from_json_file(connections_filename)

    def load_stations_from_json_file(self, stations_filename):
        with open(stations_filename, 'rb') as f:
            stations_json = json.load(f)

        self.load_stations_from_json(stations_json)

    def load_stations_from_json(self, stations_json):
        for _id_str, name in stations_json:
            _id = int(_id_str)
            self.create_station(_id, name)

    def load_connections_from_json_file(self, connections_filename):
        with open(connections_filename, 'rb') as f:
            connections_json = json.load(f)

        self.load_connections_from_json(connections_json)

    def load_connections_from_json(self, connections_json):
        for first_id_str, second_id_str in connections_json:
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
        self.connections = set()

    def __repr__(self):
        return '<Station %s>' % self._id

    def connect_with(self, station):
        if station in self.connections:
            return

        self.connections.add(station)
        station.connect_with(self)


class FindTheCatGame(object):
    @classmethod
    def start_and_run(cls, stations, pairs_count, iteration_count=100000):
        game = cls(stations)
        game.start(pairs_count)
        game.run(iteration_count=iteration_count)

    def __init__(self, stations):
        self.stations = stations

    def start(self, pairs_count, stations_pairs_ids=None):
        self.initialise_game_stations()
        if stations_pairs_ids is None:
            self.put_random_pairs_on_map(pairs_count)
        else:
            stations_pairs = [
                [self.by_id(first_id), self.by_id(second_id)]
                for first_id, second_id in stations_pairs_ids
            ]
            self.put_pairs_on_map(stations_pairs)

    def run(self, iteration_count=100000):
        for _ in xrange(iteration_count):
            self.step()
            if not self.roaming_pairs_exist:
                break

        print 'Total number of cats:', self.cats_count
        print 'Number of cats found:', self.cats_found

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

    def sample_game_stations(self, count):
        return sample(self.game_stations.values(), count)

    def put_random_pairs_on_map(self, pairs_count):
        stations_pairs = self.create_random_station_pairs(pairs_count)
        self.put_pairs_on_map(stations_pairs)

    def create_random_station_pairs(self, pairs_count):
        return [
            self.sample_game_stations(count=2)
            for _ in xrange(pairs_count)
        ]

    def put_pairs_on_map(self, stations_pairs):
        pairs_count = len(stations_pairs)
        self.pairs_ids = range(pairs_count)
        self.roaming_pairs_ids = set(self.pairs_ids)

        self.cats_game_stations = {}
        self.owners_game_stations = {}
        self.owners_visited_game_stations = {}

        for pair_id, (cat_game_station, owner_game_station) in \
                zip(self.pairs_ids, stations_pairs):
            cat_game_station.put_cat(pair_id)
            owner_game_station.put_owner(pair_id)

    @property
    def cats_count(self):
        return len(self.pairs_ids)

    @property
    def roaming_pairs_exist(self):
        return bool(self.roaming_pairs_ids)

    @property
    def roaming_pairs_count(self):
        return len(self.roaming_pairs_ids)

    @property
    def cats_found(self):
        return self.cats_count - self.roaming_pairs_count

    def get_matched_pairs_per_station(self):
        return {
            game_station: game_station.get_matched_pairs()
            for game_station in self.iterate_game_stations
        }

    def get_all_matched_pairs(self):
        matched_pairs_lists = self.get_matched_pairs_per_station().itervalues()
        return reduce(set.__or__, matched_pairs_lists, set())

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
            possible_game_stations = self.get_cat_possible_moves()
            if not possible_game_stations:
                continue

            next_game_station = choice(possible_game_stations)
            cat_game_station.move_cat_to(pair_id, next_game_station)

    def get_cat_possible_moves(self, pair_id):
        cat_game_station = self.cats_game_stations[pair_id]
        open_neighbours = cat_game_station.open_neighbours

        return open_neighbours

    def move_owners(self):
        for pair_id in self.roaming_pairs_ids:
            possible_game_stations = self.get_owner_possible_moves()
            if not possible_game_stations:
                continue

            next_game_station = choice(possible_game_stations)
            owner_game_station.move_owner_to(pair_id, next_game_station)

    def get_owner_possible_moves(self, pair_id):
            owner_game_station = self.owners_game_stations[pair_id]
            open_neighbours = owner_game_station.open_neighbours
            if not open_neighbours:
                open_neighbours

            visited_neighbours = self.owners_visited_game_stations[pair_id]
            not_visited_open_neighbours = open_neighbours - visited_neighbours

            if not_visited_open_neighbours:
                return not_visited_open_neighbours
            else:
                return open_neighbours


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

    def __repr__(self):
        return '<GameStation %s>' % self.station._id

    def put_cat(self, pair_id):
        self.remove_cat_from_previous_game_station(pair_id)
        self.cats.add(pair_id)
        self.game.cats_game_stations[pair_id] = self

    def put_owner(self, pair_id):
        self.remove_owner_from_previous_game_station(pair_id)
        self.owners.add(pair_id)
        self.game.owners_game_stations[pair_id] = self
        self.game.owners_visited_game_stations\
            .setdefault(pair_id, set())\
            .add(self)

    def remove_cat(self, pair_id):
        if pair_id in self.cats:
            self.cats.remove(pair_id)

    def remove_cat_from_previous_game_station(self, pair_id):
        previous_game_station = self.game.cats_game_stations.get(pair_id)
        if previous_game_station:
            previous_game_station.remove_cat(pair_id)

    def remove_owner(self, pair_id):
        if pair_id in self.owners:
            self.owners.remove(pair_id)

    def remove_owner_from_previous_game_station(self, pair_id):
        previous_game_station = self.game.owners_game_stations.get(pair_id)
        if previous_game_station:
            previous_game_station.remove_owner(pair_id)

    def get_matched_pairs(self):
        return self.cats & self.owners

    def close(self):
        self.is_open = False
        self.remove_matched_pairs()

    def remove_matched_pairs(self):
        matched_pairs = self.get_matched_pairs()
        self.cats -= matched_pairs
        self.owners -= matched_pairs

    @property
    def neighbours(self):
        return {
            self.game.game_stations[station._id]
            for station in self.station.connections
        }

    @property
    def open_neighbours(self):
        return {
            game_station
            for game_station in self.neighbours
            if game_station.is_open
        }

    def move_cat_to(self, pair_id, game_station):
        self.remove_cat(pair_id)
        game_station.put_cat(pair_id)

    def move_owner_to(self, pair_id, game_station):
        self.remove_owner(pair_id)
        game_station.put_owner(pair_id)


def main():
    success, arguments = get_arguments()
    if not success:
        return

    pairs_count, = arguments

    stations = Stations.from_json_files("./tfl_stations.json", "./tfl_connections.json")
    FindTheCatGame.start_and_run(stations, pairs_count=pairs_count)


def get_arguments():
    if len(sys.argv) < 2:
        print 'Please put the number of pairs'
        return False, []

    if len(sys.argv) > 2:
        print 'Too many arguments - only put the number of pairs'
        return False, []

    pairs_count_str = sys.argv[1]
    try:
        pairs_count = int(pairs_count_str)
    except ValueError:
        print 'Please enter a positive numeric value for the number of pairs'
        return False, []

    if pairs_count < 1:
        print 'Please enter a positive numeric value for the number of pairs'
        return False, []

    return True, [pairs_count]

if __name__ == '__main__':
    main()
