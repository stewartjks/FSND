import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
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
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(
    app,
    origins='*'
  )

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  # @app.after_request()
  # def after_request(response):
  #   response.headers.add('Access-Control-Allow-Headers', 'Content-Type', 'Authorization')
  #   response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
  #   return response

  '''
  @TODO: 
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
    print(result)
    result_json = jsonify(result)
    print(result_json)
    return result_json

  '''
  @TODO: 
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
    categories_object = []
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
  @TODO: 
  Create an endpoint to DELETE a question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:id>', methods = ['DELETE'])
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
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/question', methods = ['POST'])
  def create_question():
    error = False
    response = {}
    try:
      new_q_content = request.get_json()['question']
      new_answer = request.get_json()['answer']
      new_difficulty = request.get_json()['difficulty']
      new_category = request.get_json()['category']
      new_question = Question(question=new_q_content, answer=new_answer, difficulty=new_difficulty, category=new_category)
      db.session.add(new_question)
      db.session.commit()
    except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
    finally:
      db.session.close()
      result.update(
        {
          "success": True
        }
      )
    if error:
      abort(400)
    else:
      response_json = jsonify(result)
      return response_json

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions', methods = ['POST'])
  def get_search_results():
    error = False
    response = {}
    try:
      search_term = request.get_json()['searchTerm']
      matches = Question.query.filter(Question.question.ilike('%' + search_term + '%')).all()
      match_list = []
      for match in matches:
        match_list.append(match.question)
      response.update(
        {
          "matches": match_list 
        }
      )
      print(response)
    except:
      error = True
      print(sys.exc_info())
    if error:
      abort(400)
    else:
      response_json = jsonify(response)
      return response_json

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  @TODO: Fix issue with template not picking up attributes

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions', methods = ['GET'])
  def get_category_questions(category_id):
    error = False
    result = {}
    try:
      category_questions = Question.query.filter_by(id = category_id)
      questions_list = []
      for question_object in category_questions:
        questions_list.append(
          question_object.question
        )
      total_questions = Question.query.filter_by(id = category_id).count()
      current_category = category_questions[0].category
      result.update({
        "questions": questions_list,
        "total_questions": total_questions,
        "current_category": current_category
      })
      print(result)
    except:
      error = True
      abort(400)
    finally:
      response_object = jsonify(result)
      return response_object


  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  
  return app

    