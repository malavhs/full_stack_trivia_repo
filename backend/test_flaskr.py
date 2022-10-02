import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    Write at least one test for each test for successful operation and for expected errors.
    """
    
    def test_404_resource_not_found_error(self):
        new_list = self.client().get('/categories/1000')
        self.assertEqual(new_list.status_code, 404)
        self.assertEqual(json.loads(new_list.data)['success'], False)

    def test_categories_list_get_method(self):
        new_list = self.client().get('/categories')
        self.assertEqual(new_list.status_code, 200)
        self.assertEqual(json.loads(new_list.data)['success'], True)
    



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()