from unittest import TestCase, main as unittest_main

import main


class TestStations(TestCase):
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

	def create_stations(self):
		return main.Stations()

	def create_stations_with_json_stations(self):
		stations = self.create_stations()
		stations.load_stations_from_json(self.STATIONS_JSON)

		return stations

	def create_stations_with_json_stations_and_connections(self):
		stations = self.create_stations_with_json_stations()
		stations.load_connections_from_json(self.CONNECTIONS_JSON)

		return stations

	def test_create_stations(self):
		self.create_stations()

	def test_loading_stations(self):
		self.create_stations_with_json_stations()

	def test_station_by_id_name_matches_from_loaded_stations(self):
		stations = self.create_stations_with_json_stations()

		self.assertIn(self.STATION_1_ID, stations.stations_by_id)
		station_1 = stations.by_id(self.STATION_1_ID)
		self.assertEquals(station_1._id, self.STATION_1_ID)
		self.assertEquals(station_1.name, self.STATION_1_NAME)

	def test_loading_connections(self):
		stations = self.create_stations_with_json_stations_and_connections()

	def test_stations_are_connected(self):
		stations = self.create_stations_with_json_stations_and_connections()

		station_1 = stations.by_id(self.STATION_1_ID)
		station_2 = stations.by_id(self.STATION_2_ID)

		self.assertIn(station_2, station_1.connections)
		self.assertIn(station_1, station_2.connections)

	def test_stations_are_not_connected(self):
		stations = self.create_stations_with_json_stations_and_connections()

		station_1 = stations.by_id(self.STATION_1_ID)
		station_2 = stations.by_id(self.STATION_2_ID)
		station_3 = stations.by_id(self.STATION_3_ID)

		self.assertNotIn(station_3, station_1.connections)
		self.assertNotIn(station_1, station_3.connections)
		self.assertNotIn(station_3, station_2.connections)
		self.assertNotIn(station_2, station_3.connections)


if __name__ == '__main__':
	unittest_main()
