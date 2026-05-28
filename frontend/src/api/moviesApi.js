import api from './axios'

export const getMovies = () => api.get('/movies/').then(r => r.data)

export const getMovie = (id) => api.get(`/movies/${id}`).then(r => r.data)

export const createMovie = (data) => api.post('/movies/', data).then(r => r.data)

export const updateMovie = (id, data) => api.post(`/movies/change_info/${id}`, data).then(r => r.data)

export const getMovieCopies = (movieId) => api.get(`/movies/${movieId}/copies`).then(r => r.data)

export const addMovieCopies = (movieId, count) =>
  api.post(`/movies/${movieId}/copies?copies_count=${count}`).then(r => r.data)

export const getCategories = () => api.get('/categories/').then(r => r.data)

export const createCategory = (data) => api.post('/categories/', data).then(r => r.data)
