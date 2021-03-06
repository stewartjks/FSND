import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from  sqlalchemy.sql.expression import func, select
from flask_cors import CORS
import random
import json
from requests.models import Response
import sys

from models import db, setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  Set up CORS. Allow '*' for origins.
  '''
  CORS(
    app,
    origins='*'
  )

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, DELETE')
    return response

  '''
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories', methods = ['GET'])
  def get_all_categories():
    categories = Category.query.all()
    categories_list = []
    result = {}
    for category in categories:
      categories_list.append(category.type)
    result.update(
      {
        "categories": categories_list
      }
    )
    result_json = jsonify(result)
    return result_json

  '''
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions', methods = ['GET'])
  def get_questions():
    result = {}
    page_number_string = request.args.get('page')
    if page_number_string:
      page_number = int(page_number_string)
    else:
      page_number = 1
    questions = Question.query.paginate(page=page_number, error_out=False, max_per_page=10)
    questions_object = []
    for question in questions.items:
      questions_object.append(
        {
          "id": question.id,
          "question": question.question,
          "answer": question.answer,
          "category": question.category,
          "difficulty": question.difficulty
        }
      )
    questions_count = Question.query.count()
    categories = Category.query.all()
    # Add placeholder at zero-index since categories are not (but should be) zero-indexed in database
    categories_object = ['']
    for category in categories:
      categories_object.append(category.type)
    first_question = Question.query.first()
    first_question_category = first_question.category
    result.update({
      "questions": questions_object,
      "total_questions": questions_count,
      "categories": categories_object,
      "current_category": first_question_category
    })
    response_json = jsonify(result)
    return response_json
  
  '''
  Create an endpoint to DELETE a question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:id>/delete', methods = ['DELETE'])
  def delete_question(id):
    result = {}
    error = False
    try:
      question = Question.query.get(id)
      question_id = question.id
      db.session.delete(question)
      db.session.commit()
    except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
    finally:
      db.session.close()
      result.update(
        {
         "deleted_question": question_id
        }
      )
    if error:
      abort(400)
    else:
      response_json = jsonify(result)
      return response_json

  '''
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions/create', methods = ['POST'])
  def create_question():
    error = False
    response = {}
    try:
      new_q_content = request.get_json()['question']
      new_answer = request.get_json()['answer']
      new_difficulty = request.get_json()['difficulty']
      new_category_raw = (request.get_json()['category'])
      # Increment category by one to account for non-zero indexing in starter code
      new_category = (int(new_category_raw) + 1)
      new_question = Question(question=new_q_content, answer=new_answer, difficulty=new_difficulty, category=new_category)
      db.session.add(new_question)
      db.session.commit()
    except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
    finally:
      db.session.close()
      response.update(
        {
          "success": True
        }
      )
    if error:
      abort(400)
    else:
      response_json = jsonify(response)
      return response_json

  '''
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods = ['POST'])
  def get_search_results():
    error = False
    response = {}
    try:
      search_term = request.get_json()['searchTerm']
      matches = Question.query.filter(Question.question.ilike('%' + search_term + '%')).all()
      matches_list = []
      for match in matches:
        matches_list.append(
          {
            "id": match.id,
            "question": match.question,
            "answer": match.answer,
            "category": match.category,
            "difficulty": match.difficulty
          }
        )
      response.update(
        {
          "questions": matches_list 
        }
      )
    except:
      error = True
      print(sys.exc_info())
    if error:
      abort(400)
    else:
      response_json = jsonify(response)
      return response_json

  '''
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions', methods = ['GET'])
  def get_category_questions(category_id):
    error = False
    result = {}
    try:
      category_questions = Question.query.filter_by(category = category_id)
      questions_list = []
      for question_object in category_questions:
        questions_list.append(
          {
            "id": question_object.id,
            "question": question_object.question,
            "answer": question_object.answer,
            "category": question_object.category,
            "difficulty": question_object.difficulty
          }
        )
      total_questions = Question.query.filter_by(id = category_id).count()
      current_category = category_id
      result.update({
        "questions": questions_list,
        "total_questions": total_questions,
        "current_category": current_category
      })
    except:
      error = True
      abort(400)
    finally:
      response_object = jsonify(result)
      return response_object


  '''
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take a category and a previous question as parameters 
  and return a random question that is is not one of the previous questions and is
  within the given category, if one was provided.

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes/<int:quiz_id>/play', methods = ['POST'])
  def create_quiz(quiz_id):
    error = False
    response = {}
    try:
      category_selected = request.get_json()['quiz_category']
      category_id = category_selected['id']
      excluded_questions = request.get_json()['previous_questions']
      quiz_category = Category.query.get(category_id)
      excluded_question_ids = []
      for question in excluded_questions:
        excluded_question_ids.append(question['id'])
      # Get question list and randomize as informed by Stack Overflow question 60805, "Getting Random Row Through Sqlalchemy"
      all_questions = Question.query.order_by(func.random()).all()
      new_question_selected = False
      question_dict = {}
      for question in all_questions:
        while new_question_selected == False:
          if question.id in excluded_question_ids:
            pass
          elif question.id not in excluded_question_ids:
            question_dict.update(
              {
                "id": question.id,
                "question": question.question,
                "answer": question.answer,
                "category": question.category,
                "difficulty": question.difficulty
              }
            )
            response.update(
              {
                "question": question_dict
              }
            )
            new_question_selected = True
          else:
            pass
    except:
      error = True
      print(sys.exc_info())
      abort(400)
    finally:
      response_object = jsonify(response)
      return response_object

  '''
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(400)
  def generic_error(e):
    return jsonify(
      {
        "errorCode": 400,
        "message": "Sorry, something went wrong.",
        "errorDetails": e
      }
    )

  @app.errorhandler(403)
  def authorization_error(e):
    return jsonify(
      {
        "errorCode": 403,
        "message": "Sorry, this request was not correctly authorized."
      }
    )

  @app.errorhandler(404)
  def resource_not_found(e):
    return jsonify(
        {
          "errorCode": 404,
          "message": "Sorry, there's no page or resource at this location."
        }
      )
  
  @app.errorhandler(422)
  def unprocessable_request(e):
    return jsonify(
        {
          "errorCode": 422,
          "message": "Sorry, this request is not valid for this resource."
        }
      )
  
  @app.errorhandler(500)
  def server_error(e):
    return jsonify(
        {
          "errorCode": 500,
          "message": "Sorry, the server encountered an error in processing your request."
        }
      )
  
  return app

    