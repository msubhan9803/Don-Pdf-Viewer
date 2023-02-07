import fitz
import multiprocessing as mp

def highlight_text(page_range, categories, pdf_file):
    print (' ')
    # Open the PDF file
    pdf = fitz.open(pdf_file)
    
    for i in page_range:
        for category in categories:
            print('index: ', i)
            print('text_list: ', category['text_list'])
            # Get the current page
            page = pdf[i]
            print('page: ', page)
            text_list = category['text_list']
            color = category['color']
            
            for text in text_list:
                # Search for the text on the current page
                inst = page.search_for(text, quads=True)

                highlight = page.add_highlight_annot(inst)
                highlight.set_colors(stroke=[round(color['r']/255, 1), round(color['g']/255, 1), round(color['b']/255, 1)])
                highlight.update()
    
    # Save the PDF
    pdf.save(pdf_file, incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)
    pdf.close()
    
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

if __name__ == "__main__":
    # Specify the PDF file to be highlighted
    pdf_file = "article_1.pdf"
    
    # Define the categories to be highlighted with the unique color
    categories = [
        {"category": "Category 1", "text_list": ["Since 2008", "This conceptual"], "color": { "r": 133, "g": 193, "b": 233 }},
        {"category": "Category 2", "text_list": ["Individualism", "Collectivism"], "color": { "r": 133, "g": 193, "b": 233 }},
        {"category": "Category 3", "text_list": ["Awards", "Australia"], "color": { "r": 133, "g": 193, "b": 233 }},
    ]
    
    # Call the main function
    main(pdf_file, categories)
