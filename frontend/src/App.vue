<script setup>
import { onLaunch } from '@dcloudio/uni-app'
onLaunch(() => {
  console.log('御膳房 App Launch')
})
</script>

<style>
page {
  background-color: #f5f5f5;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  color: #333;
  font-size: 28rpx;
}

/* 全局按钮样式 */
button {
  font-size: 28rpx;
}
button::after {
  border: none;
}
</style>
