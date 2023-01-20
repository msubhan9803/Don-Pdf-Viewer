## Instruction to run the project:
1. You need to run php. So I placed the folder in xampp htdocs directory (to run php)
2. Run the python api with following commands
3. Open the web/Home.html file in browser i.e. http://127.0.0.1/don-pdf/web/Home.html

## Commands to run python api:
set FLASK_APP=app.py
set FLASK_ENV=development
python -m flask run


# FLow:
1. we hit the summary text api with the file from frontend
gets the summary
2. hits the python api and gets the highlighted file