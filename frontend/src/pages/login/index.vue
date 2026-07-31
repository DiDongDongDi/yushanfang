<template>
  <view class="container">
    <view class="header">
      <text class="title">御膳房</text>
      <text class="subtitle">智能点菜小程序</text>
    </view>
    <view class="form">
      <view class="input-wrap">
        <input v-model="username" class="input" type="text" maxlength="50" placeholder="请输入用户名（3-50位）" />
      </view>
      <view class="input-wrap">
        <input v-model="password" class="input" type="password" maxlength="100" placeholder="请输入密码（6位以上）" />
      </view>
      <view class="input-wrap">
        <input v-model="nickname" class="input" type="text" maxlength="50" placeholder="昵称（可选）" />
      </view>
      <button class="login-btn" @click="handleRegister">注册</button>
      <button class="login-btn secondary" @click="handleLogin">登录</button>
      <view class="toggle-mode" @click="isLoginMode = !isLoginMode">
        <text>{{ isLoginMode ? '没有账号？去注册' : '已有账号？去登录' }}</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { register as registerApi, login as loginApi } from '@/api'

const username = ref('')
const password = ref('')
const nickname = ref('')
const isLoginMode = ref(true)  // true=登录模式, false=注册模式

async function handleRegister() {
  if (!username.value || !password.value) {
    uni.showToast({ title: '请填写用户名和密码', icon: 'none' })
    return
  }
  if (username.value.length < 3) {
    uni.showToast({ title: '用户名至少3位', icon: 'none' })
    return
  }
  if (password.value.length < 6) {
    uni.showToast({ title: '密码至少6位', icon: 'none' })
    return
  }
  const res = await registerApi({
    username: username.value,
    password: password.value,
    nickname: nickname.value || null
  })
  if (res.id) {
    uni.showToast({ title: '注册成功，请登录', icon: 'success' })
    isLoginMode.value = true
    nickname.value = ''
  }
}

async function handleLogin() {
  if (!username.value || !password.value) {
    uni.showToast({ title: '请填写用户名和密码', icon: 'none' })
    return
  }
  const res = await loginApi(username.value, password.value)
  if (res.access_token) {
    uni.setStorageSync('token', res.access_token)
    uni.showToast({ title: '登录成功', icon: 'success' })
    setTimeout(() => {
      uni.switchTab({ url: '/pages/index/index' })
    }, 800)
  }
}
</script>

<style scoped>
.container { padding: 60rpx 40rpx; }
.header { text-align: center; margin-bottom: 80rpx; }
.title { font-size: 56rpx; font-weight: bold; color: #e74c3c; }
.subtitle { display: block; margin-top: 10rpx; color: #999; }
.form { background: #fff; border-radius: 16rpx; padding: 40rpx; }
.input-wrap { border: 2rpx solid #eee; border-radius: 12rpx; margin-bottom: 24rpx; }
.input { height: 88rpx; line-height: 88rpx; padding: 0 24rpx; font-size: 28rpx; width: 100%; box-sizing: border-box; }
.login-btn { background: #e74c3c; color: #fff; border-radius: 12rpx; height: 88rpx; line-height: 88rpx; font-size: 32rpx; margin-top: 24rpx; width: 100%; }
.login-btn.secondary { background: #fff; color: #e74c3c; border: 2rpx solid #e74c3c; }
.toggle-mode { text-align: center; margin-top: 30rpx; color: #999; font-size: 26rpx; }
</style>
