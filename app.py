import datetime
import random
import fitz
from flask import Flask, Response, request
import random
import string
import os
import multiprocessing as mp
import json

app = Flask(__name__)

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
    print('file: ', file)
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

if __name__ == "__main__":
    app.run(debug=False)

# set FLASK_APP=app.py
# set FLASK_ENV=development
# python -m flask run
# python -m http.server