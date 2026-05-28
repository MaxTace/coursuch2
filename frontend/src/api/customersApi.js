import api from './axios'

export const getCustomers = () => api.get('/customers/').then(r => r.data)

export const createCustomer = (data) => api.post('/customers/', data).then(r => r.data)
