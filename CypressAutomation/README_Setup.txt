Step 1:
Open up Windows terminal/command prompt/Powershell 

Step 2:
Change directory to Cypress Automation (e.g cd cd '.\AirQualitySensors\CypressAutomation\)

Step 3.0:
run the command "npm install" 

	Step 3.1:
	if step 3.0 did not work, run the command "npm install cypress --save-dev"


Step 4: Setting up JSON file.

Create a copy  of the JSON file called "Template.JSON" inside the fixtures folder and rename this copy "Plume.JSON"


Step 4.1: Inserting the required data 

Within your new "Plume.JSON" file you MUST replace the infomation with your own login credentials.

An example of this is shown below

{
    "email": "example@example.com",
    "password": "example",
    "dateStart": "07/12/2021",
    "dateEnd": "07/22/2021",
    "sensors":["sensor_18699", "sensor_18720", "sensor_18749"]
}


Step 5.0: Execute cypress through command
(Ensure your current directory is CypressAutomation, or you will create a new Cypress project) 

run the command " 
 .\node_modules\.bin\cypress run --spec "cypress\integration\examples\PlumeAutomation.js" 
 "

	Step 5.2: Open Cypress Test runner:
	
	if step 5.0 did not work,
	(Ensure your current directory is CypressAutomation, or you will create a new Cypress project) 

	run the command ".\node_modules\.bin\cypress open"
