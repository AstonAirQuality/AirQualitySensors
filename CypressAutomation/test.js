const prompt = require('prompt');
const {Client} = require('pg')

const client = new Client({
    host: "localhost",
    port: 5432,
    user:"Riyad", 
    password:"123",
    database:"airQuality"
})

//12/07/2021
//14/07/2021
//02:00:00:00:43:8b,02:00:00:00:48:45
//Y

var sensors = []
var dateStart,dateEnd
var data = []

// Start the prompt
prompt.start();

// Get properties from the user: username and email
prompt.get(['dateStart', 'dateEnd', 'serialnumbers'], function (err, result) {
    // Log the results.
    console.log('Command-line input received:');

    //adjusting the date format
    dateStart = result.dateStart.split(/\//);
    dateStart = [dateStart[1], dateStart[0], dateStart[2]].join('/');

    dateEnd = result.dateEnd.split(/\//);
    dateEnd = [dateEnd[1], dateEnd[0], dateEnd[2]].join('/');

    //splitting the results into an array
    sensors = result.serialnumbers.split(',');

    //displaying the results to user
    console.log('  dateStart: ' + dateStart);
    console.log('  dateend: ' + dateEnd);
    console.log('  serialnums: ' + sensors);

    data.push(dateStart, dateEnd, sensors)
    data[2] = prepareQueryString(data[2])
    
    //data[2] = getIds(data[2])
    getPlumeIdsFromPostgres(data[2],extractPlumeIds)
    //writeJson(data)
});

//
function prepareQueryString(array) {
    sensors = []
    for (let i = 0; i < array.length; i++) {
        str = "\'" + array[i] + "\'";
        sensors.push(str)
        }
    sensors = "\(" + sensors + "\)"
    return sensors
    }

function getPlumeIdsFromPostgres(array,myCallback){

    client.connect()
    .then(() => console.log("Connection Successful"))
    .then(() => client.query(`SELECT plume_id FROM sensor_network.sensors WHERE sensor_serial_number IN ${array}`))
    .then(results => { client.end(); myCallback(results.rows);}) //return results.rows // console.log(typeof(results.rows))
    // .catch(e => console.log(e))
    // .finally(() => client.end())
}

//extract the plume id from the result
function extractPlumeIds(prop){
    ids = []
    for (let i = 0; i < prop.length; i++) {
        id = prop[i]['plume_id'];
        ids.push(id)
    }
    data[2] = ids
    writeJson(data)
}

//write a new json file for the broswer automation
function writeJson(a) {
    // const fs = require('fs');
    // var name = '.\/cypress\/fixtures\/Plume.json';
    // var m = JSON.parse(fs.readFileSync(name).toString());
    // m.forEach(function(p){
    //     p.name= m.name;
    // });
    // fs.writeFileSync(name, JSON.stringify(m));
    console.log(a)
    }





// // var obj = {"dateStart":dateStart, "dateEnd":dateEnd, "sensors":'hello'};
// // console.log(obj);


// async function getIds(array){
//     sensors = []

//     await client.connect()
//         .then(() => console.log("Connection Successful"))
//     const results = await client.query(`SELECT plume_id FROM sensor_network.sensors WHERE sensor_serial_number IN ${array}`)
//     await client.end()

//     //get each plume lookup id
//     console.log(results.rows.length)
//     for (let i = 0; i < results.rows.length; i++) {
//         id = results.rows[0]['plume_id'];
//         sensors.push(id)
//         }
    
//     //console.log(sensors)
//     return sensors
// }