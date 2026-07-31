<template>
  <view class="container">
    <view class="header">
      <text class="title">烹饪记录详情</text>
      <text class="status">{{ record.status }}</text>
    </view>

    <view v-if="record.dishes_json" class="section">
      <view class="section-title">🍽️ 本次菜品</view>
      <view class="dishes-list">
        <text v-for="(name, idx) in dishes" :key="idx" class="dish-tag">{{ name }}</text>
      </view>
    </view>

    <view v-if="record.buy_list" class="section">
      <view class="section-title">🛒 买菜清单</view>
      <view v-for="(item, idx) in buyList" :key="idx" class="check-item" @click="toggle(idx, 'buy')">
        <view class="step-check" :class="{ done: buyDone[idx] }">✓</view>
        <text class="step-text" :class="{ done: buyDone[idx] }">{{ item }}</text>
      </view>
    </view>

    <view v-if="record.prep_steps" class="section">
      <view class="section-title">🔪 备菜步骤</view>
      <view v-for="(step, idx) in prepList" :key="idx" class="check-item" @click="toggle(idx, 'prep')">
        <view class="step-check" :class="{ done: prepDone[idx] }">✓</view>
        <text class="step-text" :class="{ done: prepDone[idx] }">{{ step }}</text>
      </view>
    </view>

    <view v-if="record.cook_steps" class="section">
      <view class="section-title">🍳 烹饪步骤</view>
      <view v-for="(step, idx) in cookList" :key="idx" class="check-item" @click="toggle(idx, 'cook')">
        <view class="step-check" :class="{ done: cookDone[idx] }">✓</view>
        <text class="step-text" :class="{ done: cookDone[idx] }">{{ step.text || step }}</text>
      </view>
    </view>

    <view v-if="!record.buy_list && !record.prep_steps && !record.cook_steps" class="empty">
      <text>该记录暂无详细内容</text>
    </view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { getRecord } from '@/api'

const recordId = ref(null)
const record = ref({})
const buyDone = ref({})
const prepDone = ref({})
const cookDone = ref({})

const dishes = computed(() => {
  try {
    return JSON.parse(record.value.dishes_json || '[]').map((id, i) => `菜品 ${i + 1}`)
  } catch (e) {
    return []
  }
})
const buyList = computed(() => (record.value.buy_list || '').split('\n').filter(Boolean).map(s => s.replace(/^[\d、.,\s-]+/, '').trim()).filter(Boolean))
const prepList = computed(() => (record.value.prep_steps || '').split('\n').filter(Boolean).map(s => s.replace(/^[\d、.,\s-]+/, '').trim()).filter(Boolean))
const cookList = computed(() => (record.value.cook_steps || '').split('\n').filter(Boolean).map(s => {
  const match = s.match(/(\d+)\s*分钟/)
  return { text: s, minutes: match ? Number(match[1]) : 0 }
}))

onLoad(async (options) => {
  recordId.value = Number(options.id || options.recordId || 0)
  if (recordId.value) {
    const res = await getRecord(recordId.value)
    record.value = res || {}
  }
})

function toggle(idx, type) {
  if (type === 'buy') buyDone.value[idx] = !buyDone.value[idx]
  else if (type === 'prep') prepDone.value[idx] = !prepDone.value[idx]
  else cookDone.value[idx] = !cookDone.value[idx]
}
</script>

<style scoped>
.container { padding: 30rpx; }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30rpx; }
.title { font-size: 40rpx; font-weight: bold; }
.status { color: #e74c3c; font-size: 26rpx; }
.section { background: #fff; border-radius: 16rpx; padding: 30rpx; margin-bottom: 24rpx; }
.section-title { font-size: 32rpx; font-weight: bold; margin-bottom: 16rpx; color: #e74c3c; }
.dishes-list { display: flex; flex-wrap: wrap; gap: 16rpx; }
.dish-tag { background: #fff3f0; color: #e74c3c; padding: 10rpx 20rpx; border-radius: 8rpx; font-size: 26rpx; }
.check-item { display: flex; align-items: flex-start; padding: 16rpx 0; border-bottom: 1rpx solid #f5f5f5; }
.step-check { width: 36rpx; height: 36rpx; border-radius: 50%; border: 2rpx solid #ddd; margin-right: 16rpx; display: flex; align-items: center; justify-content: center; font-size: 22rpx; color: #fff; flex-shrink: 0; }
.step-check.done { background: #e74c3c; border-color: #e74c3c; }
.step-text { flex: 1; font-size: 28rpx; line-height: 1.6; }
.step-text.done { text-decoration: line-through; color: #999; }
.empty { text-align: center; color: #999; padding: 100rpx 0; }
</style>
