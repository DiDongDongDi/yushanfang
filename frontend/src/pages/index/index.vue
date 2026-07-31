<template>
  <view class="container">
    <view class="header">
      <text class="greeting">御膳房</text>
      <text class="date">{{ today }}</text>
    </view>

    <view class="section">
      <view class="section-title">📋 快捷点菜</view>
      <view class="quick-order">
        <input v-model="newDish" class="input" placeholder="输入菜名直接点菜" @confirm="orderDish(newDish)" />
        <button class="order-btn" @click="orderDish(newDish)">点菜</button>
      </view>
    </view>

    <view class="section">
      <view class="section-title">📜 最近做过的菜</view>
      <view v-if="historyList.length" class="history-list">
        <view v-for="dish in historyList" :key="dish.id" class="history-item" @click="goDish(dish.id)">
          <text>{{ dish.name }}</text>
        </view>
      </view>
      <text v-else class="empty">暂无历史记录</text>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getDishes } from '@/api'

const today = new Date().toLocaleDateString('zh-CN', { month: 'long', day: 'numeric', weekday: 'long' })
const historyList = ref([])
const newDish = ref('')

async function loadHistory() {
  const res = await getDishes()
  historyList.value = res || []
}

function orderDish(name) {
  if (!name) return
  uni.navigateTo({ url: `/pages/dish/index?name=${encodeURIComponent(name)}` })
}

function goDish(id) {
  uni.navigateTo({ url: `/pages/dish/index?id=${id}` })
}

onMounted(() => {
  loadHistory()
})
</script>

<style scoped>
.container { padding: 30rpx; }
.header { margin-bottom: 40rpx; }
.greeting { font-size: 48rpx; font-weight: bold; display: block; }
.date { color: #999; font-size: 26rpx; }
.section { margin-bottom: 40rpx; background: #fff; border-radius: 16rpx; padding: 30rpx; }
.section-title { font-size: 32rpx; font-weight: bold; margin-bottom: 20rpx; }
.quick-order { display: flex; gap: 16rpx; }
.input { flex: 1; border: 2rpx solid #eee; border-radius: 12rpx; padding: 16rpx; }
.history-item { padding: 20rpx 0; border-bottom: 1rpx solid #f5f5f5; }
.empty { color: #999; font-size: 26rpx; }
</style>
