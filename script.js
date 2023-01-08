const form = document.getElementById('upload-form');

form.addEventListener('submit', event => {
    event.preventDefault();
    const file = document.getElementById('file').files[0];
    const formData = new FormData();
    formData.append('file', file);
    formData.append("summaryList", "[\"Since 2008, the role of awards has been revitalized due to the Rudd Labor government’s policy of ‘award modernization’, which has both restored the effectiveness of awards as a safety net for wages and working hours and expanded their coverage (Murray & Owens, 2009).\",\"This conceptual lacuna is particularly problematic because of the complexity of the processes under examination.\",\"This is a long-standing practice in Europe, through works councils and board representation, and has recently become\",\"The following account divides the history of awards in Australia into three time periods, determined by the political complexion of the government and the types of laws they made.\"]");
    fetch('http://127.0.0.1:5000/upload', {
        method: 'POST',
        body: formData
    })
    .then(result => result.json())
        .then(response => {
            console.log('response: ', response)
            summarizedFileUrl = response.summarizedFileUrl;
            document.getElementById('summary-doc').setAttribute('src', summarizedFileUrl);
            document.getElementById('summary-doc').classList.add('block')
            document.getElementById('summary-doc').classList.remove('hidden')

        })
        .catch(error => {
            // Handle error
        });
});