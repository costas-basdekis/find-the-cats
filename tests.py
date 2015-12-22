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
        [STATION_1_ID_STR, STATION_4_ID_STR],
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

    def test_loading_connections(self):
        stations = StationsFactory.create_stations_with_json_stations_and_connections()


class TestConnections(TestCase):
    def setUp(self):
        self.stations = StationsFactory.create_stations_with_json_stations_and_connections()

    def test_stations_are_connected(self):
        station_1 = self.stations.by_id(StationsFactory.STATION_1_ID)
        station_2 = self.stations.by_id(StationsFactory.STATION_2_ID)

        self.assertIn(station_2, station_1.connections)
        self.assertIn(station_1, station_2.connections)

    def test_stations_are_not_connected(self):
        station_1 = self.stations.by_id(StationsFactory.STATION_1_ID)
        station_2 = self.stations.by_id(StationsFactory.STATION_2_ID)
        station_3 = self.stations.by_id(StationsFactory.STATION_3_ID)

        self.assertNotIn(station_3, station_1.connections)
        self.assertNotIn(station_1, station_3.connections)
        self.assertNotIn(station_3, station_2.connections)
        self.assertNotIn(station_2, station_3.connections)


class TestGame(TestCase):
    def test_creating_game(self):
        game = GameFactory.create_game()

    def test_starting_game(self):
        game, pairs_count = GameFactory.create_and_start_game()


class TestGameMatching(TestCase):
    def setUp(self):
        self.game, self.pairs_count = GameFactory.create_and_start_game()

    def test_just_started_game_counts(self):
        self.assertEquals(self.game.cats_count, self.pairs_count)
        self.assertEquals(self.game.cats_found, 0)
        self.assertEquals(self.game.roaming_pairs_count, self.pairs_count)
        self.assertEquals(self.game.roaming_pairs_exist, True)

    def test_matched_pairs_on_just_started_game(self):
        self.assertNotEquals(GameFactory.MATCHED_PAIRS_ON_START, set())
        self.assertEquals(self.game.get_all_matched_pairs(),
                          GameFactory.MATCHED_PAIRS_ON_START)

    def test_moving_a_cat_and_an_owner_to_a_station_matches_them(self):
        originally_unmatched_pair_id = GameFactory.UNMATCHED_PAIRS_ON_START[0]
        # Fixures sanity check
        self.assertNotIn(originally_unmatched_pair_id, self.game.get_all_matched_pairs())

        GameFactory.move_cat_and_owner_to_same_game_station(
            self.game, originally_unmatched_pair_id)
        self.assertIn(originally_unmatched_pair_id, self.game.get_all_matched_pairs())

    def test_matched_pairs_on_first_step_disappear(self):
        self.game.find_and_close_stations()
        self.assertEquals(self.game.get_all_matched_pairs(), set())

    def test_moving_a_cat_and_an_owner_to_a_station_closes_the_station(self):
        originally_unmatched_pair_id = GameFactory.UNMATCHED_PAIRS_ON_START[0]

        game_station = GameFactory.move_cat_and_owner_to_same_game_station(
            self.game, originally_unmatched_pair_id)
        # Fixures sanity check
        self.assertTrue(game_station.is_open)

        self.game.find_and_close_stations()
        self.assertFalse(game_station.is_open)

    def test_a_station_without_matching_pairs_stays_open(self):
        a_station_without_matches = self.game.by_id(
            GameFactory.STATIONS_WITHOUT_MATCHED_PAIRS[0])
        # Fixures sanity check
        self.assertTrue(a_station_without_matches.is_open)

        self.game.find_and_close_stations()
        self.assertTrue(a_station_without_matches.is_open)


class TestVisiting(TestCase):
    def setUp(self):
        self.game, self.pairs_count = GameFactory.create_and_start_game()

    def test_possible_cat_moves_in_just_started_game(self):
        a_pair_id = 0
        cat_game_station = self.game.cats_game_stations[a_pair_id]
        # Fixures sanity check
        self.assertEquals(cat_game_station.station._id, StationsFactory.STATION_1_ID)

        cat_game_station_neighbours = {
            self.game.by_id(StationsFactory.STATION_2_ID),
            self.game.by_id(StationsFactory.STATION_4_ID),
        }
        # Fixures sanity check
        self.assertEquals(cat_game_station.neighbours, cat_game_station_neighbours)

        cat_possible_moves = self.game.get_cat_possible_moves(a_pair_id)
        self.assertEquals(cat_possible_moves, cat_game_station_neighbours)

    def test_possible_cat_moves_dont_contain_game_station_after_closing(self):
        a_pair_id = 0
        cat_game_station = self.game.cats_game_stations[a_pair_id]
        # Fixures sanity check
        self.assertEquals(cat_game_station.station._id, StationsFactory.STATION_1_ID)

        a_neighbour_game_station = list(cat_game_station.neighbours)[0]
        self.assertIn(a_neighbour_game_station,
                      self.game.get_cat_possible_moves(a_pair_id))

        a_neighbour_game_station.close()
        self.assertNotIn(a_neighbour_game_station,
                         self.game.get_cat_possible_moves(a_pair_id))

    def test_possible_owner_moves_in_just_started_game(self):
        a_pair_id = 5
        owner_game_station = self.game.owners_game_stations[a_pair_id]
        # Fixures sanity check
        self.assertEquals(owner_game_station.station._id, StationsFactory.STATION_1_ID)

        owner_game_station_neighbours = {
            self.game.by_id(StationsFactory.STATION_2_ID),
            self.game.by_id(StationsFactory.STATION_4_ID),
        }
        # Fixures sanity check
        self.assertEquals(owner_game_station.neighbours, owner_game_station_neighbours)

        owner_possible_moves = self.game.get_owner_possible_moves(a_pair_id)
        self.assertEquals(owner_possible_moves, owner_game_station_neighbours)

    def test_possible_owner_moves_dont_contain_game_station_after_closing(self):
        a_pair_id = 5
        owner_game_station = self.game.owners_game_stations[a_pair_id]
        # Fixures sanity check
        self.assertEquals(owner_game_station.station._id, StationsFactory.STATION_1_ID)

        a_neighbour_game_station = list(owner_game_station.neighbours)[0]
        self.assertIn(a_neighbour_game_station,
                      self.game.get_owner_possible_moves(a_pair_id))

        a_neighbour_game_station.close()
        self.assertNotIn(a_neighbour_game_station,
                         self.game.get_owner_possible_moves(a_pair_id))

    def test_possible_owner_moves_dont_contain_game_station_after_visiting(self):
        a_pair_id = 5
        owner_game_station = self.game.owners_game_stations[a_pair_id]
        # Fixures sanity check
        self.assertEquals(owner_game_station.station._id, StationsFactory.STATION_1_ID)

        a_neighbour_game_station = list(owner_game_station.neighbours)[0]
        a_neighbour_game_station.put_owner(a_pair_id)

        owner_game_station.put_owner(a_pair_id)
        self.assertNotIn(a_neighbour_game_station,
                         self.game.get_owner_possible_moves(a_pair_id))

    def test_possible_owner_moves_contain_game_station_after_visiting_all_neighbours(self):
        a_pair_id = 5
        owner_game_station = self.game.owners_game_stations[a_pair_id]
        # Fixures sanity check
        self.assertEquals(owner_game_station.station._id, StationsFactory.STATION_1_ID)

        for a_neighbour_game_station in owner_game_station.neighbours:
            a_neighbour_game_station.put_owner(a_pair_id)
        owner_game_station.put_owner(a_pair_id)
        self.assertIn(a_neighbour_game_station,
                      self.game.get_owner_possible_moves(a_pair_id))


if __name__ == '__main__':
    unittest_main()
