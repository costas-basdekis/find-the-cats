from unittest import TestCase, main as unittest_main

import main


class TestStations(TestCase):
	STATION_1_ID_STR, STATION_1_NAME = "1", "London Bridge"
	STATION_1_ID = int(STATION_1_ID_STR)

	STATIONS_JSON = [
		[STATION_1_ID, STATION_1_NAME],
		["2", "Westminster"],
	]

	def test_create_stations(self):
		main.Stations()

	def test_loading_stations(self):
		stations = main.Stations()
		stations.load_stations_from_json(self.STATIONS_JSON)

	def test_station_by_id_name_matches_from_loaded_stations(self):
		stations = main.Stations()
		stations.load_stations_from_json(self.STATIONS_JSON)

		self.assertIn(self.STATION_1_ID, stations.stations_by_id)
		station_1 = stations.by_id(self.STATION_1_ID)
		self.assertEquals(station_1._id, self.STATION_1_ID)
		self.assertEquals(station_1.name, self.STATION_1_NAME)


if __name__ == '__main__':
	unittest_main()
