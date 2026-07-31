<template>
  <view class="container">
    <view class="user-header">
      <view class="avatar-wrap" @click="changeAvatar">
        <image v-if="user.avatar" :src="user.avatar" class="avatar" mode="aspectFill" />
        <view v-else class="avatar-placeholder">👤</view>
        <view class="avatar-edit">📷</view>
      </view>
      <text class="nickname" @click="editNickname">{{ user.nickname || '未登录' }}</text>
      <text v-if="!token" class="login-hint" @click="goLogin">点击登录</text>
    </view>

    <view class="menu-list">
      <view class="menu-item" @click="goCookingHistory">
        <text>🍳 烹饪记录</text>
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
import { getUserInfo, updateUserInfo, uploadAvatar } from '@/api'

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
    user.value = await getUserInfo()
  } catch (e) {
    user.value = { nickname: '用户' }
  }
}

function goLogin() {
  uni.navigateTo({ url: '/pages/login/index' })
}

function goCookingHistory() {
  uni.navigateTo({ url: '/pages/cooking/history' })
}

function logout() {
  uni.removeStorageSync('token')
  token.value = ''
  user.value = {}
  uni.showToast({ title: '已退出', icon: 'success' })
}

async function changeAvatar() {
  uni.chooseImage({
    count: 1,
    success: async (res) => {
      const filePath = res.tempFilePaths[0]
      const result = await uploadAvatar(filePath)
      if (result.avatar_url) {
        user.value.avatar = result.avatar_url
        uni.showToast({ title: '头像已更新', icon: 'success' })
      }
    }
  })
}

async function editNickname() {
  if (!token.value) return
  uni.showModal({
    title: '修改昵称',
    editable: true,
    placeholderText: user.value.nickname || '请输入昵称',
    success: async (res) => {
      if (res.confirm && res.content) {
        await updateUserInfo({ nickname: res.content })
        user.value.nickname = res.content
        uni.showToast({ title: '昵称已修改', icon: 'success' })
      }
    }
  })
}
</script>

<style scoped>
.container { padding: 30rpx; }
.user-header { text-align: center; padding: 60rpx 0; background: #fff; border-radius: 16rpx; margin-bottom: 30rpx; position: relative; }
.avatar-wrap { margin-bottom: 20rpx; position: relative; display: inline-block; }
.avatar { width: 120rpx; height: 120rpx; border-radius: 50%; }
.avatar-placeholder { width: 120rpx; height: 120rpx; border-radius: 50%; background: #f5f5f5; display: inline-flex; align-items: center; justify-content: center; font-size: 48rpx; }
.avatar-edit { position: absolute; bottom: 0; right: 0; background: #e74c3c; color: #fff; width: 40rpx; height: 40rpx; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 24rpx; }
.nickname { font-size: 36rpx; font-weight: bold; display: block; }
.login-hint { color: #e74c3c; font-size: 26rpx; margin-top: 10rpx; display: block; }
.section { background: #fff; border-radius: 16rpx; padding: 30rpx; margin-bottom: 30rpx; }
.section-title { font-size: 32rpx; font-weight: bold; margin-bottom: 20rpx; }
.dish-item { display: flex; justify-content: space-between; align-items: center; padding: 20rpx 0; border-bottom: 1rpx solid #f5f5f5; }
.dish-info { display: flex; align-items: center; flex: 1; }
.dish-thumb { width: 64rpx; height: 64rpx; border-radius: 8rpx; margin-right: 16rpx; }
.dish-info .name { font-size: 28rpx; }
.arrow { color: #999; font-size: 36rpx; }
.empty { color: #999; font-size: 26rpx; }
.menu-list { background: #fff; border-radius: 16rpx; overflow: hidden; margin-bottom: 30rpx; }
.menu-item { display: flex; justify-content: space-between; align-items: center; padding: 30rpx; border-bottom: 1rpx solid #f5f5f5; }
.logout-btn { text-align: center; padding: 30rpx; background: #fff; border-radius: 16rpx; color: #e74c3c; }
</style>
