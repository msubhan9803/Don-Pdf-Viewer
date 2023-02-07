import datetime
import random
import fitz
from flask import Flask, Response, request
import random
import string
import os
import multiprocessing as mp

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
def highlight_text(page_range, categories, pdf_file, process_index, file_name):
    addSpaceHere()
    print('started process no.: ', process_index)
    print('highlighting process started for page_range', page_range)
    # Open the PDF file
    pdf = fitz.open(pdf_file)
    
    for i in page_range:
        print('page no.: ', i)
        page = pdf[i]
        print('page: ', page)
        for key in categories.keys():
            color = categories[key]['color']

            for text in categories[key]['text'].values():
                # Search for the text on the current page
                inst = page.search_for(text, quads=True)

                highlight = page.add_highlight_annot(inst)
                highlight.set_colors(stroke=[round(color['r']/255, 1), round(color['g']/255, 1), round(color['b']/255, 1)])
                highlight.update()
        print('page highlighted!')

    # Save the PDF
    # pdf.save(pdf_file, incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)
    pdf.save(file_name)
    print('saved!')
    pdf.close()
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
    pdf_merger.save(output_file)
    addSpaceHere()
    print('===>  merged file saved!')


'''
MAIN FUNCTION
'''
def main(pdf_file, categories, output_file_name):
    # Create a list of processes
    processes = []
    new_pdf_list = []
    doc = fitz.open(pdf_file)
    page_length = doc.page_count
    print('page length: ', page_length)
    doc.close()
    
    # Divide the pages of the PDF into chunks for each process
    cpu_count = mp.cpu_count()
    print('cpu_count: ', cpu_count)
    chunk_size = page_length // cpu_count
    print('chunk_size: ', chunk_size)
    chunk_start = 0
    chunk_end = chunk_size
    
    # Create a process for each chunk of pages
    for i in range(cpu_count):
        # Calculate the page range for the current process
        page_range = range(chunk_start, chunk_end)
        print('====> current dynamic page_range: ', page_range)
        
        file_name = "conversions/" + str(i) + "-"  + random_string_generator(size, chars) + "-.pdf"
        # Create the process
        
        process = mp.Process(target=highlight_text, args=(page_range, categories, pdf_file, i, file_name))

        new_pdf_list.append(file_name)
        
        # Add the process to the list of processes
        processes.append(process)
        
        # Update the chunk start and end for the next process
        chunk_start = chunk_end
        chunk_end += chunk_size

    
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
    summaryList = eval(request.form['summaryList'])

    randomString = random_string_generator(size, chars)
    newFileName = "conversions/" + randomString
    articleFileName = newFileName + "-article.pdf"
    outputFileName = newFileName + "-output.pdf"
    output_file_name = "conversions/" + random_string_generator(size, chars) + "-.pdf"

    file.save(articleFileName)

    main(articleFileName, summaryList, output_file_name)

    # doc.save(outputFileName, garbage=4, deflate=True, clean=True)
    # doc.close()

    print('output file: ', output_file_name)
    with open(output_file_name, 'rb') as pdf_file:
        print('reading article file to return in response ...')
        pdf_data = pdf_file.read()

    # os.remove(outputFileName)
    # os.remove(output_file_name)

    print('returning the file in response!')
    return Response(pdf_data, mimetype='application/pdf')

if __name__ == "__main__":
    app.run(debug=True)

# set FLASK_APP=app.py
# set FLASK_ENV=development
# python -m flask run
# python -m http.server