/**
 * Customers Management Page (Staff Only)
 * View and manage consumer accounts
 */
import { useState, useEffect } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import StaffLayout from '../../components/staff/StaffLayout'

const API_URL = import.meta.env.VITE_API_URL

export default function StaffCustomers() {
  const { getAuthHeaders } = useAuth()
  const [customers, setCustomers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCustomer, setSelectedCustomer] = useState(null)
  const [showDetailsModal, setShowDetailsModal] = useState(false)
  const [customerOrders, setCustomerOrders] = useState([])
  const [loadingOrders, setLoadingOrders] = useState(false)

  useEffect(() => {
    fetchCustomers()
  }, [])

  const fetchCustomers = async () => {
    try {
      setLoading(true)
      const response = await fetch(`${API_URL}/api/v1/customers/`, {
        headers: getAuthHeaders(),
      })

      if (!response.ok) {
        throw new Error('Failed to fetch customers')
      }

      const data = await response.json()
      setCustomers(data)
      setError('')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const fetchCustomerOrders = async (customerId) => {
    try {
      setLoadingOrders(true)
      const response = await fetch(`${API_URL}/api/v1/customers/${customerId}/orders`, {
        headers: getAuthHeaders(),
      })

      if (!response.ok) {
        throw new Error('Failed to fetch orders')
      }

      const data = await response.json()
      setCustomerOrders(data)
    } catch (err) {
      console.error('Error fetching customer orders:', err)
      setCustomerOrders([])
    } finally {
      setLoadingOrders(false)
    }
  }

  const openDetailsModal = async (customer) => {
    setSelectedCustomer(customer)
    setShowDetailsModal(true)
    await fetchCustomerOrders(customer.id)
  }

  const closeDetailsModal = () => {
    setSelectedCustomer(null)
    setShowDetailsModal(false)
    setCustomerOrders([])
  }

  // Filter customers by search term
  const filteredCustomers = customers.filter((customer) => {
    const searchLower = searchTerm.toLowerCase()
    return (
      customer.email.toLowerCase().includes(searchLower) ||
      customer.first_name?.toLowerCase().includes(searchLower) ||
      customer.last_name?.toLowerCase().includes(searchLower) ||
      customer.phone?.toLowerCase().includes(searchLower)
    )
  })

  const totalCustomers = customers.length
  const customersWithOrders = customers.filter((c) => c.id).length // Would need order count from backend for accuracy

  return (
    <StaffLayout>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Customer Management</h1>
        <p className="text-gray-600 mt-2">View and manage consumer accounts</p>
      </div>

      {error && (
        <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">Total Customers</p>
              <p className="text-3xl font-bold text-gray-900">{totalCustomers}</p>
            </div>
            <div className="text-4xl">👤</div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">Active Accounts</p>
              <p className="text-3xl font-bold text-green-600">{totalCustomers}</p>
            </div>
            <div className="text-4xl">✅</div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">Showing</p>
              <p className="text-3xl font-bold text-blue-600">{filteredCustomers.length}</p>
            </div>
            <div className="text-4xl">🔍</div>
          </div>
        </div>
      </div>

      {/* Search Bar */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="flex items-center space-x-4">
          <label className="text-sm font-medium text-gray-700">Search:</label>
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search by name, email, or phone..."
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
      </div>

      {/* Customers Table */}
      {loading ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading customers...</p>
        </div>
      ) : filteredCustomers.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <div className="text-6xl mb-4">👤</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">No customers found</h2>
          <p className="text-gray-600">
            {searchTerm ? `No customers match "${searchTerm}"` : 'No customer accounts registered yet.'}
          </p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Customer
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Email
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Phone
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Registered
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredCustomers.map((customer) => (
                <tr key={customer.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div className="text-sm">
                      <div className="font-medium text-gray-900">
                        {customer.first_name} {customer.last_name}
                      </div>
                      <div className="text-gray-500 text-xs">ID: {customer.id.substring(0, 8)}...</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">{customer.email}</td>
                  <td className="px-6 py-4 text-sm text-gray-900">{customer.phone || 'N/A'}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {new Date(customer.created_at).toLocaleDateString('en-IN', {
                      year: 'numeric',
                      month: 'short',
                      day: 'numeric',
                    })}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                    <button
                      onClick={() => openDetailsModal(customer)}
                      className="text-blue-600 hover:text-blue-900 font-medium"
                    >
                      View Details
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Customer Details Modal */}
      {showDetailsModal && selectedCustomer && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-10 mx-auto p-5 border w-full max-w-2xl shadow-lg rounded-md bg-white">
            <div className="mb-4 border-b pb-4">
              <h3 className="text-xl font-bold text-gray-900">Customer Details</h3>
              <p className="text-sm text-gray-600 mt-1">
                {selectedCustomer.first_name} {selectedCustomer.last_name}
              </p>
            </div>

            <div className="space-y-4 mb-6">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-gray-700">First Name</label>
                  <p className="text-gray-900">{selectedCustomer.first_name || 'N/A'}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-700">Last Name</label>
                  <p className="text-gray-900">{selectedCustomer.last_name || 'N/A'}</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-gray-700">Email</label>
                  <p className="text-gray-900">{selectedCustomer.email}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-700">Phone</label>
                  <p className="text-gray-900">{selectedCustomer.phone || 'N/A'}</p>
                </div>
              </div>

              <div>
                <label className="text-sm font-medium text-gray-700">Customer ID</label>
                <p className="text-gray-900 text-xs font-mono">{selectedCustomer.id}</p>
              </div>

              <div>
                <label className="text-sm font-medium text-gray-700">Registered</label>
                <p className="text-gray-900">
                  {new Date(selectedCustomer.created_at).toLocaleString('en-IN')}
                </p>
              </div>
            </div>

            {/* Customer Orders */}
            <div className="border-t pt-4">
              <h4 className="font-semibold text-gray-900 mb-3">Order History</h4>
              {loadingOrders ? (
                <p className="text-gray-600">Loading orders...</p>
              ) : customerOrders.length === 0 ? (
                <p className="text-gray-600">No orders placed yet</p>
              ) : (
                <>
                  <div className="space-y-2 mb-4">
                    {customerOrders.slice(0, 5).map((order) => (
                      <div key={order.id} className="flex justify-between text-sm py-2 border-b">
                        <span className="text-blue-600">{order.order_number}</span>
                        <span className="text-gray-900">
                          ₹{parseFloat(order.total_amount).toLocaleString('en-IN')}
                        </span>
                        <span className="text-gray-600">
                          {new Date(order.created_at).toLocaleDateString('en-IN')}
                        </span>
                        <span className="text-gray-500 text-xs">{order.status}</span>
                      </div>
                    ))}
                    {customerOrders.length > 5 && (
                      <p className="text-sm text-gray-600 text-center pt-2">
                        +{customerOrders.length - 5} more orders
                      </p>
                    )}
                  </div>
                  <div className="bg-blue-50 rounded-lg p-3">
                    <p className="text-sm text-gray-700">
                      <strong>Total Orders:</strong> {customerOrders.length}
                    </p>
                    <p className="text-sm text-gray-700">
                      <strong>Total Spent:</strong> ₹
                      {customerOrders
                        .reduce((sum, order) => sum + parseFloat(order.total_amount), 0)
                        .toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                    </p>
                  </div>
                </>
              )}
            </div>

            <div className="mt-6 flex justify-end">
              <button
                onClick={closeDetailsModal}
                className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </StaffLayout>
  )
}
