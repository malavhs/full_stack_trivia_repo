from crypt import methods
import json
from nis import cat
import os
import re
from site import abs_paths
from unicodedata import category
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category
QUESTIONS_PER_PAGE = 10

def create_pagination_list(request, actuals):
    top_page = request.args.get('page',1,int) - 1 
    existing_ques = []
    for ques in actuals:
        existing_ques.append(ques.format())
    actual_list = existing_ques[((top_page) * QUESTIONS_PER_PAGE):((top_page) * QUESTIONS_PER_PAGE) + QUESTIONS_PER_PAGE]
    return actual_list


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

    
    """
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories', methods = ['GET'])
    def access_category_list():
        cat_list = Category.query.all()
        cat_final = {}
        for cat in cat_list:
            cat_final[cat.id] = cat.type
        if not cat_list:
            abort(404)    
       
        return jsonify({
            'success': True,
            'categories': cat_final
        })
        
    """
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions', methods = ['GET'])
    def access_questions_list():
        questions = Question.query.all()
        total_ques_len = len(questions)
        new_ques = create_pagination_list(request, questions)
        if not new_ques:
            abort(404)
        
        cat = Category.query.all()
        final_cat = {}
        for c in cat:
            final_cat[c.id] = c.type
    
        return jsonify({
            'success': True,
            'questions': new_ques,
            'total_questions': total_ques_len,
            'categories': final_cat,
            'current_category': final_cat[1]
        })

    """
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:ques_id>', methods = ['DELETE'])
    def delete_question(ques_id):
        to_delete_question = Question.query.filter(Question.id == ques_id).scalar()
        if not to_delete_question:
            abort(404)
        to_delete_question.delete()
        return jsonify({
                'success': True,
                'deleted': ques_id
            })
       

    """
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods = ['POST'])
    def add_questions():
        details = request.get_json()
        if not details:
            abort(422)
        add_question = details.get('question')
        add_difficulty = details.get('difficulty')
        add_answer =  details.get('answer')
        add_category = details.get('category')
        
        additional_question = Question(question=add_question, answer=add_answer, difficulty=add_difficulty, category=add_category)
        additional_question.insert()
        return jsonify({
            "success": True,
            "created" : additional_question.id
        })
        


    """
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/questions/find', methods = ['POST'])
    def search_questions():
        data = request.get_json()
        search_parameter = data.get('searchTerm', None)
        search_parameter = search_parameter.lower()
        if not data:
            abort(422)
        if search_parameter:
            search_results = Question.query.filter(Question.question.contains(search_parameter)).all()
            tot_search_results = len(search_results)
            final_ques = []
            for ques_list in search_results:
                final_ques.append(ques_list.format())
            return jsonify({
                'success': True,
                'questions': final_ques,
                'total_questions': tot_search_results,
                'current_category': None
            })
        abort(404)



    """
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:cat_id>/questions', methods = ['GET'])
    def pick_category(cat_id):
        try:
            select_category = Question.query.filter(Question.category == cat_id).all()
            current_questions = create_pagination_list(request, select_category)
            tot_questions = len(select_category)
            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': tot_questions,
                'current_category': cat_id
            })
        except:
            abort(404)


    """
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods = ['POST'])
    def quiz_game():
        data = request.get_json()
        # missing data test
        if not data:
            abort(422)
        quiz_cat = data.get('quiz_category')
        prev_ques = data.get('previous_questions')

        # Missing parameter test
        if quiz_cat is None:
            abort(400)
        if prev_ques is None:
            abort(400)
        # Get ID of selected category
        interest_id = quiz_cat['id']    
        if interest_id == 0:
            # All 
            condition = ~Question.id.in_(prev_ques)
            ques_list = Question.query.filter(condition).all()
        else:
            # Specific ID filter
            condition = ~Question.id.in_(prev_ques)
            ques_list = Question.query.filter(Question.category == interest_id).filter(condition).all()
        # Total number of trivia questions that can be asked to the user
        tot_ques_list = len(ques_list)
        if tot_ques_list > 0:
            # Pick a random question from the list of questions that can be asked depending on use selection
            gen_rand_number = random.randint(0, len(ques_list) - 1)
            next_ques = ques_list[gen_rand_number]
            next_ques = next_ques.format()
        else:
            next_ques = None
        
        return jsonify({
            'success': True,
            'question': next_ques
        })
    


    """


    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler
    def resource_not_available(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Resource Not Found'
        }), 404

    @app.errorhandler
    def incorrect_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'This is a Bad Request'
        }), 400

    @app.errorhandler
    def request_unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'Request is Unprocessable'
        }), 422

    @app.errorhandler
    def server_error(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'Internal Server Error'
        }), 500
    return app

