import { useState, useEffect } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import StaffLayout from '../../components/staff/StaffLayout'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function DatabaseManager() {
  const { getAuthHeaders: contextGetAuthHeaders } = useAuth()
  const [stats, setStats] = useState(null)
  const [events, setEvents] = useState([])
  const [mappings, setMappings] = useState([])
  const [processing, setProcessing] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [activeTab, setActiveTab] = useState('dashboard') // dashboard, events, mappings
  const [filter, setFilter] = useState({
    is_processed: null,
    event_type: '',
    limit: 100
  })

  const getAuthHeaders = () => ({
    ...contextGetAuthHeaders(),
    'Content-Type': 'application/json',
  })

  // Fetch Database Manager stats
  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_URL}/api/v1/database-manager/stats`, {
        headers: getAuthHeaders(),
      })

      if (!response.ok) throw new Error('Failed to fetch stats')

      const data = await response.json()
      setStats(data)
    } catch (err) {
      console.error('Error fetching stats:', err)
    }
  }

  // Fetch events
  const fetchEvents = async () => {
    try {
      const params = new URLSearchParams()
      if (filter.is_processed !== null) params.append('is_processed', filter.is_processed)
      if (filter.event_type) params.append('event_type', filter.event_type)
      params.append('limit', filter.limit)

      const response = await fetch(`${API_URL}/api/v1/events?${params}`, {
        headers: getAuthHeaders(),
      })

      if (!response.ok) throw new Error('Failed to fetch events')

      const data = await response.json()
      setEvents(data)
    } catch (err) {
      console.error('Error fetching events:', err)
      setError('Failed to fetch events')
    }
  }

  // Fetch event mappings
  const fetchMappings = async () => {
    try {
      const response = await fetch(`${API_URL}/api/v1/database-manager/mappings`, {
        headers: getAuthHeaders(),
      })

      if (!response.ok) throw new Error('Failed to fetch mappings')

      const data = await response.json()
      setMappings(data)
    } catch (err) {
      console.error('Error fetching mappings:', err)
    }
  }

  // Process pending events
  const handleProcessEvents = async () => {
    setProcessing(true)
    setError('')
    setSuccess('')

    try {
      const response = await fetch(`${API_URL}/api/v1/database-manager/process?limit=100`, {
        method: 'POST',
        headers: getAuthHeaders(),
      })

      if (!response.ok) throw new Error('Failed to process events')

      const result = await response.json()

      setSuccess(
        `Processed ${result.total_events} events: ${result.successful} successful, ${result.failed} failed`
      )

      // Refresh data
      await fetchStats()
      await fetchEvents()
    } catch (err) {
      console.error('Error processing events:', err)
      setError('Failed to process events: ' + err.message)
    } finally {
      setProcessing(false)
    }
  }

  // Initial load
  useEffect(() => {
    const loadData = async () => {
      setLoading(true)
      await Promise.all([fetchStats(), fetchEvents(), fetchMappings()])
      setLoading(false)
    }

    loadData()
  }, [])

  // Reload events when filter changes
  useEffect(() => {
    if (!loading) {
      fetchEvents()
    }
  }, [filter])

  if (loading) {
    return (
      <StaffLayout>
        <div className="flex justify-center items-center h-64">
          <div className="text-xl text-gray-600">Loading Database Manager...</div>
        </div>
      </StaffLayout>
    )
  }

  return (
    <StaffLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Database Manager</h1>
            <p className="text-gray-600 mt-1">
              Monitor and process events from the event sourcing log
            </p>
          </div>
          <button
            onClick={handleProcessEvents}
            disabled={processing || (stats && stats.events_pending === 0)}
            className={`px-6 py-3 rounded-lg font-semibold text-white transition-colors ${
              processing || (stats && stats.events_pending === 0)
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700'
            }`}
          >
            {processing ? (
              <>
                <span className="animate-spin inline-block mr-2">⚙️</span>
                Processing...
              </>
            ) : (
              <>🔄 Process Pending Events</>
            )}
          </button>
        </div>

        {/* Success/Error Messages */}
        {success && (
          <div className="bg-green-50 border border-green-200 text-green-800 px-4 py-3 rounded-lg">
            ✅ {success}
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg">
            ❌ {error}
          </div>
        )}

        {/* Tabs */}
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('dashboard')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'dashboard'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              📊 Dashboard
            </button>
            <button
              onClick={() => setActiveTab('events')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'events'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              📝 Event Stream
            </button>
            <button
              onClick={() => setActiveTab('mappings')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'mappings'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              🗺️ Event Mappings
            </button>
          </nav>
        </div>

        {/* Dashboard Tab */}
        {activeTab === 'dashboard' && stats && (
          <div className="space-y-6">
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="bg-blue-50 p-6 rounded-lg border border-blue-200">
                <div className="text-blue-600 text-sm font-semibold mb-1">Total Processed</div>
                <div className="text-3xl font-bold text-blue-900">
                  {stats.total_events_processed.toLocaleString()}
                </div>
              </div>

              <div className="bg-yellow-50 p-6 rounded-lg border border-yellow-200">
                <div className="text-yellow-600 text-sm font-semibold mb-1">Pending</div>
                <div className="text-3xl font-bold text-yellow-900">
                  {stats.events_pending.toLocaleString()}
                </div>
              </div>

              <div className="bg-red-50 p-6 rounded-lg border border-red-200">
                <div className="text-red-600 text-sm font-semibold mb-1">Failed</div>
                <div className="text-3xl font-bold text-red-900">
                  {stats.events_failed.toLocaleString()}
                </div>
              </div>

              <div className="bg-green-50 p-6 rounded-lg border border-green-200">
                <div className="text-green-600 text-sm font-semibold mb-1">Success Rate</div>
                <div className="text-3xl font-bold text-green-900">
                  {stats.success_rate.toFixed(1)}%
                </div>
              </div>
            </div>

            {/* Event Type Breakdown */}
            <div className="bg-white p-6 rounded-lg border border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Event Type Breakdown</h3>
              {Object.keys(stats.event_type_breakdown).length > 0 ? (
                <div className="space-y-3">
                  {Object.entries(stats.event_type_breakdown)
                    .sort((a, b) => b[1] - a[1])
                    .map(([eventType, count]) => (
                      <div key={eventType} className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <span className="text-sm font-mono text-gray-700">{eventType}</span>
                        </div>
                        <div className="flex items-center space-x-3">
                          <div className="w-48 bg-gray-200 rounded-full h-2">
                            <div
                              className="bg-blue-600 h-2 rounded-full"
                              style={{
                                width: `${(count / stats.total_events_processed) * 100}%`
                              }}
                            />
                          </div>
                          <span className="text-sm font-semibold text-gray-900 w-16 text-right">
                            {count.toLocaleString()}
                          </span>
                        </div>
                      </div>
                    ))}
                </div>
              ) : (
                <p className="text-gray-500">No events processed yet</p>
              )}
            </div>

            {/* Last Processed */}
            {stats.last_processed_at && (
              <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                <span className="text-sm text-gray-600">Last Processed: </span>
                <span className="text-sm font-semibold text-gray-900">
                  {new Date(stats.last_processed_at).toLocaleString()}
                </span>
              </div>
            )}
          </div>
        )}

        {/* Event Stream Tab */}
        {activeTab === 'events' && (
          <div className="space-y-4">
            {/* Filters */}
            <div className="bg-white p-4 rounded-lg border border-gray-200">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Processing Status
                  </label>
                  <select
                    value={filter.is_processed === null ? 'all' : filter.is_processed}
                    onChange={(e) =>
                      setFilter({
                        ...filter,
                        is_processed: e.target.value === 'all' ? null : e.target.value === 'true'
                      })
                    }
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  >
                    <option value="all">All Events</option>
                    <option value="false">Unprocessed Only</option>
                    <option value="true">Processed Only</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Event Type
                  </label>
                  <input
                    type="text"
                    placeholder="e.g., product.created"
                    value={filter.event_type}
                    onChange={(e) => setFilter({ ...filter, event_type: e.target.value })}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Limit</label>
                  <select
                    value={filter.limit}
                    onChange={(e) => setFilter({ ...filter, limit: parseInt(e.target.value) })}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  >
                    <option value="10">10 events</option>
                    <option value="50">50 events</option>
                    <option value="100">100 events</option>
                    <option value="500">500 events</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Events List */}
            <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Event #
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Type
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Aggregate
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Created By
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Created At
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Status
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {events.length > 0 ? (
                      events.map((event) => (
                        <tr key={event.id} className="hover:bg-gray-50">
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-900">
                            #{event.event_number}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-blue-600">
                            {event.event_type}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                            {event.aggregate_type}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                            {event.created_by}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                            {new Date(event.created_at).toLocaleString()}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            {event.is_processed ? (
                              <span className="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                                ✓ Processed
                              </span>
                            ) : event.processing_error ? (
                              <span className="px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800">
                                ✗ Failed
                              </span>
                            ) : (
                              <span className="px-2 py-1 text-xs font-semibold rounded-full bg-yellow-100 text-yellow-800">
                                ⏳ Pending
                              </span>
                            )}
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan="6" className="px-6 py-8 text-center text-gray-500">
                          No events found
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* Mappings Tab */}
        {activeTab === 'mappings' && (
          <div className="space-y-4">
            {mappings.map((mapping) => (
              <div key={mapping.event_type} className="bg-white p-6 rounded-lg border border-gray-200">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h3 className="text-lg font-mono font-semibold text-blue-600">
                      {mapping.event_type}
                    </h3>
                    <p className="text-sm text-gray-600 mt-1">{mapping.description}</p>
                  </div>
                  <span className="px-3 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-700">
                    {mapping.aggregate_type}
                  </span>
                </div>
                <div className="mt-4">
                  <h4 className="text-sm font-semibold text-gray-700 mb-2">Operations:</h4>
                  <ul className="list-disc list-inside space-y-1">
                    {mapping.operations.map((op, idx) => (
                      <li key={idx} className="text-sm text-gray-600">
                        {op}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </StaffLayout>
  )
}
