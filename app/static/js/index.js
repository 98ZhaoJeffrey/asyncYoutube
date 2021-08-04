const sendData = (event, form) =>{
    event.preventDefault()
    let data = new FormData(form)
    data.append(form.id,'')

    fetch(`${window.location.href}`, {
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
    .catch(error => console.log( error))

}

