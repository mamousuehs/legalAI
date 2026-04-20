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
          <button class="btn-start" @click="startChat">开始咨询 →</button>
          <p class="disclaimer">本工具仅供参考，不构成正式法律意见</p>
        </section>
      </transition>

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

              <!-- ━━━ 结构化分析卡片（仅 assistant 消息且有 analysis 数据时显示）━━━ -->
              <div v-if="msg.role === 'assistant' && msg.analysis" class="analysis-card">

                <!-- 标题栏 -->
                <div class="card-header" @click="msg.cardOpen = !msg.cardOpen">
                  <span class="card-title">📋 案件分析结果</span>
                  <span class="card-toggle">{{ msg.cardOpen ? '收起 ▲' : '展开 ▼' }}</span>
                </div>

                <div v-if="msg.cardOpen" class="card-body">

                  <!-- 1. 案件基本信息 -->
                  <div class="card-section">
                    <div class="section-label blue">📌 案件基本信息</div>
                    <div class="info-grid">
                      <div class="info-item" v-for="item in msg.analysis.caseInfo" :key="item.label">
                        <span class="info-label">{{ item.label }}</span>
                        <span class="info-value">{{ item.value }}</span>
                      </div>
                    </div>
                  </div>

                  <!-- 2. 维权路径建议 -->
                  <div class="card-section">
                    <div class="section-label green">🛤️ 建议维权路径</div>
                    <div class="path-list">
                      <div
                        class="path-item"
                        v-for="(path, i) in msg.analysis.legalPaths"
                        :key="i"
                        :class="path.recommended ? 'recommended' : ''"
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

                  <!-- 3. 所需证据清单 -->
                  <div class="card-section">
                    <div class="section-label amber">📁 所需证据清单</div>
                    <div class="evidence-list">
                      <div
                        class="evidence-item"
                        v-for="ev in msg.analysis.evidence"
                        :key="ev.name"
                      >
                        <span class="ev-icon">{{ ev.have ? '✅' : '⬜' }}</span>
                        <div class="ev-content">
                          <div class="ev-name">{{ ev.name }}</div>
                          <div class="ev-tip">{{ ev.tip }}</div>
                        </div>
                        <span class="ev-badge" :class="ev.importance">{{ ev.importance === 'key' ? '关键' : '补充' }}</span>
                      </div>
                    </div>
                  </div>

                  <!-- 4. 适用法条 -->
                  <div class="card-section">
                    <div class="section-label red">⚖️ 适用法条</div>
                    <div class="law-list">
                      <div class="law-item" v-for="law in msg.analysis.laws" :key="law.title">
                        <div class="law-title">{{ law.title }}</div>
                        <div class="law-content">{{ law.content }}</div>
                      </div>
                    </div>
                  </div>

                  <!-- 5. 争点识别 -->
                  <div class="card-section" v-if="msg.analysis.issues && msg.analysis.issues.length">
                    <div class="section-label purple">⚡ 争点识别</div>
                    <div class="issue-list">
                      <div
                        class="issue-item"
                        v-for="issue in msg.analysis.issues"
                        :key="issue.issue_code"
                      >
                        <div class="issue-header">
                          <span class="issue-name">{{ issue.issue_name }}</span>
                          <span class="issue-priority" :class="'priority-' + issue.priority">
                            {{ issue.priority === 1 ? '核心争点' : issue.priority === 2 ? '重要' : '一般' }}
                          </span>
                        </div>
                        <div class="issue-desc">{{ issue.description }}</div>
                        <div class="issue-triggers" v-if="issue.triggered_by && issue.triggered_by.length">
                          <span class="trigger-label">触发因素：</span>
                          <span class="trigger-tag" v-for="t in issue.triggered_by" :key="t">{{ t }}</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- 6. 要件匹配 -->
                  <div class="card-section" v-if="msg.analysis.element_matches && msg.analysis.element_matches.length">
                    <div class="section-label amber">🔍 要件匹配</div>
                    <div class="match-list">
                      <div
                        class="match-item"
                        v-for="match in msg.analysis.element_matches"
                        :key="match.element_name"
                      >
                        <div class="match-header">
                          <span class="match-name">{{ match.element_name }}</span>
                          <span class="match-status" :class="'status-' + match.status">
                            {{ { satisfied: '已满足', partial: '部分满足', insufficient: '证据不足', not_satisfied: '未满足' }[match.status] }}
                          </span>
                        </div>
                        <div class="match-facts" v-if="match.supporting_facts && match.supporting_facts.length">
                          <div class="match-sub-label">✅ 支持事实</div>
                          <div class="fact-tag" v-for="f in match.supporting_facts" :key="f">{{ f }}</div>
                        </div>
                        <div class="match-missing" v-if="match.missing_evidence && match.missing_evidence.length">
                          <div class="match-sub-label">⚠️ 缺失证据</div>
                          <div class="missing-tag" v-for="m in match.missing_evidence" :key="m">{{ m }}</div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- 7. IRAC 论证 -->
                  <div class="card-section" v-if="msg.analysis.irac_drafts && msg.analysis.irac_drafts.length">
                    <div class="section-label blue">📝 IRAC 论证</div>
                    <div class="irac-list">
                      <div
                        class="irac-item"
                        v-for="(irac, idx) in msg.analysis.irac_drafts"
                        :key="idx"
                      >
                        <div class="irac-toggle-header" @click="irac._open = !irac._open">
                          <span class="irac-issue-label">{{ irac.issue }}</span>
                          <span class="irac-toggle-btn">{{ irac._open ? '收起 ▲' : '展开 ▼' }}</span>
                        </div>
                        <div v-if="irac._open" class="irac-body">
                          <div class="irac-row">
                            <span class="irac-tag irac-r">规则</span>
                            <span class="irac-text">{{ irac.rule }}</span>
                          </div>
                          <div class="irac-row">
                            <span class="irac-tag irac-a">适用</span>
                            <span class="irac-text">{{ irac.application }}</span>
                          </div>
                          <div class="irac-row">
                            <span class="irac-tag irac-c">结论</span>
                            <span class="irac-text">{{ irac.conclusion }}</span>
                          </div>
                          <div class="irac-citations" v-if="irac.citations && irac.citations.length">
                            <span class="citation-item" v-for="c in irac.citations" :key="c">{{ c }}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- 8. 风险提示 -->
                  <div class="card-section" v-if="msg.analysis.verification && !msg.analysis.verification.passed">
                    <div class="section-label red">🚨 风险提示</div>
                    <div class="risk-list">
                      <div class="risk-group" v-if="msg.analysis.verification.missing_elements && msg.analysis.verification.missing_elements.length">
                        <div class="risk-group-label">缺失要件</div>
                        <div class="risk-item risk-danger" v-for="r in msg.analysis.verification.missing_elements" :key="r">{{ r }}</div>
                      </div>
                      <div class="risk-group" v-if="msg.analysis.verification.unsupported_claims && msg.analysis.verification.unsupported_claims.length">
                        <div class="risk-group-label">待补充主张</div>
                        <div class="risk-item risk-warn" v-for="r in msg.analysis.verification.unsupported_claims" :key="r">{{ r }}</div>
                      </div>
                      <div class="risk-group" v-if="msg.analysis.verification.consistency_warnings && msg.analysis.verification.consistency_warnings.length">
                        <div class="risk-group-label">一致性警告</div>
                        <div class="risk-item risk-warn" v-for="r in msg.analysis.verification.consistency_warnings" :key="r">{{ r }}</div>
                      </div>
                      <div class="risk-group" v-if="msg.analysis.verification.citation_errors && msg.analysis.verification.citation_errors.length">
                        <div class="risk-group-label">引用错误</div>
                        <div class="risk-item risk-danger" v-for="r in msg.analysis.verification.citation_errors" :key="r">{{ r }}</div>
                      </div>
                    </div>
                  </div>

                </div>
              </div>
              <!-- ━━━ 分析卡片结束 ━━━ -->

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

async function callAgentAPI(messages) {
  const lastUserText = messages[messages.length - 1].content
  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: lastUserText })
  })
  if (!response.ok) throw new Error(`API 请求失败: ${response.status}`)
  return await response.json()
}

// =====================================================================
// 假数据：模拟后端返回的结构化分析结果
// 联调时删掉这个函数，改为直接读取 result 中的真实字段即可
// =====================================================================
function getMockAnalysis() {
  return {
    // ── 1. 案件基本信息 ──────────────────────────────────────
    caseInfo: [
      { label: '当事人',   value: '张某某' },
      { label: '工作地点', value: '北京市朝阳区某建筑工地' },
      { label: '用工方',   value: '李老板（个人包工头）' },
      { label: '工种',     value: '瓦工' },
      { label: '欠薪金额', value: '¥ 18,000 元' },
      { label: '欠薪时段', value: '2024年10月—12月（3个月）' },
    ],

    // ── 2. 维权路径建议 ──────────────────────────────────────
    legalPaths: [
      {
        name: '向劳动监察部门投诉',
        desc: '拨打 12333 或前往当地劳动局，成本最低，处理速度较快，建议优先尝试。',
        recommended: true,
      },
      {
        name: '申请劳动仲裁',
        desc: '向劳动人事争议仲裁委员会提交申请，免费且具有法律效力，适合投诉无果后使用。',
        recommended: false,
      },
      {
        name: '向法院提起诉讼',
        desc: '持仲裁裁决书向法院起诉，可同时追加总包公司为共同被告，主张连带清偿。',
        recommended: false,
      },
    ],

    // ── 3. 所需证据清单 ──────────────────────────────────────
    evidence: [
      {
        name: '劳务合同 / 用工协议',
        tip: '如无书面合同，微信聊天记录确认雇佣关系也可使用',
        have: true,
        importance: 'key',
      },
      {
        name: '欠条 / 工资结算单',
        tip: '要求包工头补签欠条，注明金额和日期',
        have: false,
        importance: 'key',
      },
      {
        name: '工资转账记录',
        tip: '微信、支付宝或银行转账截图均可证明已支付部分',
        have: true,
        importance: 'key',
      },
      {
        name: '工牌 / 考勤记录',
        tip: '证明在该工地实际出勤的凭证',
        have: false,
        importance: 'supplement',
      },
      {
        name: '工友证人联系方式',
        tip: '可在仲裁或诉讼中出庭作证',
        have: false,
        importance: 'supplement',
      },
    ],

    // ── 4. 适用法条 ──────────────────────────────────────────
    laws: [
      {
        title: '《劳动法》第五十条',
        content: '工资应当以货币形式按月支付给劳动者本人，不得克扣或者无故拖欠劳动者的工资。',
      },
      {
        title: '《劳动合同法》第三十条',
        content: '用人单位应当按照劳动合同约定和国家规定，向劳动者及时足额支付劳动报酬。',
      },
      {
        title: '《保障农民工工资支付条例》第三十条',
        content: '分包单位拖欠农民工工资的，由施工总承包单位先行清偿，再依法进行追偿。',
      },
    ],

    // ── 5. 争点识别 ──────────────────────────────────────────
    issues: [
      {
        issue_code: 'ISSUE_001',
        issue_name: '劳动关系是否成立',
        description: '需确认用人单位与劳动者之间是否存在合法劳动关系，这是主张欠薪的前提。',
        priority: 1,
        triggered_by: ['未签书面合同', '口头雇佣'],
      },
      {
        issue_code: 'ISSUE_002',
        issue_name: '拖欠工资事实是否成立',
        description: '需确认用人单位实际拖欠工资的金额与时间段，是否有充分证据支撑。',
        priority: 1,
        triggered_by: ['3个月未发薪', '欠薪金额18000元'],
      },
      {
        issue_code: 'ISSUE_003',
        issue_name: '总包方是否承担连带责任',
        description: '若包工头无力偿还，可主张施工总承包单位承担连带清偿责任。',
        priority: 2,
        triggered_by: ['个人包工头', '建筑工地场景'],
      },
    ],

    // ── 6. 要件匹配 ──────────────────────────────────────────
    element_matches: [
      {
        issue_code: 'ISSUE_001',
        element_name: '存在劳动关系',
        status: 'partial',
        supporting_facts: ['有工资转账记录', '工友可作证'],
        supporting_authorities: ['劳动合同法第7条'],
        missing_evidence: ['书面劳动合同', '社保缴纳记录'],
      },
      {
        issue_code: 'ISSUE_002',
        element_name: '拖欠工资金额明确',
        status: 'satisfied',
        supporting_facts: ['欠薪18000元已明确', '时间段2024年10月—12月'],
        supporting_authorities: ['劳动法第50条'],
        missing_evidence: [],
      },
      {
        issue_code: 'ISSUE_003',
        element_name: '总包方连带责任',
        status: 'insufficient',
        supporting_facts: [],
        supporting_authorities: ['保障农民工工资支付条例第30条'],
        missing_evidence: ['总包公司名称及联系方式', '分包合同复印件'],
      },
    ],

    // ── 7. IRAC 论证 ──────────────────────────────────────────
    irac_drafts: [
      {
        issue: '劳动关系认定',
        rule: '根据《劳动合同法》第7条，用人单位自用工之日起即与劳动者建立劳动关系，无需以书面合同为前提。',
        application: '本案中虽无书面合同，但存在工资转账记录及工友证言，可初步证明双方存在事实劳动关系。',
        conclusion: '劳动关系可初步认定，建议补充社保记录或考勤记录以强化证据链。',
        citations: ['劳动合同法第7条', '最高法劳动争议司法解释（一）第1条'],
        _open: true,
      },
      {
        issue: '拖欠工资违法认定',
        rule: '《劳动法》第50条规定，用人单位不得无故拖欠劳动者工资；《劳动合同法》第30条要求及时足额支付。',
        application: '用人单位连续3个月未支付工资共计18000元，已构成无故拖欠，符合违法情形。',
        conclusion: '用人单位行为违法，劳动者可向劳动监察部门投诉或申请劳动仲裁，要求支付欠薪及25%经济补偿。',
        citations: ['劳动法第50条', '劳动合同法第30条', '违反和解除劳动合同的经济补偿办法第3条'],
        _open: false,
      },
    ],

    // ── 8. 风险提示 ──────────────────────────────────────────
    verification: {
      passed: false,
      citation_errors: [],
      missing_elements: ['书面劳动合同或替代证明材料'],
      unsupported_claims: ['总包方连带责任主张目前缺乏合同依据，需补充分包合同'],
      consistency_warnings: ['请确认欠薪金额是否包含加班费，前后陈述需保持一致'],
    },
  }
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
    }
  },

  methods: {
    startChat() {
      this.currentStep = 'chat'
      this.$nextTick(() => {
        this.pushAssistantMessage(
          '您好！我是您的法律咨询助手 👋\n请告诉我您的讨薪情况，比如您给谁干活？在哪里干活？欠了多少钱？我来帮您分析。'
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

      try {
        const result = await callAgentAPI(apiMessages)

        // 剥离 <think> 标签
        let finalReply = result.reply || ''
        finalReply = finalReply.replace(/<think>[\s\S]*?<\/think>/, '').trim()

        // ── 结构化分析数据 ────────────────────────────────────
        // 当前用假数据；联调时替换为：
        //   const analysis = result.analysis ?? null
        // 如果后端还没有 analysis 字段，保持 getMockAnalysis() 即可
        const analysis = getMockAnalysis()   // ← 联调时换成 result.analysis ?? null

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

    // analysis 参数：传入结构化数据对象，或 null（不展示卡片）
    pushAssistantMessage(content, quickReplies = [], analysis = null) {
      this.messages.push({
        role: 'assistant',
        content,
        quickReplies,
        analysis,
        cardOpen: true,   // 卡片默认展开
      })
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

    sendQuickReply(reply) {
      this.userInput = reply
      this.sendMessage()
    },
  },
}
</script>

<style>
/* ===== 基础变量 ===== */
:root {
  --primary:    #E85D26;
  --primary-bg: #FFF5F0;
  --secondary:  #2D6A4F;
  --text-dark:  #1A1A1A;
  --text-mid:   #555;
  --text-light: #888;
  --bg:         #F7F4EF;
  --surface:    #FFFFFF;
  --border:     #E8E0D5;
  --shadow:     0 2px 12px rgba(0,0,0,0.08);
  --radius:     16px;
  --font-body:  'Noto Sans SC', 'Microsoft YaHei', sans-serif;

  /* 卡片色系 */
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

/* ── Header ── */
.app-header {
  display: flex; align-items: center; gap: 10px;
  padding: 14px 18px; background: var(--primary);
  color: white; box-shadow: 0 2px 8px rgba(232,93,38,0.3);
}
.header-text h1 { font-size: 20px; }
.header-text p  { font-size: 12px; opacity: .85; }
.header-badge   { margin-left: auto; background: white; color: var(--primary); padding: 3px 10px; border-radius: 20px; font-size: 12px; }

/* ── Main ── */
.app-main { flex: 1; overflow: hidden; display: flex; flex-direction: column; }

/* ── Welcome ── */
.welcome-screen { flex: 1; display: flex; flex-direction: column; align-items: center; padding: 32px 24px; }
.hero-emoji     { font-size: 64px; margin-bottom: 16px; }
.welcome-hero h2 { color: var(--primary); margin-bottom: 10px; }
.hero-sub        { color: var(--text-mid); text-align: center; line-height: 1.5; margin-bottom: 20px; }
.welcome-promises { background: white; border-radius: 16px; padding: 16px; width: 100%; margin-bottom: 20px; }
.promise-item   { padding: 8px 0; border-bottom: 1px solid var(--border); }
.btn-start      { width: 100%; padding: 18px; background: var(--primary); color: white; border: none; border-radius: 16px; font-size: 18px; font-weight: bold; cursor: pointer; }
.disclaimer     { font-size: 11px; color: var(--text-light); margin-top: 16px; }

/* ── Chat ── */
.chat-screen        { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
.messages-container { flex: 1; overflow-y: auto; padding: 16px 14px; }

/* message-group 包裹气泡 + 分析卡片 */
.message-group { margin-bottom: 16px; }

.message-row      { display: flex; align-items: flex-end; gap: 8px; }
.message-row.user { flex-direction: row-reverse; }

.avatar            { width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.assistant-avatar  { background: var(--primary); color: white; }
.user-avatar       { background: #6B7280; }

.bubble            { max-width: 78%; padding: 12px 16px; border-radius: 16px; font-size: 15px; line-height: 1.6; box-shadow: var(--shadow); }
.bubble.assistant  { background: white; border-bottom-left-radius: 4px; }
.bubble.user       { background: var(--primary); color: white; border-bottom-right-radius: 4px; }

.loading-bubble    { display: flex; gap: 5px; padding: 14px 18px; }
.dot               { width: 8px; height: 8px; border-radius: 50%; background: var(--primary); animation: bounce 1.2s infinite; }
.dot:nth-child(2)  { animation-delay: .2s; }
.dot:nth-child(3)  { animation-delay: .4s; }
@keyframes bounce  { 0%,60%,100% { transform: translateY(0); opacity:.6; } 30% { transform: translateY(-6px); opacity:1; } }

/* ── 分析卡片 ── */
.analysis-card {
  margin: 8px 0 0 44px;   /* 与 avatar 宽度对齐 */
  background: white;
  border: 1px solid var(--border);
  border-radius: 14px;
  overflow: hidden;
  box-shadow: var(--shadow);
}

.card-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 16px;
  background: #FFF5F0;
  border-bottom: 1px solid var(--border);
  cursor: pointer; user-select: none;
}
.card-title  { font-size: 14px; font-weight: 700; color: var(--primary); }
.card-toggle { font-size: 12px; color: var(--text-light); }

.card-body { padding: 0; }

/* 每个区块 */
.card-section { padding: 14px 16px; border-bottom: 1px solid var(--border); }
.card-section:last-child { border-bottom: none; }

.section-label {
  font-size: 12px; font-weight: 700;
  padding: 3px 10px; border-radius: 20px;
  display: inline-block; margin-bottom: 12px;
}
.section-label.blue   { background: var(--blue-lt);  color: var(--blue-dk);  }
.section-label.green  { background: var(--green-lt); color: var(--green-dk); }
.section-label.amber  { background: var(--amber-lt); color: var(--amber-dk); }
.section-label.red    { background: var(--red-lt);   color: var(--red-dk);   }

/* 1. 案件信息网格 */
.info-grid  { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.info-item  { background: #F7F4EF; border-radius: 8px; padding: 8px 10px; }
.info-label { display: block; font-size: 11px; color: var(--text-light); margin-bottom: 2px; }
.info-value { display: block; font-size: 14px; font-weight: 500; color: var(--text-dark); }

/* 2. 维权路径 */
.path-list { display: flex; flex-direction: column; gap: 8px; }
.path-item {
  display: flex; align-items: flex-start; gap: 10px;
  padding: 10px 12px; border-radius: 10px;
  border: 1px solid var(--border); background: #FAFAFA;
}
.path-item.recommended { border-color: var(--green-dk); background: var(--green-lt); }
.path-step {
  width: 24px; height: 24px; border-radius: 50%; flex-shrink: 0;
  background: var(--text-light); color: white;
  display: flex; align-items: center; justify-content: center;
  font-size: 12px; font-weight: 700;
}
.path-item.recommended .path-step { background: var(--green-dk); }
.path-name { font-size: 14px; font-weight: 600; color: var(--text-dark); margin-bottom: 3px; }
.path-desc { font-size: 12px; color: var(--text-mid); line-height: 1.5; }
.tag-recommend {
  display: inline-block; margin-left: 6px;
  font-size: 11px; font-weight: 700;
  padding: 1px 7px; border-radius: 10px;
  background: var(--green-dk); color: white;
}

/* 3. 证据清单 */
.evidence-list { display: flex; flex-direction: column; gap: 8px; }
.evidence-item {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 12px; border-radius: 10px;
  border: 1px solid var(--border); background: #FAFAFA;
}
.ev-icon    { font-size: 18px; flex-shrink: 0; }
.ev-content { flex: 1; min-width: 0; }
.ev-name    { font-size: 13px; font-weight: 600; color: var(--text-dark); }
.ev-tip     { font-size: 11px; color: var(--text-light); margin-top: 2px; line-height: 1.4; }
.ev-badge   { flex-shrink: 0; font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 10px; }
.ev-badge.key        { background: var(--red-lt);   color: var(--red-dk);   }
.ev-badge.supplement { background: var(--blue-lt);  color: var(--blue-dk);  }

/* 4. 法条 */
.law-list { display: flex; flex-direction: column; gap: 8px; }
.law-item {
  padding: 10px 12px; border-radius: 10px;
  border-left: 3px solid var(--red-dk);
  background: var(--red-lt);
}
.law-title   { font-size: 12px; font-weight: 700; color: var(--red-dk); margin-bottom: 5px; }
.law-content { font-size: 12px; color: var(--text-mid); line-height: 1.6; }

/* ── 输入区 ── */
.input-area { padding: 10px 14px 12px; background: white; border-top: 1px solid var(--border); }
.input-row  { display: flex; gap: 10px; align-items: flex-end; }
.input-box  { flex: 1; padding: 10px; border: 2px solid var(--border); border-radius: 12px; resize: none; background: var(--bg); min-height: 44px; font-family: var(--font-body); font-size: 15px; }
.input-box:focus { outline: none; border-color: var(--primary); background: white; }
.send-btn   { width: 60px; height: 44px; background: var(--primary); color: white; border: none; border-radius: 12px; font-weight: bold; cursor: pointer; font-size: 15px; }
.send-btn:disabled { opacity: .5; cursor: not-allowed; }

/* ── 底部导航 ── */
.bottom-nav { display: flex; background: white; border-top: 1px solid var(--border); padding: 5px 0; }
.nav-item   { flex: 1; display: flex; flex-direction: column; align-items: center; background: none; border: none; padding: 5px; color: var(--text-mid); cursor: pointer; font-family: var(--font-body); font-size: 12px; }
.nav-icon   { font-size: 20px; }

/* ── 弹窗 ── */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: flex-end; z-index: 100; }
.modal-box     { width: 100%; max-width: 480px; margin: 0 auto; background: white; border-radius: 20px 20px 0 0; padding: 24px; }
.modal-box h3  { margin-bottom: 16px; font-size: 18px; }
.modal-box li  { padding: 10px 0; border-bottom: 1px solid var(--border); font-size: 14px; }
.btn-primary   { width: 100%; padding: 15px; background: var(--primary); color: white; border: none; border-radius: 12px; font-size: 16px; font-weight: bold; margin-top: 15px; cursor: pointer; }
.hotline-item  { display: flex; justify-content: space-between; align-items: center; padding: 15px 0; border-bottom: 1px solid var(--border); }
.hotline-number { color: var(--primary); font-size: 22px; font-weight: bold; text-decoration: none; }

/* ── 过渡动画 ── */
.fade-enter-active, .fade-leave-active { transition: opacity .3s; }
.fade-enter-from, .fade-leave-to       { opacity: 0; }
.modal-enter-active, .modal-leave-active { transition: transform .3s ease; }
.modal-enter-from, .modal-leave-to       { transform: translateY(100%); }

/* ── 5. 争点识别 ── */
.section-label.purple { background: #EDE9FB; color: #4A3A9E; }
.issue-list { display: flex; flex-direction: column; gap: 8px; }
.issue-item { border: 1px solid var(--border); border-radius: 10px; padding: 10px 12px; background: #FAFAFA; }
.issue-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 5px; }
.issue-name { font-size: 13px; font-weight: 600; color: var(--text-dark); }
.issue-priority { font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 10px; flex-shrink: 0; }
.priority-1 { background: #FADBD8; color: #C0392B; }
.priority-2 { background: #FDEBD0; color: #935116; }
.priority-3 { background: #D6EAF8; color: #1A5276; }
.issue-desc { font-size: 12px; color: var(--text-mid); line-height: 1.5; margin-bottom: 6px; }
.issue-triggers { display: flex; flex-wrap: wrap; align-items: center; gap: 5px; }
.trigger-label { font-size: 11px; color: var(--text-light); }
.trigger-tag { font-size: 11px; background: #EDE9FB; color: #4A3A9E; padding: 2px 8px; border-radius: 10px; }

/* ── 6. 要件匹配 ── */
.match-list { display: flex; flex-direction: column; gap: 8px; }
.match-item { border: 1px solid var(--border); border-radius: 10px; padding: 10px 12px; background: #FAFAFA; }
.match-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px; }
.match-name { font-size: 13px; font-weight: 600; color: var(--text-dark); }
.match-status { font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 10px; flex-shrink: 0; }
.status-satisfied    { background: #D5F5E3; color: #1E8449; }
.status-partial      { background: #FDEBD0; color: #935116; }
.status-insufficient { background: #FADBD8; color: #C0392B; }
.status-not_satisfied { background: #EAECEE; color: #555; }
.match-sub-label { font-size: 11px; color: var(--text-light); margin-bottom: 4px; margin-top: 6px; }
.match-facts, .match-missing { display: flex; flex-wrap: wrap; gap: 4px; flex-direction: column; }
.fact-tag { font-size: 11px; background: #D5F5E3; color: #1E8449; padding: 2px 8px; border-radius: 10px; display: inline-block; width: fit-content; }
.missing-tag { font-size: 11px; background: #FADBD8; color: #C0392B; padding: 2px 8px; border-radius: 10px; display: inline-block; width: fit-content; }

/* ── 7. IRAC 论证 ── */
.section-label.blue { background: #D6EAF8; color: #1A5276; }
.irac-list { display: flex; flex-direction: column; gap: 8px; }
.irac-item { border: 1px solid var(--border); border-radius: 10px; overflow: hidden; }
.irac-toggle-header { display: flex; align-items: center; justify-content: space-between; padding: 10px 12px; background: #F0F4F8; cursor: pointer; user-select: none; }
.irac-issue-label { font-size: 13px; font-weight: 600; color: #1A5276; }
.irac-toggle-btn { font-size: 11px; color: var(--text-light); }
.irac-body { padding: 10px 12px; display: flex; flex-direction: column; gap: 8px; background: white; }
.irac-row { display: flex; gap: 8px; align-items: flex-start; }
.irac-tag { font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 10px; flex-shrink: 0; margin-top: 1px; }
.irac-r { background: #D6EAF8; color: #1A5276; }
.irac-a { background: #D5F5E3; color: #1E8449; }
.irac-c { background: #FDEBD0; color: #935116; }
.irac-text { font-size: 12px; color: var(--text-mid); line-height: 1.6; }
.irac-citations { display: flex; flex-wrap: wrap; gap: 5px; padding-top: 4px; border-top: 1px solid var(--border); }
.citation-item { font-size: 11px; background: #F0F4F8; color: #1A5276; padding: 2px 8px; border-radius: 10px; }

/* ── 8. 风险提示 ── */
.risk-list { display: flex; flex-direction: column; gap: 10px; }
.risk-group { display: flex; flex-direction: column; gap: 5px; }
.risk-group-label { font-size: 11px; font-weight: 700; color: var(--text-light); margin-bottom: 2px; }
.risk-item { font-size: 12px; padding: 8px 12px; border-radius: 8px; line-height: 1.5; }
.risk-danger { background: #FADBD8; color: #C0392B; border-left: 3px solid #C0392B; border-radius: 0 8px 8px 0; }
.risk-warn   { background: #FDEBD0; color: #935116; border-left: 3px solid #E67E22; border-radius: 0 8px 8px 0; }
</style>
