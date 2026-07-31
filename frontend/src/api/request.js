const BASE_URL = '/api'

function request(path, method = 'GET', data = {}, options = {}) {
  const token = uni.getStorageSync('token')
  return new Promise((resolve, reject) => {
    uni.request({
      url: BASE_URL + path,
      method,
      data,
      header: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...(options.header || {})
      },
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data)
        } else if (res.statusCode === 401) {
          uni.removeStorageSync('token')
          uni.showToast({ title: '请先登录', icon: 'none' })
          setTimeout(() => {
            uni.navigateTo({ url: '/pages/login/index' })
          }, 1000)
          reject(res.data)
        } else {
          const msg = res.data?.detail || `请求失败(${res.statusCode})`
          uni.showToast({ title: msg, icon: 'none' })
          reject(res.data)
        }
      },
      fail: (err) => {
        uni.showToast({ title: '网络异常', icon: 'none' })
        reject(err)
      }
    })
  })
}

export default {
  get: (path, options) => request(path, 'GET', {}, options),
  post: (path, data, options) => request(path, 'POST', data, options),
  put: (path, data, options) => request(path, 'PUT', data, options),
  delete: (path, options) => request(path, 'DELETE', {}, options)
}
