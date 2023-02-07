## Instruction to run the project:
1. You need to run php. So I placed the folder in xampp htdocs directory (to run php)
2. Run the python api with following commands
3. Open the web/Home.html file in browser i.e. http://127.0.0.1/don-pdf/web/Home.html

## Commands to run python api:
set FLASK_APP=app.py
python -m flask run
python -m http.server (run in separate terminal)


# FLow:
1. we hit the summary text api with the file from frontend
gets the summary
2. hits the python api and gets the highlighted file


## Commands to deploy python api
gunicorn app:app -b 0.0.0.0:8000 --daemon

ps aux --forest | grep gunicorn

sudo kill -9 4930 4968

sudo apt-get install php-curl