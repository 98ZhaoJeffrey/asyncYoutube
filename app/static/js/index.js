const ErrorClass = "z-10 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative"
const SuccessClass = "z-10 bg-green-100 border border-red-400 text-green-700 px-4 py-3 rounded relative"


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
        if(response.status !== 200){
            console.log(response.error)
        }else{
            window.location ='room'
        }           
    })
    .catch(error => console.error(error));
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
            if(response.status !== 201){
                console.log(data.json()) 
            }
            else{
                window.location ='room'
            }
        })
    .catch(error => console.error(error));
}) 

const closeAlert = (event) => {
    const alert = event.target.parentElement.parentElement
    console.log(alert)
    if(alert){
        alert.remove()
    }
}