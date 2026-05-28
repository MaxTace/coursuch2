import { createBrowserRouter } from 'react-router-dom'
import MainLayout from './layouts/MainLayout'
import DashboardPage from './pages/DashboardPage'
import MoviesPage from './pages/MoviesPage'
import CustomersPage from './pages/CustomersPage'
import RentalsPage from './pages/RentalsPage'
import CategoriesPage from './pages/CategoriesPage'

const router = createBrowserRouter(
  [
    {
      element: <MainLayout />,
      children: [
        { index: true, element: <DashboardPage /> },
        { path: 'movies', element: <MoviesPage /> },
        { path: 'customers', element: <CustomersPage /> },
        { path: 'rentals', element: <RentalsPage /> },
        { path: 'categories', element: <CategoriesPage /> },
        { path: '*', element: <DashboardPage /> },
      ],
    },
  ],
  {
    future: {
      v7_startTransition: true,
      v7_relativeSplatPath: true,
      v7_fetcherPersist: true,
      v7_normalizeFormMethod: true,
      v7_partialHydration: true,
      v7_skipActionErrorRevalidation: true,
    },
  }
)

export default router
