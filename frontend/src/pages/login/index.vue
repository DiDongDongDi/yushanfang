<template>
  <view class="container">
    <view class="header">
      <text class="title">御膳房</text>
      <text class="subtitle">智能点菜小程序</text>
    </view>
    <view class="form">
      <input v-model="phone" class="input" type="number" maxlength="11" placeholder="请输入手机号" />
      <view class="code-row">
        <input v-model="code" class="input code-input" type="number" maxlength="6" placeholder="验证码" />
        <button class="code-btn" :disabled="countdown > 0" @click="handleSendCode">
          {{ countdown > 0 ? `${countdown}s` : '发送验证码' }}
        </button>
      </view>
      <button class="login-btn" @click="handleLogin">登录 / 注册</button>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { sendCode as sendCodeApi, login } from '@/api'

const phone = ref('')
const code = ref('')
const countdown = ref(0)

let timer = null

async function handleSendCode() {
  if (!/^1\d{10}$/.test(phone.value)) {
    uni.showToast({ title: '请输入正确手机号', icon: 'none' })
    return
  }
  const res = await sendCodeApi(phone.value)
  if (res.msg) {
    uni.showToast({ title: '验证码已发送', icon: 'success' })
    countdown.value = 60
    timer = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) clearInterval(timer)
    }, 1000)
  }
}

async function handleLogin() {
  if (!phone.value || !code.value) {
    uni.showToast({ title: '请填写完整', icon: 'none' })
    return
  }
  const res = await login(phone.value, code.value)
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
.input { border: 2rpx solid #eee; border-radius: 12rpx; padding: 24rpx; margin-bottom: 24rpx; font-size: 28rpx; }
.code-row { display: flex; gap: 16rpx; }
.code-input { flex: 1; }
.code-btn { white-space: nowrap; background: #e74c3c; color: #fff; border-radius: 12rpx; font-size: 24rpx; padding: 0 20rpx; }
.login-btn { margin-top: 40rpx; background: #e74c3c; color: #fff; border-radius: 12rpx; padding: 24rpx; font-size: 32rpx; }
</style>
