/**
 * Dashboard Page
 * Main dashboard after login
 */
import { useAuth } from '../contexts/AuthContext'
import { useNavigate, Link } from 'react-router-dom'

export default function Dashboard() {
  const { user, profile, signOut } = useAuth()
  const navigate = useNavigate()

  const handleSignOut = async () => {
    await signOut()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-gray-900">Jovey Dashboard</h1>
            </div>
            <div className="flex items-center">
              <button
                onClick={handleSignOut}
                className="ml-4 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
              >
                Sign Out
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Welcome, {profile?.first_name || user?.email}!
            </h2>

            <div className="space-y-4">
              <div>
                <h3 className="text-lg font-medium text-gray-900">Account Information</h3>
                <dl className="mt-2 border-t border-gray-200 divide-y divide-gray-200">
                  <div className="py-3 flex justify-between text-sm">
                    <dt className="font-medium text-gray-500">Email</dt>
                    <dd className="text-gray-900">{user?.email}</dd>
                  </div>
                  <div className="py-3 flex justify-between text-sm">
                    <dt className="font-medium text-gray-500">Account Type</dt>
                    <dd className="text-gray-900 capitalize">{profile?.user_type}</dd>
                  </div>
                  {profile?.company_name && (
                    <div className="py-3 flex justify-between text-sm">
                      <dt className="font-medium text-gray-500">Company</dt>
                      <dd className="text-gray-900">{profile.company_name}</dd>
                    </div>
                  )}
                  {profile?.dealer_status && (
                    <div className="py-3 flex justify-between text-sm">
                      <dt className="font-medium text-gray-500">Dealer Status</dt>
                      <dd className={`capitalize ${
                        profile.dealer_status === 'active' ? 'text-green-600' : 'text-yellow-600'
                      }`}>
                        {profile.dealer_status}
                      </dd>
                    </div>
                  )}
                  <div className="py-3 flex justify-between text-sm">
                    <dt className="font-medium text-gray-500">Member Since</dt>
                    <dd className="text-gray-900">
                      {new Date(profile?.created_at).toLocaleDateString()}
                    </dd>
                  </div>
                </dl>
              </div>

              {/* User Quick Links */}
              <div className="mt-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Links</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  <Link
                    to="/profile"
                    className="block p-6 bg-white border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:shadow-md transition"
                  >
                    <div className="text-2xl mb-2">👤</div>
                    <h4 className="font-semibold text-gray-900">My Profile</h4>
                    <p className="text-sm text-gray-600 mt-1">
                      Manage your account settings
                    </p>
                  </Link>

                  <Link
                    to="/orders"
                    className="block p-6 bg-white border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:shadow-md transition"
                  >
                    <div className="text-2xl mb-2">📋</div>
                    <h4 className="font-semibold text-gray-900">My Orders</h4>
                    <p className="text-sm text-gray-600 mt-1">
                      View your order history
                    </p>
                  </Link>

                  <Link
                    to="/products"
                    className="block p-6 bg-white border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:shadow-md transition"
                  >
                    <div className="text-2xl mb-2">🛒</div>
                    <h4 className="font-semibold text-gray-900">Browse Products</h4>
                    <p className="text-sm text-gray-600 mt-1">
                      Shop for water pumps
                    </p>
                  </Link>
                </div>
              </div>

              {/* Staff Quick Links */}
              {profile?.user_type === 'staff' && (
                <div className="mt-6">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Staff Tools</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    <Link
                      to="/staff/categories"
                      className="block p-6 bg-white border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:shadow-md transition"
                    >
                      <div className="text-2xl mb-2">📁</div>
                      <h4 className="font-semibold text-gray-900">Categories</h4>
                      <p className="text-sm text-gray-600 mt-1">
                        Manage product categories
                      </p>
                    </Link>

                    <Link
                      to="/staff/products"
                      className="block p-6 bg-white border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:shadow-md transition"
                    >
                      <div className="text-2xl mb-2">📦</div>
                      <h4 className="font-semibold text-gray-900">Products</h4>
                      <p className="text-sm text-gray-600 mt-1">
                        Manage product catalog
                      </p>
                    </Link>

                    <div className="block p-6 bg-gray-50 border-2 border-gray-200 rounded-lg opacity-50">
                      <div className="text-2xl mb-2">📋</div>
                      <h4 className="font-semibold text-gray-900">Orders</h4>
                      <p className="text-sm text-gray-600 mt-1">
                        Coming soon...
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
