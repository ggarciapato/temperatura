
'use strict';
const PORT = 8888;
const express = require('express');
const puppeteer = require('puppeteer');
const {Tabletojson: tabletojson} = require('tabletojson/dist');

const App = express();

let browser;

App.get('/scrap', async (request, response) => {
    const { stationCode, startDate, endDate } = request.query;
    console.log(stationCode, startDate);
    if(!browser) browser = await puppeteer.launch(
      { 
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
      }
    );
    const page = await browser.newPage();
    await page.goto('https://tempo.inmet.gov.br/TabelaEstacoes');
    
    await page.waitForNetworkIdle();
    // console.log('seleciona produto');
    const produtoSelector = '#wrapper > div > ul > li:nth-child(3) > select';
    await page.select(produtoSelector, 'TabelaEstacoes');
 
    await page.waitForNetworkIdle();
    // console.log('seleciona tipo de estacao')
    const tipoSelector = '#menu_EstacoesTabela > li:nth-child(1) > select';
    const isAuto = stationCode.startsWith('A') || stationCode.startsWith('B') || stationCode.startsWith('F');
    const stationType = isAuto ? 'T' : 'M';
    await page.select(tipoSelector, stationType);

    await page.waitForNetworkIdle();
    const estacaoSelector = '#menu_EstacoesTabela > li:nth-child(2) > select';
    await page.select(estacaoSelector, stationCode);

    await page.waitForNetworkIdle();
    const inicioSelector = '#datepicker_EstacoesTabela_Inicio';
    await page.$eval(inicioSelector, (el, start) => el.value = start, startDate);
  
    await page.waitForNetworkIdle();
    const finalSelector = '#datepicker_EstacoesTabela_Fim';
    await page.$eval(finalSelector, (el, end) => el.value = end, endDate);
  
    await page.waitForNetworkIdle();
    const submitSelector = '#EstacoesTabela';
    const submitHandle = await page.$(submitSelector);
    submitHandle.click();

    await page.waitForNetworkIdle();
    // console.log('carregou tabela');

    const tableSelector = '#tabela';

    const tableContent = await page.$eval(tableSelector, (el) => {return el.outerHTML});
    const tableJson = tabletojson.convert(tableContent);
    
    response.send(tableJson);
    await page.close()

});

App.listen(PORT, () => {
    console.log(`server app listening at http://localhost:${PORT}`)
})