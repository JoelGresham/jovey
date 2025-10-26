/**
 * Dealers Management Page (Staff Only)
 * Manage dealer accounts and approvals
 */
import { useState, useEffect } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import StaffLayout from '../../components/staff/StaffLayout'

const API_URL = import.meta.env.VITE_API_URL

export default function StaffDealers() {
  const { getAuthHeaders } = useAuth()
  const [dealers, setDealers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [selectedDealer, setSelectedDealer] = useState(null)
  const [showDetailsModal, setShowDetailsModal] = useState(false)
  const [showStatusModal, setShowStatusModal] = useState(false)
  const [newStatus, setNewStatus] = useState('')
  const [statusNotes, setStatusNotes] = useState('')
  const [updating, setUpdating] = useState(false)
  const [dealerOrders, setDealerOrders] = useState([])
  const [loadingOrders, setLoadingOrders] = useState(false)

  useEffect(() => {
    fetchDealers()
  }, [statusFilter])

  const fetchDealers = async () => {
    try {
      setLoading(true)
      const url = statusFilter
        ? `${API_URL}/api/v1/dealers/?status_filter=${statusFilter}`
        : `${API_URL}/api/v1/dealers/`

      const response = await fetch(url, {
        headers: getAuthHeaders(),
      })

      if (!response.ok) {
        throw new Error('Failed to fetch dealers')
      }

      const data = await response.json()
      setDealers(data)
      setError('')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const fetchDealerOrders = async (dealerId) => {
    try {
      setLoadingOrders(true)
      const response = await fetch(`${API_URL}/api/v1/dealers/${dealerId}/orders`, {
        headers: getAuthHeaders(),
      })

      if (!response.ok) {
        throw new Error('Failed to fetch orders')
      }

      const data = await response.json()
      setDealerOrders(data)
    } catch (err) {
      console.error('Error fetching dealer orders:', err)
      setDealerOrders([])
    } finally {
      setLoadingOrders(false)
    }
  }

  const openDetailsModal = async (dealer) => {
    setSelectedDealer(dealer)
    setShowDetailsModal(true)
    await fetchDealerOrders(dealer.id)
  }

  const closeDetailsModal = () => {
    setSelectedDealer(null)
    setShowDetailsModal(false)
    setDealerOrders([])
  }

  const openStatusModal = (dealer) => {
    setSelectedDealer(dealer)
    setNewStatus(dealer.dealer_status)
    setStatusNotes('')
    setShowStatusModal(true)
  }

  const closeStatusModal = () => {
    setSelectedDealer(null)
    setShowStatusModal(false)
    setNewStatus('')
    setStatusNotes('')
  }

  const handleStatusUpdate = async (e) => {
    e.preventDefault()
    setUpdating(true)

    try {
      const response = await fetch(`${API_URL}/api/v1/dealers/${selectedDealer.id}/status`, {
        method: 'PUT',
        headers: {
          ...getAuthHeaders(),
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          dealer_status: newStatus,
          notes: statusNotes,
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to update status')
      }

      // Refresh dealers
      await fetchDealers()
      closeStatusModal()
    } catch (err) {
      setError(err.message)
    } finally {
      setUpdating(false)
    }
  }

  const getStatusColor = (status) => {
    const colors = {
      pending: 'bg-yellow-100 text-yellow-800',
      active: 'bg-green-100 text-green-800',
      inactive: 'bg-gray-100 text-gray-800',
      rejected: 'bg-red-100 text-red-800',
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }

  const pendingCount = dealers.filter((d) => d.dealer_status === 'pending').length
  const activeCount = dealers.filter((d) => d.dealer_status === 'active').length

  return (
    <StaffLayout>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dealer Management</h1>
        <p className="text-gray-600 mt-2">Manage dealer accounts and approvals</p>
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
              <p className="text-sm font-medium text-gray-600">Total Dealers</p>
              <p className="text-3xl font-bold text-gray-900">{dealers.length}</p>
            </div>
            <div className="text-4xl">👥</div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">Pending Approval</p>
              <p className="text-3xl font-bold text-yellow-600">{pendingCount}</p>
            </div>
            <div className="text-4xl">⏳</div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">Active Dealers</p>
              <p className="text-3xl font-bold text-green-600">{activeCount}</p>
            </div>
            <div className="text-4xl">✅</div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="flex items-center space-x-4">
          <label className="text-sm font-medium text-gray-700">Filter by Status:</label>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">All Dealers</option>
            <option value="pending">Pending Approval</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="rejected">Rejected</option>
          </select>
        </div>
      </div>

      {/* Dealers Table */}
      {loading ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dealers...</p>
        </div>
      ) : dealers.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <div className="text-6xl mb-4">👥</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">No dealers found</h2>
          <p className="text-gray-600">
            {statusFilter ? `No dealers with status "${statusFilter}"` : 'No dealer accounts registered yet.'}
          </p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Company
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Contact
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Location
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Registered
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {dealers.map((dealer) => (
                <tr key={dealer.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div className="text-sm">
                      <div className="font-medium text-gray-900">{dealer.company_name || 'N/A'}</div>
                      <div className="text-gray-500">ID: {dealer.id.substring(0, 8)}...</div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm">
                      <div className="text-gray-900">
                        {dealer.first_name} {dealer.last_name}
                      </div>
                      <div className="text-gray-500">{dealer.email}</div>
                      {dealer.phone && <div className="text-gray-500">{dealer.phone}</div>}
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    {dealer.city || 'N/A'}
                    {dealer.state && `, ${dealer.state}`}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {new Date(dealer.created_at).toLocaleDateString('en-IN', {
                      year: 'numeric',
                      month: 'short',
                      day: 'numeric',
                    })}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor(
                        dealer.dealer_status
                      )}`}
                    >
                      {dealer.dealer_status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm space-x-2">
                    <button
                      onClick={() => openDetailsModal(dealer)}
                      className="text-blue-600 hover:text-blue-900 font-medium"
                    >
                      View Details
                    </button>
                    <button
                      onClick={() => openStatusModal(dealer)}
                      className="text-green-600 hover:text-green-900 font-medium"
                    >
                      Update Status
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Dealer Details Modal */}
      {showDetailsModal && selectedDealer && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-10 mx-auto p-5 border w-full max-w-2xl shadow-lg rounded-md bg-white">
            <div className="mb-4 border-b pb-4">
              <h3 className="text-xl font-bold text-gray-900">Dealer Details</h3>
              <p className="text-sm text-gray-600 mt-1">{selectedDealer.company_name}</p>
            </div>

            <div className="space-y-4 mb-6">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-gray-700">Company Name</label>
                  <p className="text-gray-900">{selectedDealer.company_name || 'N/A'}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-700">Status</label>
                  <p>
                    <span
                      className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor(
                        selectedDealer.dealer_status
                      )}`}
                    >
                      {selectedDealer.dealer_status}
                    </span>
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-gray-700">Contact Person</label>
                  <p className="text-gray-900">
                    {selectedDealer.first_name} {selectedDealer.last_name}
                  </p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-700">Email</label>
                  <p className="text-gray-900">{selectedDealer.email}</p>
                </div>
              </div>

              {selectedDealer.phone && (
                <div>
                  <label className="text-sm font-medium text-gray-700">Phone</label>
                  <p className="text-gray-900">{selectedDealer.phone}</p>
                </div>
              )}

              <div>
                <label className="text-sm font-medium text-gray-700">Registered</label>
                <p className="text-gray-900">
                  {new Date(selectedDealer.created_at).toLocaleString('en-IN')}
                </p>
              </div>
            </div>

            {/* Dealer Orders */}
            <div className="border-t pt-4">
              <h4 className="font-semibold text-gray-900 mb-3">Order History</h4>
              {loadingOrders ? (
                <p className="text-gray-600">Loading orders...</p>
              ) : dealerOrders.length === 0 ? (
                <p className="text-gray-600">No orders placed yet</p>
              ) : (
                <div className="space-y-2">
                  {dealerOrders.slice(0, 5).map((order) => (
                    <div key={order.id} className="flex justify-between text-sm py-2 border-b">
                      <span className="text-blue-600">{order.order_number}</span>
                      <span className="text-gray-900">
                        ₹{parseFloat(order.total_amount).toLocaleString('en-IN')}
                      </span>
                      <span className="text-gray-600">
                        {new Date(order.created_at).toLocaleDateString('en-IN')}
                      </span>
                    </div>
                  ))}
                  {dealerOrders.length > 5 && (
                    <p className="text-sm text-gray-600 text-center pt-2">
                      +{dealerOrders.length - 5} more orders
                    </p>
                  )}
                </div>
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

      {/* Status Update Modal */}
      {showStatusModal && selectedDealer && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mb-4">
              <h3 className="text-lg font-bold text-gray-900">Update Dealer Status</h3>
              <p className="text-sm text-gray-600 mt-1">{selectedDealer.company_name}</p>
            </div>

            <form onSubmit={handleStatusUpdate}>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">New Status *</label>
                <select
                  value={newStatus}
                  onChange={(e) => setNewStatus(e.target.value)}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="pending">Pending</option>
                  <option value="active">Active</option>
                  <option value="inactive">Inactive</option>
                  <option value="rejected">Rejected</option>
                </select>
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Notes (optional)
                </label>
                <textarea
                  value={statusNotes}
                  onChange={(e) => setStatusNotes(e.target.value)}
                  rows="3"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Add any notes about this status change..."
                />
              </div>

              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={closeStatusModal}
                  disabled={updating}
                  className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 disabled:opacity-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={updating}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                >
                  {updating ? 'Updating...' : 'Update Status'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </StaffLayout>
  )
}
