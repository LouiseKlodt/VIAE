import unittest
from flask import Flask
from flask_testing import TestCase
from flask_testing import LiveServerTestCase
from selenium import webdriver
import urllib


class TestServerSetup(LiveServerTestCase):


    def create_app(self):
        app = Flask(__name__)
        app.config['TESTING'] = True
        return app
    

    def test_server_is_up_and_running(self):
        response = urllib.request.urlopen(self.get_server_url())
        self.assertEqual(response.code, 200)



if __name__ == '__main__':
    unittest.main()