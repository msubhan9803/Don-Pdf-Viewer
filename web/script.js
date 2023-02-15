document.getElementById('file-upload-button').addEventListener('click', handleGetPdfSummarizedFile);
document.getElementById('recreate-button').addEventListener('click', handleRecreateButton);
console.log('pdfjsLib: ', pdfjsLib)
document.getElementById('search-button').addEventListener('click', scrollToText);

let summaryList = [];

async function handleRecreateButton() {
    window.location.reload();
}

async function handleGetPdfSummarizedFile(event) {
    event.preventDefault();
    document.getElementById('file-search-loader').classList.add('block');
    document.getElementById('file-search-loader').classList.remove('hidden');
    document.getElementById('file-upload-dropzone').classList.add('hidden');
    document.getElementById('file-upload-dropzone').classList.remove('block');

    const file = document.getElementById('my-file-input').files[0];

    // Here I will hit DOn's api
    const result = await handleGetPdfSummary(file);
    debugger;
    const parsedResult = JSON.parse(result);
    console.log('result parsed: ', parsedResult);
    const parsedSummaryList = {};
    const keys = Object.keys(parsedResult[0]);

    let colorList = [
        {
            r: 240, g: 178, b: 122
        },
        {
            r: 130, g: 224, b: 170
        },
        {
            r: 133, g: 193, b: 233
        },
        {
            r: 187, g: 143, b: 206
        },
        {
            r: 241, g: 148, b: 138
        }
    ];
    const categorizedColor = {}
    for (let index = 0; index < keys.length; index++) {
        const key = keys[index];
        const optionsE = getRandomRgb(colorList);
        const removedE = colorList.splice(optionsE, 1);

        let categoryList = []
        for (let index = 0; index < parsedResult.length; index++) {
            const page = parsedResult[index];
            const currentTextObj = JSON.parse(page[key]);
            categoryList = [...categoryList, ...Object.values(currentTextObj)]
        }

        parsedSummaryList[key] = {
            text: categoryList,
            color: removedE[0]
        };
        categorizedColor[key] = removedE[0]
    }

    console.log(JSON.stringify(parsedSummaryList))

    // Initializing cards
    initializeSummaryListCards(parsedSummaryList);

    document.getElementById('file-search-loader').classList.add('hidden');
    document.getElementById('pdf-viewer-area').classList.add('block');
    document.getElementById('pdf-viewer-area').classList.remove('hidden');

    const payloadContent = {
        pageSummary: parsedResult,
        color: categorizedColor
    }
    console.log(JSON.stringify(payloadContent))

    const formData = new FormData();
    formData.append('file', file);
    formData.append("summaryContent", JSON.stringify(payloadContent));

    await fetch(`highlight.php`, {
        method: 'POST',
        body: formData
    })
        .then((response) => response.body)
        .then((stream) => new Response(stream))
        .then((response) => response.blob())
        .then((blob) => {
            console.log('blob: ', blob);
            document.getElementById('my-custom-card-section').classList.remove('hidden');
            document.getElementById('my-custom-card-section').classList.add('block');

            document.getElementById('recreate-button').classList.add('block');
            document.getElementById('recreate-button').classList.remove('hidden');

            document.getElementById('pdf-viewer-spinner').classList.remove('block');
            document.getElementById('pdf-viewer-spinner').classList.add('hidden');

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

    for (let i = 0; i < Object.keys(list).length; i++) {
        const key = Object.keys(list)[i]
        const object = list[key];
        const color = object.color;

        const h1 = document.createElement('h1');
        h1.innerHTML = capitalizeFirstLetter(key.replace('_', ' '));
        cardContainer.appendChild(h1);

        const textList = object.text;
        for (let index = 0; index < textList.length; index++) {
            const text = textList[index];
            const card = document.createElement('div');

            card.innerHTML = text;
            card.onclick = function () {
                scrollToText(text);
            }
            card.classList.add('card');
            const borderColor = `3px solid rgba(${color.r},${color.g},${color.b})`;
            card.style.border = borderColor;
            cardContainer.appendChild(card);
        }
    }
}

// Helpers
function scrollToText(text) {
    console.log('clicking...')
    document.getElementById('findInput').setAttribute('value', text)
    document.getElementById('findInput').dispatchEvent(new Event('input'));
}

function getRandomRgb(colorList) {
    return Math.floor(Math.random() * colorList.length);
}

function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}