from flask import Flask, flash, request, redirect, url_for ,jsonify , make_response , Response
from werkzeug.utils import secure_filename
import json
from utils import parse_pdf
from utils2 import extract_text_from_pdf
from simpletransformers.classification import ClassificationModel, ClassificationArgs
import nltk
import os
import jwt
import datetime

import random
import fitz
import string
import multiprocessing as mp


from functools import wraps

os.environ['NLTK_DATA'] = 'nltk_data'
nltk.download('punkt')

UPLOAD_FOLDER = 'pdf_buffer'
ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


import pandas as pd
# Load classification model
saved_model = ClassificationModel(
    "bert", "saved_model_bert_tiny", use_cuda=False, num_labels=5
)


def classify_senetences(parsed_text):
    dic = {}
    parsed_text = parsed_text.replace("\n", " ")
    parsed_text = parsed_text.replace("\r", " ")
    parsed_text = parsed_text.replace("\t", " ")
    parsed_text = parsed_text.split("REFERENCES")[0]
    #parsed_text = parsed_text.replace("(cid:0)", "")
    sentences = nltk.sent_tokenize(parsed_text)
    #result = []
    #for sentence in sentences:
    #    result.append(saved_model.predict(sentence))
    sentences = [ x for x in sentences if "(cid:" not in x ]
    sentences = [item for item in sentences if not all(len(elem) == 1 for elem in item.split()[:20])]

    single_space_sentences = []

    predictions, _ = saved_model.predict(sentences)

    result_df = pd.DataFrame({"sentence": sentences, "label": predictions})
    result_df.drop_duplicates(keep="first", inplace=True)
    result_df.reset_index(drop=True, inplace=True)

    mask = (result_df['sentence'].str.len() > 100)
    result_df = result_df.loc[mask]
    result_df.reset_index(drop=True, inplace=True)

    # print(result_df.set_index('label').to_dict())

    out_df = result_df[result_df["label"] == "Context"]
    out_df.reset_index(drop=True, inplace=True)
    dic["context"] = out_df["sentence"].to_json()

    out_df = result_df[result_df["label"] == "Key insights"]
    out_df.reset_index(drop=True, inplace=True)
    dic["key_insights"] = out_df["sentence"].to_json()

    out_df = result_df[result_df["label"] == "Key findings"]
    out_df.reset_index(drop=True, inplace=True)
    dic["key_findings"] = out_df["sentence"].to_json()

    out_df = result_df[result_df["label"] == "Definitions"]
    out_df.reset_index(drop=True, inplace=True)
    dic["definitions"] = out_df["sentence"].to_json()

    out_df = result_df[result_df["label"] == "Unknown"]
    out_df.reset_index(drop=True, inplace=True)
    dic["unknown"] = out_df["sentence"].to_json()

    return  dic

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def token_required(f):
    @wraps(f)
    def  decrated(*args, **kwargs):

        token = None
        print(request.headers)
        print(request.headers["x_access_token"])
        if 'x_access_token' in request.headers:
            token = request.headers['x_access_token']

        if not token:
            return jsonify({"massage" : "Token is missing!"}) , 403

        if token != "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9" and  token != "xyJ3eXCiOiJKV2QiLCJhbGciOiXIUzI1NiX8":

            return jsonify({"massage" : "Token is missing!"}) , 403

        return f(*args , **kwargs)

    return decrated

@app.route('/poc', methods=['GET', 'POST'])
def poc():

    return """<form action="/data_processing method="post" enctype="multipart/form-data">
                  <input type="file" id="myFile" name="file">
                  <input type="submit">
            </form>"""

@app.route('/data_processing', methods=['GET', 'POST'])
@token_required
def data_processing():
    # print(request.form)

    if request.method == 'POST':
        print('here')
        # check if the post request has the file part
        if 'file' not in request.files:
            return jsonify({"massage" : "Key not found!"}) , 403

        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            return jsonify({"massage" : "No selected file!"}) , 403

        if file and allowed_file(file.filename):
            print('file exist')
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            try:
                # parsed_text = parse_pdf(app.config['UPLOAD_FOLDER'] + "/" + filename)
                parsed_text_list = extract_text_from_pdf(app.config['UPLOAD_FOLDER'] + "/" + filename)

                # json.dumps(classify_senetences(parsed_text), indent=4)
                # print(parsed_text_list)

                classified_page_text = []
                for pageText in parsed_text_list:
                    # print('pageText: ', pageText)
                    for key in pageText:
                        # print('key', key)
                        classified_text = classify_senetences(pageText[key])
                        # print('classified_text: ', classified_text)
                        classified_page_text.append(classified_text)

                # print('classified_page_text: ', classified_page_text)

                response = app.response_class(
                    # response=json.dumps(classify_senetences(parsed_text), indent=4),
                    response=json.dumps(classified_page_text, indent=4),
                    status=200,
                    mimetype='application/json'
                )
                # added by PRASAD
                response.headers.add('Access-Control-Allow-Origin', '*')

                return response
            except Exception as e:
                response = app.response_class(
                    response=json.dumps({"error" : e}, indent=4),
                    status=400,
                    mimetype='application/json'
                )

                return response

    return jsonify({"massage" : "wrong mothod send value in post method!"}) , 403




## Subahns CODE - FOR Hilight PDF


def random_string_generator(str_size, allowed_chars):
    return ''.join(random.choice(allowed_chars) for x in range(str_size)) + '-' + str(int(datetime.datetime.now().timestamp()))

chars = string.ascii_letters + string.digits
size = 12

def addSpaceHere():
    print('         ')

'''
HIGHLIGHT FUNCTION
'''
def highlight_text(page_range, pageSummary, color, pdf_file, process_index, new_file_name):
    print('color: ', color)
    addSpaceHere()
    print('started process no.: ', process_index)
    print('highlighting process started for page_range', page_range)
    # Open the PDF file
    pdf = fitz.open(pdf_file)
    new_pdf = fitz.open()
    start_index_val = page_range[0]
    last_index_val = page_range[len(page_range) - 1]

    for i in page_range:
        print('page no.: ', i, ' process no.: ', process_index)
        page = pdf[i]
        print('page: ', page)
        pageCategories = pageSummary[i]

        for key in pageCategories.keys():
            currentColor = color[key]
            currentCategory = json.loads(pageCategories[key])
            if len(currentCategory.keys()) > 0:

                for text in currentCategory.values():
                    # Search for the text on the current page
                    inst = page.search_for(text, quads=True)

                    highlight = page.add_highlight_annot(inst)
                    highlight.set_colors(stroke=[round(currentColor['r']/255, 1), round(currentColor['g']/255, 1), round(currentColor['b']/255, 1)])
                    highlight.update()

    new_pdf.insert_pdf(pdf, from_page = start_index_val, to_page = last_index_val)
    print('page highlighted!')

    # Save the PDF
    new_pdf.save(new_file_name)
    print('saved!')
    new_pdf.close()
    print('closed!')
    addSpaceHere()


'''
MERGING PDF BACK TO ONE
'''
def merge_pdfs(pdf_files, output_file):
    pdf_merger = fitz.open()
    for pdf_file in pdf_files:
        pdf = fitz.open(pdf_file)
        pdf_merger.insert_pdf(pdf)
        pdf.close()
        os.remove(pdf_file)
    pdf_merger.save(output_file)
    addSpaceHere()
    print('===>  merged file saved!')


'''
CHUNK FUNCTION
'''
def chunk_array(page_length, chunk_size, cpu_count):
    chunks = []
    chunk = []

    for page_no in range(page_length):
        if len(chunks) < cpu_count:
            if len(chunk) < chunk_size:
                chunk.append(page_no)

            if len(chunk) == chunk_size:
                chunks.append(chunk)
                chunk = []
        else:
            chunks[len(chunks) - 1].append(page_no)

    return chunks


'''
MAIN FUNCTION
'''
def main(pdf_file, pageSummary, color, output_file_name):
    # Create a list of processes
    processes = []
    new_pdf_list = []
    doc = fitz.open(pdf_file)
    page_length = doc.page_count
    print('page length: ', page_length)
    doc.close()

    # Divide the pages of the PDF into chunks for each process
    cpu_count = mp.cpu_count()
    if page_length > cpu_count:
        chunk_size = page_length // cpu_count
        remainder_after_equal = page_length - (chunk_size * cpu_count)
    else:
        chunk_size = 1
        remainder_after_equal = 0
        cpu_count = page_length
    
    chunks = chunk_array(page_length, chunk_size, cpu_count)
    
    print('cpu_count: ', cpu_count)
    print('chunk_size: ', chunk_size)
    print('remainder_after_equal: ', remainder_after_equal)
    print('======> chunks: ', chunks)

    # Create a process for each chunk of pages
    for i in range(cpu_count):
        chunk = chunks[i]
        # Calculate the page range for the current process
        page_range = chunk
        print('====> current dynamic page_range: ', page_range)

        file_name = "conversions/" + str(i) + "-"  + random_string_generator(size, chars) + "-.pdf"
        # Create the process

        process = mp.Process(target=highlight_text, args=(page_range, pageSummary, color, pdf_file, i, file_name))
        process.daemon = True

        new_pdf_list.append(file_name)

        # Add the process to the list of processes
        processes.append(process)


    addSpaceHere()
    # Start all processes
    for process in processes:
        addSpaceHere()
        print('process started!')
        process.start()

    addSpaceHere()

    # Wait for all processes to finish
    for process in processes:
        print('waiting for process to finish!')
        process.join()

    addSpaceHere()
    print('all processed done!')

    print('new_pdf_list', new_pdf_list)
    merge_pdfs(new_pdf_list, output_file_name)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    print('preparing pdf annonations ...')
    file = request.files['file']
    summaryContent = eval(request.form['summaryContent'])
    pageSummary = summaryContent['pageSummary']
    color = summaryContent['color']

    randomString = random_string_generator(size, chars)
    newFileName = "conversions/" + randomString
    articleFileName = newFileName + "-article.pdf"
    outputFileName = newFileName + "-output.pdf"
    output_file_name = "conversions/" + random_string_generator(size, chars) + "-.pdf"

    file.save(articleFileName)

    # Stating
    main(articleFileName, pageSummary, color, output_file_name)

    print('output file: ', output_file_name)
    with open(output_file_name, 'rb') as pdf_file:
        print('reading article file to return in response ...')
        pdf_data = pdf_file.read()

    os.remove(articleFileName)
    os.remove(output_file_name)

    print('returning the file in response!')
    return Response(pdf_data, mimetype='application/pdf')


if __name__ == '__main__':
    app.run( debug=True , host="0.0.0.0")