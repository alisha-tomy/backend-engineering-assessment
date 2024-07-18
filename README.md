# Engineering Assessment

Starter project to use for the engineering assessment exercise

## Requirements
- Docker
- docker compose

## Getting started
Build the docker container and run the container for the first time
```docker compose up```

Rebuild the container after adding any new packages
``` docker compose up --build```

The run command script creates a super-user with username & password picked from `.env` file

## Quiz Application API

This application provides a set of APIs for quiz creation and participation. The service is accessible through a web browser with the Swagger page at http://0.0.0.0:8000/.

## Authentication
Token authentication is implemented for the service. Only the user creation API is accessible without authentication.

## API Endpoints

### 1. Create Users
Url: /user-profiles/
Method: POST 
Description:
    is_creator should be true for quiz creators and false for participants.
    This API is open and does not require authentication.

Sample json to create a Quiz creator
{
  "user": {
    "username": "creator1",
    "email": "creator1@example.com",
    "password": "creator1"
  },
  "is_creator": true
}

Sample json to create a participant
{
  "user": {
    "username": "participant1",
    "email": "participant1@example.com",
    "password": "participant1"
  },
  "is_creator": false
}
All the other operations required authentication

### 2. Login
Once a creator user or the participant user is created, they can log in using this API to receive a user token
Url: /login/ 
Method: POST
{
  "username": "creator1",
  "password": "creator1"
}

Use the token from the above login API for the following actions:

### Creator User Actions

1. Question add: 
    Url: /questions/add/
    Method: POST
    Sample Data:
        {
            "question_text": "What is the capital of czech republic?",
            "options": [
                {
                "option_text": "Prague",
                "is_correct": true
                },
                {
                "option_text": "Delhi",
                "is_correct": false
                }
            ]
        }
2. Question list: Lists all questions added by the authenticated creator user
    Url: /questions/
    Method: GET

3. Question edit: 
    Url: /questions/edit/<question id>/
    Method: POST
    Sample Data:
        {
            "question_text": "What is the capital of czech?",
            "options": [
                {
                "id": 13,
                "option_text": "Prague",
                "is_correct": true
                },
                {
                "id": 14,
                "option_text": "Brno",
                "is_correct": false
                }
            ]
            }
    Description:
        "id" is the PK of corresponding Option table and question id is PK of Question table

4. Create Quiz: 
    Url: /quiz/create/
    Method: POST
    Sample Data:
        {
            "title": "Capital city quiz 1",
            "description": "quiz 1",
            "questions": [
                1, 2
            ]
        }
    Description:
        Values in questions key are list of question IDs from the Question table

5. Assign Quiz to user: 
    Url: /challenge/assign/
    Method: POST
    Sample Data:
        {
            "user_id": 2,
            "quiz_id": 1
        }
    Description:
        user_id is PK of UserProfile and quiz_id is PK of Quiz

6. View Quiz List: Lists all the quizzes created by the authenticated creator user
    Url: /quizzes/
    Method: GET

7. View challenges of a list: Lists all the challenges created for a quiz
    Url: quizzes/<quiz id>/challenges/
    Method: GET
    Description:
        quiz id is PK of Quiz table

8. View challenge details (scores / progress): Returns all details of a challenge
    Url: /challenges/<challenge id>/
    Method: GET
    Description:
        challenge id is PK of Challenge table

### Participant User Actions

1. View all challenges: Lists all challenges assigned to the participant
    Url: /challenges/
    Method: GET

2. Accept Quiz Challenge
    Url: /challenges/accept/<challenge id>/
    Method: POST
    Description:
        challenge id is PK of Challenge table

3. Answer a question in challenge
    Url: /challenges/<challenge id>/answer/
    Method: POST
    Sample Date:
        {
        "challenge": 1,
        "option": 2
        }
    Description:
        challenge is PK of Challenge table and option is PK of Option table

4. Finish challenge
    Url: /challenge/<challenge id>/finish/
    Method: POST
    Description:
        challenge id is PK of Challenge table

5. View challenge details (scores / progress): Returns all details of a challenge
    Url: /challenges/<challenge id>/
    Method: GET
    Description:
        challenge id is PK of Challenge table

Notes: 
    Number of correct answers will be updated only after the finish challenge API
    Random test cases are added in the tests.py