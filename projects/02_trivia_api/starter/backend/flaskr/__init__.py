import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
	page = request.args.get('page', 1, type=int)
	start =  (page - 1) * QUESTIONS_PER_PAGE
	end = start + QUESTIONS_PER_PAGE

	questions = [question.format() for question in selection]
	current_questions = questions[start:end]

	return current_questions

def create_app(test_config=None):
	# create and configure the app
	app = Flask(__name__)
	setup_db(app)
	cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

	# CORS Headers 
	@app.after_request
	def after_request(response):
		response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
		response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
		return response

	@app.route('/api/categories/', methods=['GET'])
	def retrieve_categories():
		categories = Category.query.order_by(Category.id).all()
		formatted_categories = [category.format() for category in categories]

		return jsonify({
			'success': True,
			'categories': formatted_categories
		})

	@app.route('/api/questions', methods=['GET'])
	def retrieve_questions():
		selection = Question.query.order_by(Question.id).all()
		current_questions = paginate_questions(request, selection)
		categories = Category.query.order_by(Category.id).all()
		formatted_categories = [category.format() for category in categories]

		# https://stackoverflow.com/questions/7961363/removing-duplicates-in-lists
		current_list = list(set([question['category'] for question in current_questions]))

		if len(current_questions) == 0:
			abort(404)

		return jsonify({
			'success': True,
			'questions': current_questions,
			'total_questions': len(selection),
			'categories': formatted_categories,
			'current_category': current_list
		})

	@app.route('/api/questions/<int:question_id>', methods=['DELETE'])
	def delete_question(question_id):
		try:
			question = Question.query.filter(Question.id == question_id).one_or_none()
			question.delete()

			return jsonify({
				'success': True,
				'deleted': question_id,
			})

		except:
			abort(422)

	@app.route('/api/questions', methods=['POST'])
	def create_question():
		body = request.get_json()

		new_question = body.get('question', None)
		new_answer = body.get('answer', None)
		new_difficulty = body.get('difficulty', None)
		new_category = body.get('category', None)
		search = body.get('searchTerm', None)

		try:
			if search:
				selection = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(search)))
				current_questions = paginate_questions(request, selection)

				return jsonify({
					'success': True,
					'questions': current_questions,
					'total_questions': len(selection.all())
				})

			else:
				question = Question(question=new_question, answer=new_answer,difficulty=new_difficulty,category=new_category)
				question.insert()

				return jsonify({
					'success': True,
					'created': question.id
				})

		except:
			abort(422)

	@app.route('/api/categories/<int:category_id>/questions')
	def retrieve_questions_by_category(category_id):
		selection = Question.query.order_by(Question.id).filter(Question.category == category_id).all()
		current_questions = paginate_questions(request, selection)

		if len(current_questions) == 0:
			abort(404)

		return jsonify({
			'success': True,
			'questions': current_questions,
			'total_questions': len(selection),
			'current_category': category_id
		})

	@app.route('/api/quizzes', methods=['POST'])
	def retrieve_play_quiz():
		body = request.get_json()

		previous_questions = body.get('previous_questions', [])
		quiz_category = body.get('quiz_category', None)
		selection = Question.query.filter(Question.id.notin_(previous_questions)).order_by(func.random())

		if quiz_category is not None and quiz_category['id'] > 0:
			selection = selection.filter(Question.category == quiz_category['id'])

		selection = selection.first()

		if not selection:
			return jsonify({
					'success': False,
					'question': False
				})

		return jsonify({
			'success': True,
			'question': selection.format()
		})

	@app.errorhandler(400)
	def bad_request(error):
		return jsonify({
			"success": False,
			"error": 400,
			"message": "bad request"
			}), 400

	@app.errorhandler(404)
	def not_found(error):
		return jsonify({
			"success": False,
			"error": 404,
			"message": "resource not found"
			}), 404

	@app.errorhandler(422)
	def unprocessable(error):
		return jsonify({
		"success": False,
		"error": 422,
		"message": "unprocessable"
		}), 422

	@app.errorhandler(405)
	def unprocessable(error):
		return jsonify({
		"success": False,
		"error": 405,
		"message": "method not allowed"
		}), 405
	
	return app

		