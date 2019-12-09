import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
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
@app.route('/drinks', methods=['GET'])
def retrieve_drinks():
	selection = Drink.query.order_by(Drink.id).all()

	if len(selection) == 0:
		abort(404)
	
	formatted_drinks = [drink.short() for drink in selection]

	return jsonify({
		'success': True,
		'drinks': formatted_drinks
	})


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def retrieve_drinks_detail(payload):
	selection = Drink.query.order_by(Drink.id).all()
	formatted_drinks = [drink.long() for drink in selection]

	if len(selection) == 0:
		abort(404)

	return jsonify({
		'success': True,
		'drinks': formatted_drinks
	})


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drinks(payload):
	body = request.get_json()

	new_title = body.get('title', None)
	new_recipe = body.get('recipe', None)
	recipe_json	= json.dumps(new_recipe)

	try:
		drink = Drink(title=new_title, recipe=recipe_json)
		drink.insert()

		return jsonify({
			'success': True,
			'drinks': [drink.long()]
		})

	except:
		abort(422)


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drinks(payload, drink_id):
	body = request.get_json()

	drink = Drink.query.get(drink_id)

	if drink is None:
		abort(404)

	new_title = body.get('title', None)
	new_recipe = body.get('recipe', None)

	if new_title is None and new_recipe is None:
		abort(422)


	try:
		if new_title is not None:
			drink.title = new_title
		
		if new_recipe is not None:
			recipe_json	= json.dumps(new_recipe)
			drink.recipe = recipe_json

		drink.update()

		return jsonify({
			'success': True,
			'drinks': [drink.long()]
		})

	except:
		abort(422)


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(payload, drink_id):

	drink = Drink.query.get(drink_id)

	if drink is None:
		abort(404)

	try:
		drink.delete()

		return jsonify({
			'success': True,
			'delete': drink_id
		})

	except:
		abort(422)

## Error Handling

@app.errorhandler(422)
def unprocessable(error):
	return jsonify({
		"success": False, 
		"error": 422,
		"message": "unprocessable"
	}), 422


@app.errorhandler(404)
def not_found(error):
	return jsonify({
		"success": False,
		"error": 404,
		"message": "resource not found"
		}), 404


@app.errorhandler(AuthError)
def unauthorized(err):
	return jsonify({
		"success": False,
		"error": err.status_code,
		"message": err.error
		}), 401