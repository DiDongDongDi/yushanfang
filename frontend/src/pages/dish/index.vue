<template>
  <view class="container">
    <view class="dish-header">
      <text class="dish-name">{{ dishName }}</text>
      <view v-if="dish.image" class="dish-image-wrap">
        <image :src="dish.image" mode="aspectFill" class="dish-image" />
      </view>
      <view class="dish-actions">
        <button class="btn-primary" @click="generateRecipe" :loading="generating">
          {{ recipe ? '重新生成' : 'AI 生成菜谱' }}
        </button>
      </view>
    </view>

    <view v-if="generating" class="loading-tip">
      <text>AI 正在生成菜谱，请稍候...</text>
    </view>

    <template v-if="recipe">
      <view class="section">
        <view class="section-title">🛒 需要买的菜</view>
        <text class="section-content">{{ recipe.buy_list }}</text>
      </view>
      <view class="section">
        <view class="section-title">🔪 备菜步骤</view>
        <text class="section-content">{{ recipe.prep_steps }}</text>
      </view>
      <view class="section">
        <view class="section-title">🍳 烹饪做法</view>
        <text class="section-content">{{ recipe.cook_steps }}</text>
      </view>

      <view class="bottom-bar">
        <button class="btn-primary" @click="addToCart">加入本次做饭</button>
        <button class="btn-secondary" @click="saveToMyDishes">保存到我的菜</button>
      </view>
    </template>

    <view v-else-if="!generating" class="empty-tip">
      <text>点击上方按钮，让 AI 为你生成这道菜的完整菜谱</text>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { aiGenerateRecipe, createDish } from '@/api'

const dishName = ref('')
const dishId = ref(null)
const dish = ref({})
const recipe = ref(null)
const generating = ref(false)

onLoad((options) => {
  dishName.value = decodeURIComponent(options.name || '')
  if (options.id) {
    dishId.value = Number(options.id)
    getDishInfo()
  }
})

async function getDishInfo() {
  const { getDish } = await import('@/api')
  dish.value = await getDish(dishId.value)
  dishName.value = dish.value.name
  if (dish.value.recipe_json) {
    recipe.value = JSON.parse(dish.value.recipe_json)
  }
}

async function generateRecipe() {
  generating.value = true
  recipe.value = null
  const res = await aiGenerateRecipe(dishName.value)
  if (res.buy_list || res.prep_steps || res.cook_steps) {
    recipe.value = {
      buy_list: res.buy_list || '',
      prep_steps: res.prep_steps || '',
      cook_steps: res.cook_steps || ''
    }
  } else if (res.result) {
    recipe.value = { buy_list: res.result, prep_steps: '', cook_steps: '' }
  } else if (res.error) {
    recipe.value = {
      buy_list: '（AI 服务未配置，请联系管理员）',
      prep_steps: '',
      cook_steps: ''
    }
  }
  generating.value = false
}

function addToCart() {
  let cart = uni.getStorageSync('cart') || []
  const name = dishName.value
  if (!cart.find((d) => d.name === name)) {
    cart.push({ name, recipe })
    uni.setStorageSync('cart', cart)
  }
  uni.showToast({ title: '已加入本次做饭', icon: 'success' })
  setTimeout(() => {
    uni.navigateTo({ url: '/pages/cooking/index' })
  }, 800)
}

async function saveToMyDishes() {
  if (!recipe.value) return
  await createDish({
    name: dishName.value,
    description: JSON.stringify(recipe.value),
    recipe_json: JSON.stringify(recipe.value)
  })
  uni.showToast({ title: '已保存', icon: 'success' })
}
</script>

<style scoped>
.container { padding: 30rpx; padding-bottom: 160rpx; }
.dish-header { margin-bottom: 30rpx; }
.dish-name { font-size: 44rpx; font-weight: bold; display: block; margin-bottom: 20rpx; }
.dish-image-wrap { margin-bottom: 20rpx; }
.dish-image { width: 100%; height: 360rpx; border-radius: 16rpx; }
.section { background: #fff; border-radius: 16rpx; padding: 30rpx; margin-bottom: 24rpx; }
.section-title { font-size: 32rpx; font-weight: bold; margin-bottom: 16rpx; color: #e74c3c; }
.section-content { font-size: 28rpx; color: #333; white-space: pre-wrap; line-height: 1.8; }
.btn-primary { background: #e74c3c; color: #fff; border-radius: 12rpx; margin-top: 20rpx; }
.btn-secondary { background: #fff; color: #e74c3c; border: 2rpx solid #e74c3c; border-radius: 12rpx; margin-top: 20rpx; }
.bottom-bar { position: fixed; bottom: 0; left: 0; right: 0; background: #fff; padding: 20rpx 30rpx; display: flex; gap: 20rpx; box-shadow: 0 -2rpx 10rpx rgba(0,0,0,0.05); }
.bottom-bar .btn-primary, .bottom-bar .btn-secondary { flex: 1; margin-top: 0; }
.loading-tip, .empty-tip { text-align: center; color: #999; padding: 60rpx 0; }
</style>
