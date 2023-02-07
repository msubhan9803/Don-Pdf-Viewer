import os
import fitz
import multiprocessing as mp

def highlight_text(doc, text_list, color, lock):
    print('=====================================')
    print('highlight_text in progress ...')
    for page in doc:
        for txt in text_list:
            inst = page.search_for(txt, quads=True)
            # ### HIGHLIGHT
            highlight = page.add_highlight_annot(inst)
            highlight.set_colors(stroke=[round(color['r']/255, 1), round(color['g']/255, 1), round(color['b']/255, 1)])
            highlight.update()

def highlight_pdf(pdf_file, summaryList):
    lock = mp.Lock()
    processes = []
    # Loop through each category
    for category in categories:
        # Get the color and list of text for the current category
        color = category['color']
        text_list = category['text_list']
        # Start a new process to highlight the text in the current category
        process = mp.Process(target=highlight_text, args=(doc, text_list, color, lock))
        processes.append(process)

    for key in summaryList.keys():
        process = mp.Process(target=highlight_text, args=(summaryList, key))
        processes.append(process)

    for process in processes:
        process.start()
    # Wait for all processes to finish
    for process in processes:
        process.join()



if __name__ == '__main__':
    # List of categories, where each category is a dictionary with a color and a list of text
    summaryList = {
        "context": {
            "text": {
                "0": "Since 2008",
                "1": "This conceptual"
            },
            "color": {
                "r": 133,
                "g": 193,
                "b": 233
            }
        },
        "key_insights": {
            "text": {
                "0": "At the same time",
                "1": "Awards have always"
            },
            "color": {
                "r": 130,
                "g": 224,
                "b": 170
            }
        },
        "key_findings": {
            "text": {
                "0": "simply put",
                "1": "relations, although"
            },
            "color": {
                "r": 240,
                "g": 178,
                "b": 122
            }
        },
        "definitions": {
            "text": {
                "0": "simply put",
                "1": "relations, although"
            },
            "color": {
                "r": 187,
                "g": 143,
                "b": 206
            }
        },
        "unknown": {
            "text": {
                "0": " for example, saw individualism",
                "1": "offered the notion"
            },
            "color": {
                "r": 241,
                "g": 148,
                "b": 138
            }
        }
    }

    # PDF file to highlight
    pdf_file = './article_1.pdf'
    textObjList = highlight_pdf(summaryList)
    
    # Open the PDF file and start a PyMuPDF session
    # doc = fitz.open(pdf_file)

    # doc.save(outputFileName, garbage=4, deflate=True, clean=True)