<template>
  <div class="app-wrapper">
    <!-- 顶部标题栏 -->
    <header class="app-header">
      <div class="header-icon">⚖️</div>
      <div class="header-text">
        <h1>讨薪帮手</h1>
        <p>免费法律咨询 · 专为农民工服务</p>
      </div>
      <div class="header-badge">免费</div>
    </header>

    <!-- 主内容区 -->
    <main class="app-main">

      <!-- 欢迎引导页 -->
      <transition name="fade">
        <section v-if="currentStep === 'welcome'" class="welcome-screen">
          <div class="welcome-hero">
            <div class="hero-emoji">🏗️</div>
            <h2>工资被拖欠了？</h2>
            <p class="hero-sub">我来帮你！只需和我说说情况，<br>我帮你分析怎么要回工资。</p>
          </div>
          <div class="welcome-promises">
            <div class="promise-item">✅ 完全免费，不收任何费用</div>
            <div class="promise-item">✅ 帮你生成维权申请书</div>
          </div>
          <button class="btn-start" @click="startChat">
            开始咨询 →
          </button>
          <p class="disclaimer">本工具仅供参考，不构成正式法律意见</p>
        </section>
      </transition>

      <!-- 对话界面 -->
      <transition name="fade">
        <section v-if="currentStep === 'chat'" class="chat-screen">

          <!-- 消息列表 -->
          <div class="messages-container" ref="messagesContainer">
            <div
              v-for="(msg, index) in messages"
              :key="index"
              class="message-row"
              :class="msg.role"
            >
              <!-- AI头像 -->
              <div v-if="msg.role === 'assistant'" class="avatar assistant-avatar">⚖️</div>

              <div class="bubble" :class="msg.role">
                <div class="bubble-text" v-html="formatMessage(msg.content)"></div>
                <!-- 快捷回复按钮 -->
                <div v-if="msg.quickReplies && msg.quickReplies.length" class="quick-replies">
                  <button
                    v-for="reply in msg.quickReplies"
                    :key="reply"
                    class="quick-reply-btn"
                    @click="sendQuickReply(reply)"
                    :disabled="isLoading"
                  >
                    {{ reply }}
                  </button>
                </div>
              </div>

              <!-- 用户头像 -->
              <div v-if="msg.role === 'user'" class="avatar user-avatar">👷</div>
            </div>

            <!-- 加载中动画 -->
            <div v-if="isLoading" class="message-row assistant">
              <div class="avatar assistant-avatar">⚖️</div>
              <div class="bubble assistant loading-bubble">
                <span class="dot"></span>
                <span class="dot"></span>
                <span class="dot"></span>
              </div>
            </div>
          </div>

          <!-- 提取信息进度条（可选显示） -->
          <transition name="slide-up">
            <div v-if="extractedInfo && hasExtractedData" class="info-panel">
              <div class="info-panel-header" @click="showInfoPanel = !showInfoPanel">
                <span>📋 已收集信息 ({{ extractedCount }}/{{ totalFields }})</span>
                <span class="toggle-icon">{{ showInfoPanel ? '▲' : '▼' }}</span>
              </div>
              <transition name="collapse">
                <div v-if="showInfoPanel" class="info-panel-body">
                  <div v-for="(val, key) in extractedInfo" :key="key" class="info-row" v-if="val">
                    <span class="info-label">{{ fieldLabels[key] }}</span>
                    <span class="info-value">{{ val }}</span>
                  </div>
                </div>
              </transition>
            </div>
          </transition>

          <!-- 输入区 -->
          <div class="input-area">
            <div class="input-row">
              <textarea
                ref="inputBox"
                v-model="userInput"
                class="input-box"
                placeholder="用自己的话说情况，比如：我叫xxx，在xx地点为xx单位工作，老板拖欠我3个月工资，一直不给..."
                color.placeholder="gray"
                rows="2"
                :disabled="isLoading"
                @keydown.enter.exact.prevent="sendMessage"
                @input="autoResize"
              ></textarea>
              <button
                class="send-btn"
                @click="sendMessage"
                :disabled="isLoading || !userInput.trim()"
              >
                <span v-if="!isLoading">发送</span>
                <span v-else>...</span>
              </button>
            </div>
            <!-- 生成申请书按钮（信息足够时显示） -->
            <transition name="slide-up">
              <button
                v-if="canGenerateDoc"
                class="btn-generate"
                @click="generateDocument"
                :disabled="isGenerating"
              >
                {{ isGenerating ? '生成中...' : '📄 生成维权申请书' }}
              </button>
            </transition>
          </div>

        </section>
      </transition>

      <!-- 申请书预览页 -->
      <transition name="fade">
        <section v-if="currentStep === 'document'" class="document-screen">
          <div class="doc-header">
            <button class="btn-back" @click="currentStep = 'chat'">← 返回</button>
            <h2>维权申请书</h2>
            <button class="btn-copy" @click="copyDocument">📋 复制</button>
          </div>
          <div class="document-body" ref="documentBody">
            <pre class="document-text">{{ generatedDocument }}</pre>
          </div>
          <div class="doc-actions">
            <button class="btn-secondary" @click="currentStep = 'chat'">继续完善信息</button>
            <button class="btn-primary" @click="downloadDocument">⬇️ 下载文件</button>
          </div>
          <p class="doc-disclaimer">⚠️ 请在专业律师或法律援助机构指导下使用此申请书</p>
        </section>
      </transition>

    </main>

    <!-- 底部导航 -->
    <nav v-if="currentStep === 'chat'" class="bottom-nav">
      <button class="nav-item" @click="showHelp = true">
        <span class="nav-icon">❓</span>
        <span>帮助</span>
      </button>
      <button class="nav-item" @click="restartChat">
        <span class="nav-icon">🔄</span>
        <span>重新开始</span>
      </button>
      <button class="nav-item" @click="showLegalAid">
        <span class="nav-icon">📞</span>
        <span>法律援助</span>
      </button>
    </nav>

    <!-- 帮助弹窗 -->
    <transition name="modal">
      <div v-if="showHelp" class="modal-overlay" @click.self="showHelp = false">
        <div class="modal-box">
          <h3>💡 使用提示</h3>
          <ul>
            <li>直接说出你的情况，不用担心说错</li>
            <li>信息越详细，申请书越有力</li>
            <li>可以多次对话补充信息</li>
            <li>生成申请书后可以复制或下载</li>
          </ul>
          <button class="btn-primary" @click="showHelp = false">知道了</button>
        </div>
      </div>
    </transition>

    <!-- 法律援助弹窗 -->
    <transition name="modal">
      <div v-if="showLegalAidModal" class="modal-overlay" @click.self="showLegalAidModal = false">
        <div class="modal-box">
          <h3>📞 法律援助热线</h3>
          <div class="hotline-item">
            <span class="hotline-label">全国法律援助</span>
            <a href="tel:12348" class="hotline-number">12348</a>
          </div>
          <div class="hotline-item">
            <span class="hotline-label">劳动监察投诉</span>
            <a href="tel:12333" class="hotline-number">12333</a>
          </div>
          <div class="hotline-item">
            <span class="hotline-label">信访投诉</span>
            <a href="tel:12345" class="hotline-number">12345</a>
          </div>
          <button class="btn-primary" @click="showLegalAidModal = false">关闭</button>
        </div>
      </div>
    </transition>

  </div>
</template>

<script>
// ====================================================================
// API 配置 — 对接 FastAPI 智能体的接口层
// 替换 API_BASE_URL 为实际部署地址即可
// ====================================================================
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ' https://xxxx.cpolar.cn/api/chat'

/**
 * 核心 API 调用函数
 * 与 FastAPI 智能体通信，发送对话历史，返回 AI 回复及提取的结构化信息
 *
 * FastAPI 端期望接收的请求体：
 * {
 *   messages: [{ role: 'user'|'assistant', content: string }],
 *   extracted_info: { ... }  // 当前已提取的信息
 * }
 *
 * FastAPI 端期望返回的响应体：
 * {
 *   reply: string,                  // AI 回复文本
 *   quick_replies: string[],        // 可选的快捷回复选项
 *   extracted_info: { ... },        // 更新后的结构化信息
 *   can_generate_doc: boolean,      // 是否已收集足够信息生成申请书
 *   conversation_stage: string      // 当前对话阶段
 * }
 */
async function callAgentAPI(messages, extractedInfo) {
  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      messages,
      extracted_info: extractedInfo,
    }),
  })

  if (!response.ok) {
    throw new Error(`API 请求失败: ${response.status}`)
  }

  return await response.json()
}

// 假设这是你的发送方法（保持不变）
const sendMessage = async (userText) => {
  try {
    const res = await fetch('https://759a989a.r29.cpolar.top/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ message: userText })
    });

    if (!res.ok) {
      throw new Error(`HTTP 错误，状态码: ${res.status}`);
    }

    const data = await res.json();

    if (data.status === 'success') {
      const rawReply = data.reply;

      // 剥离 AI 思考过程
      let thinkProcess = "";
      let finalAnswer = rawReply;

      const thinkMatch = rawReply.match(/<think>([\s\S]*?)<\/think>/);
      if (thinkMatch) {
        thinkProcess = thinkMatch[1].trim();
        finalAnswer = rawReply.replace(/<think>[\s\S]*?<\/think>/, '').trim();
      }

      console.log("后台查到的法律参考:", data.retrieved_context);
      console.log("AI 的思考过程:", thinkProcess);
      console.log("最终给用户的回答:", finalAnswer);
    }
  } catch (error) {
    console.error("请求失败:", error);
  }
};


// ✅ 关键修改：页面加载自动执行（默认启用）
window.addEventListener('load', () => {
  sendMessage("你好");  // 👉 这里可以改成你想默认问的问题
});

/**
 * 生成申请书 API
 * FastAPI 端期望接收：{ extracted_info: { ... } }
 * 返回：{ document: string }  // 完整申请书文本
 */
async function generateDocumentAPI(extractedInfo) {
  const response = await fetch(`${API_BASE_URL}/api/generate-document`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      extracted_info: extractedInfo,
    }),
  })

  if (!response.ok) {
    throw new Error(`生成文书失败: ${response.status}`)
  }

  return await response.json()
}


// ====================================================================
// 本地 Mock — 未对接智能体时的降级逻辑（开发调试用）
// 正式部署时可删除或保留作为离线模式
// ====================================================================
const MOCK_FLOW = {
  initial: {
    reply: '您好！我是您的法律咨询助手 👋\n\n我来帮您分析讨薪情况，请先告诉我：\n\n<b>您的姓名？</b>\n\n<b>您是给包工头干活还是给公司干活？</b>\n\n<b>您的工作地点？</b>\n\n<b>您工作了多久？</b>',
    quick_replies: [],
    extracted_info: {worker_name: '', employer_name: '', work_location: '', work_period: ''},
    can_generate_doc: false,
    conversation_stage: 'employer_type',
  },
}

async function mockAgentAPI(messages, extractedInfo) {
  await new Promise(r => setTimeout(r, 1200))

  const lastUserMsg = messages[messages.length - 1]?.content || ''
  const stage = extractedInfo._stage || 'initial'

  // 简单的 mock 对话逻辑
  if (stage === 'initial') {
    if (lastUserMsg.includes('包工头')) {
      return {
        reply: '明白了，您是给个人包工头干活的。\n\n<b>您的包工头的姓名？</b>\n\n<b>您和包工头有没有签书面劳务合同或用工协议？</b>',
        quick_replies: ['有签合同', '没有签合同'],
        extracted_info: { ...extractedInfo, employer_type: '个人包工头', _stage: 'contractor_contract' },
        can_generate_doc: false,
        conversation_stage: 'contractor_contract',
      }
    } else if (lastUserMsg.includes('公司') || lastUserMsg.includes('单位')) {
      return {
        reply: '明白了，您是给公司/单位干活的。\n\n<b>您的公司或单位的名称？</b>\n\n<b>您和公司有没有签书面劳动合同？</b>',
        quick_replies: ['有签劳动合同', '没有签劳动合同'],
        extracted_info: { ...extractedInfo, employer_type: '公司/单位', _stage: 'company_contract' },
        can_generate_doc: false,
        conversation_stage: 'company_contract',
      }
    }
    return MOCK_FLOW.initial
  }

  if (stage === 'contractor_contract') {
    if (lastUserMsg.includes('有') || lastUserMsg.includes('签')) {
      return {
        reply: '好的，您有书面合同。\n\n合同里有没有约定工资标准和结算方式？\n\n另外，<b>包工头有没有给您写过欠条或工资结算单？</b>',
        quick_replies: ['有欠条/结算单', '没有欠条'],
        extracted_info: { ...extractedInfo, has_contract: '有', _stage: 'iou' },
        can_generate_doc: false,
      }
    } else {
      return {
        reply: '没有书面合同也不要紧，还可以通过其他证据维权。\n\n<b>您有没有以下任何一种证据？</b>\n• 工牌或工服照片\n• 考勤记录\n• 和包工头的微信聊天记录\n• 工友可以作证',
        quick_replies: ['有以上证据', '没有这些证据'],
        extracted_info: { ...extractedInfo, has_contract: '没有', _stage: 'evidence' },
        can_generate_doc: false,
      }
    }
  }

  if (stage === 'company_contract') {
    if (lastUserMsg.includes('有') || lastUserMsg.includes('签')) {
      return {
        reply: '好的，您有书面合同。\n\n合同里有没有约定工资标准和结算方式？\n\n另外，<b>公司有没有给您写过欠条或工资结算单？</b>',
        quick_replies: ['有欠条/结算单', '没有欠条'],
        extracted_info: { ...extractedInfo, has_contract: '有', _stage: 'iou' },
        can_generate_doc: false,
      }
    } else {
      return {
        reply: '没有书面合同也不要紧，还可以通过其他证据维权。\n\n<b>您有没有以下任何一种证据？</b>\n• 工牌或工服照片\n• 考勤记录\n• 和老板的微信聊天记录\n• 工友可以作证',
        quick_replies: ['有以上证据', '没有这些证据'],
        extracted_info: { ...extractedInfo, has_contract: '没有', _stage: 'evidence' },
        can_generate_doc: false,
      }
    }
  }

  if (stage === 'iou') {
    return {
      reply: `我已经了解了您的基本情况。\n\n让我再确认几个关键信息：\n\n<b>1. 您被欠了多少工资？</b>（大概金额）\n<b>2. 欠薪从什么时候开始？</b>`,
      quick_replies: [],
      extracted_info: { ...extractedInfo, has_iou: lastUserMsg.includes('有') ? '有' : '没有', _stage: 'amount' },
      can_generate_doc: false,
    }
  }

  if (stage === 'amount' || stage === 'evidence') {
    const amountMatch = lastUserMsg.match(/(\d+[\d,.]*)\s*(万|千|百)?/)
    return {
      reply: '谢谢您提供的信息！\n\n我已经收集了足够的信息来帮您生成<b>维权申请书</b>。\n\n根据您的情况，建议您：\n1. 先向当地劳动监察大队投诉\n2. 同时保存好所有证据\n3. 必要时申请劳动仲裁\n\n点击下方按钮生成申请书👇',
      quick_replies: ['我还想补充情况'],
      extracted_info: {
        ...extractedInfo,
        amount: amountMatch ? amountMatch[0] : lastUserMsg,
        _stage: 'complete',
      },
      can_generate_doc: true,
    }
  }

  // 默认回复
  return {
    reply: '我明白了，您能再具体说说情况吗？\n比如：欠了多久了？大概欠了多少钱？',
    quick_replies: [],
    extracted_info: extractedInfo,
    can_generate_doc: false,
  }
}

async function mockGenerateDocumentAPI(extractedInfo) {
  await new Promise(r => setTimeout(r, 2000))
  const date = new Date().toLocaleDateString('zh-CN')
  return {
    document: `劳动报酬追索申请书

申请人：${extractedInfo.worker_name || '申请人姓名'}
被申请人：${extractedInfo.employer_type || '用人单位'}

申请事项：
  请依法责令被申请人支付申请人拖欠的劳动报酬${extractedInfo.amount ? '人民币' + extractedInfo.amount + '元' : ''}。

事实与理由：

  申请人自${extractedInfo.work_period || '入职时间'}起受雇于被申请人，从事${extractedInfo.work_location || '工作内容'}工作。双方${extractedInfo.has_contract === '有' ? '签订了书面劳动合同' : '虽未签订书面合同，但存在事实劳动关系'}。

  申请人按时完成工作任务，但被申请人自${extractedInfo.overdue_months || '欠薪起始时间'}起拒绝支付工资，累计欠薪${extractedInfo.amount ? extractedInfo.amount + '元' : '若干元'}，至今未予支付。

  申请人多次催讨，被申请人均以各种理由拒绝支付，严重侵害了申请人的合法权益。

  根据《中华人民共和国劳动法》第五十条、《保障农民工工资支付条例》等相关规定，特提出申请，请求贵部门依法处理。

证据清单：
  1. ${extractedInfo.has_contract === '有' ? '劳动合同/劳务协议' : '相关证明材料'}
  2. ${extractedInfo.has_iou === '有' ? '欠条/工资结算单' : '工作证明材料'}
  3. 其他相关证明材料

申请人：_______________（签名）

日期：${date}

附：申请人联系方式：_______________
`,
  }
}

// ====================================================================
// 是否使用 Mock（无后端时自动降级）
// ====================================================================
const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true' || false

export default {
  name: 'MigrantWorkerLegal',

  data() {
    return {
      // 页面状态
      currentStep: 'welcome', // 'welcome' | 'chat' | 'document'
      showHelp: false,
      showLegalAidModal: false,
      showInfoPanel: false,

      // 对话状态
      messages: [],
      userInput: '',
      isLoading: false,
      isGenerating: false,

      // 智能体提取的结构化信息
      extractedInfo: {
        employer_type: '',       // 雇主类型：个人包工头 / 公司单位
        has_contract: '',        // 是否有合同
        has_iou: '',             // 是否有欠条
        worker_name: '',         // 农民工姓名
        employer_name: '',       // 雇主/公司名称
        work_location: '',       // 工作地点
        work_period: '',         // 工作时间段
        amount: '',              // 欠薪金额
        overdue_months: '',      // 欠薪月数
        evidence_types: '',      // 已有证据类型
        complaint_history: '',   // 是否投诉过
        project_type: '',        // 是否建设工程类
        _stage: 'initial',       // 内部流程阶段标记
      },

      // 文书
      canGenerateDoc: false,
      generatedDocument: '',

      // 字段标签映射
      fieldLabels: {
        employer_type: '雇主类型',
        has_contract: '是否有合同',
        has_iou: '是否有欠条',
        worker_name: '您的姓名',
        employer_name: '雇主名称',
        work_location: '工作地点',
        work_period: '工作时间',
        amount: '欠薪金额',
        overdue_months: '欠薪月数',
        evidence_types: '已有证据',
        complaint_history: '投诉情况',
        project_type: '工程类型',
      },

      totalFields: 8, // 生成申请书所需关键字段数
    }
  },

  computed: {
    hasExtractedData() {
      return Object.entries(this.extractedInfo)
        .some(([k, v]) => !k.startsWith('_') && v)
    },
    extractedCount() {
      return Object.entries(this.extractedInfo)
        .filter(([k, v]) => !k.startsWith('_') && v).length
    },
  },

  methods: {
    // ------------------------------------------------------------------
    // 初始化
    // ------------------------------------------------------------------
    startChat() {
      this.currentStep = 'chat'
      this.$nextTick(() => {
        this.sendInitialGreeting()
      })
    },

    async sendInitialGreeting() {
      this.isLoading = true
      try {
        const result = USE_MOCK
          ? await mockAgentAPI([], this.extractedInfo)
          : await callAgentAPI([], this.extractedInfo)

        this.pushAssistantMessage(result.reply, result.quick_replies)
        this.updateExtractedInfo(result)
      } catch (e) {
        this.pushAssistantMessage('您好！请告诉我您的讨薪情况，我来帮您分析。')
      } finally {
        this.isLoading = false
      }
    },

    // ------------------------------------------------------------------
    // 消息收发
    // ------------------------------------------------------------------
    async sendMessage() {
      const text = this.userInput.trim()
      if (!text || this.isLoading) return

      this.userInput = ''
      this.pushUserMessage(text)
      await this.callAgent(text)
    },

    async sendQuickReply(reply) {
      if (this.isLoading) return
      this.pushUserMessage(reply)
      await this.callAgent(reply)
    },

    /**
     * 调用智能体核心方法
     * 构建对话历史并请求 FastAPI 智能体
     */
    async callAgent(userText) {
      this.isLoading = true
      this.scrollToBottom()

      // 构建发送给后端的对话历史（过滤掉快捷回复按钮信息）
      const apiMessages = this.messages
        .filter(m => !m.isSystem)
        .map(m => ({ role: m.role, content: m.content }))

      try {
        const result = USE_MOCK
          ? await mockAgentAPI(apiMessages, this.extractedInfo)
          : await callAgentAPI(apiMessages, this.extractedInfo)

        this.pushAssistantMessage(result.reply, result.quick_replies)
        this.updateExtractedInfo(result)
        this.canGenerateDoc = result.can_generate_doc || false

      } catch (e) {
        console.error('Agent API error:', e)
        this.pushAssistantMessage(
          '抱歉，暂时无法连接到服务器，请检查网络后重试。\n如需紧急帮助，请拨打12348法律援助热线。'
        )
      } finally {
        this.isLoading = false
        this.$nextTick(() => this.scrollToBottom())
      }
    },

    // ------------------------------------------------------------------
    // 生成申请书
    // ------------------------------------------------------------------
    async generateDocument() {
      this.isGenerating = true
      try {
        const result = USE_MOCK
          ? await mockGenerateDocumentAPI(this.extractedInfo)
          : await generateDocumentAPI(this.extractedInfo)

        this.generatedDocument = result.document
        this.currentStep = 'document'
      } catch (e) {
        alert('生成申请书失败，请重试')
      } finally {
        this.isGenerating = false
      }
    },

    // ------------------------------------------------------------------
    // 消息辅助
    // ------------------------------------------------------------------
    pushUserMessage(content) {
      this.messages.push({ role: 'user', content })
      this.$nextTick(() => this.scrollToBottom())
    },

    pushAssistantMessage(content, quickReplies = []) {
      this.messages.push({ role: 'assistant', content, quickReplies })
      this.$nextTick(() => this.scrollToBottom())
    },

    updateExtractedInfo(result) {
      if (result.extracted_info) {
        this.extractedInfo = { ...this.extractedInfo, ...result.extracted_info }
      }
    },

    formatMessage(text) {
      return text
        .replace(/\n/g, '<br>')
        .replace(/\*\*(.*?)\*\*/g, '<b>$1</b>')
    },

    scrollToBottom() {
      const el = this.$refs.messagesContainer
      if (el) el.scrollTop = el.scrollHeight
    },

    autoResize(e) {
      const el = e.target
      el.style.height = 'auto'
      el.style.height = Math.min(el.scrollHeight, 120) + 'px'
    },

    // ------------------------------------------------------------------
    // 文书操作
    // ------------------------------------------------------------------
    copyDocument() {
      navigator.clipboard.writeText(this.generatedDocument)
        .then(() => alert('已复制到剪贴板！'))
        .catch(() => alert('复制失败，请手动长按选择文字复制'))
    },

    downloadDocument() {
      const blob = new Blob([this.generatedDocument], { type: 'text/plain;charset=utf-8' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = '维权申请书.txt'
      a.click()
      URL.revokeObjectURL(url)
    },

    // ------------------------------------------------------------------
    // 其他操作
    // ------------------------------------------------------------------
    restartChat() {
      if (!confirm('确定要重新开始吗？当前对话内容将清空。')) return
      this.messages = []
      this.extractedInfo = {
        employer_type: '', has_contract: '', has_iou: '',
        worker_name: '', employer_name: '', work_location: '',
        work_period: '', amount: '', overdue_months: '',
        evidence_types: '', complaint_history: '', project_type: '',
        _stage: 'initial',
      }
      this.canGenerateDoc = false
      this.generatedDocument = ''
      this.currentStep = 'welcome'
    },

    showLegalAid() {
      this.showLegalAidModal = true
    },
  },
}
</script>

<style scoped>
/* ===== 基础变量 ===== */
:root {
  --primary: #E85D26;
  --primary-light: #FF7A45;
  --primary-bg: #FFF5F0;
  --secondary: #2D6A4F;
  --text-dark: #1A1A1A;
  --text-mid: #555;
  --text-light: #888;
  --bg: #F7F4EF;
  --surface: #FFFFFF;
  --border: #E8E0D5;
  --bubble-user: #E85D26;
  --bubble-ai: #FFFFFF;
  --shadow: 0 2px 12px rgba(0,0,0,0.08);
  --radius: 16px;
  --font-display: 'Noto Serif SC', 'SimSun', serif;
  --font-body: 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
  -webkit-tap-highlight-color: transparent;
}

/* ===== 应用整体布局 ===== */
.app-wrapper {
  display: flex;
  flex-direction: column;
  height: 100dvh;
  max-width: 480px;
  margin: 0 auto;
  background: var(--bg);
  font-family: var(--font-body);
  overflow: hidden;
  position: relative;
}

/* ===== 顶部标题栏 ===== */
.app-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 18px;
  background: var(--primary);
  color: white;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(232,93,38,0.3);
}

.header-icon {
  font-size: 28px;
  line-height: 1;
}

.header-text h1 {
  font-family: var(--font-display);
  font-size: 20px;
  font-weight: 700;
  letter-spacing: 2px;
}

.header-text p {
  font-size: 12px;
  opacity: 0.85;
  margin-top: 1px;
}

.header-badge {
  margin-left: auto;
  background: white;
  color: var(--primary);
  font-weight: 700;
  font-size: 12px;
  padding: 3px 10px;
  border-radius: 20px;
}

/* ===== 主内容区 ===== */
.app-main {
  flex: 1;
  overflow: hidden;
  position: relative;
  display: flex;
  flex-direction: column;
}

/* ===== 欢迎页 ===== */
.welcome-screen {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 32px 24px;
  overflow-y: auto;
}

.welcome-hero {
  text-align: center;
  margin-bottom: 28px;
}

.hero-emoji {
  font-size: 64px;
  line-height: 1;
  margin-bottom: 16px;
  filter: drop-shadow(0 4px 8px rgba(0,0,0,0.1));
}

.welcome-hero h2 {
  font-family: var(--font-display);
  font-size: 26px;
  color: var(--primary);
  font-weight: 700;
  margin-bottom: 10px;
}

.hero-sub {
  font-size: 16px;
  color: var(--text-mid);
  line-height: 1.7;
}

.welcome-promises {
  width: 100%;
  background: var(--surface);
  border-radius: var(--radius);
  padding: 16px 20px;
  margin-bottom: 28px;
  box-shadow: var(--shadow);
  border: 1px solid var(--border);
}

.promise-item {
  font-size: 15px;
  color: var(--text-dark);
  padding: 8px 0;
  border-bottom: 1px solid var(--border);
  line-height: 1.5;
}

.promise-item:last-child {
  border-bottom: none;
}

.btn-start {
  width: 100%;
  padding: 18px;
  background: var(--primary);
  color: gray;
  border: none;
  border-radius: var(--radius);
  font-size: 20px;
  font-weight: 700;
  font-family: var(--font-body);
  cursor: pointer;
  letter-spacing: 2px;
  box-shadow: 0 4px 16px rgba(232,93,38,0.4);
  transition: transform 0.1s, box-shadow 0.1s;
}

.btn-start:active {
  transform: scale(0.98);
  box-shadow: 0 2px 8px rgba(232,93,38,0.3);
}

.disclaimer {
  font-size: 11px;
  color: var(--text-light);
  margin-top: 16px;
  text-align: center;
}

/* ===== 对话页 ===== */
.chat-screen {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 16px 14px;
  scroll-behavior: smooth;
}

/* 消息行 */
.message-row {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  margin-bottom: 16px;
}

.message-row.user {
  flex-direction: row-reverse;
}

/* 头像 */
.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
}

.assistant-avatar {
  background: var(--primary);
}

.user-avatar {
  background: #6B7280;
}

/* 气泡 */
.bubble {
  max-width: 78%;
  padding: 12px 16px;
  border-radius: var(--radius);
  font-size: 15px;
  line-height: 1.65;
  box-shadow: var(--shadow);
}

.bubble.assistant {
  background: var(--bubble-ai);
  border: 1px solid var(--border);
  border-bottom-left-radius: 4px;
  color: var(--text-dark);
}

.bubble.user {
  background: var(--bubble-user);
  color: white;
  border-bottom-right-radius: 4px;
}

/* 快捷回复 */
.quick-replies {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.quick-reply-btn {
  padding: 8px 14px;
  background: var(--primary-bg);
  color: var(--primary);
  border: 1.5px solid var(--primary);
  border-radius: 20px;
  font-size: 14px;
  font-family: var(--font-body);
  cursor: pointer;
  font-weight: 600;
  transition: all 0.15s;
}

.quick-reply-btn:active {
  background: var(--primary);
  color: white;
}

.quick-reply-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 加载动画 */
.loading-bubble {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 14px 18px;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--primary);
  opacity: 0.6;
  animation: bounce 1.2s infinite;
}

.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes bounce {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.6; }
  30% { transform: translateY(-6px); opacity: 1; }
}

/* ===== 信息面板 ===== */
.info-panel {
  margin: 0 14px 8px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  overflow: hidden;
  font-size: 13px;
}

.info-panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  background: #FFF5F0;
  cursor: pointer;
  color: var(--primary);
  font-weight: 600;
}

.info-panel-body {
  padding: 8px 0;
}

.info-row {
  display: flex;
  justify-content: space-between;
  padding: 6px 14px;
  border-bottom: 1px solid var(--border);
}

.info-row:last-child { border-bottom: none; }

.info-label {
  color: var(--text-light);
  flex-shrink: 0;
}

.info-value {
  color: var(--text-dark);
  font-weight: 500;
  text-align: right;
  margin-left: 8px;
}

/* ===== 输入区 ===== */
.input-area {
  flex-shrink: 0;
  padding: 10px 14px 12px;
  background: var(--surface);
  border-top: 1px solid var(--border);
}

.input-row {
  display: flex;
  gap: 10px;
  align-items: flex-end;
}

.input-box {
  flex: 1;
  padding: 10px 14px;
  border: 2px solid var(--border);
  border-radius: 12px;
  font-size: 15px;
  font-family: var(--font-body);
  resize: none;
  background: var(--bg);
  color: var(--text-dark);
  line-height: 1.5;
  transition: border-color 0.2s;
  min-height: 44px;
}

.input-box:focus {
  outline: none;
  border-color: var(--primary);
  background: white;
}

.input-box::placeholder {
  color: var(--text-light);
  font-size: 13px;
}

.send-btn {
  width: 56px;
  height: 44px;
  background: var(--primary);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  flex-shrink: 0;
  transition: opacity 0.15s;
}

.send-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.btn-generate {
  width: 100%;
  margin-top: 10px;
  padding: 14px;
  background: var(--secondary);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 700;
  font-family: var(--font-body);
  cursor: pointer;
  letter-spacing: 1px;
  box-shadow: 0 2px 8px rgba(45,106,79,0.3);
}

.btn-generate:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* ===== 申请书页 ===== */
.document-screen {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 0;
}

.doc-header {
  display: flex;
  align-items: center;
  padding: 14px 16px;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  gap: 12px;
}

.doc-header h2 {
  flex: 1;
  text-align: center;
  font-family: var(--font-display);
  font-size: 18px;
  color: var(--text-dark);
}

.btn-back, .btn-copy {
  padding: 6px 12px;
  border: 1.5px solid var(--border);
  background: white;
  border-radius: 8px;
  font-size: 13px;
  cursor: pointer;
  color: var(--text-mid);
}

.document-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px 18px;
  background: #FFFEF9;
}

.document-text {
  font-family: var(--font-body);
  font-size: 14px;
  line-height: 2;
  color: var(--text-dark);
  white-space: pre-wrap;
  word-break: break-all;
}

.doc-actions {
  display: flex;
  gap: 12px;
  padding: 14px 16px;
  background: var(--surface);
  border-top: 1px solid var(--border);
}

.btn-secondary {
  flex: 1;
  padding: 13px;
  border: 2px solid var(--primary);
  background: white;
  color: var(--primary);
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}

.btn-primary {
  flex: 1;
  padding: 13px;
  background: var(--primary);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}

.doc-disclaimer {
  text-align: center;
  font-size: 11px;
  color: var(--text-light);
  padding: 8px 16px 12px;
  background: var(--surface);
}

/* ===== 底部导航 ===== */
.bottom-nav {
  display: flex;
  background: var(--surface);
  border-top: 1px solid var(--border);
  flex-shrink: 0;
}

.nav-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 0 10px;
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-mid);
  font-size: 11px;
  gap: 2px;
  font-family: var(--font-body);
}

.nav-icon {
  font-size: 20px;
}

/* ===== 弹窗 ===== */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.45);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  z-index: 100;
  padding-bottom: env(safe-area-inset-bottom, 0);
}

.modal-box {
  width: 100%;
  max-width: 480px;
  background: white;
  border-radius: 20px 20px 0 0;
  padding: 24px 24px 32px;
}

.modal-box h3 {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 16px;
  color: var(--text-dark);
}

.modal-box ul {
  list-style: none;
  margin-bottom: 20px;
}

.modal-box li {
  padding: 10px 0;
  border-bottom: 1px solid var(--border);
  font-size: 15px;
  color: var(--text-mid);
  line-height: 1.5;
}

.modal-box li::before {
  content: '• ';
  color: var(--primary);
  font-weight: bold;
}

.modal-box .btn-primary {
  width: 100%;
  padding: 15px;
  font-size: 16px;
}

.hotline-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 0;
  border-bottom: 1px solid var(--border);
}

.hotline-label {
  font-size: 15px;
  color: var(--text-dark);
}

.hotline-number {
  font-size: 22px;
  font-weight: 700;
  color: var(--primary);
  text-decoration: none;
  letter-spacing: 1px;
}

/* ===== 过渡动画 ===== */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.25s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

.slide-up-enter-active {
  transition: all 0.3s ease;
}
.slide-up-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.modal-enter-active, .modal-leave-active {
  transition: opacity 0.2s;
}
.modal-enter-from, .modal-leave-to {
  opacity: 0;
}

.collapse-enter-active, .collapse-leave-active {
  transition: all 0.2s;
  overflow: hidden;
}
.collapse-enter-from, .collapse-leave-to {
  max-height: 0;
  opacity: 0;
}
.collapse-enter-to, .collapse-leave-from {
  max-height: 500px;
  opacity: 1;
}

/* ===== 滚动条美化 ===== */
.messages-container::-webkit-scrollbar,
.document-body::-webkit-scrollbar {
  width: 3px;
}
.messages-container::-webkit-scrollbar-thumb,
.document-body::-webkit-scrollbar-thumb {
  background: var(--border);
  border-radius: 2px;
}
</style>
