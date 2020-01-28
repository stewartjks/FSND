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
    # TODO replace hard-code value with db query
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
    error = False
    try:
        drink_title = request.get_json()['title']
        print(drink_title, type(drink_title))
        drink_recipe = request.get_json()['recipe']
        print(drink_recipe, type(drink_recipe))
        new_drink = Drink(title = "Espresso", recipe = "Make it")
        print(new_drink)
        new_drink.insert()
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

# def create_venue_submission():
#   error = False
#   body = {}
#   try:
#     venue_name = request.get_json()['name']
#     venue_city = request.get_json()['city']
#     venue_state = request.get_json()['state']
#     venue_address = request.get_json()['address']
#     venue_phone = request.get_json()['phone']
#     venue_genres = request.get_json()['genres']
#     venue_facebook_link = request.get_json()['facebook_link']
#     new_venue = Venue(name = venue_name, city = venue_city, state = venue_state, address = venue_address, phone = venue_phone, genres = venue_genres, facebook_link = venue_facebook_link)
#     # Add new venue record to db
#     db.session.add(new_venue)
#     db.session.commit()
#   except:
#     error = True
#     db.session.rollback()
#     print(sys.exc_info())
#   finally:
#     db.session.close()
#   if error:
#     abort(400)
#   else:
#     flash('Venue ' + venue_name + ' was successfully listed!')
#     return render_template('pages/home.html')

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
