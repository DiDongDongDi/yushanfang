<template>
  <view class="container">
    <view class="user-header">
      <view class="avatar-wrap">
        <image v-if="user.avatar" :src="user.avatar" class="avatar" />
        <view v-else class="avatar-placeholder">👤</view>
      </view>
      <text class="nickname">{{ user.nickname || '未登录' }}</text>
      <text v-if="!token" class="login-hint" @click="goLogin">点击登录</text>
    </view>

    <view class="menu-list">
      <view class="menu-item" @click="goHistory">
        <text>📜 历史菜品</text>
        <text class="arrow">›</text>
      </view>
      <view class="menu-item" @click="goCookingHistory">
        <text>🍳 烹饪记录</text>
        <text class="arrow">›</text>
      </view>
      <view class="menu-item" @click="clearCache">
        <text>🗑️ 清除缓存</text>
        <text class="arrow">›</text>
      </view>
    </view>

    <view v-if="token" class="logout-btn" @click="logout">
      <text>退出登录</text>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { onShow } from '@dcloudio/uni-app'

const token = ref('')
const user = ref({})

onShow(() => {
  token.value = uni.getStorageSync('token')
  if (token.value) {
    loadUser()
  }
})

async function loadUser() {
  try {
    const { getUserInfo } = await import('@/api')
    user.value = await getUserInfo()
  } catch (e) {
    user.value = { nickname: '用户' }
  }
}

function goLogin() {
  uni.navigateTo({ url: '/pages/login/index' })
}

function goHistory() {
  uni.navigateTo({ url: '/pages/menu/index' })
}

function goCookingHistory() {
  uni.navigateTo({ url: '/pages/cooking/history' })
}

function clearCache() {
  uni.removeStorageSync('cart')
  uni.showToast({ title: '缓存已清除', icon: 'success' })
}

function logout() {
  uni.removeStorageSync('token')
  token.value = ''
  user.value = {}
  uni.showToast({ title: '已退出', icon: 'success' })
}
</script>

<style scoped>
.container { padding: 30rpx; }
.user-header { text-align: center; padding: 60rpx 0; background: #fff; border-radius: 16rpx; margin-bottom: 30rpx; }
.avatar-wrap { margin-bottom: 20rpx; }
.avatar { width: 120rpx; height: 120rpx; border-radius: 50%; }
.avatar-placeholder { width: 120rpx; height: 120rpx; border-radius: 50%; background: #f5f5f5; display: inline-flex; align-items: center; justify-content: center; font-size: 48rpx; }
.nickname { font-size: 36rpx; font-weight: bold; display: block; }
.login-hint { color: #e74c3c; font-size: 26rpx; margin-top: 10rpx; display: block; }
.menu-list { background: #fff; border-radius: 16rpx; overflow: hidden; margin-bottom: 30rpx; }
.menu-item { display: flex; justify-content: space-between; align-items: center; padding: 30rpx; border-bottom: 1rpx solid #f5f5f5; }
.arrow { color: #999; font-size: 36rpx; }
.logout-btn { text-align: center; padding: 30rpx; background: #fff; border-radius: 16rpx; color: #e74c3c; }
</style>
