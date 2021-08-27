/// <reference types="cypress" />

/// Loading JSON fixture file directly using the built-in JavaScript bundler @ts-ignore
const plume = require('../../fixtures/Plume')

//clears any local storage before the script is run 
window.localStorage.clear();


describe('MytestSuite', function()
{
      beforeEach(() => {
        cy.fixture('Plume.json').as('plume');
        //cy.clearLocalStorage(); doesn't work consistently!
        Cypress.LocalStorage.clear = () => {};
      });
      
    it('Verify title of the page', function()
    {
        //uses baseUrl in config file
        cy.visit("/");
        
        //testing eq (equaltiy)
        cy.title().should('eq', 'Flow Dashboard');
    })

    it('Logging in', function()
    {
         //testing username input
         cy.get('input[name="username"]')
         .type(plume.email).should('have.value', plume.email);

        //testing password input
        cy.get('input[name="password"]')
        .type(plume.password).should('have.value', plume.password);

        //submit login
        cy.get("form").submit();

        cy.intercept('GET', '**/user/organizations/').as('dashboard')
        cy.wait('@dashboard').its('response.statusCode').should('eq', 200)
        cy.url().should('eq', 'https://dashboard-flow.plumelabs.com/');
    })
   
    it('Navigating to organisation', function()
    {
       //navigating to the Aston organisation in dashboard
       cy.get('a[href*="/organizations/85/show"]').click();
       //exporting data
       cy.get('a[href*="/organizations/85/sensors/export"]').click();
    })
   
    it('Selecting the sensors', function()
    {
     //iterates through the list of sensors
     for (var i = 0; i < plume.sensors.length; i++) { 
         var lblStr = "label[for='" + plume.sensors[i] +  "']";
         cy.get(lblStr).click();
     }

    })

    it('Selecting and applying dates', function()
    {
        cy.get('.btn-dates').click()
        
        cy.get('.left > .daterangepicker_input > .input-mini')
        .clear()
        .type(plume.dateStart)
        .type('{enter}')

        cy.get('.right > .daterangepicker_input > .input-mini')
        .clear()
        .type(plume.dateEnd)
        .type('{enter}')

        //applying the dates
        cy.get('.applyBtn').click()
    })

    it('Submitting data: preparing for export', function(){
        //submitting data 
        cy.get('.form-group > .btn').click()
    })

    it('Downloading data', function()
    {
        cy.intercept('GET', '**/user/export-tasks/*').as('userExport')
        cy.wait('@userExport').its('response.statusCode').should('eq', 200)

        // //check app logo works 
        // cy.intercept('GET', '**static/media/**').as('appLogo')
        // cy.wait('@appLogo').its('response.statusCode').should('eq', 200)

        cy.intercept('OPTIONS', '**/user/export-tasks/*').as('export')
        cy.wait('@export').its('response.statusCode').should('eq', 200)

        cy.get('.form-group > .btn').should('have.attr', 'href').and('include', 'https://s3.eu-west-3.amazonaws.com')
        .then(href => {
            cy.writeFile('urls/url.txt', href)
            cy.readFile('urls/url.txt').then((text) => {
            expect(text).to.equal(href) // true
            })
      });
       

    })

     it('Logging out', function()
     {
        cy.get('#basic-nav-dropdown')
        cy.get('.caret').click()
        cy.get('[role="menuitem"] > a').click()
     })
})