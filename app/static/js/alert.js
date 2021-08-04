const addAlert = (msg)=>{
    const alertDiv = document.getElementById("alerts")
    const alert = document.createElement('div')
    const alertType = msg['status'] === 'Success' ? 'green' : 'red'

    alert.className = `z-10 bg-${alertType}-100 w-2/3 border border-${alertType}-400 text-${alertType}-700 px-4 py-3 rounded relative items-center`
    alert.innerHTML = `<span class="closebtn" onclick="this.parentElement.remove();">&times;</span> <strong>${msg['status']}</strong> ${msg['message']}` 
    alertDiv.prepend(alert)
}