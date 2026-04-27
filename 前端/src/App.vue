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
                placeholder="例：张三（包工头）或某建筑公司"
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
                这笔钱是您哪段时间干活的工资？
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

            <div class="form-item limitation-section">
              <label class="form-label">
                <span class="label-icon">⏰</span>
                老板原本【最晚】该在什么时候发这笔钱给您？
              </label>
              <input 
                class="form-input" 
                type="month" 
                v-model="intakeForm.wageDueDate" 
              />
              
              <div v-if="intakeForm.wageDueDate" class="fade-in-question">
                <p style="margin: 10px 0; font-size: 14px; color: #555;">在那之后，您有没有向老板讨要过这笔钱（如微信催要、录音等），并且能找到证据？</p>
                <div class="toggle-group">
                  <button class="toggle-btn" :class="{ active: intakeForm.hasDemanded === true }" @click="intakeForm.hasDemanded = true">有去要过</button>
                  <button class="toggle-btn" :class="{ active: intakeForm.hasDemanded === false }" @click="intakeForm.hasDemanded = false">没要过/没证据</button>
                </div>
              </div>

              <div v-if="intakeForm.hasDemanded === true" class="fade-in-question">
                <p style="margin: 10px 0; font-size: 14px; color: #555;">从第一次讨要开始，直到现在，您是一直在断断续续地催老板给钱吗？</p>
                <div class="toggle-group">
                  <button class="toggle-btn" :class="{ active: intakeForm.isContinuousDemand === true }" @click="intakeForm.isContinuousDemand = true">是的，一直在催</button>
                  <button class="toggle-btn" :class="{ active: intakeForm.isContinuousDemand === false }" @click="intakeForm.isContinuousDemand = false">不是</button>
                </div>
              </div>

              <div v-if="intakeForm.isContinuousDemand === true" class="fade-in-question">
                <p style="margin: 10px 0; font-size: 14px; color: #555;">在这期间，有没有哪两次讨要之间，中间停了 <b style="color:#e65100">超过 3 年</b> 没去管它？</p>
                <div class="toggle-group">
                  <button class="toggle-btn" :class="{ active: intakeForm.hasLongGap === true }" @click="intakeForm.hasLongGap = true">有停过3年以上</button>
                  <button class="toggle-btn" :class="{ active: intakeForm.hasLongGap === false }" @click="intakeForm.hasLongGap = false">没有，经常催</button>
                </div>
              </div>
            </div>

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

              <div v-if="intakeForm.hasArbitration === false" class="fade-in-question">
                <p style="margin: 10px 0; font-size: 14px; color: #555;">
                  从老板本该发工资那天（或者您离职那天）算起，到现在 <b style="color:#e65100">超过 1 年</b> 了吗？
                </p>
                <div class="toggle-group">
                  <button class="toggle-btn" :class="{ active: intakeForm.isOverOneYear === false }" @click="intakeForm.isOverOneYear = false">没有超1年</button>
                  <button class="toggle-btn" :class="{ active: intakeForm.isOverOneYear === true }" @click="intakeForm.isOverOneYear = true">已超过1年</button>
                </div>
              </div>

              <div v-if="intakeForm.hasArbitration === false && intakeForm.isOverOneYear === true" class="fade-in-question">
                <p style="margin: 10px 0; font-size: 14px; color: #555;">
                  超过 1 年不要紧！在这期间，您有没有去催老板给钱、或者找过劳动局（并且留下了微信记录或录音等证据）？
                </p>
                <div class="toggle-group">
                  <button class="toggle-btn" :class="{ active: intakeForm.hasDemandedInOneYear === true }" @click="intakeForm.hasDemandedInOneYear = true">有证据去要过</button>
                  <button class="toggle-btn" :class="{ active: intakeForm.hasDemandedInOneYear === false }" @click="intakeForm.hasDemandedInOneYear = false">没要过/没证据</button>
                </div>
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
            <div class="doc-actions">
              <p class="doc-hint" :class="{ warning: shouldRecommendArbitrationDoc }">
                {{ documentHelperText }}
              </p>
              <button
                class="doc-btn"
                @click="generateWordDocument"
                :disabled="isLoading || isGeneratingDoc || !canGenerateWord"
              >
                <span v-if="!isGeneratingDoc">{{ documentButtonText }}</span>
                <span v-else>生成中...</span>
              </button>
            </div>
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

function buildCaseInputPayload(messages, intakeData) {
  return {
    messages,
    extracted_info: intakeData,
    case_type_hint: 'taoxin',
  }
}

async function callAgentAPI(messages, intakeData) {
  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(buildCaseInputPayload(messages, intakeData))
  })
  if (!response.ok) {
    const errorText = await response.text()
    throw new Error(`API 请求失败: ${response.status} ${errorText}`)
  }
  return await response.json()
}

async function downloadDocumentWordAPI(messages, intakeData) {
  const response = await fetch(`${API_BASE_URL}/api/generate-document-docx`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(buildCaseInputPayload(messages, intakeData))
  })
  if (!response.ok) {
    const errorText = await response.text()
    throw new Error(`Word 文书生成失败: ${response.status} ${errorText}`)
  }

  const blob = await response.blob()
  const filename = extractFilenameFromDisposition(response.headers.get('Content-Disposition'))
  return {
    blob,
    filename: filename || '劳动维权申请书.docx',
  }
}

function extractFilenameFromDisposition(contentDisposition) {
  if (!contentDisposition) return ''

  const utf8Match = contentDisposition.match(/filename\*=UTF-8''([^;]+)/i)
  if (utf8Match && utf8Match[1]) {
    return decodeURIComponent(utf8Match[1])
  }

  const plainMatch = contentDisposition.match(/filename="?([^";]+)"?/i)
  return plainMatch && plainMatch[1] ? plainMatch[1] : ''
}

function normalizeEvidenceTypes(evidenceTypes) {
  if (Array.isArray(evidenceTypes)) return evidenceTypes
  if (typeof evidenceTypes !== 'string') return []

  return evidenceTypes
    .split(/[、，,]/)
    .map(item => item.trim())
    .filter(Boolean)
}

function hasContractEvidence(contractStatus) {
  return contractStatus === true || contractStatus === '有'
}


// =====================================================================
// 将表单内容拼成自然语言，作为对话首条消息（已加入严密之时效逻辑）
// =====================================================================
function buildIntakeSummary(form) {
  const parts = []
  if (form.name)         parts.push(`我叫${form.name}`)
  if (form.workLocation) parts.push(`在${form.workLocation}工作`)
  if (form.employerType) parts.push(`给"${form.employerType}"干活`)
  if (form.wageAmount)   parts.push(`被拖欠工资共 ${form.wageAmount} 元`)
  
  // 拖欠哪段时期的工资
  if (form.wageStartMonth && form.wageEndMonth) {
    parts.push(`这笔钱是 ${form.wageStartMonth} 至 ${form.wageEndMonth} 期间干活的工资`)
  } else if (form.wageStartMonth) {
    parts.push(`从 ${form.wageStartMonth} 开始欠薪`)
  }

  // 时效逻辑转化
  if (form.wageDueDate) {
    parts.push(`这笔钱本来最晚该在 ${form.wageDueDate} 发给我`)
    if (form.hasDemanded === false) {
      parts.push(`但我之后一直没有去要过，或者没有留下讨要的证据`)
    } else if (form.hasDemanded === true) {
      parts.push(`之后我有去讨要过并且有证据`)
      if (form.isContinuousDemand === true) {
        if (form.hasLongGap === false) {
          parts.push(`从那以后我一直在断断续续地催，两次催要之间从来没有间隔超过3年`)
        } else if (form.hasLongGap === true) {
          parts.push(`虽然我一直在催，但中间有一次停了超过3年没去管`)
        }
      } else if (form.isContinuousDemand === false) {
        parts.push(`但并没有一直持续去催要`)
      }
    }
  }

  // 仲裁及1年时效逻辑转化
  if (form.hasArbitration === true) {
    parts.push('我已经完成了劳动仲裁')
  } else if (form.hasArbitration === false) {
    let arbStr = '我尚未进行劳动仲裁'
    if (form.isOverOneYear === false) {
      arbStr += '，且距离发生欠薪到现在还没超过 1 年'
    } else if (form.isOverOneYear === true) {
      arbStr += '，距离发生欠薪到现在已经超过 1 年了'
      if (form.hasDemandedInOneYear === true) {
        arbStr += '（但我这期间有去讨要过，且有证据）'
      } else if (form.hasDemandedInOneYear === false) {
        arbStr += '（并且我这期间一直没去要过，或者拿不出讨要的证据）'
      }
    }
    parts.push(arbStr)
  }
  if (parts.length === 0) return null
  return parts.join('，') + '。请结合劳动争议时效帮我分析如何维权。'
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
      isGeneratingDoc: false,

      // 联调关键：记住后端的提问阶段
      currentStage: 'initial', 
      extractedInfoState: {},

      intakeForm: {
        name:           '',    // 姓名
        workLocation:   '',    // 工作地址
        employerType:   '',    // 用工方描述
        wageAmount:     '',    // 欠薪金额（元）
        wageStartMonth: '',    // 欠薪开始月份 yyyy-MM
        wageEndMonth:   '',    // 欠薪结束月份 yyyy-MM
        hasArbitration: null,  // true | false | null
        
        // 新增：时效审查字段
        wageDueDate: '',           // 本该发工资的日期
        hasDemanded: null,         // 是否有过追讨
        isContinuousDemand: null,  // 是否持续追讨
        hasLongGap: null,          // 间隔是否超过3年
        // 👇 新增：1年仲裁时效变量
          isOverOneYear: null,          // 超过1年了吗？
          hasDemandedInOneYear: null,   // 期间有要过吗？
      },
    }
  },

  computed: {
    apiMessages() {
      return this.messages
        .filter(m => !m.isSystem)
        .map(m => ({ role: m.role, content: m.content }))
    },

    currentIntakeData() {
      return {
        ...this.extractedInfoState,
        name: this.intakeForm.name || this.extractedInfoState.name || null,
        work_location: this.intakeForm.workLocation || this.extractedInfoState.work_location || null,
        employer_type: this.intakeForm.employerType || this.extractedInfoState.employer_type || null,
        wage_amount: this.intakeForm.wageAmount
          ? Number(this.intakeForm.wageAmount)
          : (this.extractedInfoState.wage_amount ?? null),
        wage_period: (this.intakeForm.wageStartMonth && this.intakeForm.wageEndMonth)
          ? `${this.intakeForm.wageStartMonth} 至 ${this.intakeForm.wageEndMonth}`
          : (this.extractedInfoState.wage_period || null),
        has_arbitration: this.intakeForm.hasArbitration ?? this.extractedInfoState.has_arbitration ?? null,
        is_over_one_year: this.intakeForm.isOverOneYear ?? null,
        has_demanded_in_one_year: this.intakeForm.hasDemandedInOneYear ?? null,
        // 把时效数据传给后端
        wage_due_date: this.intakeForm.wageDueDate || null,
        has_demanded: this.intakeForm.hasDemanded ?? null,
        is_continuous_demand: this.intakeForm.isContinuousDemand ?? null,
        has_long_gap: this.intakeForm.hasLongGap ?? null,
        
        _stage: this.currentStage,
      }
    },

    canGenerateWord() {
      return this.apiMessages.some(message => message.role === 'user')
    },

    shouldRecommendArbitrationDoc() {
      return this.currentIntakeData.has_arbitration === false
    },

    documentButtonText() {
      return this.shouldRecommendArbitrationDoc
        ? '生成仲裁申请书 Word'
        : '生成申请书 Word'
    },

    documentHelperText() {
      return this.shouldRecommendArbitrationDoc
        ? '您尚未完成劳动仲裁，建议优先生成并下载劳动仲裁申请书。'
        : '可根据当前对话直接生成 Word 文书并下载。'
    },
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

      const apiMessages = this.apiMessages
      const intakeData = this.currentIntakeData

      try {
        const result = await callAgentAPI(apiMessages, intakeData)

        if (result.conversation_stage) {
          this.currentStage = result.conversation_stage
        }
        if (result.extracted_info) {
          this.extractedInfoState = {
            ...this.extractedInfoState,
            ...result.extracted_info,
          }
        }

        let finalReply = result.reply || ''
        finalReply = finalReply.replace(/<think>[\s\S]*?<\/think>/, '').trim()

        const analysis = this.adaptRealDataToFrontend(result)
        this.pushAssistantMessage(finalReply, result.quick_replies || [], analysis)

      } catch (e) {
        console.error('API调用报错:', e)
        this.pushAssistantMessage('抱歉，暂时无法连接到服务器，请检查大模型后端是否启动。')
      } finally {
        this.isLoading = false
        this.$nextTick(() => this.scrollToBottom())
      }
    },

    async generateWordDocument() {
      if (!this.canGenerateWord || this.isGeneratingDoc) return

      this.isGeneratingDoc = true
      try {
        const { blob, filename } = await downloadDocumentWordAPI(this.apiMessages, this.currentIntakeData)
        const downloadUrl = URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = downloadUrl
        link.download = filename
        document.body.appendChild(link)
        link.click()
        link.remove()
        window.setTimeout(() => URL.revokeObjectURL(downloadUrl), 1000)
      } catch (e) {
        console.error('Word文书生成报错:', e)
        this.pushAssistantMessage('抱歉，暂时无法生成 Word 文书，请稍后重试。')
      } finally {
        this.isGeneratingDoc = false
      }
    },

    adaptRealDataToFrontend(response) {
      if (!response || !response.extracted_info) return null;
      
      const info = response.extracted_info || {};
      
      // 现在我们确信这两个函数一定存在了，因为我们把它们写在了最上面
      const evidenceTypes = normalizeEvidenceTypes(info.evidence_types);
                            
      const laws = (response.retrieved_authorities || [])
        .filter(auth => auth.source_type === 'norm' || auth.source_type === 'law')
        .map(auth => ({
          title: auth.title || '适用法条',
          content: auth.snippet || '暂无内容概要'
        }))
        
      const hasStructuredInfo = [
        info.worker_name, info.name, info.location, info.work_location,
        info.employer_name, info.employer_type, info.job_title,
        info.amount, info.wage_amount, info.time_period, info.wage_period,
      ].some(Boolean)

      if (!hasStructuredInfo && !laws.length && !(response.issues || []).length) {
        return null
      }

      const hasArbitration = info.has_arbitration ?? this.currentIntakeData.has_arbitration
      const legalPaths = hasArbitration === false
        ? [
            { name: '申请劳动仲裁', desc: '您尚未完成劳动仲裁，建议先生成仲裁申请书并向劳动人事争议仲裁委员会提交。', recommended: true },
            { name: '向劳动监察部门投诉', desc: '拨打 12333 或前往当地劳动局，可与仲裁程序并行补充维权。', recommended: false },
            { name: '向法院提起诉讼', desc: '通常需要在仲裁裁决或终局处理后，再进入诉讼程序。', recommended: false },
          ]
        : [
            { name: '向劳动监察部门投诉', desc: '拨打 12333 或前往当地劳动局，成本最低，建议优先尝试。', recommended: true },
            { name: '申请劳动仲裁', desc: '向劳动人事争议仲裁委员会提交申请，免费且具有法律效力。', recommended: false },
            { name: '向法院提起诉讼', desc: '持仲裁裁决书向法院起诉，可追加总包公司为共同被告。', recommended: false },
          ]
      
      return {
        caseInfo: [
          { label: '当事人',   value: info.worker_name || info.name || '待补充' },
          { label: '工作地点', value: info.location || info.work_location || '待补充' },
          { label: '用工方',   value: info.employer_name || info.employer_type || '待补充' },
          { label: '工种',     value: info.job_title || '待补充' },
          { label: '欠薪金额', value: info.amount || info.wage_amount || '待补充' },
          { label: '欠薪时段', value: info.time_period || info.wage_period || '待补充' },
        ],
        legalPaths,
        evidence: [
          { name: '劳务合同 / 用工协议', tip: '如无书面合同，微信聊天记录也可使用', 
            have: hasContractEvidence(info.has_contract), importance: 'key' },
          { name: '欠条 / 工资结算单',   tip: '要求包工头补签欠条，注明金额和日期',  
            have: evidenceTypes.includes('欠条') || evidenceTypes.includes('工资结算单'), importance: 'key' },
          { name: '工资转账记录',        tip: '微信、支付宝或银行转账截图均可',      
            have: evidenceTypes.includes('转账记录') || evidenceTypes.includes('工资转账记录'), importance: 'key' },
        ],
        laws,
      };
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
      this.extractedInfoState = {}
      this.intakeForm = {
        name: '', workLocation: '', employerType: '', wageAmount: '', 
        wageStartMonth: '', wageEndMonth: '', hasArbitration: null,
        wageDueDate: '', hasDemanded: null, isContinuousDemand: null, hasLongGap: null,hasArbitration: null, isOverOneYear: null, hasDemandedInOneYear: null,
      }
      this.currentStep = 'welcome'
      this.currentStage = 'initial'
      this.isGeneratingDoc = false
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
.doc-actions { display: flex; flex-direction: column; gap: 8px; margin-bottom: 10px; }
.doc-hint { font-size: 12px; line-height: 1.5; color: var(--text-light); }
.doc-hint.warning { color: var(--red-dk); font-weight: 600; }
.doc-btn {
  width: 100%;
  padding: 12px 14px;
  border: none;
  border-radius: 12px;
  background: linear-gradient(135deg, #F59E0B, #E85D26);
  color: white;
  font-family: var(--font-body);
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 8px 20px rgba(232,93,38,0.18);
}
.doc-btn:disabled { opacity: .55; cursor: not-allowed; box-shadow: none; }
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

.fade-in-question {
  padding: 12px;
  margin-top: 10px;
  background-color: #fff9f5;
  border-left: 3px solid #ff7f50;
  border-radius: 4px;
  animation: slideDown 0.3s ease-out;
}

@keyframes slideDown {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
