import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getMovies } from '../api/moviesApi'
import { getCustomers } from '../api/customersApi'
import { getRentals } from '../api/rentalsApi'

export default function DashboardPage() {
  const [movies, setMovies] = useState([])
  const [customers, setCustomers] = useState([])
  const [rentals, setRentals] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([getMovies(), getCustomers(), getRentals()])
      .then(([m, c, r]) => { setMovies(m); setCustomers(c); setRentals(r) })
      .finally(() => setLoading(false))
  }, [])

  const activeRentals = rentals.filter(r => r.is_active)
  const overdueRentals = activeRentals.filter(r => new Date(r.planned_return_date) < new Date())

  if (loading) return <div className="loading">Загрузка…</div>

  return (
    <>
      <div className="page-header">
        <h2 className="page-title">Сводка</h2>
        <p className="page-subtitle">Общая статистика системы</p>
      </div>

      <div className="page-body">
        <div className="stats-row">
          <div className="stat-card">
            <div className="stat-label">Фильмов</div>
            <div className="stat-value accent">{movies.length}</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Клиентов</div>
            <div className="stat-value">{customers.length}</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Активных аренд</div>
            <div className="stat-value success">{activeRentals.length}</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Просрочено</div>
            <div className="stat-value warning">{overdueRentals.length}</div>
          </div>
        </div>

        {overdueRentals.length > 0 && (
          <div className="card" style={{ marginBottom: 20 }}>
            <div className="card-header">
              <span className="card-title">Просроченные аренды</span>
              <span className="badge badge-red">{overdueRentals.length}</span>
            </div>
            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Клиент</th>
                    <th>Фильм</th>
                    <th>Инв. №</th>
                    <th>Срок возврата</th>
                    <th>Дней просрочки</th>
                  </tr>
                </thead>
                <tbody>
                  {overdueRentals.map(r => {
                    const days = Math.ceil((new Date() - new Date(r.planned_return_date)) / 86400000)
                    return (
                      <tr key={r.id}>
                        <td className="td-muted">{r.id}</td>
                        <td>{r.customer_name}</td>
                        <td>{r.movie_title}</td>
                        <td className="td-mono">{r.inventory_code}</td>
                        <td>{new Date(r.planned_return_date).toLocaleDateString('ru-RU')}</td>
                        <td><span className="badge badge-red">+{days} дн.</span></td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}

        <div className="card">
          <div className="card-header">
            <span className="card-title">Последние аренды</span>
            <Link to="/rentals" className="btn btn-secondary btn-sm">Все аренды</Link>
          </div>
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>#</th>
                  <th>Клиент</th>
                  <th>Фильм</th>
                  <th>Выдано</th>
                  <th>Статус</th>
                </tr>
              </thead>
              <tbody>
                {rentals.slice(-10).reverse().map(r => (
                  <tr key={r.id}>
                    <td className="td-muted">{r.id}</td>
                    <td>{r.customer_name}</td>
                    <td>{r.movie_title}</td>
                    <td className="td-muted">{new Date(r.issue_date).toLocaleDateString('ru-RU')}</td>
                    <td>
                      {r.is_active
                        ? <span className="badge badge-blue">Активна</span>
                        : <span className="badge badge-gray">Возвращён</span>}
                    </td>
                  </tr>
                ))}
                {rentals.length === 0 && (
                  <tr><td colSpan={5} className="td-muted" style={{ textAlign: 'center', padding: 32 }}>Аренд нет</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </>
  )
}
