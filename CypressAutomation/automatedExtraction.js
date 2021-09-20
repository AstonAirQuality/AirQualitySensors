const moment = require('moment')
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

main()

function main(){
    
    jsonReader('./cypress/fixtures/loginDetails.json', (err, response) => {
        //if the login detials don't already exist then create a new one
        if (err) {
            console.log('⚠️: No login details file found:')
            console.log('Attempting to write new login details file \n')
            getLoginDetails();
            return
        }

        //else get the date and sensor info for plume and zephyrs
        else{   
            userDetails = []
            userDetails.push(response.PlumeUsername,response.PlumePassword,response.ZephyrUsername,response.ZephyrPassword)
            getDatesandSensors(userDetails);
        }
    })
}

//prompts the user to enter thier login details
function getLoginDetails() {
    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout,
      });
    
      //plume
      rl.question("What is your PLUME email/Username? ", function (answer1) {
          rl.question("What is your PLUME Password? ", function (answer2) {
              console.log(`Email/Username: ${answer1}`);
              console.log(`Password: ${answer2}`);
               //zephyr
                rl.question("What is your ZEPHYR email/Username? ", function (answer3) {
                    rl.question("What is your ZEPHYR Password? ", function (answer4) {
                        console.log(`Email/Username: ${answer3}`);
                        console.log(`Password: ${answer4}`);

                        userDetails = []
                        userDetails.push(answer1,answer2,answer3,answer4)
                        writeLoginDetails(userDetails)

                        console.log("Closing the interface");
                        rl.close();
                    });
                });    

            });
      });           
}

function writeLoginDetails(userDetails) { 
    const loginDetails = {
        PlumeUsername: userDetails[0],
        PlumePassword: userDetails[1],
        ZephyrUsername: userDetails[2],
        ZephyrPassword: userDetails[3]
    }

    fs.writeFile('./cypress/fixtures/loginDetails.json', JSON.stringify(loginDetails), (err) => {
        if (err) console.log('Error writing file:', err)
        else {
            console.log('Edit successful, restart the program')
        }
    })
}

//look for active sensors 
function getDatesandSensors(userDetails){
    client.connect()
    .then(() => console.log("✅: Connection Successful"))
    
    //plume sensors
    .then(() => client.query(`SELECT lookup_id, last_update FROM sensor_network.sensors WHERE active = TRUE AND type_id = 1`))
    .then(results => {extractSensorIds(userDetails[0],userDetails[1],results.rows,1)}) 
   
    //zephyr sensors
    .then(() => client.query(`SELECT lookup_id, last_update FROM sensor_network.sensors WHERE active = TRUE AND type_id = 2`))
    .then(results => {extractSensorIds(userDetails[2],userDetails[3],results.rows,2)}) 
    
    .catch(e => console.log(e))
    .finally(() => client.end())

}


//extract the lookup id from the result
function extractSensorIds(username,password,result,type_id){
    ids = []
    startDate = ""
    endDate = moment() //set end date to today

    for (let i = 0; i < result.length; i++) {
        
        //flow sensors
        if(type_id === 1){
        id = "sensor_" + result[i]['lookup_id'];
        }
        //zephyrs
        else if (type_id === 2){
        id = result[i]['lookup_id'];
        }

        ids.push(id)

       
        newDate =  moment(result[i]['last_update'])
        
        //for each date extract the earliest and latest dates
        if (startDate == ""){
           startDate= newDate
        }
        else {
            if (moment(newDate).isBefore(startDate) === true){
                startDate = newDate
            }
        }

    }
    
    //if start and end dates are the same, then we nortify that update is not needed
    if(moment(endDate).isSame(startDate) == true){
        console.warn('⚠️: All active sensors are already up to date!');
        return;
    }

    else{

        fileName = ""

        //flow sensors
        if(type_id === 1){
            startDate = moment(startDate).format('MM/DD/YYYY')
            endDate = moment(endDate).format('MM/DD/YYYY')
            fileName= 'Plume'
        }

        //zephyr sensors
        else if (type_id === 2){
            startDate = moment(startDate).format('YYYYMMDD')
            endDate = moment(endDate).format('YYYYMMDD')

            startDate = startDate + "0000"
            endDate = endDate + "0000"
            fileName= 'Zephyr'
        }
   
        var reqData = []
        reqData.push(startDate,endDate,ids)
        writeJson(username,password,reqData,fileName)
    }
}


//write a new json file for the browser automation
function writeJson(username,password,reqData,fileName) {

    jsonReader('./cypress/fixtures/Template.json', (err, response) => {
        if (err) {
            console.log('Error reading file:',err)
            return
        }
    
    // updating the fields
        response.dateStart = reqData[0]
        response.dateEnd = reqData[1]
        response.sensors = reqData[2]
        response.email = username
        response.password = password

    fs.writeFile(`./cypress/fixtures/${fileName}.json`, JSON.stringify(response), (err) => {
            if (err) console.log(`🛑: Error writing filefor ${fileName}:`, err)
            else console.log(`✅: Writing new request for ${fileName} was successful!`)
        })
    })

    //console.log(reqData)
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
