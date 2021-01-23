const request = require('postman-request')

const forecast = (lat , lon, callback) => {
    const url = 'http://api.weatherstack.com/current?access_key=e177b1a9078394604813ebd4fb127b03&query='+lat+','+lon+'&units=m'
    request({ url, json:true}, (error, { body }) => {
        if(error){
            callback('Unabke to connect to weather services', undefined)
        }else if(body.error){
            callback('Unable to find location', undefined)
        } else {
            callback(undefined, {
                description: body.current.weather_descriptions[0],
                temperature: body.current.temperature,
                rain: body.current.precip,
                time: body.current.observation_time,
                humidity: body.current.humidity
            })
        }
    })
}

module.exports = forecast