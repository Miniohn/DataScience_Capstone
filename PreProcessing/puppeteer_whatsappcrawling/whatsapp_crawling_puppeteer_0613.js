const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

class WhatsAppFinalCrawler {
    constructor() {
        this.browser = null;
        this.page = null;
        this.outputDir = './whatsapp_exports';
        this.chatData = [];
        
        // 실제 WhatsApp 웹 구조에 맞는 업데이트된 선택자들
        this.selectors = {
            chatList: '#pane-side > div:nth-child(1) > div > div',
            chatItem: '#pane-side > div:nth-child(1) > div > div > div',
            // 실제 메시지 컨테이너 (기존 방식 + 업데이트된 선택자)
            messagesContainer: '#main > div.x1n2onr6.x1vjfegm.x1cqoux5.x14yy4lh > div > div.x10l6tqk.x13vifvy.x1o0tod.xyw6214.x9f619.x78zum5.xdt5ytf.xh8yej3.x5yr21d.x6ikm8r.x1rife3k.xjbqb8w.x1ewm37j',
            // 대안 선택자들
            messagesContainerAlt: [
                'div[tabindex="0"][role="application"]',
                '#main div[style*="overflow"]',
                '#main > div.x1n2onr6.x1vjfegm.x1cqoux5.x14yy4lh > div > div.x10l6tqk.x13vifvy.x17qophe.xyw6214.x9f619.x78zum5.xdt5ytf.xh8yej3.x5yr21d.x6ikm8r.x1rife3k.xjbqb8w.x1ewm37j > div.x3psx0u.xwib8y2.xkhd6sd.xrmvbpv.xh8yej3.xquzyny.x1gryazu.xkrivgy'
            ],
            messageText: 'span._ao3e.selectable-text.copyable-text',
            chatHeader: '#main > header > div.x78zum5.xdt5ytf.x1iyjqo2.xl56j7k.xeuugli.xtnn1bt.x9v5kkp.xmw7ebm.xrdum7p > div.x78zum5.x1cy8zhl.x1y332i5.xggjnk3.x1yc453h > div > div > div > span',
            // 업데이트된 메시지 컨테이너 (HTML 구조에 맞게)
            messageContainer: 'div.x1n2onr6',
            // 시간 선택자들
            timeSelectors: [
                'span.x1c4vz4f.x2lah0s',
                'span.x1rg5ohu.x16dsc37',
                '[data-testid="msg-meta"] span',
                'span[title]'
            ]
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
        
        let attempts = 0;
        const maxAttempts = 60;
        
        while (attempts < maxAttempts) {
            try {
                await this.page.waitForSelector(this.selectors.chatList, { timeout: 5000 });
                console.log('✅ 로그인 완료 - 채팅 목록 확인됨!');
                return true;
            } catch (error) {
                attempts++;
                console.log(`로그인 대기 중... (${attempts}/${maxAttempts})`);
                await this.sleep(5000);
            }
        }
        
        throw new Error('로그인 타임아웃');
    }

    async getAllChats() {
        console.log('\n=== 채팅 목록 수집 ===');
        
        await this.scrollChatList();
        
        const chats = await this.page.evaluate((chatItemSelector) => {
            const chatElements = document.querySelectorAll(chatItemSelector);
            const chatList = [];
            
            chatElements.forEach((chatElement, index) => {
                try {
                    let chatName = '';
                    
                    const spanElements = chatElement.querySelectorAll('span');
                    for (let span of spanElements) {
                        const text = span.textContent.trim();
                        const title = span.getAttribute('title');
                        
                        if (title && title.includes('last seen')) {
                            continue;
                        }
                        if (text.includes('last seen')) {
                            continue;
                        }
                        
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
        
        await this.sleep(10000);
        console.log('채팅 목록 스크롤 완료');
    }

    // 메시지 컨테이너 찾기 및 스크롤 필요성 확인
    async findAndCheckScrollNeed() {
        console.log('메시지 컨테이너 찾기 및 스크롤 필요성 확인 중...');
        
        const result = await this.page.evaluate((selectors) => {
            let container = null;
            let containerSelector = null;
            
            // 1. 기본 메시지 컨테이너 찾기
            container = document.querySelector(selectors.messagesContainer);
            if (container) {
                containerSelector = selectors.messagesContainer;
                console.log('기본 선택자로 컨테이너 발견');
            } else {
                // 2. 대안 선택자들 시도
                for (const altSelector of selectors.messagesContainerAlt) {
                    container = document.querySelector(altSelector);
                    if (container) {
                        containerSelector = altSelector;
                        console.log('대안 선택자로 컨테이너 발견:', altSelector);
                        break;
                    }
                }
            }
            
            if (!container) {
                console.error('메시지 컨테이너를 찾을 수 없습니다');
                return { found: false };
            }
            
            // 3. 스크롤 필요성 확인
            const scrollInfo = {
                scrollHeight: container.scrollHeight,
                clientHeight: container.clientHeight,
                scrollTop: container.scrollTop,
                offsetHeight: container.offsetHeight
            };
            
            // 스크롤이 필요한 조건들:
            // - 컨텐츠가 화면보다 큼 (scrollHeight > clientHeight)
            // - 현재 맨 위에 있지 않음 (scrollTop > 0) 또는
            // - 스크롤 가능한 충분한 컨텐츠가 있음 (scrollHeight - clientHeight > 100)
            const hasScrollableContent = scrollInfo.scrollHeight > scrollInfo.clientHeight;
            const notAtTop = scrollInfo.scrollTop > 0;
            const significantContent = (scrollInfo.scrollHeight - scrollInfo.clientHeight) > 100;
            
            const needsScroll = hasScrollableContent && (notAtTop || significantContent);
            
            console.log('스크롤 정보:', scrollInfo);
            console.log('스크롤 필요:', needsScroll);
            
            return {
                found: true,
                selector: containerSelector,
                needsScroll: needsScroll,
                scrollInfo: scrollInfo
            };
            
        }, this.selectors);

        if (!result.found) {
            throw new Error('메시지 컨테이너를 찾을 수 없습니다');
        }

        console.log(`✅ 메시지 컨테이너: ${result.selector}`);
        console.log(`📜 스크롤 필요: ${result.needsScroll ? 'Yes' : 'No'}`);
        console.log(`📊 스크롤 정보:`, result.scrollInfo);
        
        return result;
    }

    async extractChatHistory(chat) {
        console.log(`\n"${chat.name}" 채팅 기록 추출 중...`);
        
        try {
            await this.page.click(chat.selector);
            await this.sleep(3000);

            let chatTitle = chat.name;
            try {
                await this.page.waitForSelector(this.selectors.chatHeader, { timeout: 5000 });
                
                chatTitle = await this.page.evaluate((headerSelector) => {
                    let headerElement = document.querySelector(headerSelector);
                    if (headerElement && headerElement.textContent && !headerElement.textContent.includes('last seen')) {
                        return headerElement.textContent.trim();
                    }
                    
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

            // 메시지 컨테이너 찾기 및 스크롤 필요성 확인
            const scrollResult = await this.findAndCheckScrollNeed();

            // 스크롤이 필요한 경우에만 스크롤 실행
            if (scrollResult.needsScroll) {
                console.log('📜 스크롤이 필요하여 채팅을 맨 위로 스크롤합니다...');
                await this.scrollToTopOfChat(scrollResult.selector);
            } else {
                console.log('📜 채팅이 충분히 짧거나 이미 맨 위에 있어서 스크롤을 건너뜁니다.');
            }

            // 메시지 추출
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

    // 기존 스크롤 로직 활용 (선택자만 파라미터로 받도록 수정)
    async scrollToTopOfChat(messagesContainerSelector) {
        console.log('채팅을 맨 위로 스크롤 중...');
        
        await this.page.evaluate((selector) => {
            return new Promise((resolve) => {
                const messagesContainer = document.querySelector(selector);
                if (!messagesContainer) {
                    console.error('메시지 컨테이너를 찾을 수 없습니다:', selector);
                    resolve();
                    return;
                }
                
                let previousScrollTop = messagesContainer.scrollTop;
                let attempts = 0;
                const maxAttempts = 100;
                let stableCount = 0;

                const scrollUp = () => {
                    if (attempts >= maxAttempts) {
                        console.log('최대 스크롤 시도 횟수 도달');
                        resolve();
                        return;
                    }
                    
                    // 점진적으로 위로 스크롤 (1000px씩)
                    const scrollAmount = Math.min(1000, messagesContainer.scrollTop);
                    if (scrollAmount > 0) {
                        messagesContainer.scrollTop -= scrollAmount;
                    } else {
                        messagesContainer.scrollTop = 0;
                    }
                    attempts++;
                    
                    setTimeout(() => {
                        const currentScrollTop = messagesContainer.scrollTop;
                        
                        // 맨 위에 도달했는지 확인
                        if (currentScrollTop === 0) {
                            console.log('맨 위에 도달');
                            resolve();
                            return;
                        }
                        
                        // 스크롤 위치가 변하지 않는지 확인
                        if (currentScrollTop === previousScrollTop) {
                            stableCount++;
                            if (stableCount >= 3) {
                                console.log('스크롤 위치 안정화됨');
                                resolve();
                                return;
                            }
                        } else {
                            stableCount = 0;
                        }
                        
                        previousScrollTop = currentScrollTop;
                        console.log(`스크롤 진행: ${attempts}/${maxAttempts}, 현재 위치: ${currentScrollTop}`);
                        
                        scrollUp();
                    }, 500);
                };
                
                scrollUp();
            });
        }, messagesContainerSelector);
        
        console.log('채팅 스크롤 완료');
    }

    async extractAllMessages() {
        console.log('메시지 추출 중...');
        
        const messages = await this.page.evaluate((selectors) => {
            const messageContainers = document.querySelectorAll(selectors.messageContainer);
            const extractedMessages = [];
            
            console.log(`발견된 메시지 컨테이너 수: ${messageContainers.length}`);
            
            messageContainers.forEach((msgContainer, index) => {
                try {
                    // 메시지 텍스트 추출
                    const textElement = msgContainer.querySelector(selectors.messageText);
                    const messageText = textElement ? textElement.textContent.trim() : '';
                    
                    // 시간 추출
                    let timestamp = '';
                    for (const timeSelector of selectors.timeSelectors) {
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
                    
                    // 발신자 구분 (HTML 구조에 맞게 개선)
                    const isOutgoing = msgContainer.classList.contains('message-out') ||
                                     msgContainer.querySelector('.message-out') ||
                                     msgContainer.closest('.message-out') ||
                                     msgContainer.innerHTML.includes('message-out') ||
                                     msgContainer.querySelector('span[aria-label="You:"]') ||
                                     msgContainer.closest('div[class*="message-out"]') ||
                                     msgContainer.parentElement.innerHTML.includes('tail-out');
                    
                    // 시스템 메시지 확인
                    const isSystemMsg = msgContainer.textContent.includes('joined') || 
                                       msgContainer.textContent.includes('left') ||
                                       msgContainer.textContent.includes('created') ||
                                       msgContainer.textContent.includes('added') ||
                                       msgContainer.textContent.includes('removed') ||
                                       msgContainer.textContent.includes('Messages and calls are end-to-end encrypted');
                    
                    if (messageText || isSystemMsg) {
                        extractedMessages.push({
                            timestamp: timestamp,
                            sender: isSystemMsg ? 'System' : (isOutgoing ? 'Me' : 'Contact'),
                            message: messageText,
                            isSystem: isSystemMsg,
                            index: index
                        });
                    }
                } catch (error) {
                    console.error(`메시지 ${index} 추출 중 오류:`, error);
                }
            });
            
            return extractedMessages;
        }, this.selectors);

        console.log(`📝 ${messages.length}개의 메시지를 추출했습니다.`);
        
        // 메시지 순서 정렬 (오래된 것부터)
        messages.sort((a, b) => a.index - b.index);
        
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
                
                await this.sleep(3000);
            }
            
            await this.saveAllChatsData();
            
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