# Full Stack Trivia API Backend

## Getting Started

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Enviornment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server. 

## Database Setup
With Postgres running, restore a database using the trivia.psql file provided. From the backend folder in terminal run:
```bash
psql trivia < trivia.psql
```
or **windows**:
```bash
psql -f trivia.psql trivia
```
**Note:** Make sure that you are using the correct owner for the database, else add `-U <username>`.

## Running the server

From within the `backend` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```
or **windows**:
```bash
$env:FLASK_ENV = "development"
$env:FLASK_APP = "flaskr"
flask run
```

Setting the `FLASK_ENV` variable to `development` will detect file changes and restart the server automatically.

Setting the `FLASK_APP` variable to `flaskr` directs flask to use the `flaskr` directory and the `__init__.py` file to find the application. 

## Tasks

One note before you delve into your tasks: for each endpoint you are expected to define the endpoint and response data. The frontend will be a plentiful resource because it is set up to expect certain endpoints and response data formats already. You should feel free to specify endpoints in your own way; if you do so, make sure to update the frontend or you will get some unexpected behavior. 

1. Use Flask-CORS to enable cross-domain requests and set response headers. 
2. Create an endpoint to handle GET requests for questions, including pagination (every 10 questions). This endpoint should return a list of questions, number of total questions, current category, categories. 
3. Create an endpoint to handle GET requests for all available categories. 
4. Create an endpoint to DELETE question using a question ID. 
5. Create an endpoint to POST a new question, which will require the question and answer text, category, and difficulty score. 
6. Create a POST endpoint to get questions based on category. 
7. Create a POST endpoint to get questions based on a search term. It should return any questions for whom the search term is a substring of the question. 
8. Create a POST endpoint to get questions to play the quiz. This endpoint should take category and previous question parameters and return a random questions within the given category, if provided, and that is not one of the previous questions. 
9. Create error handlers for all expected errors including 400, 404, 422 and 500. 

## API Endpoints
### GET `/api/categories`
- Fetches a dictionary of categories in which the keys are the ids and the value is the corresponding string of the category
- Request Arguments: None
- Returns: categories array that contains object with structure `{ id: category_id, type: category_type }`. 
```
{
  "categories": [
    {
      "id": 1, 
      "type": "Science"
    }, 
    {
      "id": 2, 
      "type": "Art"
    }, 
    ...
  ]
}
```
### GET `/api/questions`
- Fetches questions in a paginated way split by 10 at a time, it also includes categories (same as `/api/categories`),  current categories of the retrieved questions and the total of questions in the database.
- Request Arguments: **optional**: page=int, used for pagination to show the next batch of questions available.
- Returns: question in an object with parameters: answer, category, difficulty, question.
```
{
  "categories": [
    {
      "id": 1, 
      "type": "Science"
    }, 
    ...
  ], 
  "current_category": [
    3, 
    4, 
    5, 
    6
  ], 
  "questions": [
    {
      "answer": "Apollo 13", 
      "category": 5, 
      "difficulty": 4, 
      "id": 2, 
      "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"
    }, 
    ...
  ], 
  "success": true, 
  "total_questions": 19
}
```
### POST `/api/questions`
- Post request used for two things: to generate new questions **or** search for questions based on a string parameter.
- Request Arguments: `{ question:"", answer:"", difficulty:1, category: 1 }` **or** `{ searchTerm: "" }`
- Returns: if creating a new question, returns a success value along with the id of the newly created question. For search results, it returns a success value along with list of questions retrieved and the amount of questions that match search result.
#### New question
```
{
  'success': true,
  'created': question_id
}
```
#### Search
```
{
  'success': true,
  'questions': [
      {
        "answer": "Apollo 13", 
        "category": 5, 
        "difficulty": 4, 
        "id": 2, 
        "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"
      }, 
      ...
  ], 
  'total_questions': 20
}
```
### DELETE `/api/questions/<int:question_id>`
- Endpoint to delete a question with given question id.
- Request Arguments: None.
- Returns: returns a success parameter along with the delete id as confirmation.
```
{
  'success': true,
  'deleted': question_id,
}
```
### GET `/api/categories/<int:category_id>/questions`
- Fetches a list of questions based on a specific category paginated 10 at a time.
- Request Arguments: **optional**: page=int, used for pagination to show the next batch of questions available.
- Returns: returns list of questions along with a success value, total of questions and the current category id.
```
{
  'success': true,
  'questions': [
      {
        "answer": "Apollo 13", 
        "category": 5, 
        "difficulty": 4, 
        "id": 2, 
        "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"
      }, 
      ...
  ], 
  'total_questions': 5
  'current_category': category_id
}
```
### POST `/api/quizzes`
- Endpoint used to create a quiz, it returns a random question based on the to parameters it receives: quiz category (or 0 to match any category) you want questions from and an array of previous questions to filter out.
- Request Arguments: `{ previous_questions: [], quiz_category: 1 }`
- Returns: returns a random question filtered by the arguments received. If there is no more questions available (from a category or in general no more questions) it will return false.
```
{
  'success': true,
  'question': {
      "answer": "Apollo 13", 
      "category": 5, 
      "difficulty": 4, 
      "id": 2, 
      "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"
    }
}
```
#### Fail attempt
```
{
  'success': false,
  'question' false
}
```

## Testing
To run the tests, run
```bash
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```