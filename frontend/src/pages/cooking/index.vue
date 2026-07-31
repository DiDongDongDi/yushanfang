<template>
  <view class="container">
    <view class="header">
      <text class="title">本次做饭</text>
      <view class="header-right">
        <button class="ai-optimize-btn" @click="summaryPlan" :loading="summarizing">
          <text class="btn-icon">✨</text>
          <text>AI 生成菜谱</text>
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

    <!-- 每道菜单独生成菜谱 -->
    <view v-if="cart.length > 0" class="dish-cards">
      <view v-for="(dish, idx) in cart" :key="idx" class="dish-card">
        <view class="dish-card-header">
          <text class="dish-name">{{ dish.name }}</text>
          <button v-if="!dish.recipe" class="gen-btn" :loading="generatingIdx === idx" @click="generateOne(idx)">
            AI 生成菜谱
          </button>
          <text v-else class="gen-done">✓ 已生成</text>
        </view>
        <view v-if="dish.recipe" class="dish-recipe">
          <view class="recipe-section">
            <text class="recipe-title">🛒 买菜清单</text>
            <view v-for="(item, sidx) in parseBuyList(dish.recipe.buy_list)" :key="sidx" class="step-item" @click="toggleDishBuy(idx, sidx)">
              <view class="step-check" :class="{ done: dish.buyDone?.[sidx] }">✓</view>
              <text class="step-text" :class="{ done: dish.buyDone?.[sidx] }">{{ item }}</text>
            </view>
            <text v-if="!dish.recipe.buy_list" class="recipe-content">暂无</text>
          </view>
          <view class="recipe-section">
            <text class="recipe-title">🔪 备菜步骤</text>
            <view v-for="(step, sidx) in (dish.recipe.prep_steps || '').split('\n').filter(Boolean)" :key="sidx" class="step-item" @click="toggleDishPrep(idx, sidx)">
              <view class="step-check" :class="{ done: dish.prepDone?.[sidx] }">✓</view>
              <text class="step-text" :class="{ done: dish.prepDone?.[sidx] }">{{ step }}</text>
            </view>
            <text v-if="!dish.recipe.prep_steps" class="recipe-content">暂无</text>
          </view>
          <view class="recipe-section">
            <text class="recipe-title">🍳 做法</text>
            <view v-for="(step, sidx) in parseCookSteps(dish.recipe.cook_steps)" :key="sidx" class="step-item" @click="toggleDishCook(idx, sidx)">
              <view class="step-check" :class="{ done: dish.cookDone?.[sidx] }">✓</view>
              <text class="step-text" :class="{ done: dish.cookDone?.[sidx] }">{{ step.text }}</text>
            </view>
            <text v-if="!dish.recipe.cook_steps" class="recipe-content">暂无</text>
          </view>
        </view>
      </view>
    </view>

    <!-- AI 汇总结果 -->
    <view v-if="summary && cart.length > 0" class="summary">
      <view class="summary-banner">📊 综合菜谱（已优化多菜流程）</view>

      <view class="section">
        <view class="section-title">🛒 买菜清单</view>
        <view v-if="summaryBuyList.length" class="steps-list">
          <view v-for="(item, idx) in summaryBuyList" :key="idx" class="step-item" @click="toggleBuy(idx)">
            <view class="step-check" :class="{ done: buyDone[idx] }">✓</view>
            <text class="step-text" :class="{ done: buyDone[idx] }">{{ item }}</text>
          </view>
        </view>
        <text v-else class="section-content">{{ summary.buy_list }}</text>
      </view>

      <view class="section">
        <view class="section-title">🔪 备菜步骤</view>
        <view v-if="summaryPrepList.length" class="steps-list">
          <view v-for="(step, idx) in summaryPrepList" :key="idx" class="step-item" @click="toggleStep(idx, 'prep')">
            <view class="step-check" :class="{ done: prepDone[idx] }">✓</view>
            <text class="step-text" :class="{ done: prepDone[idx] }">{{ step }}</text>
          </view>
        </view>
        <text v-else class="section-content">{{ summary.prep_steps }}</text>
      </view>

      <view class="section">
        <view class="section-title">🍳 烹饪步骤</view>
        <view v-if="summaryCookList.length" class="steps-list">
          <view v-for="(step, idx) in summaryCookList" :key="idx" class="step-item" @click="toggleStep(idx, 'cook')">
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
        <text v-else class="section-content">{{ summary.cook_steps }}</text>
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
const generatingIdx = ref(null)
const summarizing = ref(false)
const summary = ref(null)
const buyDone = ref({})
const prepDone = ref({})
const cookDone = ref({})
const timers = ref({})

const summaryBuyList = computed(() => parseBuyList(summary.value?.buy_list))
const summaryPrepList = computed(() => (summary.value?.prep_steps || '').split('\n').filter(Boolean))
const summaryCookList = computed(() => parseCookSteps(summary.value?.cook_steps))

function parseBuyList(text) {
  if (!text) return []
  return text.split('\n').filter(Boolean).map((line) => line.replace(/^[\d、.,\s-]+/, '').trim())
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

async function generateOne(idx) {
  const dish = cart.value[idx]
  generatingIdx.value = idx
  const res = await aiGenerateRecipe(dish.name)
  if (res.buy_list || res.prep_steps || res.cook_steps) {
    dish.recipe = {
      buy_list: res.buy_list || '',
      prep_steps: res.prep_steps || '',
      cook_steps: res.cook_steps || ''
    }
    dish.buyDone = {}
    dish.prepDone = {}
    dish.cookDone = {}
  } else if (res.error) {
    uni.showToast({ title: '生成失败，请检查 AI 配置', icon: 'none' })
  }
  cart.value.splice(idx, 1, dish)
  uni.setStorageSync('cart', cart.value)
  generatingIdx.value = null
}

function toggleDishBuy(dishIdx, itemIdx) {
  const dish = cart.value[dishIdx]
  if (!dish.buyDone) dish.buyDone = {}
  dish.buyDone[itemIdx] = !dish.buyDone[itemIdx]
  uni.setStorageSync('cart', cart.value)
}

function toggleDishPrep(dishIdx, itemIdx) {
  const dish = cart.value[dishIdx]
  if (!dish.prepDone) dish.prepDone = {}
  dish.prepDone[itemIdx] = !dish.prepDone[itemIdx]
  uni.setStorageSync('cart', cart.value)
}

function toggleDishCook(dishIdx, itemIdx) {
  const dish = cart.value[dishIdx]
  if (!dish.cookDone) dish.cookDone = {}
  dish.cookDone[itemIdx] = !dish.cookDone[itemIdx]
  uni.setStorageSync('cart', cart.value)
}

async function summaryPlan() {
  const ready = cart.value.filter((d) => d.recipe)
  if (!ready.length) {
    uni.showToast({ title: '请先为每道菜生成菜谱', icon: 'none' })
    return
  }
  summarizing.value = true
  const dishNames = ready.map((d) => d.name)
  const plans = ready.map((d) => d.recipe || {})
  const res = await aiOptimizePlan(dishNames, plans)
  summary.value = {
    buy_list: res.buy_list || '',
    prep_steps: res.prep_steps || '',
    cook_steps: res.cook_steps || ''
  }
  buyDone.value = {}
  prepDone.value = {}
  cookDone.value = {}
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
.dish-tag { background: #fff3f0; color: #e74c3c; padding: 10rpx 20rpx; border-radius: 8rpx; font-size: 26rpx; }
.remove { margin-left: 10rpx; color: #999; }

.dish-cards { display: flex; flex-direction: column; gap: 20rpx; margin-bottom: 30rpx; }
.dish-card { background: #fff; border-radius: 16rpx; padding: 24rpx; }
.dish-card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16rpx; }
.dish-name { font-size: 32rpx; font-weight: bold; }
.gen-btn { background: #e74c3c; color: #fff; border-radius: 30rpx; font-size: 24rpx; padding: 8rpx 24rpx; border: none; }
.gen-done { color: #27ae60; font-size: 24rpx; }
.dish-recipe { background: #fafafa; border-radius: 12rpx; padding: 20rpx; }
.recipe-section { margin-bottom: 16rpx; }
.recipe-section:last-child { margin-bottom: 0; }
.recipe-title { font-size: 26rpx; font-weight: bold; color: #e74c3c; display: block; margin-bottom: 8rpx; }
.recipe-content { font-size: 24rpx; color: #666; white-space: pre-wrap; line-height: 1.7; }

.summary { margin-bottom: 30rpx; }
.summary-banner { background: linear-gradient(135deg, #e74c3c, #ff6b6b); color: #fff; text-align: center; padding: 16rpx; border-radius: 12rpx; font-size: 28rpx; font-weight: bold; margin-bottom: 20rpx; }
.section { background: #fff; border-radius: 16rpx; padding: 30rpx; margin-bottom: 24rpx; }
.section-title { font-size: 32rpx; font-weight: bold; margin-bottom: 16rpx; color: #e74c3c; }
.section-content { font-size: 28rpx; color: #333; white-space: pre-wrap; line-height: 1.8; }
.step-item { display: flex; align-items: flex-start; padding: 16rpx 0; border-bottom: 1rpx solid #f5f5f5; }
.step-check { width: 40rpx; height: 40rpx; border-radius: 50%; border: 2rpx solid #ddd; margin-right: 16rpx; display: flex; align-items: center; justify-content: center; font-size: 24rpx; color: #fff; flex-shrink: 0; }
.step-check.done { background: #e74c3c; border-color: #e74c3c; }
.step-text { flex: 1; font-size: 28rpx; line-height: 1.6; }
.step-text.done { text-decoration: line-through; color: #999; }
.step-content { flex: 1; }
.timer-row { margin-top: 10rpx; display: flex; align-items: center; gap: 16rpx; }
.timer-label { font-size: 24rpx; color: #e74c3c; }
.timer-btn { background: #e74c3c; color: #fff; font-size: 22rpx; padding: 4rpx 16rpx; border-radius: 8rpx; }
.bottom-bar { position: fixed; bottom: 0; left: 0; right: 0; background: #fff; padding: 20rpx 30rpx; box-shadow: 0 -2rpx 10rpx rgba(0,0,0,0.05); }
.btn-primary { background: #e74c3c; color: #fff; border-radius: 12rpx; }
.empty { color: #999; font-size: 26rpx; }
</style>
