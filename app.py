import datetime
import random
import fitz
from flask import Flask, Response, request, jsonify
from flask_cors import CORS, cross_origin
import urllib.request
import random
import string
import re

app = Flask(__name__)

def random_string_generator(str_size, allowed_chars):
    return ''.join(random.choice(allowed_chars) for x in range(str_size)) + '-' + str(int(datetime.datetime.now().timestamp()))

chars = string.ascii_letters + string.digits
size = 12

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    print('preparing pdf annonations ...')
    file = request.files['file']
    summaryList = eval(request.form['summaryList'])

    randomString = random_string_generator(size, chars)
    newFileName = "conversions/" + randomString
    articleFileName = newFileName + "-article.pdf"
    outputFileName = newFileName + "-output.pdf"
    outputFileNameRoot = randomString + "-output.pdf"

    file.save(articleFileName)

    doc = fitz.open('./'+articleFileName)
    for page in doc:
        for key in summaryList.keys():
            print(key)
            color = summaryList[key]['color']
            print(color)
            for text in summaryList[key]['text'].values():
                inst = page.search_for(text, quads=True)
                ### HIGHLIGHT
                highlight = page.add_highlight_annot(inst)
                highlight.set_colors(stroke=[round(color['r']/255, 1), round(color['g']/255, 1), round(color['b']/255, 1)])
                highlight.update()

    doc.save(outputFileName, garbage=4, deflate=True, clean=True)

    with open(outputFileName, 'rb') as pdf_file:
        pdf_data = pdf_file.read()

        

    return Response(pdf_data, mimetype='application/pdf')

if __name__ == "__main__":
    app.run(debug=True)

# set FLASK_APP=app.py
# set FLASK_ENV=development
# python -m flask run
# python -m http.server