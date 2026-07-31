<template>
  <view class="container">
    <view class="header">
      <text class="title">烹饪记录</text>
    </view>

    <view v-if="records.length" class="record-list">
      <view v-for="record in records" :key="record.id" class="record-item" @click="goRecord(record.id)">
        <text class="record-date">{{ formatDate(record.created_at) }}</text>
        <text class="record-status">{{ record.status }}</text>
        <text class="record-arrow">›</text>
      </view>
    </view>
    <view v-else class="empty">
      <text>暂无烹饪记录</text>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getRecords } from '@/api'

const records = ref([])

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getMonth() + 1}月${d.getDate()}日 ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

function goRecord(id) {
  uni.navigateTo({ url: `/pages/cooking/history?recordId=${id}` })
}

onMounted(async () => {
  const res = await getRecords()
  records.value = res || []
})
</script>

<style scoped>
.container { padding: 30rpx; }
.header { margin-bottom: 30rpx; }
.title { font-size: 40rpx; font-weight: bold; }
.record-list { background: #fff; border-radius: 16rpx; overflow: hidden; }
.record-item { display: flex; align-items: center; padding: 30rpx; border-bottom: 1rpx solid #f5f5f5; }
.record-date { flex: 1; font-size: 28rpx; }
.record-status { color: #e74c3c; font-size: 24rpx; margin-right: 16rpx; }
.record-arrow { color: #999; font-size: 36rpx; }
.empty { text-align: center; color: #999; padding: 100rpx 0; }
</style>
