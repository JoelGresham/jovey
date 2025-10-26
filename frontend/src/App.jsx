/**
 * Main App Component
 * Handles routing and authentication
 */
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import { CartProvider } from './contexts/CartContext'
import ProtectedRoute from './components/auth/ProtectedRoute'
import Login from './pages/auth/Login'
import Register from './pages/auth/Register'
import Dashboard from './pages/Dashboard'
import Home from './pages/Home'
import Categories from './pages/staff/Categories'
import StaffProducts from './pages/staff/Products'
import StaffOrders from './pages/staff/Orders'
import StaffDealers from './pages/staff/Dealers'
import StaffCustomers from './pages/staff/Customers'
import DatabaseManager from './pages/staff/DatabaseManager'
import Products from './pages/Products'
import ProductDetail from './pages/ProductDetail'
import Cart from './pages/Cart'
import Checkout from './pages/Checkout'
import OrderConfirmation from './pages/OrderConfirmation'
import OrderHistory from './pages/user/OrderHistory'
import Profile from './pages/user/Profile'

function App() {
  return (
    <Router>
      <AuthProvider>
        <CartProvider>
          <Routes>
          {/* Public routes */}
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/products" element={<Products />} />
          <Route path="/products/:slug" element={<ProductDetail />} />
          <Route path="/cart" element={<Cart />} />
          <Route path="/checkout" element={<Checkout />} />
          <Route path="/order-confirmation/:orderNumber" element={<OrderConfirmation />} />

          {/* Protected routes */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />

          {/* Dealer portal */}
          <Route
            path="/dealer"
            element={
              <ProtectedRoute requiredUserType="dealer">
                <Dashboard />
              </ProtectedRoute>
            }
          />

          {/* Staff dashboard */}
          <Route
            path="/staff"
            element={
              <ProtectedRoute requiredUserType="staff">
                <Dashboard />
              </ProtectedRoute>
            }
          />

          {/* Staff categories management */}
          <Route
            path="/staff/categories"
            element={
              <ProtectedRoute requiredUserType="staff">
                <Categories />
              </ProtectedRoute>
            }
          />

          {/* Staff products management */}
          <Route
            path="/staff/products"
            element={
              <ProtectedRoute requiredUserType="staff">
                <StaffProducts />
              </ProtectedRoute>
            }
          />

          {/* Staff orders management */}
          <Route
            path="/staff/orders"
            element={
              <ProtectedRoute requiredUserType="staff">
                <StaffOrders />
              </ProtectedRoute>
            }
          />

          {/* Staff dealers management */}
          <Route
            path="/staff/dealers"
            element={
              <ProtectedRoute requiredUserType="staff">
                <StaffDealers />
              </ProtectedRoute>
            }
          />

          {/* Staff customers management */}
          <Route
            path="/staff/customers"
            element={
              <ProtectedRoute requiredUserType="staff">
                <StaffCustomers />
              </ProtectedRoute>
            }
          />

          {/* Database Manager */}
          <Route
            path="/staff/database-manager"
            element={
              <ProtectedRoute requiredUserType="staff">
                <DatabaseManager />
              </ProtectedRoute>
            }
          />

          {/* User profile routes */}
          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <Profile />
              </ProtectedRoute>
            }
          />

          <Route
            path="/orders"
            element={
              <ProtectedRoute>
                <OrderHistory />
              </ProtectedRoute>
            }
          />

          {/* Catch all - redirect to home */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
        </CartProvider>
      </AuthProvider>
    </Router>
  )
}

export default App
