document.getElementById('file-upload-button').addEventListener('click', handleGetPdfSummarizedFile);
console.log('pdfjsLib: ', pdfjsLib)
document.getElementById('search-button').addEventListener('click', scrollToText);

let summaryList = [];

async function handleGetPdfSummarizedFile(event) {
    event.preventDefault();
    console.log('event: ', event)
    const file = document.getElementById('my-file-input').files[0];

    // Here I will hit DOn's api
    const result = await handleGetPdfSummary(file);
    const keys = JSON.parse(result);
    const parsedSummaryList = {};
    
    let colorList = [
        {
            r: 240, g: 178, b:122
        },
        {
            r: 130, g: 224, b:170
        },
        {
            r: 133, g: 193, b:233
        },
        {
            r: 187, g: 143, b:206
        },
        {
            r: 241, g: 148, b:138
        }
    ];
    for (let index = 0; index < Object.keys(keys).length; index++) {
        const key = Object.keys(keys)[index];
        const optionsE = getRandomRgb(colorList);
        const removedE = colorList.splice(optionsE, 1);
        parsedSummaryList[key] = {
            text: JSON.parse(keys[key]),
            color: removedE[0]
        };
    }
    console.log('parsed summary list: ', parsedSummaryList)
    // summaryList = [
    //     "Since 2008, the role of awards has been revitalized due to the Rudd Labor government’s policy of ‘award modernization’, which has both restored the effectiveness of awards as a safety net for wages and working hours and expanded their coverage (Murray & Owens, 2009).",
    //     "This conceptual lacuna is particularly problematic because of the complexity of the processes under examination.",
    //     "This is a long-standing practice in Europe, through works councils and board representation, and has recently become",
    //     "The following account divides the history of awards in Australia into three time periods, determined by the political complexion of the government and the types of laws they made."
    // ];

    // Initializing cards
    initializeSummaryListCards(parsedSummaryList);

    const formData = new FormData();
    formData.append('file', file);
    formData.append("summaryList", JSON.stringify(parsedSummaryList));

    await fetch('http://127.0.0.1:5000/upload', {
        method: 'POST',
        body: formData
    })
    .then((response) => response.body)
    .then((stream) => new Response(stream))
    .then((response) => response.blob())
    .then((blob) => {
            debugger;
            // const summarizedFileUrl = response.summarizedFileUrl;
            document.getElementById('my-custom-card-section').classList.remove('hidden');
            document.getElementById('my-custom-card-section').classList.add('block');

            // const url = {
            //     url: "http://127.0.0.1:8000/" + summarizedFileUrl,
            //     // originalUrl: summarizedFileUrl
            //     originalUrl: URL.createObjectURL(response.body)
            // };
            // PDFViewerApplication.open(url);
            var url = URL.createObjectURL(blob);
            PDFViewerApplication.open(url, 0);
        })
        .catch(error => {
            // Handle error
        });
}

function handleGetPdfSummary(file) {
    var formdata = new FormData();
    formdata.append("file", file, file.name);

    return fetch('script.php', {
        method: 'POST',
        body: formdata
    })
        .then(response => response.text())
        .then(result => result)
        .catch(error => console.log('error', error));
}

function initializeSummaryListCards(list) {
    const cardContainer = document.getElementById('card-container');

    for (let i = 0; i < Object.values(list).length; i++) {
        const category = Object.values(list);
        const key = Object.keys(list)[i]

        const h1 = document.createElement('h1');
        h1.innerHTML = key;
        cardContainer.appendChild(h1);

        for (let index = 0; index < category.length; index++) {
            const textObj = category[index];
            const color = textObj.color;

            for (let index = 0; index < Object.values(textObj).length; index++) {
                const text = Object.values(textObj.text)[index];
                const card = document.createElement('div');

                card.innerHTML = text;
                card.onclick = function () {
                    scrollToText(text);
                }
                card.classList.add('card');
                const borderColor = `3px solid rgba(${color.r},${color.g},${color.b})`;
                // console.log('borderColor: ', borderColor);
                card.style.border = borderColor;
                cardContainer.appendChild(card);
            }
        }
    }
}

function scrollToText(text) {
    console.log('clicking...')
    document.getElementById('findInput').setAttribute('value', text)
    document.getElementById('findInput').dispatchEvent(new Event('input'));
}

function getRandomRgb(colorList) {
    return Math.floor(Math.random() * colorList.length);
}