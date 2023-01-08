document.getElementById('file-upload-button').addEventListener('click', handleGetPdfSummarizedFile);
console.log('pdfjsLib: ', pdfjsLib)
document.getElementById('search-button').addEventListener('click', scrollToText);

async function handleGetPdfSummarizedFile(event) {
    event.preventDefault();
    console.log('event: ', event)
    const file = document.getElementById('my-file-input').files[0];
    const formData = new FormData();
    formData.append('file', file);
    formData.append("summaryList", "[\"Since 2008, the role of awards has been revitalized due to the Rudd Labor government’s policy of ‘award modernization’, which has both restored the effectiveness of awards as a safety net for wages and working hours and expanded their coverage (Murray & Owens, 2009).\",\"This conceptual lacuna is particularly problematic because of the complexity of the processes under examination.\",\"This is a long-standing practice in Europe, through works councils and board representation, and has recently become\",\"The following account divides the history of awards in Australia into three time periods, determined by the political complexion of the government and the types of laws they made.\"]");

    await fetch('http://127.0.0.1:5000/upload', {
        method: 'POST',
        body: formData
    })
        .then(result => result.json())
        .then(response => {
            console.log('response: ', response)
            const summarizedFileUrl = response.summarizedFileUrl;
            document.getElementById('my-custom-card-section').classList.remove('hidden');
            document.getElementById('my-custom-card-section').classList.add('block');

            const url = {
                url: "http://127.0.0.1:8000/" + summarizedFileUrl,
                originalUrl: summarizedFileUrl
            };
            PDFViewerApplication.open(url);
        })
        .catch(error => {
            // Handle error
        });
}

function scrollToText() {
    var pdfViewer = PDFViewerApplication.pdfViewer;
    console.log('pdfViewer: ', pdfViewer)

    // Get the current page of the PDF
    var page = pdfViewer.currentPageNumber;

    // Search for the text within the PDF
    const result = pdfViewer.findController.executeCommand('find', {
        caseSensitive: false,
        findPrevious: undefined,
        highlightAll: true,
        phraseSearch: true,
        query: 'The literature on individualism and collectivism'
    });

    console.log('result: ', result)
}