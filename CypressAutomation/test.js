const prompt = require('prompt');
const {Client} = require('pg')
const fs = require('fs');
const readline = require("readline");

const client = new Client({
    host: "localhost",
    port: 5432,
    user:"Riyad", 
    password:"123",
    database:"airQuality"
})

var data = []

main()

function main(){
    
    jsonReader('./cypress/fixtures/loginDetails.json', (err, response) => {
        //if the login detials don't already exist then create a new one
        if (err) {
            console.log('Error login details reading file:')
            console.log('Attempting to write new login details file \n')
            getLoginDetails();
            return
        }
        //else get the date and sensor info 
        else{
            getDatesandSensors(response.email,response.password);
        }
    })

    //getLoginDetails();
    //getDatesandSensors();
}

//test data
//180129650@aston.ac.uk
//Riyad888
function getLoginDetails() {
    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout,
      });
      
      rl.question("What is your email/Username? ", function (answer1) {
          rl.question("What is your Password? ", function (answer2) {
              console.log(`Email/Username: ${answer1}`);
              console.log(`Password: ${answer2}`);
              writeLoginDetails(answer1,answer2)
              console.log("Closing the interface");
              rl.close();
            });
      });           
}

function writeLoginDetails(user,pass) { 
    const loginDetails = {
        email: user,
        password: pass
    }

    fs.writeFile('./cypress/fixtures/loginDetails.json', JSON.stringify(loginDetails), (err) => {
        if (err) console.log('Error writing file:', err)
        else {
            console.log('Edit successful, restart the program')
        }
    })
}

//test data
//01/08/2021
//25/08/2021
//02:00:00:00:3f:15,02:00:00:00:49:fd,02:00:00:00:4b:94,02:00:00:00:43:8b,02:00:00:00:48:13
function getDatesandSensors(username,password){

    var sensors = []
    var dateStart,dateEnd
    
    // Start the prompt
    prompt.start()
    
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
        console.log('dateStart: ' + dateStart);
        console.log('dateend: ' + dateEnd);
        console.log('serialnums: ' + sensors);
    
        data.push(dateStart, dateEnd, sensors,username,password)
        data[2] = prepareQueryString(data[2])
        
        //data[2] = getIds(data[2])
        getPlumeIdsFromPostgres(data[2],extractPlumeIds)
        //writeJson(data)
    });
}


//prepares the serial numbers for SQL query
function prepareQueryString(array) {
    sensors = []
    for (let i = 0; i < array.length; i++) {
        str = "\'" + array[i] + "\'";
        sensors.push(str)
        }
    sensors = "\(" + sensors + "\)"
    return sensors
    }

//searches for the plume sensor ids 
function getPlumeIdsFromPostgres(array,myCallback){

    client.connect()
    .then(() => console.log("Connection Successful"))
    .then(() => client.query(`SELECT plume_id FROM sensor_network.sensors WHERE sensor_serial_number IN ${array}`))
    .then(results => { myCallback(results.rows);}) //return results.rows // console.log(typeof(results.rows))
    .catch(e => console.log(e))
    .finally(() => client.end())
}

//extract the plume id from the result
function extractPlumeIds(prop){
    ids = []
    for (let i = 0; i < prop.length; i++) {
        id = "sensor_" +  prop[i]['plume_id'];
        ids.push(id)
    }
    data[2] = ids
    writeJson(data)
}

//write a new json file for the browser automation
function writeJson(reqData) {

    jsonReader('./cypress/fixtures/Template.json', (err, response) => {
        if (err) {
            console.log('Error reading file:',err)
            return
        }
    
    // updating the fields
        response.dateStart = reqData[0]
        response.dateEnd = reqData[1]
        response.sensors = reqData[2]
        response.email = reqData[3]
        response.password = reqData[4]

    fs.writeFile('./cypress/fixtures/Plume.json', JSON.stringify(response), (err) => {
            if (err) console.log('Error writing file:', err)
            else console.log('Edit successful.')
        })
    })

    console.log(reqData)
    }

//reads path to the file and a callback to receive the parsed object and any errors.
function jsonReader(filePath, cb) {
    fs.readFile(filePath, (err, fileData) => {
        if (err) {
            return cb && cb(err)
        }
        try {
            const object = JSON.parse(fileData)
            return cb && cb(null, object)
            } 
        catch(err) {
            return cb && cb(err)
            }
        })
    }
