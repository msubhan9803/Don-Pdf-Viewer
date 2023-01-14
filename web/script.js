document.getElementById('file-upload-button').addEventListener('click', handleGetPdfSummarizedFile);
console.log('pdfjsLib: ', pdfjsLib)
document.getElementById('search-button').addEventListener('click', scrollToText);

let summaryList = [];

async function handleGetPdfSummarizedFile(event) {
    event.preventDefault();
    console.log('event: ', event)
    const file = document.getElementById('my-file-input').files[0];

    // Here I will hit DOn's api
    const result = handleGetPdfSummary(file);
    summaryList = [
        "Since 2008, the role of awards has been revitalized due to the Rudd Labor government’s policy of ‘award modernization’, which has both restored the effectiveness of awards as a safety net for wages and working hours and expanded their coverage (Murray & Owens, 2009).",
        "This conceptual lacuna is particularly problematic because of the complexity of the processes under examination.",
        "This is a long-standing practice in Europe, through works councils and board representation, and has recently become",
        "The following account divides the history of awards in Australia into three time periods, determined by the political complexion of the government and the types of laws they made."
    ];

    // Initializing cards
    initializeSummaryListCards(summaryList);

    const formData = new FormData();
    formData.append('file', file);
    formData.append("summaryList", JSON.stringify(summaryList));

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

function handleGetPdfSummary(file) {
    var myHeaders = new Headers();
    myHeaders.append("Content-Type", "multipart/form-data");
    myHeaders.append("Access-Control-Allow-Origin", "*");
    myHeaders.append("x_access_token", "xyJ3eXCiOiJKV2QiLCJhbGciOiXIUzI1NiX8");

    var formdata = new FormData();
    formdata.append("file", file, file.name);

    var requestOptions = {
        method: 'POST',
        headers: myHeaders,
        body: formdata,
        redirect: 'follow'
    };

    fetch("http://3.1.240.237/data_processing", requestOptions)
        .then(response => response.text())
        .then(result => console.log(result))
        .catch(error => console.log('error', error));
}

function initializeSummaryListCards(list) {
    const cardContainer = document.getElementById('card-container');

    for (let i = 0; i < list.length; i++) {
        const card = document.createElement('div');
        card.innerHTML = list[i];
        card.onclick = function () {
            scrollToText(list[i]);
        }
        card.classList.add('card');
        cardContainer.appendChild(card);
    }
}

function scrollToText(text) {
    console.log('clicking...')
    document.getElementById('findInput').setAttribute('value', text)
    document.getElementById('findInput').dispatchEvent(new Event('input'));
}