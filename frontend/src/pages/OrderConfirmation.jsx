/**
 * Order Confirmation Page
 * Shows order details after successful checkout
 */
import { useState, useEffect } from 'react'
import { Link, useParams, useLocation } from 'react-router-dom'

const API_URL = import.meta.env.VITE_API_URL

export default function OrderConfirmation() {
  const { orderNumber } = useParams()
  const location = useLocation()
  const accountCreated = location.state?.accountCreated || false

  const [order, setOrder] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchOrder()
  }, [orderNumber])

  const fetchOrder = async () => {
    try {
      const response = await fetch(`${API_URL}/api/v1/orders/number/${orderNumber}`)

      if (!response.ok) {
        throw new Error('Order not found')
      }

      const data = await response.json()
      setOrder(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading order details...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center bg-white rounded-lg shadow p-12">
          <div className="text-6xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Order Not Found</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <Link
            to="/products"
            className="inline-block px-6 py-3 bg-blue-600 text-white font-semibold rounded-md hover:bg-blue-700"
          >
            Continue Shopping
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <Link to="/" className="text-2xl font-bold text-blue-600">
            Jovey
          </Link>
        </div>
      </div>

      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Success Message */}
        <div className="bg-white rounded-lg shadow-lg p-8 mb-6">
          <div className="text-center">
            <div className="text-6xl mb-4">✅</div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Order Confirmed!</h1>
            <p className="text-gray-600 mb-4">
              Thank you for your order. We've sent a confirmation email to{' '}
              <span className="font-medium">{order?.order?.customer_email}</span>
            </p>

            {accountCreated && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
                <div className="flex items-start">
                  <div className="text-2xl mr-3">🎉</div>
                  <div className="text-left">
                    <h3 className="font-semibold text-green-900 mb-1">Account Created!</h3>
                    <p className="text-sm text-green-700 mb-2">
                      Your account has been created successfully. You can now log in to track your orders and manage your profile.
                    </p>
                    <Link
                      to="/login"
                      className="inline-block text-sm font-medium text-green-700 hover:text-green-800 underline"
                    >
                      Log in to your account →
                    </Link>
                  </div>
                </div>
              </div>
            )}

            <div className="text-2xl font-bold text-blue-600 mb-6">
              Order #{order?.order?.order_number}
            </div>
          </div>

          {/* Order Details */}
          <div className="border-t pt-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Order Details</h2>

            <div className="grid grid-cols-2 gap-6 mb-6">
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-2">Customer Information</h3>
                <p className="text-gray-900">
                  {order?.order?.customer_first_name} {order?.order?.customer_last_name}
                </p>
                <p className="text-gray-600 text-sm">{order?.order?.customer_email}</p>
                {order?.order?.customer_phone && (
                  <p className="text-gray-600 text-sm">{order?.order?.customer_phone}</p>
                )}
              </div>

              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-2">Shipping Address</h3>
                <p className="text-gray-900 text-sm">
                  {order?.order?.shipping_address_line1}
                  {order?.order?.shipping_address_line2 && `, ${order?.order?.shipping_address_line2}`}
                </p>
                <p className="text-gray-600 text-sm">
                  {order?.order?.shipping_city}, {order?.order?.shipping_state} {order?.order?.shipping_postal_code}
                </p>
                <p className="text-gray-600 text-sm">{order?.order?.shipping_country}</p>
              </div>
            </div>

            {/* Order Items */}
            <div className="border-t pt-4">
              <h3 className="text-sm font-medium text-gray-700 mb-3">Items Ordered</h3>
              <div className="space-y-3">
                {order?.items?.map((item) => (
                  <div key={item.id} className="flex justify-between items-center py-2 border-b">
                    <div>
                      <p className="font-medium text-gray-900">{item.product_name}</p>
                      <p className="text-sm text-gray-600">Quantity: {item.quantity}</p>
                    </div>
                    <p className="font-medium text-gray-900">
                      ₹{parseFloat(item.subtotal).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                    </p>
                  </div>
                ))}
              </div>
            </div>

            {/* Order Summary */}
            <div className="border-t pt-4 mt-4">
              <div className="space-y-2">
                <div className="flex justify-between text-gray-600">
                  <span>Subtotal</span>
                  <span>₹{parseFloat(order?.order?.subtotal).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
                </div>
                <div className="flex justify-between text-gray-600">
                  <span>Shipping</span>
                  <span className="text-green-600">FREE</span>
                </div>
                <div className="flex justify-between text-gray-600">
                  <span>Tax</span>
                  <span>₹{parseFloat(order?.order?.tax_amount).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
                </div>
                <div className="border-t pt-2 flex justify-between text-lg font-bold">
                  <span>Total</span>
                  <span>₹{parseFloat(order?.order?.total_amount).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
                </div>
              </div>
            </div>

            {/* Order Status */}
            <div className="border-t pt-4 mt-4">
              <div className="bg-blue-50 rounded-lg p-4">
                <div className="flex items-center">
                  <div className="text-2xl mr-3">📦</div>
                  <div>
                    <p className="font-medium text-blue-900">Order Status: {order?.order?.status}</p>
                    <p className="text-sm text-blue-700">
                      We'll send you updates about your order via email
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="border-t pt-6 mt-6 flex gap-4 justify-center">
            <Link
              to="/products"
              className="px-6 py-3 bg-blue-600 text-white font-semibold rounded-md hover:bg-blue-700"
            >
              Continue Shopping
            </Link>
            {accountCreated && (
              <Link
                to="/login"
                className="px-6 py-3 border border-blue-600 text-blue-600 font-semibold rounded-md hover:bg-blue-50"
              >
                Log In
              </Link>
            )}
          </div>
        </div>

        {/* What's Next */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">What's Next?</h2>
          <div className="space-y-3 text-gray-600">
            <div className="flex items-start">
              <span className="text-2xl mr-3">📧</span>
              <p>You'll receive an order confirmation email shortly with your order details</p>
            </div>
            <div className="flex items-start">
              <span className="text-2xl mr-3">📦</span>
              <p>We'll notify you when your order ships with tracking information</p>
            </div>
            <div className="flex items-start">
              <span className="text-2xl mr-3">💬</span>
              <p>If you have questions, contact us at support@jovey.com</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
