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
    # print('summaryList: ', summaryList)

    randomString = random_string_generator(size, chars)
    newFileName = "conversions/" + randomString
    articleFileName = newFileName + "-article.pdf"
    outputFileName = newFileName + "-output.pdf"
    outputFileNameRoot = randomString + "-output.pdf"

    file.save(articleFileName)

    doc = fitz.open('./'+articleFileName)
    for page in doc:
        text_instances = []
        ### SEARCH
        # for text in summaryList:
        #     text_instances.append(page.search_for(text, quads=True))
        # ### HIGHLIGHT
        # for inst in text_instances:
        #     highlight = page.add_highlight_annot(inst)
        #     highlight.set_colors(stroke=[0.5, 1, 1])
        #     highlight.update()

        for key in summaryList.keys():
            print(key)
            color = summaryList[key]['color']
            print(color)
            for text in summaryList[key]['text'].values():
                # print('text: ', text)
                inst = page.search_for(text, quads=True)
                ### HIGHLIGHT
                highlight = page.add_highlight_annot(inst)
                highlight.set_colors(stroke=[0.5, 1, 1])
                highlight.update()


    # print('text_instances: ', text_instances)

    doc.save(outputFileName, garbage=4, deflate=True, clean=True)

    return jsonify({
        "message": "Success",
        "status": 200,
        "summarizedFileUrl": outputFileNameRoot
    })

if __name__ == "__main__":
    app.run(debug=True)

# set FLASK_APP=app.py
# set FLASK_ENV=development
# python -m flask run
# python -m http.server