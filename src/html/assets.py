# -*- coding: UTF-8 -*-
"""Assets: CSS placeholder and inline JS for fund pages."""

def get_css_style():
    """样式已合并到 static/css/style.css，此处仅保留空字符串以兼容调用方。"""
    return ""


def get_javascript_code():
    return r"""
    <!-- Import Map for ESM modules -->
    <script>
    // Polyfill process for React libraries
    window.process = {
        env: {
            NODE_ENV: 'production'
        }
    };
    window.onerror = function(message, source, lineno, colno, error) {
        console.error("Global Error Caught:", error);
        const root = document.getElementById('pro-chat-root');
        if (root && root.innerHTML === '') {
            root.innerHTML = `<div style="padding:20px; color:red;">
                <h3>Failed to load Pro Chat</h3>
                <p>Error: ${message}</p>
                <p>Dependencies might be missing in CDN mode.</p>
                <button onclick="location.reload()" style="padding:5px 10px; margin-top:10px;">Retry</button>
            </div>`;
        }
    };
    </script>
    <link rel="stylesheet" href="https://unpkg.com/quikchat/dist/quikchat.css">
    <script src="https://unpkg.com/quikchat"></script>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>

    <script>
    document.addEventListener('DOMContentLoaded', function() {
        // Initialize Auto Colorize
        autoColorize();

        // 🔧 独立的对话历史管理 - 不依赖 QuikChat 内部状态
        let conversationHistory = [];

        // Initialize QuikChat
        const chat = new quikchat('#pro-chat-root', async (instance, message) => {
            // Display user message immediately
            instance.messageAddNew(message, 'You', 'right');
            
            // 🔧 添加用户消息到独立历史
            conversationHistory.push({
                role: 'user',
                content: message
            });
            
            console.log("💬 Current conversation history:", conversationHistory);
            
            // 不再收集前端context，所有数据由后端获取
            console.log("Sending message to backend (context will be fetched by backend)");

            // Create loading indicator
            const loadingHtml = '<div class="ai-loading-indicator" style="display: flex; align-items: center; gap: 10px;"><div class="typing-indicator"><span></span><span></span><span></span></div><span style="color: #999;">AI Analyst is thinking...</span></div>';
            instance.messageAddNew(loadingHtml, 'System', 'left');

            try {
                let streamingContent = '';
                let hasReceivedContent = false;
                let contentDisplayed = false;
                let loadingRemoved = false;
                let currentStepElement = null; // Track current step status element
                
                // Helper to remove loading indicator
                function removeLoadingIndicator() {
                    if (!loadingRemoved) {
                        try {
                            // Find and remove by class name
                            const loadingElements = document.querySelectorAll('.ai-loading-indicator');
                            loadingElements.forEach(el => {
                                const messageDiv = el.closest('.quikchat-message');
                                if (messageDiv) {
                                    messageDiv.remove();
                                }
                            });
                            loadingRemoved = true;
                            console.log('Loading indicator removed');
                        } catch (e) {
                            console.warn('Failed to remove loading indicator:', e);
                        }
                    }
                }
                
                // Helper to show step status
                function showStepStatus(message, icon = '⏳') {
                    // Remove previous step if exists
                    if (currentStepElement) {
                        try {
                            currentStepElement.remove();
                            console.log('Previous step removed');
                        } catch (e) {
                            console.warn('Failed to remove previous step:', e);
                        }
                    }
                    
                    // Create new step status
                    const stepHtml = `<div style="display: flex; align-items: center; gap: 8px; padding: 4px 8px; background: rgba(13,138,188,0.1); border-radius: 4px;">
                        <span style="font-size: 1.2em;">${icon}</span>
                        <span style="color: #42a5f5; font-size: 0.9em;">${message}</span>
                    </div>`;
                    
                    instance.messageAddNew(stepHtml, 'System', 'left');
                    
                    // Get the newly added element
                    setTimeout(() => {
                        const allMessages = document.querySelectorAll('.quikchat-message');
                        currentStepElement = allMessages[allMessages.length - 1];
                    }, 10);
                }
                
                // Use fetch with SSE
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        message: message,
                        history: conversationHistory.slice(0, -1)  // 🔧 使用独立历史，排除刚添加的当前消息
                    })
                });

                if (!response.ok) {
                    instance.messageAddNew('Network Error: ' + response.statusText, 'System', 'left');
                    return;
                }

                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let buffer = '';
                let lastChunkTime = Date.now();
                
                // Timeout checker
                const timeoutChecker = setInterval(() => {
                    const timeSinceLastChunk = Date.now() - lastChunkTime;
                    if (timeSinceLastChunk > 30000) { // 30 seconds timeout
                        console.warn('Stream timeout detected');
                        clearInterval(timeoutChecker);
                        reader.cancel();
                    }
                }, 5000);
                
                // Helper function to detect and render content
                function renderContent(content) {
                    const looksLikeHTML = content.trim().startsWith('<') && /<[^>]+>/.test(content);
                    if (looksLikeHTML) {
                        return content;
                    } else {
                        try {
                            if (typeof marked !== 'undefined') {
                                return marked.parse(content);
                            }
                        } catch (e) {
                            console.warn('Marked.js not available or parsing failed:', e);
                        }
                        return content;
                    }
                }
                
                // Helper function to display content with typewriter effect
                function displayWithTypewriter(content) {
                    if (contentDisplayed) return; // Prevent duplicate display
                    contentDisplayed = true;
                    
                    // 🔧 重要：将AI的真实回复保存到独立历史中
                    conversationHistory.push({
                        role: 'assistant',
                        content: content  // 保存原始内容（HTML格式）
                    });
                    console.log('✅ AI response saved to conversation history');
                    console.log('💬 Updated conversation history:', conversationHistory);
                    
                    const uniqueId = 'typewriter-' + Date.now();
                    instance.messageAddNew(`<div id="${uniqueId}"></div>`, 'AI Analyst', 'left');
                    
                    setTimeout(() => {
                        const typewriterDiv = document.getElementById(uniqueId);
                        if (typewriterDiv) {
                            const contentLength = content.length;
                            let currentIndex = 0;
                            
                            let speed, interval;
                            if (contentLength < 500) {
                                speed = 15;
                                interval = 20;
                            } else if (contentLength < 2000) {
                                speed = 30;
                                interval = 15;
                            } else {
                                speed = 50;
                                interval = 10;
                            }
                            
                            console.log(`Typewriter: ${contentLength} chars, speed=${speed}, interval=${interval}ms`);

                            const typewriterInterval = setInterval(() => {
                                if (currentIndex < contentLength) {
                                    currentIndex += speed;
                                    typewriterDiv.textContent = content.substring(0, Math.min(currentIndex, contentLength));

                                    // Auto-scroll to keep the message visible
                                    typewriterDiv.scrollIntoView({ behavior: 'smooth', block: 'end' });
                                } else {
                                    const renderedContent = renderContent(content);
                                    typewriterDiv.innerHTML = renderedContent;
                                    typewriterDiv.removeAttribute('id');
                                    clearInterval(typewriterInterval);

                                    // Final scroll to ensure full content is visible
                                    typewriterDiv.scrollIntoView({ behavior: 'smooth', block: 'end' });
                                    console.log('Content rendered');
                                }
                            }, interval);
                        }
                    }, 50);
                }
                
                while (true) {
                    const { done, value } = await reader.read();
                    
                    if (done) {
                        clearInterval(timeoutChecker);
                        break;
                    }
                    
                    lastChunkTime = Date.now();
                    buffer += decoder.decode(value, { stream: true });
                    
                    // Process SSE messages
                    const lines = buffer.split('\n');
                    buffer = lines.pop(); // Keep incomplete line in buffer
                    
                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            try {
                                const data = JSON.parse(line.substring(6));
                                
                                if (data.type === 'status') {
                                    // Remove initial loading indicator on first status
                                    removeLoadingIndicator();
                                    
                                    // Show step status with animated icon
                                    showStepStatus(data.message, '⏳');
                                    console.log('Status:', data.message);
                                } else if (data.type === 'tool_call') {
                                    // Show tool call step
                                    const toolNames = data.tools.join(', ');
                                    showStepStatus(`正在调用: ${toolNames}`, '🔍');
                                    console.log('Calling tools:', data.tools);
                                } else if (data.type === 'content') {
                                    // Remove all status indicators when content starts
                                    removeLoadingIndicator();
                                    if (currentStepElement) {
                                        currentStepElement.remove();
                                        currentStepElement = null;
                                    }
                                    console.log('All indicators removed, starting content');
                                    
                                    streamingContent += data.chunk;
                                    hasReceivedContent = true;
                                } else if (data.type === 'done') {
                                    console.log('Streaming complete, total length:', streamingContent.length);
                                    // Remove any remaining step indicators
                                    if (currentStepElement) {
                                        currentStepElement.remove();
                                        currentStepElement = null;
                                    }
                                    if (streamingContent) {
                                        displayWithTypewriter(streamingContent);
                                    }
                                } else if (data.type === 'error' || data.error) {
                                    // Remove step indicators on error
                                    if (currentStepElement) {
                                        currentStepElement.remove();
                                        currentStepElement = null;
                                    }
                                    instance.messageAddNew('Error: ' + (data.message || data.error), 'System', 'left');
                                }
                            } catch (e) {
                                console.error('Failed to parse SSE data:', e, 'Line:', line);
                            }
                        }
                    }
                }

                // Fallback: if we received content but no 'done' signal, display it anyway
                if (hasReceivedContent && streamingContent && !contentDisplayed) {
                    console.warn('Stream ended without done signal, displaying partial content');
                    displayWithTypewriter(streamingContent);
                } else if (!streamingContent && !contentDisplayed) {
                    instance.messageAddNew('No response received.', 'System', 'left');
                }

            } catch (err) {
                console.error('Chat error:', err);
                instance.messageAddNew('Network Error: ' + err.message, 'System', 'left');
            }
        }, {
            theme: 'quikchat-theme-dark',
            botName: 'AI Analyst',
            userAvatar: 'https://ui-avatars.com/api/?name=User&background=0D8ABC&color=fff',
            botAvatar: 'https://ui-avatars.com/api/?name=AI&background=ff9900&color=fff',
            placeholder: 'Ask about market data...'
        });

        // Add welcome message
        setTimeout(() => {
            const welcomeMsg = "Welcome to LanFund Pro Terminal. Connected to market data stream.";
            chat.messageAddNew(welcomeMsg, 'System', 'left');
            
            // 🔧 将欢迎消息也添加到历史中（作为 assistant 消息）
            conversationHistory.push({
                role: 'assistant',
                content: welcomeMsg
            });
            console.log('💬 Initialized conversation history with welcome message');
        }, 500);

        // Initialize resize functionality
        const resizeHandle = document.getElementById('resize-handle');
        const chatSidebar = document.getElementById('chat-sidebar');
        let isResizing = false;
        let startX = 0;
        let startWidth = 0;

        resizeHandle.addEventListener('mousedown', function(e) {
            isResizing = true;
            startX = e.clientX;
            startWidth = chatSidebar.offsetWidth;
            resizeHandle.classList.add('resizing');
            document.body.style.cursor = 'ew-resize';
            document.body.style.userSelect = 'none';
            e.preventDefault();
        });

        document.addEventListener('mousemove', function(e) {
            if (!isResizing) return;
            
            const dx = startX - e.clientX; // Reversed because we're dragging from the left
            const newWidth = startWidth + dx;
            
            // Constrain width between min and max
            const minWidth = 300;
            const maxWidth = 800;
            const constrainedWidth = Math.min(Math.max(newWidth, minWidth), maxWidth);
            
            chatSidebar.style.width = constrainedWidth + 'px';
        });

        document.addEventListener('mouseup', function() {
            if (isResizing) {
                isResizing = false;
                resizeHandle.classList.remove('resizing');
                document.body.style.cursor = '';
                document.body.style.userSelect = '';
            }
        });
    });

    // Toggle chat sidebar function
    function toggleChatSidebar() {
        const chatSidebar = document.getElementById('chat-sidebar');
        const toggleIcon = document.getElementById('chat-toggle-icon');

        if (chatSidebar.classList.contains('hidden')) {
            chatSidebar.classList.remove('hidden');
            toggleIcon.textContent = '◀';
        } else {
            chatSidebar.classList.add('hidden');
            toggleIcon.textContent = '▶';
        }
    }
    </script>


    <!-- Standard JS for table coloring -->
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        autoColorize();
    });

    function autoColorize() {
        const cells = document.querySelectorAll('.style-table td');
        cells.forEach(cell => {
            const text = cell.textContent.trim();
            const cleanText = text.replace(/[%,亿万手]/g, '');
            const val = parseFloat(cleanText);

            if (!isNaN(val)) {
                if (text.includes('%') || text.includes('涨跌')) {
                    if (text.includes('-')) {
                        cell.classList.add('negative');
                    } else if (val > 0) {
                        cell.classList.add('positive');
                    }
                } else if (text.startsWith('-')) {
                    cell.classList.add('negative');
                } else if (text.startsWith('+')) {
                    cell.classList.add('positive');
                }
            }
        });
    }

    function sortTable(table, columnIndex) {
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        const currentSortCol = table.dataset.sortCol;
        const currentSortDir = table.dataset.sortDir || 'asc';
        let direction = 'asc';

        if (currentSortCol == columnIndex) {
            direction = currentSortDir === 'asc' ? 'desc' : 'asc';
        }
        table.dataset.sortCol = columnIndex;
        table.dataset.sortDir = direction;

        rows.sort((a, b) => {
            const aText = a.cells[columnIndex].textContent.trim();
            const bText = b.cells[columnIndex].textContent.trim();
            const valA = parseValue(aText);
            const valB = parseValue(bText);
            let comparison = 0;
            if (valA > valB) {
                comparison = 1;
            } else if (valA < valB) {
                comparison = -1;
            }
            return direction === 'asc' ? comparison : -comparison;
        });

        tbody.innerHTML = '';
        rows.forEach(row => tbody.appendChild(row));

        table.querySelectorAll('th').forEach(th => {
            th.classList.remove('sorted-asc', 'sorted-desc');
        });
        const headerToUpdate = table.querySelectorAll('th')[columnIndex];
        if (headerToUpdate) {
            headerToUpdate.classList.add(direction === 'asc' ? 'sorted-asc' : 'sorted-desc');
        }
    }

    function parseValue(val) {
        if (val === 'N/A' || val === '--' || val === '---' || val === '') {
            return -Infinity;
        }
        const cleanedVal = val.replace(/%|亿|万|元\/克|手/g, '').replace(/,/g, '');
        const num = parseFloat(cleanedVal);
        return isNaN(num) ? val.toLowerCase() : num;
    }

    function openTab(evt, tabId) {
        // Hide all tab contents
        const allContents = document.querySelectorAll('.tab-content');
        allContents.forEach(content => {
            content.classList.remove('active');
        });

        // Remove active class from all tab buttons
        const allButtons = document.querySelectorAll('.tab-button');
        allButtons.forEach(button => {
            button.classList.remove('active');
        });

        // Show the clicked tab's content and add active class to the button
        document.getElementById(tabId).classList.add('active');
        evt.currentTarget.classList.add('active');
    }

    // Fund Operations Functions
    // 板块分类数据
    const SECTOR_CATEGORIES = {
        "科技": ["人工智能", "半导体", "云计算", "5G", "光模块", "CPO", "F5G", "通信设备", "PCB", "消费电子",
                "计算机", "软件开发", "信创", "网络安全", "IT服务", "国产软件", "计算机设备", "光通信",
                "算力", "脑机接口", "通信", "电子", "光学光电子", "元件", "存储芯片", "第三代半导体",
                "光刻胶", "电子化学品", "LED", "毫米波", "智能穿戴", "东数西算", "数据要素", "国资云",
                "Web3.0", "AIGC", "AI应用", "AI手机", "AI眼镜", "DeepSeek", "TMT", "科技"],
        "医药健康": ["医药生物", "医疗器械", "生物疫苗", "CRO", "创新药", "精准医疗", "医疗服务", "中药",
                    "化学制药", "生物制品", "基因测序", "超级真菌"],
        "消费": ["食品饮料", "白酒", "家用电器", "纺织服饰", "商贸零售", "新零售", "家居用品", "文娱用品",
                "婴童", "养老产业", "体育", "教育", "在线教育", "社会服务", "轻工制造", "新消费",
                "可选消费", "消费", "家电零部件", "智能家居"],
        "金融": ["银行", "证券", "保险", "非银金融", "国有大型银行", "股份制银行", "城商行", "金融"],
        "能源": ["新能源", "煤炭", "石油石化", "电力", "绿色电力", "氢能源", "储能", "锂电池", "电池",
                "光伏设备", "风电设备", "充电桩", "固态电池", "能源", "煤炭开采", "公用事业", "锂矿"],
        "工业制造": ["机械设备", "汽车", "新能源车", "工程机械", "高端装备", "电力设备", "专用设备",
                    "通用设备", "自动化设备", "机器人", "人形机器人", "汽车零部件", "汽车服务",
                    "汽车热管理", "尾气治理", "特斯拉", "无人驾驶", "智能驾驶", "电网设备", "电机",
                    "高端制造", "工业4.0", "工业互联", "低空经济", "通用航空"],
        "材料": ["有色金属", "黄金股", "贵金属", "基础化工", "钢铁", "建筑材料", "稀土永磁", "小金属",
                "工业金属", "材料", "大宗商品", "资源"],
        "军工": ["国防军工", "航天装备", "航空装备", "航海装备", "军工电子", "军民融合", "商业航天",
                "卫星互联网", "航母", "航空机场"],
        "基建地产": ["建筑装饰", "房地产", "房地产开发", "房地产服务", "交通运输", "物流"],
        "环保": ["环保", "环保设备", "环境治理", "垃圾分类", "碳中和", "可控核聚变", "液冷"],
        "传媒": ["传媒", "游戏", "影视", "元宇宙", "超清视频", "数字孪生"],
        "主题": ["国企改革", "一带一路", "中特估", "中字头", "并购重组", "华为", "新兴产业",
                "国家安防", "安全主题", "农牧主题", "农林牧渔", "养殖业", "猪肉", "高端装备"]
    };

    // 基金选择模态框相关变量
    let currentOperation = null;
    let selectedFundsForOperation = [];
    let allFunds = [];

    // 打开基金选择模态框
    async function openFundSelectionModal(operation) {
        currentOperation = operation;
        selectedFundsForOperation = [];

        // 设置标题
        const titles = {
            'sector': '选择要标注板块的基金',
            'unsector': '选择要删除板块的基金',
            'delete': '选择要删除的基金',
            'addToGroup': '选择要加入分组的基金'
        };
        document.getElementById('fundSelectionTitle').textContent = titles[operation] || '选择基金';

        // 获取所有基金列表
        try {
            const response = await fetch('/api/fund/data');
            const fundMap = await response.json();
            allFunds = Object.entries(fundMap).map(([code, data]) => ({
                code,
                name: data.fund_name,
                shares: data.shares || 0,
                sectors: data.sectors || []
            }));

            // 渲染基金列表
            renderFundSelectionList(allFunds);

            // 显示模态框
            document.getElementById('fundSelectionModal').classList.add('active');
        } catch (e) {
            alert('获取基金列表失败: ' + e.message);
        }
    }

    // 渲染基金选择列表
    function renderFundSelectionList(funds) {
        const listContainer = document.getElementById('fundSelectionList');

        // HTML escape function to prevent XSS and syntax errors
        const escapeHtml = (text) => {
            if (!text) return '';
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        };

        // Escape fund code for use in onclick attribute
        const escapeJs = (text) => {
            if (!text) return '';
            return text.replace(/\\/g, '\\\\').replace(/'/g, "\\'");
        };

        listContainer.innerHTML = funds.map(fund => {
            const safeCode = escapeHtml(String(fund.code));
            const safeName = escapeHtml(String(fund.name));
            const safeCodeForJs = escapeJs(String(fund.code));
            const safeSectors = fund.sectors && fund.sectors.length > 0
                ? escapeHtml(fund.sectors.join(', '))
                : '';

            return `
            <div class="sector-item" style="text-align: left; padding: 12px; margin-bottom: 8px; cursor: pointer; display: flex; align-items: center; gap: 10px;"
                 onclick="toggleFundSelection('${safeCodeForJs}', this)">
                <input type="checkbox" class="fund-selection-checkbox" data-code="${safeCode}"
                       style="width: 18px; height: 18px; cursor: pointer;" onclick="event.stopPropagation();">
                <div style="flex: 1;">
                    <div style="font-weight: 600;">${safeCode} - ${safeName}</div>
                    ${(fund.shares || 0) > 0 ? '<span style="color: #8b949e; font-size: var(--font-size-sm);">持仓</span>' : ''}
                    ${safeSectors ? `<span style="color: #8b949e; font-size: var(--font-size-sm);"> 🏷️ ${safeSectors}</span>` : ''}
                </div>
            </div>
            `;
        }).join('');
    }

    // 切换基金选择状态
    function toggleFundSelection(code, element) {
        const checkbox = element.querySelector('.fund-selection-checkbox');
        checkbox.checked = !checkbox.checked;

        if (checkbox.checked) {
            if (!selectedFundsForOperation.includes(code)) {
                selectedFundsForOperation.push(code);
            }
            element.style.backgroundColor = 'rgba(102, 126, 234, 0.2)';
        } else {
            selectedFundsForOperation = selectedFundsForOperation.filter(c => c !== code);
            element.style.backgroundColor = '';
        }
    }

    // 关闭基金选择模态框
    function closeFundSelectionModal() {
        document.getElementById('fundSelectionModal').classList.remove('active');
        currentOperation = null;
        selectedFundsForOperation = [];
    }

    // 确认基金选择
    async function confirmFundSelection() {
        if (selectedFundsForOperation.length === 0) {
            alert('请至少选择一个基金');
            return;
        }

        // 根据操作类型执行相应的操作
        switch (currentOperation) {
            case 'sector':
                closeFundSelectionModal();
                openSectorModal(selectedFundsForOperation);
                return; // 不关闭，等待板块选择
            case 'unsector':
                await removeSector(selectedFundsForOperation);
                break;
            case 'delete':
                await deleteFunds(selectedFundsForOperation);
                break;
            case 'addToGroup':
                const groupId = window.portfolioAddToGroupId;
                if (!groupId) { alert('分组未指定'); return; }
                for (const code of selectedFundsForOperation) {
                    try {
                        const res = await fetch('/api/fund/groups/' + groupId + '/funds', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ code: code })
                        });
                        const data = await res.json();
                        if (!data.success) alert(code + ': ' + (data.message || '添加失败'));
                    } catch (e) { alert(code + ' 添加失败: ' + e.message); }
                }
                closeFundSelectionModal();
                window.portfolioAddToGroupId = null;
                location.reload();
                return;
        }

        closeFundSelectionModal();
    }

    // 基金选择搜索
    document.addEventListener('DOMContentLoaded', function() {
        const searchInput = document.getElementById('fundSelectionSearch');
        if (searchInput) {
            searchInput.addEventListener('input', function() {
                const keyword = this.value.toLowerCase();
                const filtered = allFunds.filter(fund =>
                    fund.code.includes(keyword) || fund.name.toLowerCase().includes(keyword)
                );
                renderFundSelectionList(filtered);
            });
        }
    });

    // 确认对话框相关函数
    let confirmCallback = null;

    function showConfirmDialog(title, message, onConfirm) {
        document.getElementById('confirmTitle').textContent = title;
        document.getElementById('confirmMessage').textContent = message;
        document.getElementById('confirmDialog').classList.add('active');
        confirmCallback = onConfirm;
    }

    function closeConfirmDialog() {
        document.getElementById('confirmDialog').classList.remove('active');
        confirmCallback = null;
    }

    document.getElementById('confirmBtn').addEventListener('click', function() {
        if (confirmCallback) {
            confirmCallback();
        }
        closeConfirmDialog();
    });

    // 添加基金
    async function addFunds() {
        const input = document.getElementById('fundCodesInput');
        const codes = input.value.trim();
        if (!codes) {
            alert('请输入基金代码');
            return;
        }

        try {
            const response = await fetch('/api/fund/add', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ codes })
            });
            const result = await response.json();
            if (result.success) {
                alert(result.message);
                location.reload();
            } else {
                alert(result.message);
            }
        } catch (e) {
            alert('操作失败: ' + e.message);
        }
    }

    // 删除基金
    async function deleteFunds(codes) {
        showConfirmDialog(
            '删除基金',
            `确定要删除 ${codes.length} 只基金吗？`,
            async () => {
                try {
                    const response = await fetch('/api/fund/delete', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ codes: codes.join(',') })
                    });
                    const result = await response.json();
                    if (result.success) {
                        alert(result.message);
                        location.reload();
                    } else {
                        alert(result.message);
                    }
                } catch (e) {
                    alert('操作失败: ' + e.message);
                }
            }
        );
    }

    // 打开板块选择模态框（用于标注板块）
    let selectedCodesForSector = [];

    function openSectorModal(codes) {
        selectedCodesForSector = codes;
        document.getElementById('sectorModal').classList.add('active');
        renderSectorCategories();
    }

    // 删除板块标记
    async function removeSector(codes) {
        showConfirmDialog(
            '删除板块标记',
            `确定要删除 ${codes.length} 只基金的板块标记吗？`,
            async () => {
                try {
                    const response = await fetch('/api/fund/sector/remove', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ codes: codes.join(',') })
                    });
                    const result = await response.json();
                    if (result.success) {
                        alert(result.message);
                        location.reload();
                    } else {
                        alert(result.message);
                    }
                } catch (e) {
                    alert('操作失败: ' + e.message);
                }
            }
        );
    }

    // 板块选择相关
    let selectedSectors = [];

    function renderSectorCategories() {
        // 生成板块分类HTML
        const container = document.getElementById('sectorCategories');
        container.innerHTML = '';

        for (const [category, sectors] of Object.entries(SECTOR_CATEGORIES)) {
            const categoryDiv = document.createElement('div');
            categoryDiv.className = 'sector-category';

            const header = document.createElement('div');
            header.className = 'sector-category-header';
            header.innerHTML = `<span>${category}</span><span>▼</span>`;
            header.onclick = () => {
                const items = categoryDiv.querySelector('.sector-items');
                items.style.display = items.style.display === 'none' ? 'grid' : 'none';
            };

            const itemsDiv = document.createElement('div');
            itemsDiv.className = 'sector-items';

            sectors.forEach(sector => {
                const item = document.createElement('div');
                item.className = 'sector-item';
                item.textContent = sector;
                item.onclick = () => {
                    item.classList.toggle('selected');
                    if (item.classList.contains('selected')) {
                        if (!selectedSectors.includes(sector)) {
                            selectedSectors.push(sector);
                        }
                    } else {
                        selectedSectors = selectedSectors.filter(s => s !== sector);
                    }
                };
                itemsDiv.appendChild(item);
            });

            categoryDiv.appendChild(header);
            categoryDiv.appendChild(itemsDiv);
            container.appendChild(categoryDiv);
        }

        selectedSectors = [];
        document.getElementById('sectorModal').classList.add('active');
    }

    function closeSectorModal() {
        document.getElementById('sectorModal').classList.remove('active');
        selectedSectors = [];
    }

    async function confirmSector() {
        if (selectedSectors.length === 0) {
            alert('请至少选择一个板块');
            return;
        }

        try {
            const response = await fetch('/api/fund/sector', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ codes: selectedCodesForSector.join(','), sectors: selectedSectors })
            });
            const result = await response.json();
            closeSectorModal();
            if (result.success) {
                alert(result.message);
                location.reload();
            } else {
                alert(result.message);
            }
        } catch (e) {
            closeSectorModal();
            alert('操作失败: ' + e.message);
        }
    }

    // ==================== 新增功能：份额管理和文件操作 ====================

    // 当前正在编辑份额的基金代码
    let currentSharesFundCode = null;

    // 获取基金份额（从内存或DOM）- 必须在 openSharesModal 之前定义
    window.getFundShares = function(fundCode) {
        // 先从全局存储获取
        if (window.fundSharesData && window.fundSharesData[fundCode]) {
            return window.fundSharesData[fundCode];
        }
        return 0;
    };

    // 更新份额按钮状态 - 必须在 openSharesModal 之前定义
    function updateSharesButton(fundCode, shares) {
        const button = document.getElementById('sharesBtn_' + fundCode);
        if (button) {
            if (shares > 0) {
                button.textContent = '修改';
                button.style.background = '#10b981';
            } else {
                button.textContent = '设置';
                button.style.background = '#3b82f6';
            }
        }
    }

    // 更新弹窗内“持仓份额”计算结果（持有份额 × 持仓成本）
    window.updateSharesModalResult = function() {
        const holdingInput = document.getElementById('sharesModalHoldingUnits');
        const costInput = document.getElementById('sharesModalCostPerUnit');
        const resultEl = document.getElementById('sharesModalResult');
        if (!holdingInput || !costInput || !resultEl) return;
        const holding = parseFloat(holdingInput.value) || 0;
        const cost = parseFloat(costInput.value) || 0;
        resultEl.textContent = (holding * cost).toLocaleString('zh-CN', {{ minimumFractionDigits: 2, maximumFractionDigits: 2 }});
    };

    // 打开份额设置弹窗（持有份额 × 持仓成本 = 持仓份额）
    window.openSharesModal = function(fundCode) {
        currentSharesFundCode = fundCode;
        const modal = document.getElementById('sharesModal');
        const fundCodeDisplay = document.getElementById('sharesModalFundCode');
        const holdingInput = document.getElementById('sharesModalHoldingUnits');
        const costInput = document.getElementById('sharesModalCostPerUnit');
        const sharesValue = window.getFundShares(fundCode) || 0;
        if (fundCodeDisplay) fundCodeDisplay.textContent = fundCode;
        if (holdingInput && costInput) {
            const hold = window.fundHoldingData && window.fundHoldingData[fundCode];
            const units = hold ? hold.holding_units : sharesValue;
            const cost = hold ? hold.cost_per_unit : 1;
            holdingInput.value = (parseFloat(units) || 0) > 0 ? (parseFloat(units) || 0).toFixed(2) : '';
            costInput.value = (parseFloat(cost) || 0) > 0 ? (parseFloat(cost) || 1).toFixed(4) : '';
            window.updateSharesModalResult();
        }
        const header = modal ? modal.querySelector('.sector-modal-header') : null;
        if (header) header.textContent = sharesValue > 0 ? '修改持仓份额' : '设置持仓份额';
        if (modal) modal.classList.add('active');
        const focusEl = holdingInput || costInput || document.getElementById('sharesModalInput');
        setTimeout(() => focusEl && focusEl.focus(), 100);
    };

    // 关闭份额设置弹窗
    window.closeSharesModal = function() {
        const modal = document.getElementById('sharesModal');
        if (modal) modal.classList.remove('active');
        currentSharesFundCode = null;
    };

    // 确认份额设置（提交 持有份额、持仓成本）
    window.confirmShares = async function() {
        if (!currentSharesFundCode) {
            alert('基金代码无效');
            return;
        }
        const holdingInput = document.getElementById('sharesModalHoldingUnits');
        const costInput = document.getElementById('sharesModalCostPerUnit');
        let holding_units, cost_per_unit, shares;
        if (holdingInput && costInput) {
            holding_units = parseFloat(holdingInput.value) || 0;
            cost_per_unit = parseFloat(costInput.value) || 0;
            if (holding_units < 0 || cost_per_unit < 0) {
                alert('持有份额与持仓成本不能为负数');
                return;
            }
            if (cost_per_unit === 0) cost_per_unit = 1;
            shares = holding_units * cost_per_unit;
        } else {
            shares = parseFloat(document.getElementById('sharesModalInput').value) || 0;
            if (shares < 0) { alert('份额不能为负数'); return; }
            holding_units = shares;
            cost_per_unit = 1;
        }
        try {
            const body = {{ code: currentSharesFundCode }};
            if (holdingInput && costInput) {{ body.holding_units = holding_units; body.cost_per_unit = cost_per_unit; }}
            else {{ body.shares = shares; }}
            const response = await fetch('/api/fund/shares', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify(body)
            }});
            const result = await response.json();
            if (result.success) {{
                if (!window.fundSharesData) window.fundSharesData = {{}};
                window.fundSharesData[currentSharesFundCode] = result.shares != null ? result.shares : shares;
                if (!window.fundHoldingData) window.fundHoldingData = {{}};
                window.fundHoldingData[currentSharesFundCode] = {{ holding_units: result.holding_units != null ? result.holding_units : holding_units, cost_per_unit: result.cost_per_unit != null ? result.cost_per_unit : cost_per_unit }};
                updateSharesButton(currentSharesFundCode, window.fundSharesData[currentSharesFundCode]);
                calculatePositionSummary();
                closeSharesModal();
            }} else {{
                alert(result.message);
            }}
        }} catch (e) {{
            alert('更新份额失败: ' + e.message);
        }}
    };

    // 下载fund_map.json
    window.updateShares = async function(fundCode, shares) {
        if (!fundCode) {
            alert('基金代码无效');
            return;
        }

        try {
            const sharesValue = parseFloat(shares) || 0;
            const response = await fetch('/api/fund/shares', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code: fundCode, shares: sharesValue })
            });
            const result = await response.json();
            if (result.success) {
                // 更新全局份额数据
                if (!window.fundSharesData) {
                    window.fundSharesData = {};
                }
                window.fundSharesData[fundCode] = sharesValue;

                // 更新按钮状态
                updateSharesButton(fundCode, sharesValue);
                // 更新成功后重新计算持仓统计
                calculatePositionSummary();
            } else {
                alert(result.message);
            }
        } catch (e) {
            alert('更新份额失败: ' + e.message);
        }
    };

    // 下载fund_map.json
    window.downloadFundMap = function() {
        window.location.href = '/api/fund/download';
    };

    // 上传fund_map.json
    window.uploadFundMap = async function(file) {
        if (!file) {
            alert('请选择文件');
            return;
        }

        if (!file.name.endsWith('.json')) {
            alert('只支持JSON文件');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/api/fund/upload', {
                method: 'POST',
                body: formData
            });
            const result = await response.json();
            if (result.success) {
                alert(result.message);
                location.reload();
            } else {
                alert(result.message);
            }
        } catch (e) {
            alert('上传失败: ' + e.message);
        }
    };

    // 计算并显示持仓统计
    async function calculatePositionSummary() {
        let totalValue = 0;
        let estimatedGain = 0;
        let actualGain = 0;
        let settledValue = 0;
        const today = new Date().toISOString().split('T')[0];

        // Get fund data map for holdings cards
        let fundDataMap = {};
        try {
            const response = await fetch('/api/fund/data');
            if (response.ok) {
                fundDataMap = await response.json();
            }
        } catch (e) {
            console.warn('Failed to fetch fund data map:', e);
        }

        // Collect held funds data for cards
        const heldFundsData = [];
        // Collect fund details for summary table
        const fundDetailsData = [];

        // 遍历所有基金行
        const fundRows = document.querySelectorAll('.style-table tbody tr');
        fundRows.forEach(row => {
            const cells = row.querySelectorAll('td');
            if (cells.length < 9) return;

            // 获取基金代码
            const codeCell = cells[1]; // 第二列是基金代码（第一列是复选框）
            const fundCode = codeCell.textContent.trim();

            // 获取份额数据（从全局数据对象）
            const shares = window.fundSharesData && window.fundSharesData[fundCode] ? parseFloat(window.fundSharesData[fundCode]) : 0;
            if (shares <= 0) return;  // 只处理有份额的基金

            try {
                // 解析净值 "1.234(2025-02-02)"
                const netValueText = cells[4].textContent.trim();
                const netValueMatch = netValueText.match(/([0-9.]+)\(([0-9-]+)\)/);
                if (!netValueMatch) return;

                const netValue = parseFloat(netValueMatch[1]);
                let netValueDate = netValueMatch[2];

                // 处理净值日期格式：API可能返回"MM-DD"或"YYYY-MM-DD"
                // 如果是"MM-DD"格式，添加当前年份
                if (netValueDate.length === 5) {  // 格式为"MM-DD"
                    const currentYear = new Date().getFullYear();
                    netValueDate = `${currentYear}-${netValueDate}`;
                }

                // 解析估值增长率
                const estimatedGrowthText = cells[5].textContent.trim();
                const estimatedGrowth = estimatedGrowthText !== 'N/A' ?
                    parseFloat(estimatedGrowthText.replace('%', '')) : 0;

                // 解析日涨幅
                const dayGrowthText = cells[6].textContent.trim();
                const dayGrowth = dayGrowthText !== 'N/A' ?
                    parseFloat(dayGrowthText.replace('%', '')) : 0;

                // 解析连涨/跌
                const consecutiveText = cells[7].textContent.trim();

                // 解析近30天
                const monthlyText = cells[8].textContent.trim();

                // 第一：分基金涨跌明细-持仓金额 由「持仓金额-修改」中的持有份额与持仓成本计算得出
                if (!window.fundHoldingData) window.fundHoldingData = {{}};
                let hold = window.fundHoldingData[fundCode];
                let holding_units = hold ? (parseFloat(hold.holding_units) || 0) : shares;
                let cost_per_unit = hold ? (parseFloat(hold.cost_per_unit) || 1) : 1;
                if (!hold) window.fundHoldingData[fundCode] = {{ holding_units: holding_units, cost_per_unit: cost_per_unit }};
                const positionAmount = netValue * holding_units;  // 持仓金额 = 净值 × 持有份额（来自修改）

                // 有份额的基金纳入持仓卡片数据（使用同一持仓金额口径）
                heldFundsData.push({
                        code: fundCode,
                        name: fundDataMap[fundCode]?.fund_name || 'Unknown',
                        sectors: fundDataMap[fundCode]?.sectors || [],
                        netValue: netValue,
                        netValueDate: netValueDate,
                        estimatedGrowth: estimatedGrowth,
                        dayGrowth: dayGrowth,
                        consecutive: consecutiveText,
                        monthly: monthlyText,
                        shares: shares,
                        positionValue: positionAmount
                    });

                if (shares > 0) {
                    // 计算预估涨跌、实际涨跌（均基于同一持仓金额：净值×持有份额）
                    const fundEstimatedGain = positionAmount * estimatedGrowth / 100;
                    estimatedGain += fundEstimatedGain;
                    let fundActualGain = 0;
                    if (netValueDate === today) {
                        fundActualGain = positionAmount * dayGrowth / 100;
                        actualGain += fundActualGain;
                        settledValue += positionAmount;
                    }

                    // Collect fund details for summary table（累计收益=(净值-持仓成本)×持有份额）
                    const fundName = cells[2].textContent.trim();
                    const cumulativeReturn = (netValue - cost_per_unit) * holding_units;
                    // 显示持仓金额：扣除未到账加仓、加上未到账减仓（与修改页一致）
                    let pendingAddSum = 0;
                    let pendingReduceSum = 0;
                    try {{
                        const pendingRaw = localStorage.getItem('lan_fund_pending_adds');
                        const pendingList = pendingRaw ? JSON.parse(pendingRaw) : [];
                        const stillPending = pendingList.filter(function (p) {{ return p.settlementDate > today; }});
                        if (stillPending.length !== pendingList.length) localStorage.setItem('lan_fund_pending_adds', JSON.stringify(stillPending));
                        pendingAddSum = stillPending.filter(function (p) {{ return p.fundCode === fundCode; }}).reduce(function (s, p) {{ return s + (p.amount || 0); }}, 0);
                    }} catch (e) {{}}
                    try {{
                        const reduceRaw = localStorage.getItem('lan_fund_pending_reduces');
                        const reduceList = reduceRaw ? JSON.parse(reduceRaw) : [];
                        const stillPendingReduce = reduceList.filter(function (p) {{ return p.settlementDate > today; }});
                        if (stillPendingReduce.length !== reduceList.length) localStorage.setItem('lan_fund_pending_reduces', JSON.stringify(stillPendingReduce));
                        pendingReduceSum = stillPendingReduce.filter(function (p) {{ return p.fundCode === fundCode; }}).reduce(function (s, p) {{ return s + (p.amount || 0); }}, 0);
                    }} catch (e) {{}}
                    const displayPositionAmount = Math.max(0, positionAmount - pendingAddSum + pendingReduceSum);
                    totalValue += displayPositionAmount;
                    fundDetailsData.push({
                        code: fundCode,
                        name: fundName,
                        shares: shares,
                        positionValue: positionAmount,
                        positionAmount: displayPositionAmount,
                        netValue: netValue,
                        holding_units: holding_units,
                        cost_per_unit: cost_per_unit,
                        cumulativeReturn: cumulativeReturn,
                        estimatedGain: fundEstimatedGain,
                        estimatedGainPct: estimatedGrowth,
                        actualGain: fundActualGain,
                        actualGainPct: netValueDate === today ? dayGrowth : 0
                    });
                }
            } catch (e) {
                console.warn('解析基金数据失败:', fundCode, e);
            }
        });

        // Update Asset Hero Section
        const assetHero = document.getElementById('assetHero');
        if (assetHero) {
            if (totalValue > 0) {
                assetHero.style.display = 'block';

            // Update total value
            document.getElementById('heroTotalValue').textContent =
                '¥' + totalValue.toLocaleString('zh-CN', {minimumFractionDigits: 2, maximumFractionDigits: 2});

            // Update estimated gain
            const estGainPct = totalValue > 0 ? (estimatedGain / totalValue * 100) : 0;
            const estSign = estimatedGain >= 0 ? '+' : '-';
            const estClass = estimatedGain >= 0 ? 'positive' : 'negative';
            document.getElementById('heroEstimatedGain').textContent =
                estSign + '¥' + Math.abs(estimatedGain).toLocaleString('zh-CN', {minimumFractionDigits: 2, maximumFractionDigits: 2});
            document.getElementById('heroEstimatedGain').className = 'asset-metric-value ' + estClass;
            document.getElementById('heroEstimatedGainPct').textContent = estSign + Math.abs(estGainPct).toFixed(2) + '%';

            // Update actual gain
            if (settledValue > 0) {
                const actGainPct = (actualGain / settledValue * 100);
                const actSign = actualGain >= 0 ? '+' : '-';
                const actClass = actualGain >= 0 ? 'positive' : 'negative';
                document.getElementById('heroActualGain').textContent =
                    actSign + '¥' + Math.abs(actualGain).toLocaleString('zh-CN', {minimumFractionDigits: 2, maximumFractionDigits: 2});
                document.getElementById('heroActualGain').className = 'asset-metric-value ' + actClass;
                document.getElementById('heroActualGainPct').textContent = actSign + Math.abs(actGainPct).toFixed(2) + '% (Settled)';
            } else {
                document.getElementById('heroActualGain').textContent = '¥0.00';
                document.getElementById('heroActualGain').className = 'asset-metric-value neutral';
                document.getElementById('heroActualGainPct').textContent = '0.00% (Settled)';
            }
            } else {
                assetHero.style.display = 'none';
            }
        }

        // Generate and populate holdings cards
        if (heldFundsData.length > 0) {
            const cardsHTML = heldFundsData.map(fund => {
                const sectorTags = fund.sectors && fund.sectors.length > 0
                    ? `<span style="color: #8b949e; font-size: var(--font-size-sm);"> 🏷️ ${fund.sectors.join(', ')}</span>`
                    : '';
                const estClass = fund.estimatedGrowth >= 0 ? 'up' : 'down';
                const dayClass = fund.dayGrowth >= 0 ? 'up' : 'down';

                return `
                <div class="fund-glass-card" data-code="${fund.code}">
                    <div class="card-header">
                        <div>
                            <div class="card-title">${fund.name}</div>
                            <div class="card-code">${fund.code} ${sectorTags}</div>
                        </div>
                        <div class="card-badge">⭐</div>
                    </div>
                    <div class="card-main-data">
                        <span class="est-pct ${estClass}">${fund.estimatedGrowth >= 0 ? '+' : '-'}${(fund.estimatedGrowth >= 0 ? fund.estimatedGrowth : Math.abs(fund.estimatedGrowth)).toFixed(2)}%</span>
                        <span style="font-size: var(--font-size-sm); color: var(--text-dim)">实时估值</span>
                    </div>
                    <div class="card-details">
                        <div class="detail-item">持仓金额 <b>¥${fund.positionValue.toLocaleString('zh-CN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</b></div>
                        <div class="detail-item">估值盈亏 <b class="${estClass}">${fund.estimatedGrowth >= 0 ? '+' : '-'}¥${Math.abs(fund.positionValue * fund.estimatedGrowth / 100).toLocaleString('zh-CN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</b></div>
                        <div class="detail-item">当前净值 <b>${fund.netValue.toFixed(4)}</b></div>
                        <div class="detail-item">日涨幅 <b class="${dayClass}">${fund.dayGrowth >= 0 ? '+' : '-'}${(fund.dayGrowth >= 0 ? fund.dayGrowth : Math.abs(fund.dayGrowth)).toFixed(2)}%</b></div>
                    </div>
                </div>
                `;
            }).join('');

            const holdingsSection = `
            <div style="margin-bottom: 24px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                    <div style="font-size: var(--font-size-xl); font-weight: 600; color: var(--text-main);">💎 核心持仓</div>
                    <div style="font-size: var(--font-size-md); color: var(--text-dim); font-family: var(--font-mono);">${heldFundsData.length} 只</div>
                </div>
                <div class="holdings-grid">
                    ${cardsHTML}
                </div>
            </div>
            `;

            document.getElementById('holdingsCardsContainer').innerHTML = holdingsSection;
        } else {
            document.getElementById('holdingsCardsContainer').innerHTML = '';
        }

        // 显示或隐藏持仓统计区域
        const summaryDiv = document.getElementById('positionSummary');
        const fundDetailsDiv = document.getElementById('fundDetailsSummary');
        if (!summaryDiv) {
            // positionSummary element not found (sidebar layout), skip old layout summary
            console.log('positionSummary element not found - using sidebar layout');
        } else if (totalValue > 0) {
            summaryDiv.style.display = 'block';

            // 更新总持仓金额
            const totalValueEl = document.getElementById('totalValue');
            if (totalValueEl) {
                totalValueEl.textContent =
                    '¥' + totalValue.toLocaleString('zh-CN', {minimumFractionDigits: 2, maximumFractionDigits: 2});
            }

            // 更新预估涨跌
            const estGainPct = totalValue > 0 ? (estimatedGain / totalValue * 100) : 0;
            const estColor = estimatedGain >= 0 ? '#ef4444' : '#10b981';
            const estimatedGainEl = document.getElementById('estimatedGain');
            if (estimatedGainEl) {
                estimatedGainEl.innerHTML =
                    `<span class="sensitive-value ${estimatedGain >= 0 ? 'positive' : 'negative'}" style="color: ${estColor}"><span class="real-value">¥${Math.abs(estimatedGain).toLocaleString('zh-CN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</span><span class="hidden-value">****</span></span><span id="estimatedGainPct" style="color: ${estColor}"> (${estGainPct.toFixed(2)}%)</span>`;
            }

            // 更新实际涨跌
            const actualGainEl = document.getElementById('actualGain');
            if (actualGainEl) {
                if (settledValue > 0) {
                    const actGainPct = (actualGain / settledValue * 100);
                    const actColor = actualGain >= 0 ? '#ef4444' : '#10b981';
                    actualGainEl.innerHTML =
                        `<span class="sensitive-value ${actualGain >= 0 ? 'positive' : 'negative'}" style="color: ${actColor}"><span class="real-value">${actualGain >= 0 ? '+' : '-'}¥${Math.abs(actualGain).toLocaleString('zh-CN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</span><span class="hidden-value">****</span></span><span id="actualGainPct" style="color: ${actColor}"> (${actualGain >= 0 ? '+' : '-'}${Math.abs(actGainPct).toFixed(2)}%)</span>`;
                } else {
                    actualGainEl.innerHTML =
                        '<span style="color: var(--text-dim);">净值未更新</span>';
                }
            }

            // 持仓统计·累计收益：明细合计 - 修正金额，修正计算后赋值存储，所有展示共用此值
            const totalCumulativeReturn = fundDetailsData.reduce((sum, f) => sum + (f.cumulativeReturn || 0), 0);
            const cumulativeCorrection = parseFloat(localStorage.getItem('lan_fund_cumulative_correction') || '0') || 0;
            const positionSummaryCumulativeReturn = totalCumulativeReturn - cumulativeCorrection;
            window.positionSummaryCumulativeReturn = positionSummaryCumulativeReturn;

            const cumulativeGainEl = document.getElementById('cumulativeGain');
            if (cumulativeGainEl) {{
                const sensSpan = cumulativeGainEl.querySelector('.sensitive-value');
                if (sensSpan) sensSpan.className = positionSummaryCumulativeReturn >= 0 ? 'sensitive-value positive' : 'sensitive-value negative';
                const realSpan = cumulativeGainEl.querySelector('.real-value');
                if (realSpan) realSpan.textContent = (positionSummaryCumulativeReturn >= 0 ? '+' : '-') + '¥' + Math.abs(positionSummaryCumulativeReturn).toLocaleString('zh-CN', {{ minimumFractionDigits: 2, maximumFractionDigits: 2 }});
            }}
            const summaryCumulativeGain = document.getElementById('summaryCumulativeGain');
            if (summaryCumulativeGain) {{
                summaryCumulativeGain.textContent = (positionSummaryCumulativeReturn >= 0 ? '+' : '-') + '¥' + Math.abs(positionSummaryCumulativeReturn).toLocaleString('zh-CN', {{ minimumFractionDigits: 2, maximumFractionDigits: 2 }});
                summaryCumulativeGain.className = 'summary-value ' + (positionSummaryCumulativeReturn > 0 ? 'positive' : (positionSummaryCumulativeReturn < 0 ? 'negative' : ''));
            }}

            // 填充分基金明细表格
            if (fundDetailsDiv && fundDetailsData.length > 0) {
                fundDetailsDiv.style.display = 'block';
                const tableBody = document.getElementById('fundDetailsTableBody');
                if (tableBody) {
                    tableBody.innerHTML = fundDetailsData.map(fund => {
                        const estColor = fund.estimatedGain >= 0 ? '#f44336' : '#4caf50';
                        const actColor = fund.actualGain >= 0 ? '#f44336' : '#4caf50';
                        const cumColor = (fund.cumulativeReturn || 0) >= 0 ? '#f44336' : '#4caf50';
                        const estSign = fund.estimatedGain >= 0 ? '+' : '-';
                        const actSign = fund.actualGain >= 0 ? '+' : '-';
                        const cumSign = (fund.cumulativeReturn || 0) >= 0 ? '+' : '-';
                        return `
                            <tr style="border-bottom: 1px solid var(--border);">
                                <td style="padding: 10px; text-align: center; white-space: nowrap; vertical-align: middle; color: var(--accent); font-weight: 500;">${fund.code}</td>
                                <td style="padding: 10px; text-align: center; white-space: nowrap; vertical-align: middle; color: var(--text-main); min-width: 120px;">${fund.name}</td>
                                <td style="padding: 10px; text-align: center; white-space: nowrap; vertical-align: middle; font-family: var(--font-mono); font-weight: 600;">¥${(fund.positionAmount != null ? fund.positionAmount : fund.positionValue).toLocaleString('zh-CN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                                <td style="padding: 10px; text-align: center; white-space: nowrap; vertical-align: middle; font-family: var(--font-mono); color: ${estColor}; font-weight: 500;">${estSign}¥${Math.abs(fund.estimatedGain).toLocaleString('zh-CN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                                <td style="padding: 10px; text-align: center; white-space: nowrap; vertical-align: middle; font-family: var(--font-mono); color: ${estColor}; font-weight: 500;">${estSign}${Math.abs(fund.estimatedGainPct).toFixed(2)}%</td>
                                <td style="padding: 10px; text-align: center; white-space: nowrap; vertical-align: middle; font-family: var(--font-mono); color: ${actColor}; font-weight: 500;">${actSign}¥${Math.abs(fund.actualGain).toLocaleString('zh-CN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                                <td style="padding: 10px; text-align: center; white-space: nowrap; vertical-align: middle; font-family: var(--font-mono); color: ${actColor}; font-weight: 500;">${actSign}${Math.abs(fund.actualGainPct).toFixed(2)}%</td>
                                <td style="padding: 10px; text-align: center; white-space: nowrap; vertical-align: middle; font-family: var(--font-mono); color: ${cumColor}; font-weight: 500;">${cumSign}¥${Math.abs(fund.cumulativeReturn || 0).toLocaleString('zh-CN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                                <td style="padding: 10px; text-align: center; vertical-align: middle;">
                                    <button type="button" class="btn-add-position" onclick="openAddPositionModal('${fund.code}')" style="margin-right: 6px; padding: 4px 10px; font-size: var(--font-size-sm); border-radius: 6px; border: 1px solid var(--accent); background: rgba(59, 130, 246, 0.15); color: var(--accent); cursor: pointer;">加仓</button>
                                    <button type="button" class="btn-reduce-position" onclick="openReducePositionModal('${fund.code}')" style="padding: 4px 10px; font-size: var(--font-size-sm); border-radius: 6px; border: 1px solid #94a3b8; background: rgba(148, 163, 184, 0.15); color: var(--text-main); cursor: pointer;">减仓</button>
                                </td>
                            </tr>
                        `;
                    }).join('');
                }
            } else if (fundDetailsDiv) {
                fundDetailsDiv.style.display = 'none';
            }
        } else {
            summaryDiv.style.display = 'none';
            if (fundDetailsDiv) {
                fundDetailsDiv.style.display = 'none';
            }
        }
    }

    // 页面加载时加载份额数据并计算持仓统计
    async function loadSharesData() {
        try {
            // 从后端API获取用户的基金数据（包含份额）
            const response = await fetch('/api/fund/data');
            if (response.ok) {
                const fundData = await response.json();

                window.fundSharesData = {};
                window.fundHoldingData = {};
                for (const [code, data] of Object.entries(fundData)) {
                    const shares = parseFloat(data.shares) || 0;
                    window.fundSharesData[code] = shares;
                    if (data.holding_units != null && data.cost_per_unit != null) {
                        window.fundHoldingData[code] = {{ holding_units: parseFloat(data.holding_units) || 0, cost_per_unit: parseFloat(data.cost_per_unit) || 1 }};
                    } else {
                        window.fundHoldingData[code] = {{ holding_units: shares, cost_per_unit: 1 }};
                    }
                }

                // 等待DOM加载完成后更新按钮状态
                updateAllSharesButtons();

                // 计算持仓统计
                calculatePositionSummary();
            }
        } catch (e) {
            console.error('加载份额数据失败:', e);
            // 即使加载失败，也尝试计算持仓统计
            calculatePositionSummary();
        }
    }

    // 更新所有份额按钮状态（在DOM加载后调用）
    function updateAllSharesButtons() {
        if (!window.fundSharesData) return;

        for (const [code, shares] of Object.entries(window.fundSharesData)) {
            updateSharesButton(code, shares);
        }
    }

    // 板块搜索功能
    document.addEventListener('DOMContentLoaded', function() {
        const searchInput = document.getElementById('sectorSearch');
        if (searchInput) {
            searchInput.addEventListener('input', function() {
                const keyword = this.value.toLowerCase();
                const categories = document.querySelectorAll('.sector-category');

                categories.forEach(category => {
                    const items = category.querySelectorAll('.sector-item');
                    let hasVisible = false;

                    items.forEach(item => {
                        const text = item.textContent.toLowerCase();
                        if (text.includes(keyword)) {
                            item.style.display = 'block';
                            hasVisible = true;
                        } else {
                            item.style.display = 'none';
                        }
                    });

                    category.style.display = hasVisible || keyword === '' ? 'block' : 'none';
                });
            });
        }

        // 初始化 - 加载份额数据
        loadSharesData();

        // 份额弹窗 - 点击外部关闭
        const sharesModal = document.getElementById('sharesModal');
        if (sharesModal) {
            sharesModal.addEventListener('click', function(e) {
                if (e.target === sharesModal) {
                    closeSharesModal();
                }
            });

            // 份额弹窗 - 回车键确认（持有份额、持仓成本输入框）
            ['sharesModalHoldingUnits', 'sharesModalCostPerUnit', 'sharesModalInput'].forEach(function(id) {
                const el = document.getElementById(id);
                if (el) el.addEventListener('keypress', function(e) {{ if (e.key === 'Enter') confirmShares(); }});
            });
        }
    });
    </script>
    """
