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

      <!-- ══════════════════════════════════════════ -->
      <!-- 步骤 1：欢迎页                             -->
      <!-- ══════════════════════════════════════════ -->
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
          <button class="btn-start" @click="currentStep = 'intake'">
            开始咨询 →
          </button>
          <p class="disclaimer">本工具仅供参考，不构成正式法律意见</p>
        </section>
      </transition>

      <!-- ══════════════════════════════════════════ -->
      <!-- 步骤 2：信息收集表单                       -->
      <!-- ══════════════════════════════════════════ -->
      <transition name="fade">
        <section v-if="currentStep === 'intake'" class="intake-screen">

          <div class="intake-header">
            <div class="intake-step-label">第 1 步 · 基本情况</div>
            <h2 class="intake-title">先告诉我一些情况</h2>
            <p class="intake-sub">填写越多，分析越准确。不确定的可以跳过。</p>
          </div>

          <div class="intake-form">

            <!-- 1. 姓名 -->
            <div class="form-item">
              <label class="form-label">
                <span class="label-icon">👤</span>
                您的姓名
              </label>
              <input
                class="form-input"
                type="text"
                v-model="intakeForm.name"
                placeholder="例：张师傅"
                maxlength="20"
              />
            </div>

            <!-- 2. 工作地址 -->
            <div class="form-item">
              <label class="form-label">
                <span class="label-icon">📍</span>
                工作地点
              </label>
              <input
                class="form-input"
                type="text"
                v-model="intakeForm.workLocation"
                placeholder="例：北京市朝阳区某建筑工地"
                maxlength="60"
              />
            </div>

            <!-- ★ 3. 为谁干活（改为填空） -->
            <div class="form-item">
              <label class="form-label">
                <span class="label-icon">🏢</span>
                您给谁干活？
              </label>
              <input
                class="form-input"
                type="text"
                v-model="intakeForm.employerType"
                placeholder="例：李老板（包工头）、北京某建筑公司"
                maxlength="50"
              />
            </div>

            <!-- 4. 欠薪金额 -->
            <div class="form-item">
              <label class="form-label">
                <span class="label-icon">💰</span>
                被拖欠的工资金额
              </label>
              <div class="input-with-unit">
                <input
                  class="form-input"
                  type="number"
                  v-model="intakeForm.wageAmount"
                  placeholder="例：18000"
                  min="0"
                />
                <span class="input-unit">元</span>
              </div>
            </div>

            <!-- 5. 欠薪时段 -->
            <div class="form-item">
              <label class="form-label">
                <span class="label-icon">📅</span>
                欠薪时间段
              </label>
              <div class="date-range-row">
                <input
                  class="form-input date-input"
                  type="month"
                  v-model="intakeForm.wageStartMonth"
                />
                <span class="date-sep">至</span>
                <input
                  class="form-input date-input"
                  type="month"
                  v-model="intakeForm.wageEndMonth"
                />
              </div>
            </div>

            <!-- 6. 是否已完成劳动仲裁 -->
            <div class="form-item">
              <label class="form-label">
                <span class="label-icon">⚖️</span>
                是否已经完成劳动仲裁？
              </label>
              <div class="toggle-group">
                <button
                  class="toggle-btn"
                  :class="{ active: intakeForm.hasArbitration === true }"
                  @click="intakeForm.hasArbitration = true"
                >
                  ✅ 已完成仲裁
                </button>
                <button
                  class="toggle-btn"
                  :class="{ active: intakeForm.hasArbitration === false }"
                  @click="intakeForm.hasArbitration = false"
                >
                  ❌ 尚未仲裁
                </button>
              </div>
            </div>

          </div>

          <!-- 底部按钮 -->
          <div class="intake-actions">
            <button class="btn-start" @click="submitIntake">
              开始分析 →
            </button>
            <button class="btn-skip" @click="skipIntake">
              跳过，直接对话
            </button>
          </div>

        </section>
      </transition>

      <!-- ══════════════════════════════════════════ -->
      <!-- 步骤 3：正式对话                           -->
      <!-- ══════════════════════════════════════════ -->
      <transition name="fade">
        <section v-if="currentStep === 'chat'" class="chat-screen">

          <div class="messages-container" ref="messagesContainer">
            <div
              v-for="(msg, index) in messages"
              :key="index"
              class="message-group"
            >
              <!-- 普通对话气泡 -->
              <div class="message-row" :class="msg.role">
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
                    >{{ reply }}</button>
                  </div>
                </div>
                <div v-if="msg.role === 'user'" class="avatar user-avatar">👷</div>
              </div>

              <!-- 结构化分析卡片 -->
              <div v-if="msg.role === 'assistant' && msg.analysis" class="analysis-card">
                <div class="card-header" @click="msg.cardOpen = !msg.cardOpen">
                  <span class="card-title">📋 案件分析结果</span>
                  <span class="card-toggle">{{ msg.cardOpen ? '收起 ▲' : '展开 ▼' }}</span>
                </div>
                <div v-if="msg.cardOpen" class="card-body">

                  <div class="card-section">
                    <div class="section-label blue">📌 案件基本信息</div>
                    <div class="info-grid">
                      <div class="info-item" v-for="item in msg.analysis.caseInfo" :key="item.label">
                        <span class="info-label">{{ item.label }}</span>
                        <span class="info-value">{{ item.value }}</span>
                      </div>
                    </div>
                  </div>

                  <div class="card-section">
                    <div class="section-label green">🛤️ 建议维权路径</div>
                    <div class="path-list">
                      <div
                        class="path-item"
                        v-for="(path, i) in msg.analysis.legalPaths"
                        :key="i"
                        :class="{ recommended: path.recommended }"
                      >
                        <div class="path-step">{{ i + 1 }}</div>
                        <div class="path-content">
                          <div class="path-name">
                            {{ path.name }}
                            <span v-if="path.recommended" class="tag-recommend">推荐</span>
                          </div>
                          <div class="path-desc">{{ path.desc }}</div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div class="card-section">
                    <div class="section-label amber">📁 所需证据清单</div>
                    <div class="evidence-list">
                      <div class="evidence-item" v-for="ev in msg.analysis.evidence" :key="ev.name">
                        <span class="ev-icon">{{ ev.have ? '✅' : '⬜' }}</span>
                        <div class="ev-content">
                          <div class="ev-name">{{ ev.name }}</div>
                          <div class="ev-tip">{{ ev.tip }}</div>
                        </div>
                        <span class="ev-badge" :class="ev.importance">
                          {{ ev.importance === 'key' ? '关键' : '补充' }}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div class="card-section">
                    <div class="section-label red">⚖️ 适用法条</div>
                    <div class="law-list">
                      <div class="law-item" v-for="law in msg.analysis.laws" :key="law.title">
                        <div class="law-title">{{ law.title }}</div>
                        <div class="law-content">{{ law.content }}</div>
                      </div>
                    </div>
                  </div>

                </div>
              </div>

            </div>

            <!-- 加载动画 -->
            <div v-if="isLoading" class="message-row assistant">
              <div class="avatar assistant-avatar">⚖️</div>
              <div class="bubble assistant loading-bubble">
                <span class="dot"></span><span class="dot"></span><span class="dot"></span>
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
              <button class="send-btn" @click="sendMessage" :disabled="isLoading || !userInput.trim()">
                <span v-if="!isLoading">发送</span>
                <span v-else>...</span>
              </button>
            </div>
          </div>

        </section>
      </transition>

    </main>

    <!-- 底部导航 -->
    <nav v-if="currentStep === 'chat'" class="bottom-nav">
      <button class="nav-item" @click="showHelp = true">
        <span class="nav-icon">❓</span><span>帮助</span>
      </button>
      <button class="nav-item" @click="restartChat">
        <span class="nav-icon">🔄</span><span>重新开始</span>
      </button>
      <button class="nav-item" @click="showLegalAidModal = true">
        <span class="nav-icon">📞</span><span>法律援助</span>
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
          <button class="btn-primary" @click="showLegalAidModal = false">关闭</button>
        </div>
      </div>
    </transition>

  </div>
</template>

<script>
// =====================================================================
// API 配置
// =====================================================================
const API_BASE_URL = 'http://127.0.0.1:8000'

async function callAgentAPI(messages, intakeData) {
  const lastUserText = messages[messages.length - 1].content
  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message: lastUserText,
      user_info: intakeData,
    })
  })
  if (!response.ok) throw new Error(`API 请求失败: ${response.status}`)
  return await response.json()
}

// =====================================================================
// 假数据（联调时替换为 result.analysis ?? null）
// =====================================================================
function getMockAnalysis() {
  return {
    caseInfo: [
      { label: '当事人',   value: '张某某' },
      { label: '工作地点', value: '北京市朝阳区某建筑工地' },
      { label: '用工方',   value: '李老板（个人包工头）' },
      { label: '工种',     value: '瓦工' },
      { label: '欠薪金额', value: '¥ 18,000 元' },
      { label: '欠薪时段', value: '2024年10月—12月（3个月）' },
    ],
    legalPaths: [
      { name: '向劳动监察部门投诉', desc: '拨打 12333 或前往当地劳动局，成本最低，建议优先尝试。', recommended: true },
      { name: '申请劳动仲裁',       desc: '向劳动人事争议仲裁委员会提交申请，免费且具有法律效力。', recommended: false },
      { name: '向法院提起诉讼',     desc: '持仲裁裁决书向法院起诉，可追加总包公司为共同被告。',   recommended: false },
    ],
    evidence: [
      { name: '劳务合同 / 用工协议', tip: '如无书面合同，微信聊天记录也可使用', have: true,  importance: 'key' },
      { name: '欠条 / 工资结算单',   tip: '要求包工头补签欠条，注明金额和日期',   have: false, importance: 'key' },
      { name: '工资转账记录',        tip: '微信、支付宝或银行转账截图均可',       have: true,  importance: 'key' },
      { name: '工牌 / 考勤记录',     tip: '证明在该工地实际出勤的凭证',           have: false, importance: 'supplement' },
      { name: '工友证人联系方式',    tip: '可在仲裁或诉讼中出庭作证',             have: false, importance: 'supplement' },
    ],
    laws: [
      { title: '《劳动法》第五十条',               content: '工资应当以货币形式按月支付给劳动者本人，不得克扣或者无故拖欠劳动者的工资。' },
      { title: '《劳动合同法》第三十条',           content: '用人单位应当按照劳动合同约定和国家规定，向劳动者及时足额支付劳动报酬。' },
      { title: '《保障农民工工资支付条例》第三十条', content: '分包单位拖欠农民工工资的，由施工总承包单位先行清偿，再依法进行追偿。' },
    ],
  }
}

// =====================================================================
// 将表单内容拼成自然语言，作为对话首条消息
// =====================================================================
function buildIntakeSummary(form) {
  const parts = []
  if (form.name)         parts.push(`我叫${form.name}`)
  if (form.workLocation) parts.push(`在${form.workLocation}工作`)
  if (form.employerType) parts.push(`给"${form.employerType}"干活`)
  if (form.wageAmount)   parts.push(`被拖欠工资共 ${form.wageAmount} 元`)
  if (form.wageStartMonth && form.wageEndMonth)
    parts.push(`欠薪时间段是 ${form.wageStartMonth} 至 ${form.wageEndMonth}`)
  else if (form.wageStartMonth)
    parts.push(`从 ${form.wageStartMonth} 开始欠薪`)
  if (form.hasArbitration === true)  parts.push('已经完成了劳动仲裁')
  if (form.hasArbitration === false) parts.push('尚未进行劳动仲裁')
  if (parts.length === 0) return null
  return parts.join('，') + '。请帮我分析如何维权。'
}

// =====================================================================
// 检查哪些字段还未填，用于对话中提醒
// =====================================================================
function getMissingFields(form) {
  const missing = []
  if (!form.name)           missing.push('您的姓名')
  if (!form.workLocation)   missing.push('工作地点')
  if (!form.employerType)   missing.push('用工方名称')
  if (!form.wageAmount)     missing.push('欠薪金额')
  if (!form.wageStartMonth) missing.push('欠薪时间段')
  if (form.hasArbitration === null) missing.push('是否已完成劳动仲裁')
  return missing
}

// =====================================================================
// Vue 组件
// =====================================================================
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

      intakeForm: {
        name:           '',    // 姓名
        workLocation:   '',    // 工作地址
        employerType:   '',    // 用工方描述（自由填写，原始字符串）
        wageAmount:     '',    // 欠薪金额（元）
        wageStartMonth: '',    // 欠薪开始月份 yyyy-MM
        wageEndMonth:   '',    // 欠薪结束月份 yyyy-MM
        hasArbitration: null,  // true | false | null
      },
    }
  },

  methods: {

    submitIntake() {
      this.currentStep = 'chat'
      this.$nextTick(() => {
        const summary = buildIntakeSummary(this.intakeForm)
        if (summary) {
          this.pushUserMessage(summary)
          this.callAgent()
        } else {
          this.pushAssistantMessage(
            '您好！我是您的法律咨询助手 👋\n请告诉我您的讨薪情况，比如您给谁干活、在哪里干活、欠了多少钱？我来帮您分析。'
          )
        }
      })
    },

    skipIntake() {
      this.currentStep = 'chat'
      this.$nextTick(() => {
        this.pushAssistantMessage(
          '您好！我是您的法律咨询助手 👋\n请告诉我您的讨薪情况，比如您给谁干活、在哪里干活、欠了多少钱？我来帮您分析。'
        )
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

      const apiMessages = this.messages
        .filter(m => !m.isSystem)
        .map(m => ({ role: m.role, content: m.content }))

      // 发送给后端的 user_info，字段名与之前保持一致
      // employerType 保持原始字符串传输，后端自行解析
      const intakeData = {
        name:            this.intakeForm.name           || null,
        work_location:   this.intakeForm.workLocation   || null,
        employer_type:   this.intakeForm.employerType   || null,
        wage_amount:     this.intakeForm.wageAmount     ? Number(this.intakeForm.wageAmount) : null,
        wage_period:     (this.intakeForm.wageStartMonth && this.intakeForm.wageEndMonth)
                           ? `${this.intakeForm.wageStartMonth} 至 ${this.intakeForm.wageEndMonth}`
                           : null,
        has_arbitration: this.intakeForm.hasArbitration,
      }

      try {
        const result = await callAgentAPI(apiMessages, intakeData)

        let finalReply = result.reply || ''
        finalReply = finalReply.replace(/<think>[\s\S]*?<\/think>/, '').trim()

        const missing = getMissingFields(this.intakeForm)
        if (missing.length > 0) {
          finalReply += `\n\n📝 **为了帮您更准确地分析，还需要了解：${missing.join('、')}，请补充说明。**`
        }

        // 联调时改为：const analysis = result.analysis ?? null
        const analysis = getMockAnalysis()

        this.pushAssistantMessage(finalReply, [], analysis)

      } catch (e) {
        console.error('API调用报错:', e)
        this.pushAssistantMessage('抱歉，暂时无法连接到服务器，请检查大模型后端是否启动。')
      } finally {
        this.isLoading = false
        this.$nextTick(() => this.scrollToBottom())
      }
    },

    pushUserMessage(content) {
      this.messages.push({ role: 'user', content })
      this.$nextTick(() => this.scrollToBottom())
    },

    pushAssistantMessage(content, quickReplies = [], analysis = null) {
      this.messages.push({ role: 'assistant', content, quickReplies, analysis, cardOpen: true })
      this.$nextTick(() => this.scrollToBottom())
    },

    sendQuickReply(reply) {
      this.userInput = reply
      this.sendMessage()
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
      this.intakeForm = {
        name: '', workLocation: '', employerType: '',
        wageAmount: '', wageStartMonth: '', wageEndMonth: '', hasArbitration: null,
      }
      this.currentStep = 'welcome'
    },
  },
}
</script>

<style>
:root {
  --primary:    #E85D26;
  --primary-bg: #FFF5F0;
  --text-dark:  #1A1A1A;
  --text-mid:   #555;
  --text-light: #888;
  --bg:         #F7F4EF;
  --surface:    #FFFFFF;
  --border:     #E8E0D5;
  --shadow:     0 2px 12px rgba(0,0,0,0.08);
  --radius:     16px;
  --font-body:  'Noto Sans SC', 'Microsoft YaHei', sans-serif;
  --blue-lt:  #D6EAF8; --blue-dk:  #1A5276;
  --green-lt: #D5F5E3; --green-dk: #1E8449;
  --amber-lt: #FDEBD0; --amber-dk: #935116;
  --red-lt:   #FADBD8; --red-dk:   #C0392B;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

.app-wrapper {
  display: flex; flex-direction: column;
  height: 100vh; max-width: 480px;
  margin: 0 auto; background: var(--bg);
  font-family: var(--font-body);
}

/* Header */
.app-header {
  display: flex; align-items: center; gap: 10px;
  padding: 14px 18px; background: var(--primary);
  color: white; box-shadow: 0 2px 8px rgba(232,93,38,0.3); flex-shrink: 0;
}
.header-text h1 { font-size: 20px; }
.header-text p  { font-size: 12px; opacity: .85; }
.header-badge   { margin-left: auto; background: white; color: var(--primary); padding: 3px 10px; border-radius: 20px; font-size: 12px; }

.app-main { flex: 1; overflow: hidden; display: flex; flex-direction: column; }

/* 欢迎页 */
.welcome-screen { flex: 1; display: flex; flex-direction: column; align-items: center; padding: 32px 24px; overflow-y: auto; }
.hero-emoji      { font-size: 64px; margin-bottom: 16px; }
.welcome-hero h2 { color: var(--primary); margin-bottom: 10px; font-size: 22px; }
.hero-sub        { color: var(--text-mid); text-align: center; line-height: 1.6; margin-bottom: 20px; }
.welcome-promises { background: white; border-radius: 16px; padding: 16px; width: 100%; margin-bottom: 20px; }
.promise-item   { padding: 8px 0; border-bottom: 1px solid var(--border); font-size: 15px; }
.promise-item:last-child { border-bottom: none; }
.btn-start      { width: 100%; padding: 18px; background: var(--primary); color: white; border: none; border-radius: 16px; font-size: 18px; font-weight: bold; cursor: pointer; transition: opacity .15s; }
.btn-start:hover { opacity: .9; }
.disclaimer     { font-size: 11px; color: var(--text-light); margin-top: 16px; text-align: center; }

/* 表单页 */
.intake-screen { flex: 1; display: flex; flex-direction: column; overflow-y: auto; padding: 20px 20px 0; }
.intake-header { margin-bottom: 20px; }
.intake-step-label { font-size: 12px; font-weight: 700; letter-spacing: .06em; color: var(--primary); margin-bottom: 6px; }
.intake-title  { font-size: 20px; color: var(--text-dark); margin-bottom: 6px; }
.intake-sub    { font-size: 13px; color: var(--text-light); }
.intake-form   { display: flex; flex-direction: column; gap: 16px; }

.form-item  { display: flex; flex-direction: column; gap: 6px; }
.form-label { font-size: 14px; font-weight: 600; color: var(--text-dark); display: flex; align-items: center; gap: 6px; }
.label-icon { font-size: 16px; }

.form-input {
  width: 100%; padding: 11px 14px;
  border: 1.5px solid var(--border); border-radius: 12px;
  background: white; font-family: var(--font-body); font-size: 15px; color: var(--text-dark);
  outline: none; transition: border-color .15s;
}
.form-input:focus { border-color: var(--primary); }
.form-input::placeholder { color: #bbb; }

.input-with-unit { position: relative; display: flex; align-items: center; }
.input-with-unit .form-input { padding-right: 36px; }
.input-unit { position: absolute; right: 14px; font-size: 14px; color: var(--text-light); pointer-events: none; }

.date-range-row { display: flex; align-items: center; gap: 8px; }
.date-input     { flex: 1; }
.date-sep       { font-size: 14px; color: var(--text-light); white-space: nowrap; }

/* 仲裁切换按钮（仅第6项保留） */
.toggle-group { display: flex; gap: 8px; }
.toggle-btn {
  flex: 1; padding: 10px 8px;
  border: 1.5px solid var(--border); border-radius: 12px;
  background: white; font-family: var(--font-body); font-size: 14px;
  color: var(--text-mid); cursor: pointer; transition: all .15s;
}
.toggle-btn:hover  { border-color: var(--primary); color: var(--primary); }
.toggle-btn.active { border-color: var(--primary); background: var(--primary-bg); color: var(--primary); font-weight: 700; }

.intake-actions { padding: 20px 0 28px; display: flex; flex-direction: column; gap: 10px; }
.btn-skip {
  width: 100%; padding: 14px; background: none;
  border: 1.5px solid var(--border); border-radius: 16px;
  font-family: var(--font-body); font-size: 15px; color: var(--text-light); cursor: pointer;
  transition: border-color .15s, color .15s;
}
.btn-skip:hover { border-color: var(--text-mid); color: var(--text-mid); }

/* 对话页 */
.chat-screen        { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
.messages-container { flex: 1; overflow-y: auto; padding: 16px 14px; }
.message-group      { margin-bottom: 16px; }
.message-row        { display: flex; align-items: flex-end; gap: 8px; }
.message-row.user   { flex-direction: row-reverse; }

.avatar           { width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.assistant-avatar { background: var(--primary); color: white; }
.user-avatar      { background: #6B7280; }

.bubble           { max-width: 78%; padding: 12px 16px; border-radius: 16px; font-size: 15px; line-height: 1.6; box-shadow: var(--shadow); }
.bubble.assistant { background: white; border-bottom-left-radius: 4px; }
.bubble.user      { background: var(--primary); color: white; border-bottom-right-radius: 4px; }

.loading-bubble   { display: flex; gap: 5px; padding: 14px 18px; }
.dot              { width: 8px; height: 8px; border-radius: 50%; background: var(--primary); animation: bounce 1.2s infinite; }
.dot:nth-child(2) { animation-delay: .2s; }
.dot:nth-child(3) { animation-delay: .4s; }
@keyframes bounce { 0%,60%,100%{transform:translateY(0);opacity:.6;}30%{transform:translateY(-6px);opacity:1;} }

/* 分析卡片 */
.analysis-card { margin: 8px 0 0 44px; background: white; border: 1px solid var(--border); border-radius: 14px; overflow: hidden; box-shadow: var(--shadow); }
.card-header   { display: flex; align-items: center; justify-content: space-between; padding: 12px 16px; background: #FFF5F0; border-bottom: 1px solid var(--border); cursor: pointer; user-select: none; }
.card-title    { font-size: 14px; font-weight: 700; color: var(--primary); }
.card-toggle   { font-size: 12px; color: var(--text-light); }
.card-section  { padding: 14px 16px; border-bottom: 1px solid var(--border); }
.card-section:last-child { border-bottom: none; }
.section-label { font-size: 12px; font-weight: 700; padding: 3px 10px; border-radius: 20px; display: inline-block; margin-bottom: 12px; }
.section-label.blue  { background: var(--blue-lt);  color: var(--blue-dk);  }
.section-label.green { background: var(--green-lt); color: var(--green-dk); }
.section-label.amber { background: var(--amber-lt); color: var(--amber-dk); }
.section-label.red   { background: var(--red-lt);   color: var(--red-dk);   }

.info-grid  { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.info-item  { background: #F7F4EF; border-radius: 8px; padding: 8px 10px; }
.info-label { display: block; font-size: 11px; color: var(--text-light); margin-bottom: 2px; }
.info-value { display: block; font-size: 14px; font-weight: 500; color: var(--text-dark); }

.path-list { display: flex; flex-direction: column; gap: 8px; }
.path-item { display: flex; align-items: flex-start; gap: 10px; padding: 10px 12px; border-radius: 10px; border: 1px solid var(--border); background: #FAFAFA; }
.path-item.recommended { border-color: var(--green-dk); background: var(--green-lt); }
.path-step { width: 24px; height: 24px; border-radius: 50%; flex-shrink: 0; background: var(--text-light); color: white; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 700; }
.path-item.recommended .path-step { background: var(--green-dk); }
.path-name { font-size: 14px; font-weight: 600; color: var(--text-dark); margin-bottom: 3px; }
.path-desc { font-size: 12px; color: var(--text-mid); line-height: 1.5; }
.tag-recommend { display: inline-block; margin-left: 6px; font-size: 11px; font-weight: 700; padding: 1px 7px; border-radius: 10px; background: var(--green-dk); color: white; }

.evidence-list { display: flex; flex-direction: column; gap: 8px; }
.evidence-item { display: flex; align-items: center; gap: 10px; padding: 10px 12px; border-radius: 10px; border: 1px solid var(--border); background: #FAFAFA; }
.ev-icon    { font-size: 18px; flex-shrink: 0; }
.ev-content { flex: 1; min-width: 0; }
.ev-name    { font-size: 13px; font-weight: 600; color: var(--text-dark); }
.ev-tip     { font-size: 11px; color: var(--text-light); margin-top: 2px; line-height: 1.4; }
.ev-badge   { flex-shrink: 0; font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 10px; }
.ev-badge.key        { background: var(--red-lt);  color: var(--red-dk);  }
.ev-badge.supplement { background: var(--blue-lt); color: var(--blue-dk); }

.law-list { display: flex; flex-direction: column; gap: 8px; }
.law-item { padding: 10px 12px; border-radius: 10px; border-left: 3px solid var(--red-dk); background: var(--red-lt); }
.law-title   { font-size: 12px; font-weight: 700; color: var(--red-dk); margin-bottom: 5px; }
.law-content { font-size: 12px; color: var(--text-mid); line-height: 1.6; }

/* 输入区 */
.input-area { padding: 10px 14px 12px; background: white; border-top: 1px solid var(--border); flex-shrink: 0; }
.input-row  { display: flex; gap: 10px; align-items: flex-end; }
.input-box  { flex: 1; padding: 10px; border: 2px solid var(--border); border-radius: 12px; resize: none; background: var(--bg); min-height: 44px; font-family: var(--font-body); font-size: 15px; }
.input-box:focus { outline: none; border-color: var(--primary); background: white; }
.send-btn   { width: 60px; height: 44px; background: var(--primary); color: white; border: none; border-radius: 12px; font-weight: bold; cursor: pointer; font-size: 15px; }
.send-btn:disabled { opacity: .5; cursor: not-allowed; }

/* 底部导航 */
.bottom-nav { display: flex; background: white; border-top: 1px solid var(--border); padding: 5px 0; flex-shrink: 0; }
.nav-item   { flex: 1; display: flex; flex-direction: column; align-items: center; background: none; border: none; padding: 5px; color: var(--text-mid); cursor: pointer; font-family: var(--font-body); font-size: 12px; }
.nav-icon   { font-size: 20px; }

/* 弹窗 */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: flex-end; z-index: 100; }
.modal-box     { width: 100%; max-width: 480px; margin: 0 auto; background: white; border-radius: 20px 20px 0 0; padding: 24px; }
.modal-box h3  { margin-bottom: 16px; font-size: 18px; }
.modal-box li  { padding: 10px 0; border-bottom: 1px solid var(--border); font-size: 14px; }
.btn-primary   { width: 100%; padding: 15px; background: var(--primary); color: white; border: none; border-radius: 12px; font-size: 16px; font-weight: bold; margin-top: 15px; cursor: pointer; }
.hotline-item  { display: flex; justify-content: space-between; align-items: center; padding: 15px 0; border-bottom: 1px solid var(--border); }
.hotline-number { color: var(--primary); font-size: 22px; font-weight: bold; text-decoration: none; }

/* 动画 */
.fade-enter-active, .fade-leave-active   { transition: opacity .25s; }
.fade-enter-from,   .fade-leave-to       { opacity: 0; }
.modal-enter-active, .modal-leave-active { transition: transform .3s ease; }
.modal-enter-from,   .modal-leave-to     { transform: translateY(100%); }
</style>
