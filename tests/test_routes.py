import os
import sys
import unittest

import json

# Add parent directory to path for import
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

from app import app, db
from app.models import Menu

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEST_DB = os.path.join(BASE_DIR, 'test.db')


class BasicTests(unittest.TestCase):

    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = \
            os.environ.get('TEST_DATABASE_URL') or \
            'sqlite:///' + TEST_DB
        self.app = app.test_client()
        db.drop_all()
        db.create_all()

    def tearDown(self):
        pass

    def test_home(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'application/json')
        body = json.loads(response.data)
        self.assertEqual(body['status'], 'ok')
        # Extended: check new fields added in our update
        self.assertIn('message', body)
        self.assertIn('version', body)
        self.assertEqual(body['message'], 'Welcome to the Daily Menu API!')

    def test_menu_empty(self):
        response = self.app.get('/menu', follow_redirects=True)
        self.assertEqual(response.status_code, 404)
        body = json.loads(response.data)
        # Extended: check available flag is False when no menu
        self.assertFalse(body['available'])

    def test_menu_item(self):
        test_name = "test"
        test_item = Menu(name=test_name)
        db.session.add(test_item)
        db.session.commit()
        response = self.app.get('/menu', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'application/json')
        body = json.loads(response.data)
        self.assertTrue('today_special' in body)
        self.assertEqual(body['today_special'], test_name)
        # Extended: check available flag is True when menu exists
        self.assertTrue(body['available'])

if __name__ == "__main__":
    unittest.main()