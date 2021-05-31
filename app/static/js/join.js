const form = document.getElementById('join')
form.addEventListener('submit', (e) => {
    e.preventDefault()
    let data = new FormData(document.getElementById('join'))
    fetch(`${window.location.href}/`, {
        method: "POST",
        body: data
    })  
    .then(response => {
        return response.json()
    })
    .then(data => {
            console.log(data)
            window.location = `${window.origin}/room`
        })
    .catch(error => console.log((JSON.parse(error)).error));
}) 