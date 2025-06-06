import datetime
import random
import fitz
from flask import Flask, Response, request
import random
import string
import os
import multiprocessing as mp
import time

app = Flask(__name__)

def random_string_generator(str_size, allowed_chars):
    return ''.join(random.choice(allowed_chars) for x in range(str_size)) + '-' + str(int(datetime.datetime.now().timestamp()))

chars = string.ascii_letters + string.digits
size = 12

def process_element(page, text, color):
    print('starting process...')
    inst = page.search_for(text, quads=True)
    ### HIGHLIGHT
    highlight = page.add_highlight_annot(inst)
    highlight.set_colors(stroke=[round(color['r']/255, 1), round(color['g']/255, 1), round(color['b']/255, 1)])
    highlight.update()

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    print('preparing pdf annonations ...')
    file = request.files['file']
    summaryList = eval(request.form['summaryList'])

    randomString = random_string_generator(size, chars)
    newFileName = "conversions/" + randomString
    articleFileName = newFileName + "-article.pdf"
    outputFileName = newFileName + "-output.pdf"

    file.save(articleFileName)

    start = time.time()

    doc = fitz.open('./'+articleFileName)
    processes = []
    for page in doc:
        for key in summaryList.keys():
            color = summaryList[key]['color']

            for text in summaryList[key]['text'].values():
                p = mp.Process(target=process_element, args=(page, text, color,))
                processes.append(p)
                # inst = page.search_for(text, quads=True)
                # ### HIGHLIGHT
                # highlight = page.add_highlight_annot(inst)
                # highlight.set_colors(stroke=[round(color['r']/255, 1), round(color['g']/255, 1), round(color['b']/255, 1)])
                # highlight.update()


    for process in processes:
        process.start()

    # for process in processes:
    #     process.join()
    end = time.time()
    
    print(end-start)

    start2 = time.time()
    doc.save(outputFileName, garbage=4, deflate=True, clean=True)

    doc.close()
    end2 = time.time()
    print(end2-start2)

    start3 = time.time()
    with open(outputFileName, 'rb') as pdf_file:
        pdf_data = pdf_file.read()

    end3 = time.time()
    print(end3-start3)

    start4 = time.time()
    os.remove(outputFileName)
    os.remove(articleFileName)
    end4 = time.time()
    print(end4-start4)

    return Response(pdf_data, mimetype='application/pdf')

if __name__ == "__main__":
    app.run(debug=True)

# set FLASK_APP=app.py
# set FLASK_ENV=development
# python -m flask run
# python -m http.server