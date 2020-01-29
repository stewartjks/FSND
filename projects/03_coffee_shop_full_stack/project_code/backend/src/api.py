import os
from flask import (
        Flask, 
        render_template,
        request,
        Response,
        flash,
        redirect,
        url_for,
        abort,
        jsonify
    )
from sqlalchemy import exc
import json
from flask_cors import CORS
import sys

from .database.models import db, db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def get_drinks():
    drinks = Drink.query.all()
    drink_data = []
    for drink in drinks:
        drink_data.append(
            drink.short()
        )
    data_object = {
        "success": True,
        "drinks": drink_data
    }
    data = jsonify(data_object)
    return data

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks-detail', methods = ['GET'])
def get_drinks_details():
    
    drinks = "Macchiato: espresso with cream and foam, Pour Over: coffee made one cup at a time, Espresso: uniformly ground condensed coffee"
    data_object = {
        "success": True,
        "drinks": drinks
    }
    data = jsonify(data_object)
    return data

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks', methods = ['POST'])
def create_drink():
    response = {}
    error = False
    try:
        drink_title = request.get_json()['title']
        drink_recipe_json = request.get_json()['recipe']
        drink_recipe = json.dumps(drink_recipe_json)
        new_drink = Drink(title = drink_title, recipe = drink_recipe)
        new_drink.insert()
        response_object = {
            "success": True
            }
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(400)
    else:
        flash('Your drink was successfully created!')
        response = json.dumps(response_object)
        return response

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods = ['DELETE'])
def delete_drink(drink_id):
    error = False
    try:
        print(drink_id)
        drink = Drink.query.get(drink_id)
        print(drink)
        drink.delete()
        response_object = {
            "success": True,
            "delete": drink_id
            }
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(400)
    else:
        flash('Your drink was successfully deleted!')
        response = json.dumps(response_object)
        return response


## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''