import unittest
from flask_testing import LiveServerTestCase
from selenium import webdriver

browser = webdriver.Safari()
browser.get('http://localhost:5000')

assert 'Django' not in browser.title



def create_app(self):
        config_name = 'testing'
        app = create_app(config_name)
        app.config.update(
            # Change the port that the liveserver listens on
            LIVESERVER_PORT=8943
        )
        return app