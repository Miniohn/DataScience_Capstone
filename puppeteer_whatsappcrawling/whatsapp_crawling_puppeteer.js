const puppeteer = require('puppeteer');

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
    
    await page.evaluate(() => {
    window.scrollTo(0, document.body.scrollHeight);
    });

    await page.waitForSelector(`#unread-filter`,{ timeout: 30000 }); 

    // Scrolling to the bottom of the people page
    await page.evaluate(() => {
      window.scrollTo(0, document.body.scrollHeight);
    });

    // Click first chat buttom
    // fix!! --> many people involved in this account 
    await page.waitForSelector(`#pane-side > div:nth-child(1) > div > div > div:nth-child(3) > div > div > div > div._ak8l._ap1_`,{ timeout: 30000 }); 
    await page.click('#pane-side > div:nth-child(1) > div > div > div:nth-child(3) > div > div > div > div._ak8l._ap1_');
    
    // await page.waitForSelector(`#main > header > div.x78zum5.xdt5ytf.x1iyjqo2.xl56j7k.xeuugli.xtnn1bt.x9v5kkp.xmw7ebm.xrdum7p > div.x78zum5.x1cy8zhl.x1y332i5.xggjnk3.x1yc453h > div > span`,{ timeout: 10000 }); 

    // Extract title
    await page.waitForSelector(`#main header span`,{ timeout: 30000 }); 

    const chatTitle = await page.evaluate(() => {
      const spans = document.querySelectorAll('#main header span');
      return spans.length > 1 ? spans[1].textContent : 'Unknown Chat';
    });
    console.log(chatTitle);

    // copy all chat, press keyboard
    // to select all text
    await page.waitForSelector('#main > header',{ timeout: 30000 }); 
    await page.click('#main > header');

    // 2. 본문 메시지 중 가장 마지막 메시지를 포함하는 div 클릭
    await page.waitForSelector('div.message-in, div.message-out',{timeout:30000}); // WhatsApp 메시지 DOM
    await page.click('div.message-in, div.message-out'); // 실제 메시지에 포커스

    // 복사 키 입력
    await page.keyboard.down('Meta');
    await page.keyboard.press('KeyA');
    await page.keyboard.up('Meta');

    await page.keyboard.down('Meta');
    await page.keyboard.press('KeyC');
    await page.keyboard.up('Meta');

    // 클립보드 읽기
    const cp = require('copy-paste');
    cp.paste((err, text) => {
      console.log(text);
    });
    
};


run();

    


    
    // // Scrolling to the top of the chat page
    // await page.evaluate(async () => {
    //     const container = document.querySelector('#main > div.x1n2onr6.x1vjfegm.x1cqoux5.x14yy4lh > div > div.x10l6tqk.x13vifvy.x17qophe.xyw6214.x9f619.x78zum5.xdt5ytf.xh8yej3.x5yr21d.x6ikm8r.x1rife3k.xjbqb8w.x1ewm37j');

    //     if (!container) {
    //         console.error("cannot find first chat");
    //         return;
    //     }

    //     // at least 30 times scroll, wait for 500ms
    //     for (let i = 0; i < 30; i++) {
    //         container.scrollTop = 0;
    //         await new Promise(resolve => setTimeout(resolve, 500));
    //     }
    // });
    
    // get first text
    // const text1 = await page.evaluate(() => 
      // document.querySelector('#main > div.x1n2onr6.x1vjfegm.x1cqoux5.x14yy4lh > div > div.x10l6tqk.x13vifvy.x17qophe.xyw6214.x9f619.x78zum5.xdt5ytf.xh8yej3.x5yr21d.x6ikm8r.x1rife3k.xjbqb8w.x1ewm37j > div.x3psx0u.xwib8y2.xkhd6sd.xrmvbpv.xh8yej3.xquzyny.x1gryazu.xkrivgy > div:nth-child(4) > div > div > div._amk4.false._amkd._amk5 > div._amk6._amlo > div:nth-child(2) > div > div.copyable-text > div > span._ao3e.selectable-text.copyable-text').textContent);
    // console.log(text1);

    // scrolling down and get text
    // source video : https://youtu.be/nDBdvqRWvCw?feature=shared

    // #main > div.x1n2onr6.x1vjfegm.x1cqoux5.x14yy4lh > div > div.x10l6tqk.x13vifvy.x17qophe.xyw6214.x9f619.x78zum5.xdt5ytf.xh8yej3.x5yr21d.x6ikm8r.x1rife3k.xjbqb8w.x1ewm37j > div.x3psx0u.xwib8y2.xkhd6sd.xrmvbpv.xh8yej3.xquzyny.x1gryazu.xkrivgy > div:nth-child("7") > div > div > div._amk4.false._amkd > div._amk6._amlo > div:nth-child("1") > div > div.copyable-text > div > span._ao3e.selectable-text.copyable-text
    


    //await browser.close();

//https://velog.io/@newsuperfi/puppeteer%EB%A1%9C-%EC%9B%B9-%EC%8A%A4%ED%81%AC%EB%9E%98%ED%95%91%ED%95%98%EA%B8%B0

// executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", 
// userDataDir: "/Users/haley/Library/Application Support/Google/Chrome",