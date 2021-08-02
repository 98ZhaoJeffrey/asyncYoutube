const alertDiv = document.getElementById("alerts")

const addAlert = (msg)=>{
    const alert = document.createElement('div')
    const alertType = msg['status'] === 'Success' ? 'green' : 'red'

    alert.className = `z-10 bg-${alertType}-100 w-2/3 border border-${alertType}-400 text-${alertType}-700 px-4 py-3 rounded relative items-center`
    alert.innerHTML = `<span class="closebtn" onclick="this.parentElement.remove();">&times;</span> <strong>${msg['status']}</strong> ${msg['message']}` 
    alertDiv.prepend(alert)
}

const sendData = (event, form) =>{
    event.preventDefault()
    let data = new FormData(form)
    data.append(form.id,'')

    fetch(`${window.origin}/`, {
        method: "POST",
        body: data
    })  
    .then(response => {
        return(response.json())
    })
    .then(data =>{
        console.log(data)
        addAlert(data)
        if(data['status'] === 'Success'){
            setTimeout(()=> window.location = '/room', 1500)
        }
        
    })
    .catch(error => console.log("error", error))

}

