import { useState, useEffect } from 'react'
import { getCustomers, createCustomer } from '../api/customersApi'
import Modal from '../components/Modal'
import { IconPlus, IconSearch, IconUsers } from '../components/Icons'

const EMPTY = { full_name: '', birth_date: '', phone: '', email: '' }

export default function CustomersPage() {
  const [customers, setCustomers] = useState([])
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [form, setForm] = useState(EMPTY)
  const [saving, setSaving] = useState(false)

  const load = () => {
    setLoading(true)
    getCustomers()
      .then(setCustomers)
      .catch(() => setError('Ошибка загрузки'))
      .finally(() => setLoading(false))
  }

  useEffect(load, [])

  const filtered = customers.filter(c =>
    c.full_name.toLowerCase().includes(search.toLowerCase()) ||
    (c.phone && c.phone.includes(search)) ||
    (c.email && c.email.toLowerCase().includes(search.toLowerCase()))
  )

  const handleSave = async (e) => {
    e.preventDefault()
    setSaving(true)
    setError('')
    try {
      await createCustomer(form)
      setShowModal(false)
      setForm(EMPTY)
      load()
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка сохранения')
    } finally {
      setSaving(false)
    }
  }

  const age = (birthDate) => {
    if (!birthDate) return '—'
    const d = new Date(birthDate)
    const now = new Date()
    return Math.floor((now - d) / (365.25 * 86400000))
  }

  return (
    <>
      <div className="page-header">
        <h2 className="page-title">Клиенты</h2>
        <p className="page-subtitle">База клиентов видеопроката</p>
      </div>

      <div className="page-body">
        {error && <div className="error-banner">{error}</div>}

        <div className="toolbar">
          <div className="search-wrap">
            <IconSearch />
            <input
              placeholder="Поиск по ФИО, телефону или email…"
              value={search}
              onChange={e => setSearch(e.target.value)}
            />
          </div>
          <button className="btn btn-primary" onClick={() => setShowModal(true)}>
            <IconPlus /> Добавить клиента
          </button>
        </div>

        <div className="card">
          {loading ? (
            <div className="loading">Загрузка…</div>
          ) : filtered.length === 0 ? (
            <div className="empty-state">
              <IconUsers />
              <p>{search ? 'Ничего не найдено' : 'Клиентов нет. Добавьте первого!'}</p>
            </div>
          ) : (
            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>#</th>
                    <th>ФИО</th>
                    <th>Возраст</th>
                    <th>Телефон</th>
                    <th>Email</th>
                    <th>Дата регистрации</th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map(c => (
                    <tr key={c.id}>
                      <td className="td-muted">{c.id}</td>
                      <td style={{ fontWeight: 500 }}>{c.full_name}</td>
                      <td className="td-muted">{age(c.birth_date)} лет</td>
                      <td className="td-muted">{c.phone || '—'}</td>
                      <td className="td-muted">{c.email || '—'}</td>
                      <td className="td-muted">
                        {c.registration_date
                          ? new Date(c.registration_date).toLocaleDateString('ru-RU')
                          : '—'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {showModal && (
        <Modal title="Добавить клиента" onClose={() => { setShowModal(false); setError('') }}>
          {error && <div className="error-banner">{error}</div>}
          <form onSubmit={handleSave}>
            <div className="form-grid">
              <div className="form-group full">
                <label>ФИО</label>
                <input required placeholder="Иванов Иван Иванович" value={form.full_name} onChange={e => setForm(f => ({ ...f, full_name: e.target.value }))} />
              </div>
              <div className="form-group">
                <label>Дата рождения</label>
                <input type="date" required value={form.birth_date} onChange={e => setForm(f => ({ ...f, birth_date: e.target.value }))} />
              </div>
              <div className="form-group">
                <label>Телефон</label>
                <input placeholder="+79001234567" value={form.phone} onChange={e => setForm(f => ({ ...f, phone: e.target.value }))} />
              </div>
              <div className="form-group full">
                <label>Email</label>
                <input type="email" placeholder="example@mail.ru" value={form.email} onChange={e => setForm(f => ({ ...f, email: e.target.value }))} />
              </div>
            </div>
            <div className="form-actions">
              <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>Отмена</button>
              <button type="submit" className="btn btn-primary" disabled={saving}>
                {saving ? 'Сохранение…' : 'Добавить'}
              </button>
            </div>
          </form>
        </Modal>
      )}
    </>
  )
}
