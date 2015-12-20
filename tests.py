from unittest import TestCase, main as unittest_main

import main


class TestCreatingStations(TestCase):
	def test_create_stations(self):
		main.Stations()


if __name__ == '__main__':
	unittest_main()
