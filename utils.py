from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO

def extract_text_from_pdf(file_path):
    text_list = []
    resource_manager = PDFResourceManager()
    string_io = StringIO()
    converter = TextConverter(resource_manager, string_io, codec='utf-8', laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)

    count = 0
    with open(file_path, 'rb') as file:
        for page in PDFPage.get_pages(file, caching=True, check_extractable=True):
            page_interpreter.process_page(page)
            page_text = string_io.getvalue()
            text_list.append({count: page_text})
            string_io.truncate(0)
            string_io.seek(0)
            count += 1

    converter.close()
    string_io.close()

    return text_list


resp = extract_text_from_pdf('./standard test case.pdf')

print(resp)