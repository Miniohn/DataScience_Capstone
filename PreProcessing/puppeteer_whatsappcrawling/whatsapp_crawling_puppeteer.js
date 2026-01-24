const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

class WhatsAppFinalCrawler {
    constructor() {
        this.browser = null;
        this.page = null;
        this.outputDir = './whatsapp_exports';
        this.chatData = [];
        
        // 실제 WhatsApp 웹 구조에 맞는 선택자들
        this.selectors = {
            chatList: '#pane-side > div:nth-child(1) > div > div',
            chatItem: '#pane-side > div:nth-child(1) > div > div > div',
            messagesContainer: '#main > div.x1n2onr6.x1vjfegm.x1cqoux5.x14yy4lh > div > div.x10l6tqk.x13vifvy.x17qophe.xyw6214.x9f619.x78zum5.xdt5ytf.xh8yej3.x5yr21d.x6ikm8r.x1rife3k.xjbqb8w.x1ewm37j > div.x3psx0u.xwib8y2.xkhd6sd.xrmvbpv.xh8yej3.xquzyny.x1gryazu.xkrivgy',
            messageText: 'span._ao3e.selectable-text.copyable-text',
            chatHeader: '#main > header > div.x78zum5.xdt5ytf.x1iyjqo2.xl56j7k.xeuugli.xtnn1bt.x9v5kkp.xmw7ebm.xrdum7p > div.x78zum5.x1cy8zhl.x1y332i5.xggjnk3.x1yc453h > div > div > div > span',
            messageContainer: 'div._amk4'
        };
    }

    async initialize() {
        if (!fs.existsSync(this.outputDir)) {
            fs.mkdirSync(this.outputDir, { recursive: true });
        }

        this.browser = await puppeteer.launch({
            executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            userDataDir: './myUserDataDir',
            headless: false,
            defaultViewport: null,
            args: ['--no-sandbox', '--disable-setuid-sandbox', '--start-maximized']
        });

        this.page = await this.browser.newPage();
        await this.page.setUserAgent(
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        );
    }

    async navigateToWhatsApp() {
        console.log('WhatsApp 웹에 접속 중...');
        await this.page.goto("https://web.whatsapp.com/", { 
            waitUntil: 'networkidle0',
            timeout: 30000 
        });
        console.log('페이지 로드 완료');
    }

    async waitForLogin() {
        console.log('로그인 대기 중... (수동으로 QR 코드를 스캔해주세요)');
        
        // 채팅 목록이 나타날 때까지 대기
        let attempts = 0;
        const maxAttempts = 60; // 5분 대기
        
        while (attempts < maxAttempts) {
            try {
                await this.page.waitForSelector(this.selectors.chatList, { timeout: 5000 });
                console.log('✅ 로그인 완료 - 채팅 목록 확인됨!');
                return true;
            } catch (error) {
                attempts++;
                console.log(`로그인 대기 중... (${attempts}/${maxAttempts})`);
                await this.sleep(5000); // 5초 대기
            }
        }
        
        throw new Error('로그인 타임아웃');
    }

    async getAllChats() {
        console.log('\n=== 채팅 목록 수집 ===');
        
        // 채팅 목록을 아래로 스크롤하여 모든 채팅 로드
        await this.scrollChatList();
        
        // 모든 채팅 항목 수집
        const chats = await this.page.evaluate((chatItemSelector) => {
            const chatElements = document.querySelectorAll(chatItemSelector);
            const chatList = [];
            
            chatElements.forEach((chatElement, index) => {
                try {
                    let chatName = '';
                    
                    // 방법 1: 정확한 이름이 들어있는 span 찾기 (last seen 제외)
                    const spanElements = chatElement.querySelectorAll('span');
                    for (let span of spanElements) {
                        const text = span.textContent.trim();
                        const title = span.getAttribute('title');
                        
                        // "last seen" 관련 텍스트는 건너뛰기
                        if (title && title.includes('last seen')) {
                            continue;
                        }
                        if (text.includes('last seen')) {
                            continue;
                        }
                        
                        // 유효한 이름 조건: 길이가 적당하고, 시간 형식이 아니며, 특수 문자가 많지 않음
                        if (text && 
                            text.length > 1 && 
                            text.length < 100 && 
                            !text.includes(':') && 
                            !text.match(/\d{1,2}:\d{2}/) &&
                            !text.includes('AM') && 
                            !text.includes('PM') &&
                            !text.includes('yesterday') &&
                            !text.includes('today') &&
                            text !== 'You') {
                                
                            chatName = text;
                            break;
                        }
                    }
                    
                    // 방법 2: data-testid나 다른 속성에서 찾기
                    if (!chatName) {
                        const nameElements = chatElement.querySelectorAll('[data-testid*="conversation"] span, [title]:not([title*="last seen"])');
                        for (let element of nameElements) {
                            const text = element.textContent.trim();
                            const title = element.getAttribute('title');
                            
                            if (title && !title.includes('last seen') && title.length > 1 && title.length < 100) {
                                chatName = title;
                                break;
                            } else if (text && text.length > 1 && text.length < 100 && 
                                      !text.includes('last seen') && !text.includes(':')) {
                                chatName = text;
                                break;
                            }
                        }
                    }
                    
                    // 방법 3: 전체 텍스트에서 첫 번째 유효한 라인 찾기
                    if (!chatName) {
                        const fullText = chatElement.textContent.trim();
                        const lines = fullText.split('\n').filter(line => line.trim().length > 0);
                        
                        for (let line of lines) {
                            line = line.trim();
                            if (line && 
                                !line.includes('last seen') && 
                                !line.includes(':') && 
                                !line.match(/\d{1,2}:\d{2}/) &&
                                line.length > 1 && 
                                line.length < 100) {
                                chatName = line;
                                break;
                            }
                        }
                    }
                    
                    // 최종 안전장치
                    if (!chatName) {
                        chatName = `Chat_${index + 1}`;
                    }
                    
                    if (chatName && chatName.length > 0) {
                        chatList.push({
                            index: index,
                            name: chatName.substring(0, 50),
                            selector: `${chatItemSelector}:nth-child(${index + 1})`
                        });
                    }
                } catch (error) {
                    console.error(`채팅 ${index} 처리 중 오류:`, error);
                }
            });
            
            return chatList;
        }, this.selectors.chatItem);

        console.log(`📋 총 ${chats.length}개의 채팅을 발견했습니다:`);
        chats.slice(0, 5).forEach((chat, i) => {
            console.log(`${i + 1}. ${chat.name}`);
        });
        
        return chats;
    }

    async scrollChatList() {
        console.log('채팅 목록 전체 로드를 위해 스크롤 중...');
        
        await this.page.evaluate((chatListSelector) => {
            const chatListContainer = document.querySelector(chatListSelector);
            if (chatListContainer) {
                let lastHeight = 0;
                let currentHeight = chatListContainer.scrollHeight;
                let attempts = 0;
                const maxAttempts = 20;
                
                const scrollInterval = setInterval(() => {
                    chatListContainer.scrollTop = chatListContainer.scrollHeight;
                    attempts++;
                    
                    setTimeout(() => {
                        currentHeight = chatListContainer.scrollHeight;
                        if (currentHeight === lastHeight || attempts >= maxAttempts) {
                            clearInterval(scrollInterval);
                        }
                        lastHeight = currentHeight;
                    }, 1000);
                }, 1500);
            }
        }, this.selectors.chatList);
        
        // 스크롤 완료 대기
        await this.sleep(10000);
        console.log('채팅 목록 스크롤 완료');
    }

    async extractChatHistory(chat) {
        console.log(`\n"${chat.name}" 채팅 기록 추출 중...`);
        
        try {
            // 채팅 클릭
            await this.page.click(chat.selector);
            await this.sleep(3000);

            // 채팅 제목 확인 - 더 정확한 방법으로 추출
            let chatTitle = chat.name;
            try {
                await this.page.waitForSelector(this.selectors.chatHeader, { timeout: 5000 });
                
                // 여러 방법으로 채팅 제목 추출 시도
                chatTitle = await this.page.evaluate((headerSelector) => {
                    // 방법 1: 정확한 헤더 선택자 사용
                    let headerElement = document.querySelector(headerSelector);
                    if (headerElement && headerElement.textContent && !headerElement.textContent.includes('last seen')) {
                        return headerElement.textContent.trim();
                    }
                    
                    // 방법 2: 다른 헤더 선택자들 시도
                    const alternativeSelectors = [
                        '#main header span:not([title*="last seen"])',
                        '#main header div span',
                        '#main header [data-testid] span'
                    ];
                    
                    for (const selector of alternativeSelectors) {
                        const elements = document.querySelectorAll(selector);
                        for (const element of elements) {
                            const text = element.textContent.trim();
                            if (text && 
                                !text.includes('last seen') && 
                                !text.includes('Search') && 
                                !text.includes('Menu') &&
                                text.length > 1 && 
                                text.length < 100) {
                                return text;
                            }
                        }
                    }
                    
                    return null;
                }, this.selectors.chatHeader);
                
                if (!chatTitle) chatTitle = chat.name;
            } catch (error) {
                console.log(`채팅 헤더를 찾을 수 없음, 기본 이름 사용: ${chat.name}`);
                chatTitle = chat.name;
            }

            console.log(`📱 현재 채팅: ${chatTitle}`);

            // 메시지 기록을 맨 위로 스크롤
            await this.scrollToTopOfChat();

            // 모든 메시지 추출
            const messages = await this.extractAllMessages();
            
            return {
                chatName: chatTitle,
                originalName: chat.name,
                messages: messages
            };

        } catch (error) {
            console.error(`채팅 "${chat.name}" 추출 중 오류:`, error);
            return null;
        }
    }

    async scrollToTopOfChat() {
        console.log('채팅을 맨 위로 스크롤 중...');
        
        await this.page.evaluate((messagesContainerSelector) => {
            const messagesContainer = document.querySelector(messagesContainerSelector);
            if (messagesContainer) {
                let previousScrollTop = messagesContainer.scrollTop;
                let attempts = 0;
                const maxAttempts = 50;

                const scrollUp = () => {
                    if (attempts >= maxAttempts) return;
                    
                    messagesContainer.scrollTop = 0;
                    attempts++;
                    
                    setTimeout(() => {
                        const currentScrollTop = messagesContainer.scrollTop;
                        if (currentScrollTop === previousScrollTop && currentScrollTop === 0) {
                            return; // 스크롤 완료
                        }
                        previousScrollTop = currentScrollTop;
                        scrollUp();
                    }, 1000);
                };
                
                scrollUp();
            }
        }, this.selectors.messagesContainer);
        
        // 스크롤 완료 대기
        await this.sleep(15000);
        console.log('채팅 스크롤 완료');
    }

    async extractAllMessages() {
        console.log('메시지 추출 중...');
        
        const messages = await this.page.evaluate((selectors) => {
            const messageContainers = document.querySelectorAll(selectors.messageContainer);
            const extractedMessages = [];
            
            messageContainers.forEach((msgContainer, index) => {
                try {
                    // 메시지 텍스트 추출
                    const textElement = msgContainer.querySelector(selectors.messageText);
                    const messageText = textElement ? textElement.textContent.trim() : '';
                    
                    // 시간 추출 (여러 방법 시도)
                    let timestamp = '';
                    const timeSelectors = [
                        '[data-testid="msg-meta"] span',
                        '.message-meta span',
                        'span[title]',
                        'span'
                    ];
                    
                    for (const timeSelector of timeSelectors) {
                        const timeElements = msgContainer.querySelectorAll(timeSelector);
                        for (const timeEl of timeElements) {
                            const timeText = timeEl.textContent.trim();
                            if (/\d{1,2}:\d{2}/.test(timeText) || timeText.includes('AM') || timeText.includes('PM')) {
                                timestamp = timeText;
                                break;
                            }
                        }
                        if (timestamp) break;
                    }
                    
                    // 발신자 구분 (outgoing/incoming)
                    const isOutgoing = msgContainer.closest('div').classList.contains('message-out') ||
                                     msgContainer.parentElement.classList.contains('message-out') ||
                                     msgContainer.innerHTML.includes('message-out');
                    
                    // 시스템 메시지 확인
                    const isSystemMsg = msgContainer.textContent.includes('joined') || 
                                       msgContainer.textContent.includes('left') ||
                                       msgContainer.textContent.includes('created') ||
                                       msgContainer.textContent.includes('added') ||
                                       msgContainer.textContent.includes('removed');
                    
                    if (messageText || isSystemMsg) {
                        extractedMessages.push({
                            timestamp: timestamp,
                            sender: isSystemMsg ? 'System' : (isOutgoing ? 'Me' : 'Contact'),
                            message: messageText,
                            isSystem: isSystemMsg
                        });
                    }
                } catch (error) {
                    console.error(`메시지 ${index} 추출 중 오류:`, error);
                }
            });
            
            return extractedMessages;
        }, this.selectors);

        console.log(`📝 ${messages.length}개의 메시지를 추출했습니다.`);
        return messages;
    }

    formatChatData(chatData) {
        let formattedText = `✨${chatData.chatName}✨\n`;
        formattedText += `Messages and calls are end-to-end encrypted. Only people in this chat can read, listen to, or share them.\n`;
        formattedText += `Welcome to the chat: ✨${chatData.chatName}✨\n\n`;
        
        chatData.messages.forEach(msg => {
            if (msg.isSystem) {
                formattedText += `${msg.message}\n`;
            } else {
                const senderName = msg.sender === 'Me' ? '~ You' : `~ ${chatData.chatName}`;
                const timeStr = msg.timestamp ? `[${msg.timestamp}] ` : '';
                formattedText += `${timeStr}${senderName}: ${msg.message}\n`;
            }
        });
        
        return formattedText;
    }

    async saveChatData(chatData) {
        const safeFileName = chatData.chatName.replace(/[^a-zA-Z0-9가-힣\s]/g, '_');
        const filename = `${safeFileName}.txt`;
        const filepath = path.join(this.outputDir, filename);
        const formattedData = this.formatChatData(chatData);
        
        fs.writeFileSync(filepath, formattedData, 'utf8');
        console.log(`💾 채팅 데이터 저장: ${filename}`);
    }

    async saveAllChatsData() {
        const allChatsFile = path.join(this.outputDir, 'all_chats_combined.txt');
        let combinedData = '';
        
        this.chatData.forEach((chat, index) => {
            combinedData += `\n${'='.repeat(60)}\n`;
            combinedData += `채팅 ${index + 1}: ${chat.chatName}\n`;
            combinedData += `${'='.repeat(60)}\n`;
            combinedData += this.formatChatData(chat);
            combinedData += '\n';
        });
        
        fs.writeFileSync(allChatsFile, combinedData, 'utf8');
        console.log('📚 통합 채팅 파일 저장: all_chats_combined.txt');
    }

    async sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    async run() {
        try {
            await this.initialize();
            await this.navigateToWhatsApp();
            await this.waitForLogin();
            
            // 로그인 후 스크린샷
            await this.page.screenshot({ 
                path: path.join(this.outputDir, 'logged_in_state.png'),
                fullPage: true 
            });
            
            const chatList = await this.getAllChats();
            
            console.log(`\n🚀 ${chatList.length}개 채팅 추출 시작!`);
            
            for (let i = 0; i < chatList.length; i++) {
                console.log(`\n⏳ 진행률: ${i + 1}/${chatList.length}`);
                
                const chatData = await this.extractChatHistory(chatList[i]);
                
                if (chatData && chatData.messages.length > 0) {
                    await this.saveChatData(chatData);
                    this.chatData.push(chatData);
                } else {
                    console.log(`⚠️  "${chatList[i].name}" 채팅에서 메시지를 찾을 수 없음`);
                }
                
                // 다음 채팅으로 넘어가기 전 대기
                await this.sleep(3000);
            }
            
            await this.saveAllChatsData();
            
            // 최종 통계
            console.log('\n🎉 크롤링 완료!');
            console.log(`📊 처리된 채팅: ${this.chatData.length}/${chatList.length}`);
            console.log(`📁 저장 위치: ${this.outputDir}`);
            
            const totalMessages = this.chatData.reduce((sum, chat) => sum + chat.messages.length, 0);
            console.log(`💬 총 메시지 수: ${totalMessages}`);
            
        } catch (error) {
            console.error('❌ 크롤링 중 오류:', error);
        } finally {
            if (this.browser) {
                console.log('\n브라우저를 5초 후 종료합니다...');
                await this.sleep(5000);
                await this.browser.close();
            }
        }
    }
}

// 실행
async function main() {
    const crawler = new WhatsAppFinalCrawler();
    await crawler.run();
}

main().catch(console.error);


// const puppeteer = require('puppeteer');

// async function run() {
//     const browser = await puppeteer.launch({executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
//         userDataDir: './myUserDataDir',
//         headless: false,
//         defaultViewport: false
//     });
//     const page = await browser.newPage();
    
//     await page.setUserAgent(
//   "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36");
    
//     await page.goto("https://web.whatsapp.com/");
    
//     await page.evaluate(() => {
//     window.scrollTo(0, document.body.scrollHeight);
//     });

//     await page.waitForSelector(`#unread-filter`,{ timeout: 30000 }); 

//     // Scrolling to the bottom of the people page
//     await page.evaluate(() => {
//       window.scrollTo(0, document.body.scrollHeight);
//     });

//     // Click first chat buttom
//     // fix!! --> many people involved in this account 
//     await page.waitForSelector(`#pane-side > div:nth-child(1) > div > div > div:nth-child(3) > div > div > div > div._ak8l._ap1_`,{ timeout: 30000 }); 
//     await page.click('#pane-side > div:nth-child(1) > div > div > div:nth-child(3) > div > div > div > div._ak8l._ap1_');
    
//     // await page.waitForSelector(`#main > header > div.x78zum5.xdt5ytf.x1iyjqo2.xl56j7k.xeuugli.xtnn1bt.x9v5kkp.xmw7ebm.xrdum7p > div.x78zum5.x1cy8zhl.x1y332i5.xggjnk3.x1yc453h > div > span`,{ timeout: 10000 }); 

//     // Extract title
//     await page.waitForSelector(`#main header span`,{ timeout: 30000 }); 

//     const chatTitle = await page.evaluate(() => {
//       const spans = document.querySelectorAll('#main header span');
//       return spans.length > 1 ? spans[1].textContent : 'Unknown Chat';
//     });
//     console.log(chatTitle);

//     // copy all chat, press keyboard
//     // to select all text
//     await page.waitForSelector('#main > header',{ timeout: 30000 }); 
//     await page.click('#main > header');

//     // last message click
//     await page.waitForSelector('div.message-in, div.message-out',{timeout:30000}); 
//     await page.click('div.message-in, div.message-out');

//     // all select and copy key
//     await page.keyboard.down('Meta');
//     await page.keyboard.press('KeyA');
//     await page.keyboard.up('Meta');

//     await page.keyboard.down('Meta');
//     await page.keyboard.press('KeyC');
//     await page.keyboard.up('Meta');

//     // clipboard
//     const cp = require('copy-paste');
//     cp.paste((err, text) => {
//       console.log(text);
//     });
    
// };


// run();

    


    
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