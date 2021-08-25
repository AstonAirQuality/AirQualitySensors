const {Client} = require('pg')
const client = new Client({
    host: "localhost",
    port: 5432,
    user:"Riyad", 
    password:"123",
    database:"airQuality"
})

serialNumbers = ['\'02:00:00:00:43:8b\'','\'02:00:00:00:48:45\'']
parameters = "\(" + serialNumbers + "\)"

console.log(parameters)

let res = []

client.connect()
.then(() => console.log("Connection Successful"))
.then(() => client.query(`SELECT plume_id FROM sensor_network.sensors WHERE sensor_serial_number IN ${parameters}`))
// .then(results => console.table(results.rows))
.then(results => {this.res = results.rows})
.catch(e => console.log(e))
.finally(() => client.end())


console.log(res)


// const results = client.query((`SELECT plume_id FROM sensor_network.sensors WHERE sensor_serial_number IN ${parameters}`), (err,res) => {
//     if (err){   
//         console.log(err.message)
//     }
//     else {
//         sensors = []
//         for (let i = 0; i < res.rows.length; i++) {
//             id = res.rows[0]['plume_id'];
//             sensors.push(id)
//             }
//         console.log(sensors)
//     }
//     client.end
//     })


