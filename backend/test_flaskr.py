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
    
    def test_categories_list_get_method(self):
        new_list = self.client().get('/categories')
        self.assertEqual(new_list.status_code, 200)
        self.assertEqual(json.loads(new_list.data)['success'], True)

    def test_404_resource_not_found_error(self):
        test_result = self.client().get('/categories/1000')
        self.assertEqual(test_result.status_code, 404)

    def test_delete_one_question_success(self):
        ques = Question.query.first()
        test_result = self.client().delete('/questions/{}'.format(ques.id))
        self.assertEqual(test_result.status_code, 200)
        exis_ques = Question.query.filter(Question.id == ques.id).one_or_none()
        self.assertEqual(exis_ques, None)

    def test_delete_question_failure(self):
        test_result = self.client().delete('/questions/99')
        self.assertEqual(test_result.status_code, 404)
        
    def test_add_questions_to_database(self):
        test_result = self.client().post('/questions', json = {'question': 'who are you?', 'answer': 'James Bond', 'difficulty': '4', 'category': '4'})
        self.assertEqual(test_result.status_code, 200)  
        final_data = json.loads(test_result.data)
        self.assertEqual(final_data['success'], True)

    def test_add_questions_failure(self):
        test_result = self.client().delete('/questions', json = {'question': 'who are you?', 'answer': 'James Bond', 'difficulty': '4', 'category': '4'})
        self.assertEqual(test_result.status_code, 405)  

    def test_search_questions_in_db(self):
        new_ques = self.client().post('/questions', json = {'question': 'who are you?', 'answer': 'James Bond', 'difficulty': '4', 'category': '4'})
        test_result = self.client().post('/questions/find', json = {'searchTerm': 'who'})
        self.assertEqual(test_result.status_code, 200)  
        final_data = json.loads(test_result.data)
        self.assertEqual(final_data['success'], True)

    def test_failure_search_questions_405(self):
        test_result = self.client().get('/questions/find', json = {'searchTerm': 'UINSS'})
        self.assertEqual(test_result.status_code, 405)  

    def test_pick_correct_category_success(self):
        cat = Category.query.first()
        test_result = self.client().get('/categories/{}/questions'.format(cat.id))
        self.assertEqual(test_result.status_code, 200)  
        final_data = json.loads(test_result.data)
        self.assertEqual(final_data['success'], True)

    def test_pick_category_failure(self):
        test_result = self.client().post('/categories/99/questions')
        self.assertEqual(test_result.status_code, 405)  
        
    def test_quiz_questions_success(self):
        test_result = self.client().post('/quizzes', json = {'previous_questions': [2,4], 'quiz_category':{'type': 'Sports', 'id': 6}})
        self.assertEqual(test_result.status_code, 200)  
        final_data = json.loads(test_result.data)
        self.assertEqual(final_data['success'], True)
    
    def test_quiz_questions_failure(self):
        test_result = self.client().get('/quizzes', json = {})
        self.assertEqual(test_result.status_code, 405)  
      
    





# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()