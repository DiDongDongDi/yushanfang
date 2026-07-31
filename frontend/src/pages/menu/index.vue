<template>
  <view class="container">
    <view class="search-bar">
      <input v-model="keyword" class="search-input" placeholder="输入菜名搜索或点菜" @confirm="searchDish" />
      <button class="search-btn" @click="searchDish">点菜</button>
    </view>

    <view class="section">
      <view class="section-title">🔥 AI 推荐</view>
      <view v-if="recommendList.length" class="recommend-list">
        <view v-for="(item, idx) in recommendList" :key="idx" class="recommend-item" @click="addDish(item.name)">
          <text class="name">{{ item.name }}</text>
          <text class="desc">{{ item.desc }}</text>
        </view>
      </view>
      <button v-else class="ai-btn" @click="getRecommend" :loading="loading">获取 AI 推荐</button>
    </view>

    <view class="section">
      <view class="section-title">📜 我的历史菜品</view>
      <view v-for="dish in dishes" :key="dish.id" class="dish-item" @click="goDish(dish.id)">
        <view class="dish-info">
          <text class="name">{{ dish.name }}</text>
          <text v-if="dish.description" class="desc">{{ dish.description }}</text>
        </view>
        <text class="add-btn" @click.stop="addDish(dish.name)">＋</text>
      </view>
      <text v-if="!dishes.length" class="empty">暂无历史菜品</text>
    </view>

    <view class="bottom-bar" v-if="cart.length > 0">
      <text class="cart-count">已选 {{ cart.length }} 道菜</text>
      <button class="btn-primary" @click="goCooking">去做饭 ›</button>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { aiRecommend, getDishes } from '@/api'

const keyword = ref('')
const recommendList = ref([])
const loading = ref(false)
const dishes = ref([])
const cart = ref(uni.getStorageSync('cart') || [])

async function getRecommend() {
  loading.value = true
  const res = await aiRecommend('')
  if (res.dishes) {
    recommendList.value = res.dishes
  } else if (res.result) {
    recommendList.value = [{ name: res.result, desc: '' }]
  }
  loading.value = false
}

async function loadDishes() {
  const res = await getDishes()
  dishes.value = res || []
}

function searchDish() {
  if (!keyword.value) {
    uni.showToast({ title: '请输入菜名', icon: 'none' })
    return
  }
  addDish(keyword.value)
}

function addDish(name) {
  if (!name) return
  if (cart.value.find((d) => d.name === name)) {
    uni.showToast({ title: '已在列表中', icon: 'none' })
    return
  }
  cart.value.push({ name })
  uni.setStorageSync('cart', cart.value)
  uni.showToast({ title: `已添加「${name}」`, icon: 'success' })
}

function goDish(id) {
  uni.navigateTo({ url: `/pages/dish/index?id=${id}` })
}

function goCooking() {
  uni.navigateTo({ url: '/pages/cooking/index' })
}

onMounted(() => {
  loadDishes()
})
</script>

<style scoped>
.container { padding: 30rpx; padding-bottom: 160rpx; }
.search-bar { display: flex; gap: 16rpx; margin-bottom: 30rpx; }
.search-input { flex: 1; border: 2rpx solid #eee; border-radius: 12rpx; padding: 20rpx; }
.search-btn { background: #e74c3c; color: #fff; border-radius: 12rpx; font-size: 28rpx; }
.section { background: #fff; border-radius: 16rpx; padding: 30rpx; margin-bottom: 24rpx; }
.section-title { font-size: 32rpx; font-weight: bold; margin-bottom: 20rpx; }
.recommend-item { display: flex; justify-content: space-between; padding: 20rpx 0; border-bottom: 1rpx solid #f5f5f5; }
.recommend-item .name { font-weight: bold; }
.recommend-item .desc { color: #999; font-size: 24rpx; max-width: 400rpx; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.dish-item { display: flex; justify-content: space-between; align-items: center; padding: 20rpx 0; border-bottom: 1rpx solid #f5f5f5; }
.dish-info { flex: 1; }
.dish-info .desc { display: block; color: #999; font-size: 24rpx; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.add-btn { color: #e74c3c; font-size: 40rpx; padding: 0 20rpx; }
.empty { color: #999; font-size: 26rpx; }
.bottom-bar { position: fixed; bottom: 0; left: 0; right: 0; background: #fff; padding: 20rpx 30rpx; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 -2rpx 10rpx rgba(0,0,0,0.05); }
.cart-count { color: #e74c3c; font-size: 28rpx; }
.btn-primary { background: #e74c3c; color: #fff; border-radius: 12rpx; font-size: 28rpx; }
.ai-btn { background: #e74c3c; color: #fff; border-radius: 12rpx; font-size: 26rpx; }
</style>
