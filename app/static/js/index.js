const joinModal = () => {
    const modal = document.getElementById('Join')
    modal.hidden = !(modal.hidden)
}

const makeModal = () => {
    const modal = document.getElementById('Make')
    modal.hidden = !(modal.hidden)
}

const JoinForm = document.getElementById('JoinForm')
JoinForm.addEventListener('submit', (e) => {
    e.preventDefault()
    let data = new FormData(document.getElementById('JoinForm'))
    data.append('join','')
    fetch(`${window.origin}/`, {
        method: "POST",
        body: data
    })  
    .then(response => {
        return response.json()
    })
    .then(data => {
            console.log(data)
            window.location ='room'
        })
    .catch(error => console.log((JSON.parse(error)).error));
}) 

const MakeForm = document.getElementById('MakeForm')
MakeForm.addEventListener('submit', (e) => {
    e.preventDefault()
    let data = new FormData(document.getElementById('MakeForm'))
    data.append('make','')
    fetch(`${window.origin}/`, {
        method: "POST",
        body: data
    })  
    .then(response => {
            return response.json
            //window.location = '/room'
        })
    .then(data => {
        console.log(data)
        window.location ='room'
    });
}) 