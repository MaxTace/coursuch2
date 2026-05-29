import { useState, useEffect } from 'react'
import { getCategories, createCategory } from '../api/moviesApi'
import Modal from '../components/Modal'
import { IconPlus, IconTag } from '../components/Icons'

export default function CategoriesPage() {
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [form, setForm] = useState({ name: '', code: '' })
  const [saving, setSaving] = useState(false)

  const load = () => {
    setLoading(true)
    getCategories()
      .then(setCategories)
      .catch(() => setError('Ошибка загрузки'))
      .finally(() => setLoading(false))
  }

  useEffect(load, [])

  const handleSave = async (e) => {
    e.preventDefault()
    setSaving(true)
    setError('')
    try {
      await createCategory({ name: form.name, code: form.code.toUpperCase() })
      setShowModal(false)
      setForm({ name: '', code: '' })
      load()
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка сохранения')
    } finally {
      setSaving(false)
    }
  }

  return (
    <>
      <div className="page-header">
        <h2 className="page-title">Категории</h2>
        <p className="page-subtitle">Жанры и типы фильмов</p>
      </div>

      <div className="page-body">
        {error && <div className="error-banner">{error}</div>}

        <div className="toolbar">
          <div style={{ flex: 1 }} />
          <button className="btn btn-primary" onClick={() => { setShowModal(true); setError('') }}>
            <IconPlus /> Добавить категорию
          </button>
        </div>

        <div className="card">
          {loading ? (
            <div className="loading">Загрузка…</div>
          ) : categories.length === 0 ? (
            <div className="empty-state">
              <IconTag />
              <p>Категорий нет. Добавьте первую!</p>
            </div>
          ) : (
            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Название</th>
                    <th>Код</th>
                  </tr>
                </thead>
                <tbody>
                  {categories.map(c => (
                    <tr key={c.id}>
                      <td className="td-muted">{c.id}</td>
                      <td style={{ fontWeight: 500 }}>{c.name}</td>
                      <td><span className="badge badge-blue">{c.code}</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {showModal && (
        <Modal title="Добавить категорию" onClose={() => { setShowModal(false); setError('') }}>
          {error && <div className="error-banner">{error}</div>}
          <form onSubmit={handleSave}>
            <div className="form-grid">
              <div className="form-group full">
                <label>Название категории</label>
                <input required placeholder="Боевик" value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))} />
              </div>
              <div className="form-group full">
                <label>Код (3-5 латинских букв)</label>
                <input
                  required maxLength={5}
                  placeholder="ACT"
                  value={form.code}
                  onChange={e => setForm(f => ({ ...f, code: e.target.value.toUpperCase().replace(/[^A-Z]/g, '') }))}
                />
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
