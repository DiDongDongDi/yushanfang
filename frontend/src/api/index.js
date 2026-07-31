import request from './request'

// 认证
export const register = (data) => request.post('/auth/register', data)
export const login = (username, password) => request.post('/auth/login', { username, password })
export const wechatLogin = (code) => request.post('/auth/wechat-login', { code })

// 用户
export const getUserInfo = () => request.get('/users/me')
export const updateUserInfo = (data) => request.put('/users/me', data)
export const uploadAvatar = (filePath) => {
  const token = uni.getStorageSync('token')
  return new Promise((resolve, reject) => {
    uni.uploadFile({
      url: '/api/upload/avatar',
      filePath,
      name: 'file',
      header: { Authorization: `Bearer ${token}` },
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(JSON.parse(res.data))
        } else {
          reject(res.data)
        }
      },
      fail: (err) => reject(err)
    })
  })
}

// 菜品
export const createDish = (data) => request.post('/dishes', data)
export const getDishes = () => request.get('/dishes')
export const getDish = (id) => request.get(`/dishes/${id}`)
export const updateDish = (id, data) => request.put(`/dishes/${id}`, data)
export const deleteDish = (id) => request.delete(`/dishes/${id}`)

// AI
export const aiRecommend = (preference) => request.post('/ai/recommend', { preference })
export const aiRecommendStream = (preference, onChunk, onDone) => {
  return streamRequest('/ai/recommend/stream', { preference }, onChunk, onDone)
}
export const aiGenerateRecipe = (dishName) => request.post('/ai/generate-recipe', { dish_name: dishName })
export const aiGenerateRecipeStream = (dishName, onChunk, onDone) => {
  return streamRequest('/ai/generate-recipe/stream', { dish_name: dishName }, onChunk, onDone)
}
export const aiOptimizePlan = (dishes, plans) => request.post('/ai/optimize-plan', { dishes, plans })
export const aiOptimizePlanStream = (dishes, plans, onChunk, onDone) => {
  return streamRequest('/ai/optimize-plan/stream', { dishes, plans }, onChunk, onDone)
}

// 流式请求封装
function streamRequest(url, data, onChunk, onDone) {
  const token = uni.getStorageSync('token')
  // #ifdef H5
  const baseURL = window.location.origin || ''
  return fetch(baseURL + url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(data)
  }).then(resp => {
    if (!resp.ok) throw new Error('请求失败')
    const reader = resp.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    let finished = false
    function read() {
      return reader.read().then(({ done, value }) => {
        if (done) {
          if (!finished) {
            finished = true
            onDone && onDone()
          }
          return
        }
        buffer += decoder.decode(value, { stream: true })
        let idx
        while ((idx = buffer.indexOf('\n\n')) !== -1) {
          const event = buffer.slice(0, idx)
          buffer = buffer.slice(idx + 2)
          if (event.startsWith('data:')) {
            const dataStr = event.slice(5).trim()
            try {
              const json = JSON.parse(dataStr)
              if (json.type === 'chunk' && onChunk) onChunk(json.content)
              if (json.type === 'done' && !finished) {
                finished = true
                onDone && onDone(json.result)
              }
            } catch (e) {}
          }
        }
        return read()
      })
    }
    return read()
  })
  // #endif
}

// 烹饪记录
export const createRecord = (dishIds) => request.post('/cooking-records', { dish_ids: dishIds })
export const getRecords = () => request.get('/cooking-records')
export const getRecord = (id) => request.get(`/cooking-records/${id}`)
export const updateRecord = (id, data) => request.put(`/cooking-records/${id}`, data)
export const createSteps = (recordId, steps) => request.post(`/cooking-records/${recordId}/steps`, steps)
export const updateStep = (stepId, data) => request.put(`/cooking-records/steps/${stepId}`, data)
