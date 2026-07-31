<template>
  <view class="container">
    <view class="header">
      <text class="title">本次做饭</text>
      <view class="header-right">
        <button class="ai-optimize-btn" @click="summaryPlan" :loading="summarizing">
          <text class="btn-icon">✨</text>
          <text>汇总生成步骤</text>
        </button>
      </view>
    </view>

    <view class="dishes-list">
      <view v-for="(dish, idx) in cart" :key="idx" class="dish-tag" @click="showDishDetail(idx)">
        <text>{{ dish.name }}</text>
        <text class="remove" @click.stop="removeDish(idx)">×</text>
      </view>
      <text v-if="cart.length === 0" class="empty">暂无菜品，去点菜吧</text>
    </view>

    <!-- 点击标签查看的菜谱详情 -->
    <view v-if="selectedDish" class="dish-detail">
      <view class="detail-header">
        <text class="detail-title">{{ selectedDish.name }} 的菜谱</text>
        <text class="detail-close" @click="selectedDish = null">×</text>
      </view>
      <template v-if="selectedDish.recipe">
        <view class="section">
          <view class="section-title">🛒 需要买的菜</view>
          <view class="checklist">
            <view v-for="(item, i) in detailBuyList" :key="i" class="check-item" @click="detailBuyDone[i] = !detailBuyDone[i]">
              <view class="step-check" :class="{ done: detailBuyDone[i] }">✓</view>
              <text class="step-text" :class="{ done: detailBuyDone[i] }">{{ item }}</text>
            </view>
          </view>
        </view>
        <view class="section">
          <view class="section-title">🔪 备菜步骤</view>
          <view class="checklist">
            <view v-for="(step, i) in detailPrepList" :key="i" class="check-item" @click="detailPrepDone[i] = !detailPrepDone[i]">
              <view class="step-check" :class="{ done: detailPrepDone[i] }">✓</view>
              <text class="step-text" :class="{ done: detailPrepDone[i] }">{{ step }}</text>
            </view>
          </view>
        </view>
        <view class="section">
          <view class="section-title">🍳 烹饪做法</view>
          <view class="checklist">
            <view v-for="(step, i) in detailCookList" :key="i" class="check-item" @click="detailCookDone[i] = !detailCookDone[i]">
              <view class="step-check" :class="{ done: detailCookDone[i] }">✓</view>
              <text class="step-text" :class="{ done: detailCookDone[i] }">{{ step }}</text>
            </view>
          </view>
        </view>
      </template>
      <view v-else class="section">
        <text class="section-content">该菜品尚未生成菜谱</text>
      </view>
    </view>

    <!-- AI 汇总结果（生成中实时显示） -->
    <view v-if="(summary || summarizing) && cart.length > 0" class="summary">
      <view class="summary-banner">📊 综合菜谱（已优化多菜流程）</view>

      <view class="section">
        <view class="section-title">🛒 买菜清单</view>
        <view v-if="summaryBuyList.length" class="steps-list">
          <view v-for="(item, idx) in summaryBuyList" :key="idx" class="step-item" @click="toggleBuy(idx)">
            <view class="step-check" :class="{ done: buyDone[idx] }">✓</view>
            <text class="step-text" :class="{ done: buyDone[idx] }">{{ item }}</text>
          </view>
        </view>
        <text v-else class="section-content generating-text">{{ summary?.buy_list || summarizing ? '正在生成...' : '' }}</text>
      </view>

      <view class="section">
        <view class="section-title">🔪 备菜步骤</view>
        <view v-if="summaryPrepList.length" class="steps-list">
          <view v-for="(step, idx) in summaryPrepList" :key="idx" class="step-item" @click="toggleStep(idx, 'prep')">
            <view class="step-check" :class="{ done: prepDone[idx] }">✓</view>
            <text class="step-text" :class="{ done: prepDone[idx] }">{{ step }}</text>
          </view>
        </view>
        <text v-else class="section-content generating-text">{{ summary?.prep_steps || summarizing ? '正在生成...' : '' }}</text>
      </view>

      <view class="section">
        <view class="section-title">🍳 烹饪步骤</view>
        <view v-if="summaryCookList.length" class="steps-list">
          <view v-for="(step, idx) in summaryCookList" :key="idx" class="step-item" @click="toggleStep(idx, 'cook')">
            <view class="step-check" :class="{ done: cookDone[idx] }">✓</view>
            <view class="step-content">
              <text class="step-text" :class="{ done: cookDone[idx] }">{{ step.text || step }}</text>
            </view>
            <view v-if="step.minutes > 0" class="timer-row">
              <button class="timer-btn" size="mini" @click.stop="startTimer(step.minutes, idx)">
                {{ timers[idx] ? `${timers[idx]}s` : '开始倒计时' }}
              </button>
            </view>
          </view>
        </view>
        <text v-else class="section-content generating-text">{{ summary?.cook_steps || summarizing ? '正在生成...' : '' }}</text>
      </view>
    </view>

    <view v-if="cart.length > 0" class="bottom-bar">
      <button class="btn-primary" @click="finishCooking">完成做饭</button>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { aiGenerateRecipe, aiOptimizePlan, createRecord, createSteps } from '@/api'

const cart = ref(uni.getStorageSync('cart') || [])
const summarizing = ref(false)
const summary = ref(null)
const buyDone = ref({})
const prepDone = ref({})
const cookDone = ref({})
const timers = ref({})
const selectedDish = ref(null)
const detailBuyDone = ref({})
const detailPrepDone = ref({})
const detailCookDone = ref({})

const detailBuyList = computed(() => parseBuyList(selectedDish.value?.recipe?.buy_list || ''))
const detailPrepList = computed(() => (selectedDish.value?.recipe?.prep_steps || '').split('\n').filter(Boolean).map(s => s.replace(/^[\d、.,\s-]+/, '').trim()).filter(Boolean))
const detailCookList = computed(() => parseCookSteps(selectedDish.value?.recipe?.cook_steps || '').map(s => s.text))

function showDishDetail(idx) {
  selectedDish.value = cart.value[idx]
  detailBuyDone.value = {}
  detailPrepDone.value = {}
  detailCookDone.value = {}
}

const summaryBuyList = computed(() => parseBuyList(summary.value?.buy_list || ''))
const summaryPrepList = computed(() => (summary.value?.prep_steps || '').split('\n').filter(Boolean))
const summaryCookList = computed(() => parseCookSteps(summary.value?.cook_steps || ''))

// 从流式文本解析三部分
function parseStreamingSummary(text) {
  let buy = '', prep = '', cook = ''
  const buyMatch = text.match(/"buy_list"\s*:\s*"([\s\S]*?)"(?=\s*,\s*"prep)/)
  if (buyMatch) buy = buyMatch[1].replace(/\\n/g, '\n').replace(/\\"/g, '"')
  const prepMatch = text.match(/"prep_steps"\s*:\s*"([\s\S]*?)"(?=\s*,\s*"cook)/)
  if (prepMatch) prep = prepMatch[1].replace(/\\n/g, '\n').replace(/\\"/g, '"')
  const cookMatch = text.match(/"cook_steps"\s*:\s*"([\s\S]*?)"(?=\s*})/)
  if (cookMatch) cook = cookMatch[1].replace(/\\n/g, '\n').replace(/\\"/g, '"')
  return { buy_list: buy, prep_steps: prep, cook_steps: cook }
}

function parseBuyList(text) {
  if (!text) return []
  return text.split('\n').filter(Boolean).map((line) => line.replace(/^[\d、.,\s-]+/, '').trim()).filter(Boolean)
}

function parseCookSteps(text) {
  if (!text) return []
  return text.split('\n').filter(Boolean).map((line) => {
    const match = line.match(/(\d+)\s*分钟/)
    return { text: line, minutes: match ? Number(match[1]) : 0 }
  })
}

function removeDish(idx) {
  cart.value.splice(idx, 1)
  uni.setStorageSync('cart', cart.value)
}

async function summaryPlan() {
  const ready = cart.value.filter((d) => d.recipe)
  if (!ready.length) {
    uni.showModal({
      title: '提示',
      content: '所有菜品均未生成菜谱，请先在菜品详情页生成菜谱',
      showCancel: false
    })
    return
  }
  summarizing.value = true
  summary.value = { buy_list: '', prep_steps: '', cook_steps: '' }
  buyDone.value = {}
  prepDone.value = {}
  cookDone.value = {}
  timers.value = {}

  // #ifdef H5
  try {
    const token = uni.getStorageSync('token')
    const dishNames = ready.map((d) => d.name)
    const plans = ready.map((d) => d.recipe || {})
    const resp = await fetch('/api/ai/optimize-plan/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ dishes: dishNames, plans })
    })
    if (!resp.ok || !resp.body) throw new Error('流式请求失败')

    const reader = resp.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    let fullText = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })

      let idx
      while ((idx = buffer.indexOf('\n\n')) !== -1) {
        const event = buffer.slice(0, idx)
        buffer = buffer.slice(idx + 2)
        if (event.startsWith('data:')) {
          const data = event.slice(5).trim()
          try {
            const json = JSON.parse(data)
            if (json.type === 'chunk') {
              fullText += json.content
              const parsed = parseStreamingSummary(fullText)
              summary.value = { ...summary.value, ...parsed }
            } else if (json.type === 'done') {
              summary.value = json.result || {}
            }
          } catch (e) { /* 忽略 */ }
        }
      }
    }
  } catch (e) {
    uni.showToast({ title: '汇总失败，请重试', icon: 'none' })
  }
  // #endif

  // #ifndef H5
  const dishNames = ready.map((d) => d.name)
  const plans = ready.map((d) => d.recipe || {})
  const res = await aiOptimizePlan(dishNames, plans)
  summary.value = {
    buy_list: res.buy_list || '',
    prep_steps: res.prep_steps || '',
    cook_steps: res.cook_steps || ''
  }
  // #endif

  summarizing.value = false
}

function toggleBuy(idx) {
  buyDone.value[idx] = !buyDone.value[idx]
}

function toggleStep(idx, type) {
  if (type === 'prep') {
    prepDone.value[idx] = !prepDone.value[idx]
  } else {
    cookDone.value[idx] = !cookDone.value[idx]
  }
}

function startTimer(minutes, idx) {
  const totalSeconds = minutes * 60
  timers.value[idx] = totalSeconds
  const timer = setInterval(() => {
    timers.value[idx]--
    if (timers.value[idx] <= 0) {
      clearInterval(timer)
      uni.showToast({ title: '倒计时结束！', icon: 'none' })
    }
  }, 1000)
}

async function finishCooking() {
  const dishIds = cart.value.map((d) => d.id).filter(Boolean)
  const record = await createRecord(dishIds)
  if (record.id) {
    const steps = summaryCookList.value.map((s, i) => ({
      title: s.text,
      detail: s.text,
      timer_minutes: s.minutes,
      sort_order: i
    }))
    await createSteps(record.id, steps)
  }
  uni.removeStorageSync('cart')
  uni.showToast({ title: '做饭完成！', icon: 'success' })
  setTimeout(() => {
    uni.switchTab({ url: '/pages/index/index' })
  }, 800)
}
</script>

<style scoped>
.container { padding: 30rpx; padding-bottom: 160rpx; }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30rpx; }
.title { font-size: 40rpx; font-weight: bold; flex: 1; }
.header-right { display: flex; align-items: center; }
.ai-optimize-btn { background: linear-gradient(135deg, #e74c3c, #ff6b6b); color: #fff; border-radius: 40rpx; font-size: 26rpx; padding: 12rpx 28rpx; display: flex; align-items: center; gap: 8rpx; box-shadow: 0 4rpx 12rpx rgba(231, 76, 60, 0.3); border: none; }
.btn-icon { font-size: 28rpx; }
.dishes-list { display: flex; flex-wrap: wrap; gap: 16rpx; margin-bottom: 30rpx; }
.dish-tag { background: #fff3f0; color: #e74c3c; padding: 10rpx 20rpx; border-radius: 8rpx; font-size: 26rpx; display: flex; align-items: center; gap: 8rpx; }
.remove { margin-left: 4rpx; color: #999; }

.dish-detail { background: #fff; border-radius: 16rpx; padding: 24rpx; margin-bottom: 30rpx; }
.detail-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20rpx; }
.detail-title { font-size: 32rpx; font-weight: bold; }
.detail-close { font-size: 40rpx; color: #999; padding: 0 10rpx; }
.checklist { padding: 0; }
.check-item { display: flex; align-items: flex-start; padding: 16rpx 0; border-bottom: 1rpx solid #f5f5f5; }
.check-item:last-child { border-bottom: none; }

.summary { margin-bottom: 30rpx; }
.summary-banner { background: linear-gradient(135deg, #e74c3c, #ff6b6b); color: #fff; text-align: center; padding: 16rpx; border-radius: 12rpx; font-size: 28rpx; font-weight: bold; margin-bottom: 20rpx; }
.generating-text { color: #999; font-style: italic; }
.section { background: #fff; border-radius: 16rpx; padding: 30rpx; margin-bottom: 24rpx; }
.section-title { font-size: 32rpx; font-weight: bold; margin-bottom: 16rpx; color: #e74c3c; }
.section-content { font-size: 28rpx; color: #333; white-space: pre-wrap; line-height: 1.8; }
.step-item { display: flex; align-items: flex-start; padding: 16rpx 0; border-bottom: 1rpx solid #f5f5f5; }
.step-check { width: 40rpx; height: 40rpx; border-radius: 50%; border: 2rpx solid #ddd; margin-right: 16rpx; display: flex; align-items: center; justify-content: center; font-size: 24rpx; color: #fff; flex-shrink: 0; }
.step-check.done { background: #e74c3c; border-color: #e74c3c; }
.step-text { flex: 1; font-size: 28rpx; line-height: 1.6; }
.step-text.done { text-decoration: line-through; color: #999; }
.step-content { flex: 1; }
.timer-row { display: flex; align-items: center; gap: 16rpx; margin-left: auto; flex-shrink: 0; }
.timer-label { font-size: 24rpx; color: #e74c3c; }
.timer-btn { background: #e74c3c; color: #fff; font-size: 22rpx; padding: 8rpx 20rpx; border-radius: 8rpx; white-space: nowrap; }
.bottom-bar { position: fixed; bottom: 0; left: 0; right: 0; background: #fff; padding: 20rpx 30rpx; box-shadow: 0 -2rpx 10rpx rgba(0,0,0,0.05); }
.btn-primary { background: #e74c3c; color: #fff; border-radius: 12rpx; }
.empty { color: #999; font-size: 26rpx; }
</style>
