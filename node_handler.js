const puppeteer = require('puppeteer');
const filesave = require('fs');

const the_key = process.argv[2]
const the_url = process.argv[3]
//let the_key = '20220101_X0001'
//let the_url = 'https://booking.qatarairways.com/nsp/views/showBooking.action?widget=MLC&searchType=S&bookingClass=B&minPurTime=null&tripType=M&allowRedemption=Y&selLang=EN&adults=1&children=0&infants=0&teenager=0&ofw=0&promoCode=&fromStation=HEL&toStation=SYD&departingHiddenMC=26-Sep-2022&departing=2022-09-26&fromStation=CBR&toStation=HEL&departingHiddenMC=11-Oct-2022&departing=2022-10-11'
//console.log(the_key + "\n" + the_url)

// broswer configuration
const max_time = 39000;
const wait_time = 2999;
const wait_opts = { waitUntil: 'networkidle0' };

// output coordinator
const exe_start = new Date();
var out_path = "./cache/" + the_key + "_" + exe_start.toISOString().substring(11, 23).replace(/[^0-9]/g,'')
var out = ["output ok", "\n<qurl>" + the_url + '</qurl>\n<timestamp>' + (exe_start.toISOString()) + '</timestamp>\n'];


(async () => {
    // start browser, block image and open the empty page 
    const browser = await puppeteer.launch({
        headless: true,
        ignoreHTTPSErrors: true,
        defaultViewport: { width: 1080, height: 1330 },
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
        //ready to do something here
        await page.goto(the_url, wait_opts);

        switch(the_url.split(".")[1]) {
            case "qatarairways":
                console.log("---QR")
                break

            case "fourseasons":
                console.log("---FSH")
                break

            case "marriott":
                console.log("---MRT")
                break

            case "accor":
                console.log("---ACR")
                break

            default:
                console.log("Undefined website")

        }



        // saving text file
        out.push('<exetime>' + (new Date() - exe_start) / 1000 + '</exetime>\n');
        filesave.writeFile(out_path + '.pp', out.join(), function(err) {});
    } catch (e) {
        out[0] = 'error';
        out.push(e);
        await page.screenshot({ path: out_path + '_XXX.png' });
        filesave.writeFile(out_path + '_ERR.pp', out.join(), function(err) {});
    }

    await browser.close()
})()


