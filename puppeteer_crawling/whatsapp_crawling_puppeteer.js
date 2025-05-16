const puppeteer = require("puppeteer")

async function run() {
    const browser = await puppeteer.launch({executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        userDataDir: './myUserDataDir',
        headless: false,
        defaultViewport: false
    });
    const page = await browser.newPage();
    
    await page.setUserAgent(
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36");
    
    await page.goto("https://web.whatsapp.com/");


}

run();



// executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", 
// userDataDir: "/Users/haley/Library/Application Support/Google/Chrome",