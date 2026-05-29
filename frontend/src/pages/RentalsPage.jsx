import { useState, useEffect } from 'react'
import { getRentals, issueRental, returnRental } from '../api/rentalsApi'
import { getCustomers } from '../api/customersApi'
import { getMovies, getMovieCopies } from '../api/moviesApi'
import Modal from '../components/Modal'
import { IconPlus, IconSearch, IconCheck, IconClipboard } from '../components/Icons'

export default function RentalsPage() {
  const [rentals, setRentals] = useState([])
  const [customers, setCustomers] = useState([])
  const [movies, setMovies] = useState([])
  const [search, setSearch] = useState('')
  const [filter, setFilter] = useState('all')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const [showIssueModal, setShowIssueModal] = useState(false)
  const [issueForm, setIssueForm] = useState({ customer_id: '', movie_id: '', movie_copy_id: '', rental_days: 1 })
  const [copies, setCopies] = useState([])
  const [saving, setSaving] = useState(false)

  const [returningId, setReturningId] = useState(null)

  const load = () => {
    setLoading(true)
    Promise.all([getRentals(), getCustomers(), getMovies()])
      .then(([r, c, m]) => { setRentals(r); setCustomers(c); setMovies(m) })
      .catch(() => setError('Ошибка загрузки'))
      .finally(() => setLoading(false))
  }

  useEffect(load, [])

  const filtered = rentals.filter(r => {
    const matchSearch = !search ||
      (r.customer_name && r.customer_name.toLowerCase().includes(search.toLowerCase())) ||
      (r.movie_title && r.movie_title.toLowerCase().includes(search.toLowerCase())) ||
      (r.inventory_code && r.inventory_code.toLowerCase().includes(search.toLowerCase()))
    const matchFilter =
      filter === 'all' ||
      (filter === 'active' && r.is_active) ||
      (filter === 'returned' && !r.is_active) ||
      (filter === 'overdue' && r.is_active && new Date(r.planned_return_date) < new Date())
    return matchSearch && matchFilter
  })

  const handleMovieChange = async (movieId) => {
    setIssueForm(f => ({ ...f, movie_id: movieId, movie_copy_id: '' }))
    if (!movieId) { setCopies([]); return }
    const data = await getMovieCopies(movieId)
    setCopies(data.filter(c => c.status === 'available'))
  }

  const handleIssue = async (e) => {
    e.preventDefault()
    setSaving(true)
    setError('')
    try {
      await issueRental({
        customer_id: +issueForm.customer_id,
        movie_copy_id: +issueForm.movie_copy_id,
        rental_days: +issueForm.rental_days,
      })
      setShowIssueModal(false)
      setIssueForm({ customer_id: '', movie_id: '', movie_copy_id: '', rental_days: 1 })
      setCopies([])
      load()
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка выдачи')
    } finally {
      setSaving(false)
    }
  }

  const handleReturn = async (id) => {
    setReturningId(id)
    try {
      await returnRental(id)
      load()
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка возврата')
    } finally {
      setReturningId(null)
    }
  }

  const isOverdue = (r) => r.is_active && new Date(r.planned_return_date) < new Date()

  const selectedMovie = movies.find(m => m.id === +issueForm.movie_id)
  const pricePreview = selectedMovie && issueForm.rental_days
    ? (+issueForm.rental_days * selectedMovie.price)
    : 0

  return (
    <>
      <div className="page-header">
        <h2 className="page-title">Аренды</h2>
        <p className="page-subtitle">Выдача и возврат фильмов</p>
      </div>

      <div className="page-body">
        {error && <div className="error-banner">{error}</div>}

        <div className="toolbar">
          <div className="search-wrap">
            <IconSearch />
            <input
              placeholder="Поиск по клиенту, фильму или коду…"
              value={search}
              onChange={e => setSearch(e.target.value)}
            />
          </div>
          <select
            value={filter}
            onChange={e => setFilter(e.target.value)}
            style={{ padding: '7px 12px', borderRadius: 6, border: '1px solid var(--border)', fontSize: 13, cursor: 'pointer' }}
          >
            <option value="all">Все</option>
            <option value="active">Активные</option>
            <option value="overdue">Просроченные</option>
            <option value="returned">Возвращённые</option>
          </select>
          <button className="btn btn-primary" onClick={() => { setShowIssueModal(true); setError('') }}>
            <IconPlus /> Выдать фильм
          </button>
        </div>

        <div className="card">
          {loading ? (
            <div className="loading">Загрузка…</div>
          ) : filtered.length === 0 ? (
            <div className="empty-state">
              <IconClipboard />
              <p>{search || filter !== 'all' ? 'Ничего не найдено' : 'Аренд нет'}</p>
            </div>
          ) : (
            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Клиент</th>
                    <th>Фильм</th>
                    <th>Инв. №</th>
                    <th>Выдан</th>
                    <th>Срок возврата</th>
                    <th>Дней</th>
                    <th>Стоимость</th>
                    <th>Залог</th>
                    <th>Штраф</th>
                    <th>Статус</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map(r => (
                    <tr key={r.id}>
                      <td className="td-muted">{r.id}</td>
                      <td style={{ fontWeight: 500 }}>{r.customer_name}</td>
                      <td>{r.movie_title}</td>
                      <td className="td-mono">{r.inventory_code}</td>
                      <td className="td-muted">{new Date(r.issue_date).toLocaleDateString('ru-RU')}</td>
                      <td className={isOverdue(r) ? '' : 'td-muted'}>
                        <span style={{ color: isOverdue(r) ? 'var(--danger)' : undefined }}>
                          {new Date(r.planned_return_date).toLocaleDateString('ru-RU')}
                        </span>
                      </td>
                      <td className="td-muted">{r.rental_days}</td>
                      <td>{r.rental_price} ₽</td>
                      <td className="td-muted">{r.deposit} ₽</td>
                      <td>
                        {r.penalty > 0
                          ? <span className="badge badge-red">{r.penalty} ₽</span>
                          : <span className="td-muted">—</span>}
                      </td>
                      <td>
                        {isOverdue(r)
                          ? <span className="badge badge-red">Просрочено</span>
                          : r.is_active
                            ? <span className="badge badge-blue">Активна</span>
                            : <span className="badge badge-gray">Возвращён</span>}
                      </td>
                      <td>
                        {r.is_active && (
                          <button
                            className="btn btn-success btn-sm"
                            onClick={() => handleReturn(r.id)}
                            disabled={returningId === r.id}
                          >
                            <IconCheck /> {returningId === r.id ? '…' : 'Вернуть'}
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {showIssueModal && (
        <Modal title="Выдача фильма" onClose={() => { setShowIssueModal(false); setError('') }} size="lg">
          {error && <div className="error-banner">{error}</div>}
          <form onSubmit={handleIssue}>
            <div className="form-grid">
              <div className="form-group full">
                <label>Клиент</label>
                <select required value={issueForm.customer_id} onChange={e => setIssueForm(f => ({ ...f, customer_id: e.target.value }))}>
                  <option value="">— выберите клиента —</option>
                  {customers.map(c => <option key={c.id} value={c.id}>{c.full_name}</option>)}
                </select>
              </div>
              <div className="form-group full">
                <label>Фильм</label>
                <select required value={issueForm.movie_id} onChange={e => handleMovieChange(e.target.value)}>
                  <option value="">— выберите фильм —</option>
                  {movies.filter(m => (m.available_copies_count ?? m.copies_count) > 0).map(m => (
                    <option key={m.id} value={m.id}>{m.title} ({m.available_copies_count ?? m.copies_count} доступных копий)</option>
                  ))}
                </select>
              </div>
              {copies.length > 0 && (
                <div className="form-group full">
                  <label>Копия (инвентарный номер)</label>
                  <select required value={issueForm.movie_copy_id} onChange={e => setIssueForm(f => ({ ...f, movie_copy_id: e.target.value }))}>
                    <option value="">— выберите копию —</option>
                    {copies.map(c => <option key={c.id} value={c.id}>{c.inventory_code} ({c.media_type})</option>)}
                  </select>
                </div>
              )}
              <div className="form-group">
                <label>Количество дней</label>
                <input
                  type="number" min="1" max="7" required
                  value={issueForm.rental_days}
                  onChange={e => setIssueForm(f => ({ ...f, rental_days: e.target.value }))}
                />
              </div>
              {pricePreview > 0 && (
                <div className="form-group">
                  <label>Стоимость аренды</label>
                  <div style={{ padding: '8px 12px', background: 'var(--accent-light)', borderRadius: 6, color: 'var(--accent)', fontWeight: 600 }}>
                    {pricePreview} ₽ + залог {pricePreview * 2} ₽ = <strong>{pricePreview * 3} ₽</strong>
                  </div>
                </div>
              )}
            </div>
            <div className="form-actions">
              <button type="button" className="btn btn-secondary" onClick={() => setShowIssueModal(false)}>Отмена</button>
              <button type="submit" className="btn btn-primary" disabled={saving || !issueForm.movie_copy_id}>
                {saving ? 'Выдача…' : 'Выдать'}
              </button>
            </div>
          </form>
        </Modal>
      )}
    </>
  )
}
