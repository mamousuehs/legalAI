<template>
  <div class="app-wrapper">
    <header class="app-header">
      <div class="header-icon">⚖️</div>
      <div class="header-text">
        <h1>讨薪帮手</h1>
        <p>免费法律咨询 · 专为农民工服务</p>
      </div>
      <div class="header-badge">免费</div>
    </header>

    <main class="app-main">

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

      <transition name="fade">
        <section v-if="currentStep === 'chat'" class="chat-screen">

          <div class="messages-container" ref="messagesContainer">
            <div
              v-for="(msg, index) in messages"
              :key="index"
              class="message-row"
              :class="msg.role"
            >
              <div v-if="msg.role === 'assistant'" class="avatar assistant-avatar">⚖️</div>

              <div class="bubble" :class="msg.role">
                <div class="bubble-text" v-html="formatMessage(msg.content)"></div>
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

              <div v-if="msg.role === 'user'" class="avatar user-avatar">👷</div>
            </div>

            <div v-if="isLoading" class="message-row assistant">
              <div class="avatar assistant-avatar">⚖️</div>
              <div class="bubble assistant loading-bubble">
                <span class="dot"></span>
                <span class="dot"></span>
                <span class="dot"></span>
              </div>
            </div>
          </div>

          <div class="input-area">
            <div class="input-row">
              <textarea
                ref="inputBox"
                v-model="userInput"
                class="input-box"
                placeholder="用自己的话说情况，比如：我叫xxx，在xx工作，拖欠3个月工资..."
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
          </div>

        </section>
      </transition>

    </main>

    <nav v-if="currentStep === 'chat'" class="bottom-nav">
      <button class="nav-item" @click="showHelp = true">
        <span class="nav-icon">❓</span>
        <span>帮助</span>
      </button>
      <button class="nav-item" @click="restartChat">
        <span class="nav-icon">🔄</span>
        <span>重新开始</span>
      </button>
      <button class="nav-item" @click="showLegalAidModal = true">
        <span class="nav-icon">📞</span>
        <span>法律援助</span>
      </button>
    </nav>

    <transition name="modal">
      <div v-if="showHelp" class="modal-overlay" @click.self="showHelp = false">
        <div class="modal-box">
          <h3>💡 使用提示</h3>
          <ul>
            <li>直接说出你的情况，不用担心说错</li>
            <li>信息越详细，申请书越有力</li>
            <li>可以多次对话补充信息</li>
          </ul>
          <button class="btn-primary" @click="showHelp = false">知道了</button>
        </div>
      </div>
    </transition>

    <transition name="modal">
      <div v-if="showLegalAidModal" class="modal-overlay" @click.self="showLegalAidModal = false">
        <div class="modal-box">
          <h3>📞 法律援助热线</h3>
          <div class="hotline-item">
            <span class="hotline-label">全国法律援助</span>
            <a href="tel:12348" class="hotline-number">12348</a>
          </div>
          <button class="btn-primary" @click="showLegalAidModal = false">关闭</button>
        </div>
      </div>
    </transition>

  </div>
</template>

<script>
// ====================================================================
// 核心 API 调用配置 (已配置为直连你的本地 Python 后端)
// ====================================================================
const API_BASE_URL = 'http://127.0.0.1:8000'

async function callAgentAPI(messages) {
  // 精准抽出用户的最后一句话
  const lastUserText = messages[messages.length - 1].content;

  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    // 严格按照 FastAPI 的要求发送
    body: JSON.stringify({
      message: lastUserText
    })
  });

  if (!response.ok) {
    throw new Error(`API 请求失败: ${response.status}`);
  }

  return await response.json();
}

export default {
  name: 'MigrantWorkerLegal',

  data() {
    return {
      currentStep: 'welcome', 
      showHelp: false,
      showLegalAidModal: false,
      messages: [],
      userInput: '',
      isLoading: false,
    }
  },

  methods: {
    startChat() {
      this.currentStep = 'chat'
      this.$nextTick(() => {
        this.pushAssistantMessage('您好！我是您的法律咨询助手 👋\n请告诉我您的讨薪情况，比如您给谁干活？在哪里干活？欠了多少钱？我来帮您分析。')
      })
    },

    async sendMessage() {
      const text = this.userInput.trim()
      if (!text || this.isLoading) return

      this.userInput = ''
      this.pushUserMessage(text)
      await this.callAgent()
    },

    async callAgent() {
      this.isLoading = true
      this.scrollToBottom()

      // 准备发送给后端的数据
      const apiMessages = this.messages
        .filter(m => !m.isSystem)
        .map(m => ({ role: m.role, content: m.content }))

      try {
        // 直接调用真实的后端接口
        const result = await callAgentAPI(apiMessages)
        
        // 剥离出 AI 的回答
        let finalReply = result.reply;
        // 如果有 <think> 标签，帮前端把它隐藏掉
        finalReply = finalReply.replace(/<think>[\s\S]*?<\/think>/, '').trim();

        this.pushAssistantMessage(finalReply)

      } catch (e) {
        console.error('API调用报错:', e)
        this.pushAssistantMessage(
          '抱歉，暂时无法连接到服务器，请检查大模型后端是否启动。'
        )
      } finally {
        this.isLoading = false
        this.$nextTick(() => this.scrollToBottom())
      }
    },

    pushUserMessage(content) {
      this.messages.push({ role: 'user', content })
      this.$nextTick(() => this.scrollToBottom())
    },

    pushAssistantMessage(content, quickReplies = []) {
      this.messages.push({ role: 'assistant', content, quickReplies })
      this.$nextTick(() => this.scrollToBottom())
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

    restartChat() {
      if (!confirm('确定要重新开始吗？当前对话内容将清空。')) return
      this.messages = []
      this.currentStep = 'welcome'
    },
  },
}
</script>

<style>
/* ===== 基础变量 ===== */
:root {
  --primary: #E85D26;
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
  --font-body: 'Noto Sans SC', 'Microsoft YaHei', sans-serif;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

.app-wrapper {
  display: flex;
  flex-direction: column;
  height: 100vh;
  max-width: 480px;
  margin: 0 auto;
  background: var(--bg);
  font-family: var(--font-body);
}

.app-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 18px;
  background: var(--primary);
  color: white;
  box-shadow: 0 2px 8px rgba(232,93,38,0.3);
}
.header-text h1 { font-size: 20px; }
.header-text p { font-size: 12px; }
.header-badge { margin-left: auto; background: white; color: var(--primary); padding: 3px 10px; border-radius: 20px; font-size: 12px;}

.app-main { flex: 1; overflow: hidden; display: flex; flex-direction: column; }
.welcome-screen { flex: 1; display: flex; flex-direction: column; align-items: center; padding: 32px 24px; }
.hero-emoji { font-size: 64px; margin-bottom: 16px; }
.welcome-hero h2 { color: var(--primary); margin-bottom: 10px; }
.hero-sub { color: var(--text-mid); text-align: center; line-height: 1.5; margin-bottom: 20px;}
.welcome-promises { background: white; border-radius: 16px; padding: 16px; width: 100%; margin-bottom: 20px;}
.promise-item { padding: 8px 0; border-bottom: 1px solid var(--border); }

.btn-start { width: 100%; padding: 18px; background: var(--primary); color: white; border: none; border-radius: 16px; font-size: 18px; font-weight: bold; cursor: pointer; }
.disclaimer { font-size: 11px; color: var(--text-light); margin-top: 16px; }

.chat-screen { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
.messages-container { flex: 1; overflow-y: auto; padding: 16px 14px; }
.message-row { display: flex; align-items: flex-end; gap: 8px; margin-bottom: 16px; }
.message-row.user { flex-direction: row-reverse; }
.avatar { width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.assistant-avatar { background: var(--primary); color: white; }
.user-avatar { background: #6B7280; }
.bubble { max-width: 78%; padding: 12px 16px; border-radius: 16px; font-size: 15px; line-height: 1.6; box-shadow: var(--shadow); }
.bubble.assistant { background: white; border-bottom-left-radius: 4px; }
.bubble.user { background: var(--primary); color: white; border-bottom-right-radius: 4px; }

.loading-bubble { display: flex; gap: 5px; padding: 14px 18px; }
.dot { width: 8px; height: 8px; border-radius: 50%; background: var(--primary); animation: bounce 1.2s infinite; }
.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce { 0%, 60%, 100% { transform: translateY(0); opacity: 0.6; } 30% { transform: translateY(-6px); opacity: 1; } }

.input-area { padding: 10px 14px 12px; background: white; border-top: 1px solid var(--border); }
.input-row { display: flex; gap: 10px; align-items: flex-end; }
.input-box { flex: 1; padding: 10px; border: 2px solid var(--border); border-radius: 12px; resize: none; background: var(--bg); min-height: 44px; }
.input-box:focus { outline: none; border-color: var(--primary); background: white;}
.send-btn { width: 60px; height: 44px; background: var(--primary); color: white; border: none; border-radius: 12px; font-weight: bold; cursor: pointer; }
.send-btn:disabled { opacity: 0.5; }

.bottom-nav { display: flex; background: white; border-top: 1px solid var(--border); padding: 5px 0;}
.nav-item { flex: 1; display: flex; flex-direction: column; align-items: center; background: none; border: none; padding: 5px; color: var(--text-mid); cursor: pointer; }
.nav-icon { font-size: 20px; }

.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: flex-end; z-index: 100; }
.modal-box { width: 100%; max-width: 480px; margin: 0 auto; background: white; border-radius: 20px 20px 0 0; padding: 24px; }
.modal-box h3 { margin-bottom: 16px; }
.modal-box li { padding: 10px 0; border-bottom: 1px solid var(--border); }
.btn-primary { width: 100%; padding: 15px; background: var(--primary); color: white; border: none; border-radius: 12px; font-size: 16px; font-weight: bold; margin-top: 15px; cursor: pointer;}
.hotline-item { display: flex; justify-content: space-between; padding: 15px 0; border-bottom: 1px solid var(--border); }
.hotline-number { color: var(--primary); font-size: 20px; font-weight: bold; text-decoration: none; }
</style>