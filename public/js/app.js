const weatherForm = document.querySelector('form')
const search = document.querySelector('input')
const messageOne = document.querySelector('#message-1')
const messageTwo = document.querySelector('#message-2')
const messageThree= document.querySelector('#message-3')

weatherForm.addEventListener('submit', (e) => {
    e.preventDefault()

    const location = search.value

    messageOne.textContent = 'Loading...'
    messageTwo.textContent = ''

    fetch('/weather?address=' + location).then((response) => {
    response.json().then((data) => {
        if (data.error){
            messageOne.textContent = data.error
        }else{
            messageOne.textContent = data.location
            messageTwo.textContent = data.forecast.description +'. It is currently '+ data.forecast.temperature +
            ' degress out.'+' There is a '+ data.forecast.rain+'% chance of rain.'
            messageThree.textContent = "Observation time is "+data.forecast.time+
            " and the humidity is "+data.forecast.humidity+"."
        }
    })
})

})
