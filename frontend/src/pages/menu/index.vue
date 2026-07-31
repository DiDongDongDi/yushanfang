<template>
  <view class="container">
    <!-- AI 推荐（最上面） -->
    <view class="section">
      <view class="section-title-row">
        <text class="section-title">🔥 AI 推荐</text>
      </view>
      <view class="preference-bar">
        <input v-model="preference" class="preference-input" placeholder="今天想吃点什么？如：辣的、清淡、海鲜..." @confirm="getRecommend" />
        <button class="recommend-btn" @click="getRecommend" :loading="loading">推荐</button>
      </view>
      <view v-if="loading" class="loading-hint">
        <text>✨ 正在为你推荐...</text>
      </view>
      <view v-if="recommendList.length" class="recommend-list">
        <view v-for="(item, idx) in recommendList" :key="idx" class="recommend-item" @click="goDishByName(item.name)">
          <text class="name">{{ item.name }}</text>
          <text v-if="item.desc" class="desc">{{ item.desc }}</text>
        </view>
      </view>
      <button v-else-if="!loading" class="ai-btn" @click="getRecommend">获取 AI 推荐</button>
    </view>

    <!-- 搜索菜品（搜索历史菜品） -->
    <view class="search-bar">
      <input v-model="keyword" class="search-input" placeholder="搜索我的历史菜品..." />
      <button class="search-btn" @click="searchDish">点菜</button>
    </view>

    <!-- 搜索结果 / 历史菜品 -->
    <view class="section">
      <view class="section-title">{{ keyword ? `搜索结果 (${filteredDishes.length})` : '📜 我的历史菜品' }}</view>
      <view v-if="filteredDishes.length" class="search-results">
        <view v-for="dish in filteredDishes" :key="dish.id" class="dish-item" @click="goDish(dish.id)">
          <view class="dish-info">
            <text class="name">{{ dish.name }}</text>
          </view>
        </view>
      </view>
      <text v-else-if="!dishes.length" class="empty">暂无历史菜品</text>
      <text v-else-if="keyword && !filteredDishes.length" class="empty">未找到「{{ keyword }}」，点击"点菜"按钮直接添加</text>
    </view>

    <view class="bottom-bar" v-if="cart.length > 0">
      <view class="cart-list">
        <view v-for="(item, idx) in cart" :key="idx" class="cart-item">
          <text class="cart-name">{{ item.name }}</text>
          <text class="cart-remove" @click="removeDish(idx)">×</text>
        </view>
      </view>
      <button class="btn-primary" @click="goCooking">去做饭 ›</button>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { aiRecommend, aiRecommendStream, getDishes } from '@/api'

const keyword = ref('')
const preference = ref('')
const recommendList = ref([])
const loading = ref(false)
const recommendRawText = ref('')
const dishes = ref([])
const cart = ref(uni.getStorageSync('cart') || [])

// 搜索历史菜品
const filteredDishes = computed(() => {
  const kw = keyword.value.trim()
  if (!kw) return dishes.value
  return dishes.value.filter((d) => d.name.includes(kw))
})

async function getRecommend() {
  loading.value = true
  recommendList.value = []
  recommendRawText.value = ''
  const pref = preference.value.trim()
  // #ifdef H5
  aiRecommendStream(pref,
    (chunk) => {
      recommendRawText.value += chunk
      const parsed = parseRecommend(recommendRawText.value)
      if (parsed.length) {
        recommendList.value = parsed
      }
    },
    (result) => {
      if (result && result.dishes) {
        recommendList.value = result.dishes
      } else if (result && result.result) {
        recommendList.value = [{ name: result.result, desc: '' }]
      }
      recommendRawText.value = ''
      loading.value = false
    }
  ).catch(e => {
    console.error('AI推荐失败:', e)
    uni.showToast({ title: 'AI推荐失败', icon: 'none' })
    recommendRawText.value = ''
    loading.value = false
  })
  // #endif
  // #ifndef H5
  const res = await aiRecommend(pref)
  if (res.dishes) {
    recommendList.value = res.dishes
  } else if (res.result) {
    recommendList.value = [{ name: res.result, desc: '' }]
  }
  loading.value = false
  // #endif
}

async function loadDishes() {
  const res = await getDishes()
  const seen = new Set()
  dishes.value = (res || []).filter((d) => {
    if (seen.has(d.name)) return false
    seen.add(d.name)
    return true
  })
}

// 从流式文本中实时解析推荐菜品
function parseRecommend(text) {
  const match = text.match(/"name"\s*:\s*"([^"]*)"/g)
  if (!match) return []
  const names = match.map(m => m.match(/"name"\s*:\s*"([^"]*)"/)[1])
  return names.map(name => ({ name, desc: '' }))
}

function searchDish() {
  const kw = keyword.value.trim()
  if (!kw) {
    uni.showToast({ title: '请输入菜名', icon: 'none' })
    return
  }
  // 优先打开匹配的历史菜品
  const match = dishes.value.find((d) => d.name === kw)
  if (match) {
    goDish(match.id)
  } else {
    goDishByName(kw)
  }
}

function goDish(id) {
  uni.navigateTo({ url: `/pages/dish/index?id=${id}` })
}

function goDishByName(name) {
  uni.navigateTo({ url: `/pages/dish/index?name=${encodeURIComponent(name)}` })
}

function goCooking() {
  uni.navigateTo({ url: '/pages/cooking/index' })
}

function removeDish(idx) {
  cart.value.splice(idx, 1)
  uni.setStorageSync('cart', cart.value)
}

onShow(() => {
  cart.value = uni.getStorageSync('cart') || []
})

onMounted(() => {
  loadDishes()
  getRecommend()
})
</script>

<style scoped>
.container { padding: 30rpx; padding-bottom: 200rpx; }
.search-bar { display: flex; gap: 16rpx; margin-bottom: 30rpx; }
.search-input { flex: 1; border: 2rpx solid #eee; border-radius: 12rpx; padding: 20rpx; }
.search-btn { background: #e74c3c; color: #fff; border-radius: 12rpx; font-size: 28rpx; height: 88rpx; display: flex; align-items: center; justify-content: center; padding: 0 30rpx; }
.section { background: #fff; border-radius: 16rpx; padding: 30rpx; margin-bottom: 24rpx; }
.section-title-row { margin-bottom: 20rpx; }
.section-title { font-size: 32rpx; font-weight: bold; }
.preference-bar { display: flex; gap: 16rpx; margin-bottom: 20rpx; }
.preference-input { flex: 1; border: 2rpx solid #eee; border-radius: 12rpx; padding: 16rpx 20rpx; font-size: 26rpx; }
.recommend-btn { background: #e74c3c; color: #fff; border-radius: 12rpx; font-size: 26rpx; height: 76rpx; display: flex; align-items: center; justify-content: center; padding: 0 30rpx; flex-shrink: 0; }
.recommend-item { padding: 20rpx 0; border-bottom: 1rpx solid #f5f5f5; }
.recommend-item .name { display: block; font-size: 30rpx; font-weight: bold; color: #333; }
.recommend-item .desc { display: block; margin-top: 8rpx; color: #999; font-size: 26rpx; line-height: 1.6; word-break: break-all; }
.dish-item { display: flex; justify-content: space-between; align-items: center; padding: 20rpx 0; border-bottom: 1rpx solid #f5f5f5; }
.dish-info { flex: 1; }
.dish-info .desc { display: block; color: #999; font-size: 24rpx; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.add-btn { color: #e74c3c; font-size: 40rpx; width: 60rpx; height: 60rpx; display: flex; align-items: center; justify-content: center; }
.empty { color: #999; font-size: 26rpx; }
.loading-hint { color: #e74c3c; font-size: 26rpx; padding: 20rpx 0; }
.bottom-bar { position: fixed; bottom: var(--window-bottom); left: 0; right: 0; background: #fff; padding: 20rpx 30rpx; display: flex; align-items: center; box-shadow: 0 -2rpx 10rpx rgba(0,0,0,0.05); z-index: 100; }
.cart-list { flex: 1; display: flex; flex-wrap: wrap; gap: 12rpx; margin-right: 20rpx; }
.cart-item { background: #fff3f0; color: #e74c3c; padding: 8rpx 16rpx; border-radius: 8rpx; font-size: 24rpx; display: flex; align-items: center; gap: 8rpx; }
.cart-name { max-width: 120rpx; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.cart-remove { font-size: 32rpx; color: #e74c3c; }
.btn-primary { background: #e74c3c; color: #fff; border-radius: 12rpx; font-size: 28rpx; height: 88rpx; display: flex; align-items: center; justify-content: center; padding: 0 30rpx; }
.ai-btn { background: #e74c3c; color: #fff; border-radius: 12rpx; font-size: 26rpx; height: 88rpx; display: flex; align-items: center; justify-content: center; }
</style>
