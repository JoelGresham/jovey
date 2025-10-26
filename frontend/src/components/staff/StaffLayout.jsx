/**
 * Staff Layout Component
 * Shared layout with navigation tabs for staff pages
 */
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'

export default function StaffLayout({ children }) {
  const location = useLocation()
  const navigate = useNavigate()
  const { user, profile, signOut } = useAuth()

  const handleSignOut = async () => {
    await signOut()
    navigate('/login')
  }

  const tabs = [
    { name: 'Categories', path: '/staff/categories', icon: '📁' },
    { name: 'Products', path: '/staff/products', icon: '📦' },
    { name: 'Orders', path: '/staff/orders', icon: '📋' },
    { name: 'Customers', path: '/staff/customers', icon: '👤' },
    { name: 'Dealers', path: '/staff/dealers', icon: '👥' },
    { name: 'Database Manager', path: '/staff/database-manager', icon: '⚙️' },
  ]

  const isActiveTab = (path) => {
    return location.pathname === path
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <Link to="/" className="text-2xl font-bold text-blue-600">
                Jovey
              </Link>
              <span className="ml-4 px-3 py-1 bg-purple-100 text-purple-800 text-xs font-semibold rounded-full">
                Staff Portal
              </span>
            </div>
            <div className="flex items-center space-x-4">
              <Link
                to="/dashboard"
                className="text-sm font-medium text-gray-700 hover:text-gray-900"
              >
                Dashboard
              </Link>
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-700">
                  {profile?.first_name || user?.email}
                </span>
                <button
                  onClick={handleSignOut}
                  className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
                >
                  Sign Out
                </button>
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Tab Navigation */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8">
            {tabs.map((tab) => (
              <Link
                key={tab.path}
                to={tab.path}
                className={`
                  flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors
                  ${
                    isActiveTab(tab.path)
                      ? 'border-blue-600 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                `}
              >
                <span className="text-lg">{tab.icon}</span>
                <span>{tab.name}</span>
              </Link>
            ))}
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </div>
  )
}
