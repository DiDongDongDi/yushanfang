<template>
  <view class="container">
    <view class="header">
      <text class="title">本次做饭</text>
      <view class="header-right">
        <button class="ai-optimize-btn" @click="optimizePlan" :loading="optimizing">
          <text class="btn-icon">✨</text>
          <text>AI 优化流程</text>
        </button>
      </view>
    </view>

    <view class="dishes-list">
      <view v-for="(dish, idx) in cart" :key="idx" class="dish-tag">
        <text>{{ dish.name }}</text>
        <text class="remove" @click="removeDish(idx)">×</text>
      </view>
      <text v-if="cart.length === 0" class="empty">暂无菜品，去点菜吧</text>
    </view>

    <view v-if="cart.length > 0" class="sections">
      <view class="section">
        <view class="section-title">🛒 买菜清单</view>
        <text class="section-content">{{ buyList || '点击"AI 优化流程"生成' }}</text>
      </view>

      <view class="section">
        <view class="section-title">🔪 备菜步骤</view>
        <view v-if="prepSteps" class="steps-list">
          <view v-for="(step, idx) in prepStepsList" :key="idx" class="step-item" @click="toggleStep(idx, 'prep')">
            <view class="step-check" :class="{ done: prepDone[idx] }">✓</view>
            <text class="step-text" :class="{ done: prepDone[idx] }">{{ step }}</text>
          </view>
        </view>
        <text v-else class="section-content">点击"AI 优化流程"生成</text>
      </view>

      <view class="section">
        <view class="section-title">🍳 烹饪步骤</view>
        <view v-if="cookSteps" class="steps-list">
          <view v-for="(step, idx) in cookStepsList" :key="idx" class="step-item" @click="toggleStep(idx, 'cook')">
            <view class="step-check" :class="{ done: cookDone[idx] }">✓</view>
            <view class="step-content">
              <text class="step-text" :class="{ done: cookDone[idx] }">{{ step.text }}</text>
              <view v-if="step.minutes > 0" class="timer-row">
                <text class="timer-label">{{ step.minutes }} 分钟</text>
                <button class="timer-btn" size="mini" @click.stop="startTimer(step.minutes, idx)">
                  {{ timers[idx] ? `${timers[idx]}s` : '开始倒计时' }}
                </button>
              </view>
            </view>
          </view>
        </view>
        <text v-else class="section-content">点击"AI 优化流程"生成</text>
      </view>
    </view>

    <view v-if="cart.length > 0" class="bottom-bar">
      <button class="btn-primary" @click="finishCooking">完成做饭</button>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { aiOptimizePlan, createRecord, createSteps } from '@/api'

const cart = ref(uni.getStorageSync('cart') || [])
const buyList = ref('')
const prepSteps = ref('')
const cookSteps = ref('')
const optimizing = ref(false)
const prepDone = ref({})
const cookDone = ref({})
const timers = ref({})

const prepStepsList = computed(() => (prepSteps.value || '').split('\n').filter(Boolean))
const cookStepsList = computed(() => parseCookSteps(cookSteps.value))

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

async function optimizePlan() {
  optimizing.value = true
  const dishNames = cart.value.map((d) => d.name)
  const plans = cart.value.map((d) => d.recipe || {})
  const res = await aiOptimizePlan(dishNames, plans)
  buyList.value = res.buy_list || ''
  prepSteps.value = res.prep_steps || ''
  cookSteps.value = res.cook_steps || ''
  optimizing.value = false
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
    const steps = cookStepsList.value.map((s, i) => ({
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
.dish-tag { background: #fff3f0; color: #e74c3c; padding: 10rpx 20rpx; border-radius: 8rpx; font-size: 26rpx; }
.remove { margin-left: 10rpx; color: #999; }
.section { background: #fff; border-radius: 16rpx; padding: 30rpx; margin-bottom: 24rpx; }
.section-title { font-size: 32rpx; font-weight: bold; margin-bottom: 16rpx; color: #e74c3c; }
.section-content { font-size: 28rpx; color: #333; white-space: pre-wrap; line-height: 1.8; }
.steps-list { }
.step-item { display: flex; align-items: flex-start; padding: 16rpx 0; border-bottom: 1rpx solid #f5f5f5; }
.step-check { width: 40rpx; height: 40rpx; border-radius: 50%; border: 2rpx solid #ddd; margin-right: 16rpx; display: flex; align-items: center; justify-content: center; font-size: 24rpx; color: #fff; }
.step-check.done { background: #e74c3c; border-color: #e74c3c; }
.step-text { flex: 1; font-size: 28rpx; line-height: 1.6; }
.step-text.done { text-decoration: line-through; color: #999; }
.timer-row { margin-top: 10rpx; display: flex; align-items: center; gap: 16rpx; }
.timer-label { font-size: 24rpx; color: #e74c3c; }
.timer-btn { background: #e74c3c; color: #fff; font-size: 22rpx; padding: 4rpx 16rpx; border-radius: 8rpx; }
.bottom-bar { position: fixed; bottom: 0; left: 0; right: 0; background: #fff; padding: 20rpx 30rpx; box-shadow: 0 -2rpx 10rpx rgba(0,0,0,0.05); }
.btn-primary { background: #e74c3c; color: #fff; border-radius: 12rpx; }
.empty { color: #999; font-size: 26rpx; }
</style>
