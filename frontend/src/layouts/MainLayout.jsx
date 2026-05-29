import { NavLink, Outlet } from 'react-router-dom'
import { IconFilm, IconUsers, IconClipboard, IconGrid, IconTag } from '../components/Icons'

const navItems = [
  { to: '/',          label: 'Сводка',     icon: <IconGrid />,      end: true },
  { to: '/movies',    label: 'Фильмы',     icon: <IconFilm /> },
  { to: '/customers', label: 'Клиенты',    icon: <IconUsers /> },
  { to: '/rentals',   label: 'Аренды',     icon: <IconClipboard /> },
  { to: '/categories',label: 'Категории',  icon: <IconTag /> },
]

export default function MainLayout() {
  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="sidebar-logo">
          <h1>Видеопрокат</h1>
          <p>Система управления</p>
        </div>
        <nav className="sidebar-nav">
          {navItems.map(({ to, label, icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
            >
              {icon}
              {label}
            </NavLink>
          ))}
        </nav>
      </aside>

      <main className="main-content">
        <Outlet />
      </main>
    </div>
  )
}
