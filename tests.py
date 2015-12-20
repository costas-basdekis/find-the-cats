from unittest import TestCase, main as unittest_main

import main


class StationsFactory(object):
	STATION_1_ID_STR, STATION_1_NAME = "1", "London Bridge"
	STATION_1_ID = int(STATION_1_ID_STR)

	STATION_2_ID_STR, STATION_2_NAME = "2", "Westminster"
	STATION_2_ID = int(STATION_2_ID_STR)

	STATION_3_ID_STR, STATION_3_NAME = "3", "Green Park"
	STATION_3_ID = int(STATION_3_ID_STR)

	STATION_4_ID_STR, STATION_4_NAME = "4", "Oxford Circus"
	STATION_4_ID = int(STATION_4_ID_STR)

	STATIONS_JSON = [
		[STATION_1_ID, STATION_1_NAME],
		[STATION_2_ID, STATION_2_NAME],
		[STATION_3_ID, STATION_3_NAME],
		[STATION_4_ID, STATION_4_NAME],
	]
	STATIONS_IDS = [
		_id
		for _id, _ in STATIONS_JSON
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
	STATIONS_PAIRS_IDS = [
		[StationsFactory.STATION_1_ID, StationsFactory.STATION_2_ID],
		[StationsFactory.STATION_2_ID, StationsFactory.STATION_2_ID],
		[StationsFactory.STATION_1_ID, StationsFactory.STATION_3_ID],
		[StationsFactory.STATION_3_ID, StationsFactory.STATION_3_ID],
		[StationsFactory.STATION_2_ID, StationsFactory.STATION_2_ID],
		[StationsFactory.STATION_3_ID, StationsFactory.STATION_1_ID],
		[StationsFactory.STATION_1_ID, StationsFactory.STATION_1_ID],
		[StationsFactory.STATION_1_ID, StationsFactory.STATION_2_ID],
		[StationsFactory.STATION_2_ID, StationsFactory.STATION_3_ID],
		[StationsFactory.STATION_1_ID, StationsFactory.STATION_3_ID],
	]
	PAIRS_COUNT = len(STATIONS_PAIRS_IDS)
	MATCHED_PAIRS_ON_START = {
		pair_id
		for pair_id, (first_id, second_id) in enumerate(STATIONS_PAIRS_IDS)
		if first_id == second_id
	}
	UNMATCHED_PAIRS_ON_START = [
		pair_id
		for pair_id, (first_id, second_id) in enumerate(STATIONS_PAIRS_IDS)
		if first_id != second_id
	]
	STATIONS_WITH_MATCHED_PAIRS = {
		first_id
		for pair_id, (first_id, second_id) in enumerate(STATIONS_PAIRS_IDS)
		if first_id == second_id
	}
	STATIONS_WITHOUT_MATCHED_PAIRS = sorted(
		set(StationsFactory.STATIONS_IDS) - STATIONS_WITH_MATCHED_PAIRS
	)

	@classmethod
	def create_game(cls, stations=None):
		if not stations:
			stations = StationsFactory.create_stations_with_json_stations_and_connections()

		return main.FindTheCatGame(stations)

	@classmethod
	def create_and_start_game(cls, stations=None, pairs_count=None,
							  stations_pairs_ids=None):
		game = cls.create_game(stations=stations)
		if pairs_count is None:
			pairs_count = cls.PAIRS_COUNT
			if stations_pairs_ids is None:
				stations_pairs_ids = cls.STATIONS_PAIRS_IDS
		game.start(pairs_count, stations_pairs_ids=stations_pairs_ids)

		return game, pairs_count

	@classmethod
	def move_cat_and_owner_to_same_game_station(cls, game, pair_id):
		a_common_station = game.by_id(StationsFactory.STATION_1_ID)
		a_common_station.put_cat(pair_id)
		a_common_station.put_owner(pair_id)

		return a_common_station


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
		game, pairs_count = GameFactory.create_and_start_game()

	def test_just_started_game_counts(self):
		game, pairs_count = GameFactory.create_and_start_game()

		self.assertEquals(game.cats_count, pairs_count)
		self.assertEquals(game.cats_found, 0)
		self.assertEquals(game.roaming_pairs_count, pairs_count)
		self.assertEquals(game.roaming_pairs_exist, True)

	def test_matched_pairs_on_just_started_game(self):
		game, pairs_count = GameFactory.create_and_start_game()

		self.assertNotEquals(GameFactory.MATCHED_PAIRS_ON_START, set())
		self.assertEquals(game.get_all_matched_pairs(),
						  GameFactory.MATCHED_PAIRS_ON_START)

	def test_moving_a_cat_and_an_owner_to_a_station_matches_them(self):
		game, pairs_count = GameFactory.create_and_start_game()

		originally_unmatched_pair_id = GameFactory.UNMATCHED_PAIRS_ON_START[0]
		self.assertNotIn(originally_unmatched_pair_id, game.get_all_matched_pairs())

		GameFactory.move_cat_and_owner_to_same_game_station(
			game, originally_unmatched_pair_id)
		self.assertIn(originally_unmatched_pair_id, game.get_all_matched_pairs())

	def test_matched_pairs_on_first_step_disappear(self):
		game, pairs_count = GameFactory.create_and_start_game()

		game.find_and_close_stations()
		self.assertEquals(game.get_all_matched_pairs(), set())

	def test_moving_a_cat_and_an_owner_to_a_station_closes_the_station(self):
		game, pairs_count = GameFactory.create_and_start_game()

		originally_unmatched_pair_id = GameFactory.UNMATCHED_PAIRS_ON_START[0]

		game_station = GameFactory.move_cat_and_owner_to_same_game_station(
			game, originally_unmatched_pair_id)
		self.assertTrue(game_station.is_open)

		game.find_and_close_stations()
		self.assertFalse(game_station.is_open)

	def test_a_station_without_matching_pairs_stays_open(self):
		game, pairs_count = GameFactory.create_and_start_game()

		a_station_without_matches = game.by_id(
			GameFactory.STATIONS_WITHOUT_MATCHED_PAIRS[0])
		self.assertTrue(a_station_without_matches.is_open)

		game.find_and_close_stations()
		self.assertTrue(a_station_without_matches.is_open)


if __name__ == '__main__':
	unittest_main()
