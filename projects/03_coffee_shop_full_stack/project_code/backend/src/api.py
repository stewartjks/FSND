import os
from flask import (
        Flask, 
        render_template,
        request,
        Response,
        redirect,
        url_for,
        abort,
        jsonify
    )
from sqlalchemy import exc
import json
# from flask_cors import CORS
import sys

# TODO Replace PATH modifications in application code with modifications on local machine
# Ensure all Python libraries can be located wherever they're installed
sys.path.append('/Users/Jac/Documents/udacity/FSND/projects/01_fyyur/env/bin')
sys.path.append('/Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/site-packages')
sys.path.append('/Users/Jac/Library/Python/3.8/lib/python/site-packages')

from .database.models import db, db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
# CORS(app)

'''
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

## ROUTES
'''
    GET /drinks
        it should be a public endpoint
        @TODO it should contain only the drink.short() data representation
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
    returns status code 200 and json {"success": True, "drinks": drink} where drink is an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks', methods = ['POST'])
def create_drink():
    response_object = {}
    error = False
    try:
        drink_title = request.get_json()['title']
        drink_recipe_json = request.get_json()['recipe']
        drink_recipe = json.dumps(drink_recipe_json)
        new_drink = Drink(title = drink_title, recipe = drink_recipe)
        new_drink.insert()
        # Instructions specify that response data should inclue drink details as a list
        new_drink_details = []
        new_drink_details_object = {
            "id": new_drink.id,
            "title": drink_title,
            "recipe": drink_recipe
        }
        new_drink_details.append(new_drink_details_object)
        response_object.update(
            {
                "success": True,
                "drinks": new_drink_details 
            }
        )
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(400)
    else:
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
@app.route('/drinks/<int:drink_id>', methods = ['PATCH'])
def update_drink(drink_id):
    error = False
    response_object = {}
    try:
        drink = Drink.query.get(drink_id)
        updated_drink_title = request.get_json()['title']
        updated_drink_recipe_json = request.get_json()['recipe']
        updated_drink_recipe = json.dumps(updated_drink_recipe_json)
        drink.title = updated_drink_title
        drink.recipe = updated_drink_recipe
        drink.update()
        new_drink_details = []
        new_drink_details_object = {
            "id": drink.id,
            "title": updated_drink_title,
            "recipe": updated_drink_recipe
        }
        new_drink_details.append(new_drink_details_object)
        response_object.update(
            {
                "success": True,
                "drinks": new_drink_details
            }
        )
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(400)
    else:
        response = json.dumps(response_object)
        return response

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
    response_object = {}
    try:
        drink = Drink.query.get(drink_id)
        drink.delete()
        response_object.update(
            {
                "success": True,
                "delete": drink_id
            }
        )
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(400)
    else:
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