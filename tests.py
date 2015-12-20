from unittest import TestCase, main as unittest_main

import main


class StationsFactory(object):
	STATION_1_ID_STR, STATION_1_NAME = "1", "London Bridge"
	STATION_1_ID = int(STATION_1_ID_STR)

	STATION_2_ID_STR, STATION_2_NAME = "2", "Westminster"
	STATION_2_ID = int(STATION_2_ID_STR)

	STATION_3_ID_STR, STATION_3_NAME = "3", "Green Park"
	STATION_3_ID = int(STATION_3_ID_STR)

	STATIONS_JSON = [
		[STATION_1_ID, STATION_1_NAME],
		[STATION_2_ID, STATION_2_NAME],
		[STATION_3_ID, STATION_3_NAME],
	]

	CONNECTIONS_JSON = [
		[STATION_1_ID_STR, STATION_2_ID_STR],
	]

	@classmethod
	def create_stations(cls):
		return main.Stations()

	@classmethod
	def create_stations_with_json_stations(cls):
		stations = cls.create_stations()
		stations.load_stations_from_json(cls.STATIONS_JSON)

		return stations

	@classmethod
	def create_stations_with_json_stations_and_connections(cls):
		stations = cls.create_stations_with_json_stations()
		stations.load_connections_from_json(cls.CONNECTIONS_JSON)

		return stations


class GameFactory(object):
	@classmethod
	def create_game(cls, stations=None):
		if not stations:
			stations = StationsFactory.create_stations_with_json_stations_and_connections()

		return main.FindTheCatGame(stations)


class TestStations(TestCase):
	def test_create_stations(self):
		StationsFactory.create_stations()

	def test_loading_stations(self):
		StationsFactory.create_stations_with_json_stations()

	def test_station_by_id_name_matches_from_loaded_stations(self):
		stations = StationsFactory.create_stations_with_json_stations()

		self.assertIn(StationsFactory.STATION_1_ID, stations.stations_by_id)
		station_1 = stations.by_id(StationsFactory.STATION_1_ID)
		self.assertEquals(station_1._id, StationsFactory.STATION_1_ID)
		self.assertEquals(station_1.name, StationsFactory.STATION_1_NAME)


class TestConnections(TestCase):
	def test_loading_connections(self):
		stations = StationsFactory.create_stations_with_json_stations_and_connections()

	def test_stations_are_connected(self):
		stations = StationsFactory.create_stations_with_json_stations_and_connections()

		station_1 = stations.by_id(StationsFactory.STATION_1_ID)
		station_2 = stations.by_id(StationsFactory.STATION_2_ID)

		self.assertIn(station_2, station_1.connections)
		self.assertIn(station_1, station_2.connections)

	def test_stations_are_not_connected(self):
		stations = StationsFactory.create_stations_with_json_stations_and_connections()

		station_1 = stations.by_id(StationsFactory.STATION_1_ID)
		station_2 = stations.by_id(StationsFactory.STATION_2_ID)
		station_3 = stations.by_id(StationsFactory.STATION_3_ID)

		self.assertNotIn(station_3, station_1.connections)
		self.assertNotIn(station_1, station_3.connections)
		self.assertNotIn(station_3, station_2.connections)
		self.assertNotIn(station_2, station_3.connections)


class TestGame(TestCase):
	def test_creating_game(self):
		game = GameFactory.create_game()

	def test_starting_game(self):
		game = GameFactory.create_game()
		game.start(10)

	def test_just_started_game_counts(self):
		game = GameFactory.create_game()
		pairs_count = 10
		game.start(pairs_count)

		self.assertEquals(game.cats_count, pairs_count)
		self.assertEquals(game.cats_found, 0)
		self.assertEquals(game.roaming_pairs_count, pairs_count)
		self.assertEquals(game.roaming_pairs_exist, True)


if __name__ == '__main__':
	unittest_main()
