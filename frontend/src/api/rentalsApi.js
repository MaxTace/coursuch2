import api from './axios'

export const getRentals = () => api.get('/rentals/').then(r => r.data)

export const issueRental = (data) => api.post('/rentals/issue', data).then(r => r.data)

export const returnRental = (rentalId) => api.post(`/rentals/${rentalId}/return`).then(r => r.data)
