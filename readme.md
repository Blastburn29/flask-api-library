# This repository is about API development using Flask

In `app.py` all the API endpoints exist. I am yet to create seperate folders for librarian and member endpoints. I still have to add blueprint for both. I have added the flask and sqlite initializations in `backend` folder

I have created `models` folder where you will find the classes for each table named as `books` `history` `librarian` and `member`. It also has the `schema.py` where I have handled the JSON Seralization when returning json reponse to a request on frontend.

----

API endpoints expect for
```
/register and /login
```
are *`JWT`* (JSON Web Token) protected.

To download projects requirements
```
pip install -r requirements.txt
```