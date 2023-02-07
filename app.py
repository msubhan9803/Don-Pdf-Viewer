import datetime
import random
import fitz
from flask import Flask, Response, request
import random
import string
import multiprocessing as mp

app = Flask(__name__)

def random_string_generator(str_size, allowed_chars):
    return ''.join(random.choice(allowed_chars) for x in range(str_size)) + '-' + str(int(datetime.datetime.now().timestamp()))

chars = string.ascii_letters + string.digits
size = 12


'''
HIGHLIGHT FUNCTION
'''
def highlight_text(page_range, categories, pdf_file):
    # Open the PDF file
    pdf = fitz.open(pdf_file)
    
    for i in page_range:
        page = pdf[i]
        for key in categories.keys():
            color = categories[key]['color']

            for text in categories[key]['text'].values():
                # Search for the text on the current page
                inst = page.search_for(text, quads=True)

                highlight = page.add_highlight_annot(inst)
                highlight.set_colors(stroke=[round(color['r']/255, 1), round(color['g']/255, 1), round(color['b']/255, 1)])
                highlight.update()


        # for category in categories:
        #     print('index: ', i)
        #     print('text_list: ', category['text_list'])
        #     # Get the current page
        #     page = pdf[i]
        #     print('page: ', page)
        #     text_list = category['text_list']
        #     color = category['color']
            
        #     for text in text_list:
        #         # Search for the text on the current page
        #         inst = page.search_for(text, quads=True)

        #         highlight = page.add_highlight_annot(inst)
        #         highlight.set_colors(stroke=[round(color['r']/255, 1), round(color['g']/255, 1), round(color['b']/255, 1)])
        #         highlight.update()
    
    # Save the PDF
    pdf.save(pdf_file, incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)
    pdf.close()


'''
MAIN FUNCTION
'''
def main(pdf_file, categories):
    # Create a list of processes
    processes = []
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
        print('page_range', page_range)
        
        # Create the process
        process = mp.Process(target=highlight_text, args=(page_range, categories, pdf_file))
        
        # Add the process to the list of processes
        processes.append(process)
        
        # Update the chunk start and end for the next process
        chunk_start = chunk_end
        chunk_end += chunk_size
    
    # Start all processes
    for process in processes:
        process.start()
        
    # Wait for all processes to finish
    for process in processes:
        process.join()


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

    main(articleFileName, summaryList)

    # doc.save(outputFileName, garbage=4, deflate=True, clean=True)

    # doc.close()

    # with open(outputFileName, 'rb') as pdf_file:
    #     pdf_data = pdf_file.read()

    # os.remove(outputFileName)
    # os.remove(articleFileName)

    return Response(pdf_data, mimetype='application/pdf')

if __name__ == "__main__":
    app.run(debug=True)

# set FLASK_APP=app.py
# set FLASK_ENV=development
# python -m flask run
# python -m http.server