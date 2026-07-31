import request from './request'

// 认证
export const sendCode = (phone) => request.post('/auth/send-code', { phone })
export const login = (phone, code, nickname) => request.post('/auth/login', { phone, code, nickname })
export const wechatLogin = (code) => request.post('/auth/wechat-login', { code })

// 用户
export const getUserInfo = () => request.get('/users/me')
export const updateUserInfo = (data) => request.put('/users/me', data)

// 菜品
export const createDish = (data) => request.post('/dishes', data)
export const getDishes = () => request.get('/dishes')
export const getDish = (id) => request.get(`/dishes/${id}`)
export const updateDish = (id, data) => request.put(`/dishes/${id}`, data)
export const deleteDish = (id) => request.delete(`/dishes/${id}`)

// AI
export const aiRecommend = (preference) => request.post('/ai/recommend', { preference })
export const aiGenerateRecipe = (dishName) => request.post('/ai/generate-recipe', { dish_name: dishName })
export const aiOptimizePlan = (dishes, plans) => request.post('/ai/optimize-plan', { dishes, plans })

// 烹饪记录
export const createRecord = (dishIds) => request.post('/cooking-records', { dish_ids: dishIds })
export const getRecords = () => request.get('/cooking-records')
export const getRecord = (id) => request.get(`/cooking-records/${id}`)
export const updateRecord = (id, data) => request.put(`/cooking-records/${id}`, data)
export const createSteps = (recordId, steps) => request.post(`/cooking-records/${recordId}/steps`, steps)
export const updateStep = (stepId, data) => request.put(`/cooking-records/steps/${stepId}`, data)
