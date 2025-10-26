/**
 * Public Products Catalog Page
 * Browse all products available for purchase
 */
import { useState, useEffect } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { useCart } from '../contexts/CartContext'

const API_URL = import.meta.env.VITE_API_URL

export default function Products() {
  const [searchParams, setSearchParams] = useSearchParams()
  const { getCartCount } = useCart()
  const [products, setProducts] = useState([])
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const selectedCategory = searchParams.get('category') || ''
  const searchQuery = searchParams.get('search') || ''
  const cartCount = getCartCount()

  // Fetch products and categories
  const fetchData = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams()
      if (selectedCategory) params.append('category_id', selectedCategory)
      if (searchQuery) params.append('search', searchQuery)

      const [productsRes, categoriesRes] = await Promise.all([
        fetch(`${API_URL}/api/v1/products/?${params.toString()}`),
        fetch(`${API_URL}/api/v1/categories/`)
      ])

      if (!productsRes.ok || !categoriesRes.ok) {
        throw new Error('Failed to fetch data')
      }

      const [productsData, categoriesData] = await Promise.all([
        productsRes.json(),
        categoriesRes.json()
      ])

      setProducts(productsData)
      setCategories(categoriesData)
      setError('')
    } catch (err) {
      setError('Failed to load products')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [selectedCategory, searchQuery])

  const handleCategoryChange = (categoryId) => {
    if (categoryId) {
      searchParams.set('category', categoryId)
    } else {
      searchParams.delete('category')
    }
    searchParams.delete('search')
    setSearchParams(searchParams)
  }

  const handleSearch = (e) => {
    e.preventDefault()
    const formData = new FormData(e.target)
    const search = formData.get('search')

    if (search) {
      searchParams.set('search', search)
    } else {
      searchParams.delete('search')
    }
    searchParams.delete('category')
    setSearchParams(searchParams)
  }

  const clearFilters = () => {
    setSearchParams({})
  }

  const getCategoryName = (id) => {
    const cat = categories.find(c => c.id === id)
    return cat ? cat.name : ''
  }

  if (loading && products.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="text-center">Loading products...</div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex justify-between items-center">
            <div>
              <Link to="/" className="text-2xl font-bold text-blue-600">
                Jovey
              </Link>
              <p className="text-gray-600 mt-1">Water Pump Solutions</p>
            </div>
            <div className="flex items-center space-x-4">
              <Link to="/" className="text-gray-700 hover:text-gray-900">
                Home
              </Link>
              <Link to="/products" className="text-blue-600 font-medium">
                Products
              </Link>
              <Link to="/cart" className="relative text-gray-700 hover:text-gray-900">
                <span className="text-2xl">🛒</span>
                {cartCount > 0 && (
                  <span className="absolute -top-1 -right-1 bg-blue-600 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                    {cartCount}
                  </span>
                )}
              </Link>
              <Link
                to="/login"
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
              >
                Sign In
              </Link>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col lg:flex-row gap-8">
          {/* Sidebar - Filters */}
          <aside className="lg:w-64 flex-shrink-0">
            <div className="bg-white rounded-lg shadow p-6 sticky top-8">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Filters</h2>

              {/* Search */}
              <form onSubmit={handleSearch} className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Search
                </label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    name="search"
                    defaultValue={searchQuery}
                    placeholder="Search products..."
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                  <button
                    type="submit"
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 text-sm"
                  >
                    Go
                  </button>
                </div>
              </form>

              {/* Categories */}
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-3">Categories</h3>
                <div className="space-y-2">
                  <button
                    onClick={() => handleCategoryChange('')}
                    className={`w-full text-left px-3 py-2 rounded-md text-sm ${
                      !selectedCategory
                        ? 'bg-blue-50 text-blue-700 font-medium'
                        : 'text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    All Products
                  </button>
                  {categories.map((category) => (
                    <button
                      key={category.id}
                      onClick={() => handleCategoryChange(category.id)}
                      className={`w-full text-left px-3 py-2 rounded-md text-sm ${
                        selectedCategory === category.id
                          ? 'bg-blue-50 text-blue-700 font-medium'
                          : 'text-gray-700 hover:bg-gray-50'
                      }`}
                    >
                      {category.name}
                    </button>
                  ))}
                </div>
              </div>

              {/* Clear Filters */}
              {(selectedCategory || searchQuery) && (
                <button
                  onClick={clearFilters}
                  className="w-full mt-4 px-4 py-2 text-sm text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50"
                >
                  Clear Filters
                </button>
              )}
            </div>
          </aside>

          {/* Main Content - Products Grid */}
          <main className="flex-1">
            {/* Results Header */}
            <div className="mb-6">
              <h1 className="text-3xl font-bold text-gray-900">
                {selectedCategory ? getCategoryName(selectedCategory) : 'All Products'}
              </h1>
              <p className="text-gray-600 mt-2">
                {products.length} {products.length === 1 ? 'product' : 'products'} found
                {searchQuery && ` for "${searchQuery}"`}
              </p>
            </div>

            {error && (
              <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                {error}
              </div>
            )}

            {/* Products Grid */}
            {products.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {products.map((product) => (
                  <Link
                    key={product.id}
                    to={`/products/${product.slug}`}
                    className="bg-white rounded-lg shadow hover:shadow-lg transition overflow-hidden group"
                  >
                    {/* Product Image */}
                    {product.images && product.images.length > 0 ? (
                      <div className="h-48 bg-gray-100 overflow-hidden">
                        <img
                          src={product.images[0]}
                          alt={product.name}
                          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                          onError={(e) => {
                            e.target.onerror = null
                            e.target.src = 'https://placehold.co/400x300/dbeafe/60a5fa?text=No+Image'
                          }}
                        />
                      </div>
                    ) : (
                      <div className="h-48 bg-gradient-to-br from-blue-100 to-blue-200 flex items-center justify-center">
                        <div className="text-6xl text-blue-400">💧</div>
                      </div>
                    )}

                    <div className="p-6">
                      {/* Category Badge */}
                      {product.category_name && (
                        <span className="inline-block px-2 py-1 text-xs font-semibold text-blue-600 bg-blue-50 rounded mb-2">
                          {product.category_name}
                        </span>
                      )}

                      {/* Product Name */}
                      <h3 className="text-lg font-semibold text-gray-900 mb-2 group-hover:text-blue-600 transition">
                        {product.name}
                      </h3>

                      {/* Short Description */}
                      {product.short_description && (
                        <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                          {product.short_description}
                        </p>
                      )}

                      {/* Pricing */}
                      <div className="flex items-baseline gap-2 mb-4">
                        {product.sale_price ? (
                          <>
                            <span className="text-2xl font-bold text-green-600">
                              ₹{parseFloat(product.sale_price).toLocaleString('en-IN')}
                            </span>
                            <span className="text-lg text-gray-400 line-through">
                              ₹{parseFloat(product.base_price).toLocaleString('en-IN')}
                            </span>
                          </>
                        ) : (
                          <span className="text-2xl font-bold text-gray-900">
                            ₹{parseFloat(product.base_price).toLocaleString('en-IN')}
                          </span>
                        )}
                      </div>

                      {/* Features Preview */}
                      {product.specifications && Object.keys(product.specifications).length > 0 && (
                        <div className="text-sm text-gray-600 mb-4">
                          {product.specifications.power && (
                            <div className="flex items-center gap-2">
                              <span className="font-medium">Power:</span>
                              <span>{product.specifications.power}</span>
                            </div>
                          )}
                        </div>
                      )}

                      {/* Stock Status */}
                      <div className="flex items-center justify-between">
                        {product.stock_quantity > 0 ? (
                          <span className="text-sm text-green-600 font-medium">
                            ✓ In Stock
                          </span>
                        ) : (
                          <span className="text-sm text-red-600 font-medium">
                            Out of Stock
                          </span>
                        )}

                        {product.is_featured && (
                          <span className="text-yellow-500">⭐</span>
                        )}
                      </div>

                      {/* View Details Link */}
                      <div className="mt-4 pt-4 border-t">
                        <span className="text-blue-600 text-sm font-medium group-hover:underline">
                          View Details →
                        </span>
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            ) : (
              <div className="text-center py-12 bg-white rounded-lg shadow">
                <div className="text-6xl mb-4">🔍</div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">No products found</h3>
                <p className="text-gray-600 mb-4">
                  Try adjusting your search or filter criteria
                </p>
                {(selectedCategory || searchQuery) && (
                  <button
                    onClick={clearFilters}
                    className="px-4 py-2 text-sm text-white bg-blue-600 rounded-md hover:bg-blue-700"
                  >
                    View All Products
                  </button>
                )}
              </div>
            )}
          </main>
        </div>
      </div>
    </div>
  )
}
