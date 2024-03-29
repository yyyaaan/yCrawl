const puppeteer = require('puppeteer')
const filesave = require('fs')

const DEBUG_MODE = false
const the_key = process.argv[2]
const the_url = process.argv[3]

// broswer configuration
const max_time = 70000
const wait_opts = { waitUntil: 'networkidle0' }

// output coordinator, ; required for asynce next
const exe_start = new Date();
var out_path = "./cache/" + the_key + "_" + exe_start.toISOString().substring(11, 23).replace(/[^0-9]/g, '')
var out = ["<nodeinfo>ok</nodeinfo>", 
    "<vmid>" + String(process.env['VMID']) + "</vmid>",
    "<qurl>" + the_url + "</qurl>", 
    "<timestamp>" + exe_start.toISOString() + "</timestamp>"
];


(async () => {
    // start browser, block image and open the empty page 
    const browser = await puppeteer.launch({
        headless: true,
        ignoreHTTPSErrors: true,
        defaultViewport: { width: 1680, height: 800 },
        args: ['--no-sandbox']
    });
    const page = await browser.newPage();
    await page.setUserAgent('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36');
    page.setDefaultTimeout(max_time);
    page.setDefaultNavigationTimeout(max_time);
    page.setRequestInterception(true);
    page.on('request', (request) => {
        if (request.resourceType() === 'image') request.abort();
        else request.continue();
    });


    try {
        await page.goto(the_url, wait_opts);

        switch (the_url.split(".")[1]) {
            case "qatarairways":
                if (DEBUG_MODE) console.log("---QR---")

                await page.waitForSelector('div.flightDetail')    
                await page.evaluate( () => {window.scrollBy(0, 150);});
                await page.waitForTimeout(3000)
                // cookie accept
                let cookie_asked = await page.evaluate(() => {
                    let el = document.querySelector("#cookieContainer")
                    return el ? true : false
                })
                if (cookie_asked) {
                    await page.click("a#cookie-close-accept-all")
                    await page.waitForTimeout(2000)
                }

                await page.click('a#flightDetailForm_outbound\\:calendarInitiator')
                console.log("click ok")
                await page.waitForSelector('h3.csJHeadDeprt');
                
                out.push('<exetime>' + (new Date() - exe_start)/1000 + '</exetime>\n');
                out.push(await page.evaluate(() => document.querySelector('div#previousSearch').outerHTML));
                out.push(await page.evaluate(() => document.querySelector('div.csRight').innerHTML));
                break


            case "fourseasons":
                if (DEBUG_MODE) console.log("---FSH---")

                var availability = await page.evaluate(() => document.querySelector('div.booking-messages').innerText);
                if(availability.toLowerCase().search('unable to book') >= 0) {
                out.push("<flag>Sold Out</flag>")
                }
                else {
                await page.waitForSelector('ul.search-results');
                out.push("<flag>Available</flag>")
                    //out.push(await page.evaluate(() => document.querySelector('div.search-summary-group').outerHTML));
                    out.push(await page.evaluate(() => document.querySelector('div.main-inner').outerHTML));
                }
                break


            case "marriott":
                if (DEBUG_MODE) console.log("---MRT---")

                const selectorArea = 'div.search-form-container > div > div > div > div > div.container.property-card-outer-container.pr-0 > div > div:nth-child(1) > div > div > div.color-scheme1.text-container > div.lower-section';
                await page.click('#advanced-search-form > div > div.l-s-col-4.l-xl-col-2.l-xl-last-col.l-hsearch-find > button');
                await page.waitForSelector('div.search-form-container');
                await page.waitForSelector('div.property-card-container');
                await page.waitForSelector(selectorArea);

                var availability = await page.evaluate((selectorArea) => {
                    const element = document.querySelector(selectorArea);
                    return element ? element.innerText : 'selector empty';
                  }, selectorArea);

                if (availability.toLowerCase().search('unavailable') >= 0) {
                    out.push("<flag>Sold Out</flag><content>" + availability + "</content>")
                }
                else {
                    out.push("<flag>Available</flag>");
                    await page.click(selectorArea + ' > div.price-container > a > button');
                    await page.waitForSelector('div.rate-content-container');
                    out.push(await page.evaluate(() => document.querySelector('body').outerHTML));
                }
                break


            case "hilton":
                if(DEBUG_MODE) console.log("---HLT---")

                var availability = await page.evaluate(() => document.querySelector('div.container > div.flex > div.flex-1').innerText);

                if(availability.toLowerCase().search('any rooms available') >= 0) {
                    out.push("<flag>Sold Out</flag>");
                }
                else {
                    out.push("<flag>Available</flag>")
                    await page.waitForSelector('main.relative')
                    out.push(await page.evaluate(() => document.querySelector('main').outerHTML))
                }
                break
            

            case "accor":
                if (DEBUG_MODE) console.log("---ACR---")
                await page.waitForTimeout(6999)
                await page.waitForSelector('.default__main');

                var availability = await page.evaluate(() => document.querySelector('.default__main').innerText);
                if(availability.toLowerCase().search('sorry') >= 0) {
                  out.push("<flag>Sold Out</flag>");
                }
                else {
                  out.push("<flag>Available</flag>");
                      out.push(await page.evaluate(() => document.querySelector('ul.rooms-list').outerHTML));
                      out.push(await page.evaluate(() => document.querySelector('div.basket-hotel-info').outerHTML));
                }
                break

            default:
                if (DEBUG_MODE) console.log("---Undefined website")

        }

        if(DEBUG_MODE) await page.screenshot({path: out_path + '.png'})
        out.push('<exetime>' + (new Date() - exe_start) / 1000 + '</exetime>\n')
        filesave.writeFile(out_path + '.pp', out.join(''), function (err) {})

    } catch (e) {

        out[0] = '<nodeinfo>error</nodeinfo>'
        out.push(e)
        // await page.screenshot({ path: out_path + '_XXX.png'})
        filesave.writeFile(out_path + '_ERR.pp', out.join(''), function (err) {})
    }

    await browser.close()
})()


