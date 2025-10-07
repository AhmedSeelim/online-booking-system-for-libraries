import React from 'react'
import ReactDOM from 'react-dom/client'
import { createBrowserRouter, RouterProvider, Navigate } from 'react-router-dom'
import './styles/index.css'

import { AuthProvider, useAuth } from './context/AuthContext'
import { AIActionProvider } from './context/AIActionContext'
import Layout from './components/Layout'
import Home from './pages/Home'
import Login from './pages/Login'
import Register from './pages/Register'
import Books from './pages/Books'
import BookDetail from './pages/BookDetail'
import Resources from './pages/Resources'
import ResourceDetail from './pages/ResourceDetail'
import MyBookings from './pages/MyBookings'

// Wrapper to protect routes
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { currentUser, isLoading } = useAuth();
  if (isLoading) {
    return <div>Loading session...</div>;
  }
  return currentUser ? <>{children}</> : <Navigate to="/login" replace />;
};

const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      { index: true, element: <Home /> },
      { path: 'books', element: <Books /> },
      { path: 'books/:id', element: <BookDetail /> },
      { path: 'resources', element: <Resources /> },
      { path: 'resources/:id', element: <ProtectedRoute><ResourceDetail /></ProtectedRoute> },
      { path: 'my-bookings', element: <ProtectedRoute><MyBookings /></ProtectedRoute> },
    ],
  },
  { path: '/login', element: <Login /> },
  { path: '/register', element: <Register /> },
]);

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <AuthProvider>
      <AIActionProvider>
        <RouterProvider router={router} />
      </AIActionProvider>
    </AuthProvider>
  </React.StrictMode>,
)
