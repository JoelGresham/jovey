/**
 * Products Management Page (Staff Only)
 * Manage product catalog
 */
import { useState, useEffect } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import StaffLayout from '../../components/staff/StaffLayout'

const API_URL = import.meta.env.VITE_API_URL

export default function Products() {
  const { user, profile, getAuthHeaders } = useAuth()
  const [products, setProducts] = useState([])
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [editingProduct, setEditingProduct] = useState(null)
  const [selectedFile, setSelectedFile] = useState(null)
  const [imagePreview, setImagePreview] = useState(null)
  const [uploadingImage, setUploadingImage] = useState(false)

  const [formData, setFormData] = useState({
    name: '',
    slug: '',
    sku: '',
    description: '',
    short_description: '',
    category_id: '',
    base_price: '',
    sale_price: '',
    stock_quantity: 0,
    is_in_stock: true,
    is_featured: false,
    is_active: true,
    manufacturer: '',
    model_number: '',
    warranty_months: 12,
  })

  // SKU Builder fields
  const [skuBuilder, setSkuBuilder] = useState({
    power: '',
    application: '',
    material: '',
    flow_rate: '',
    pressure: '',
  })

  // Fetch products and categories
  const fetchData = async () => {
    try {
      setLoading(true)
      const [productsRes, categoriesRes] = await Promise.all([
        fetch(`${API_URL}/api/v1/products/?include_inactive=true`),
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
      setError('Failed to load data')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  // Auto-generate slug from name
  const handleNameChange = (e) => {
    const name = e.target.value
    const slug = name
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-+|-+$/g, '')

    setFormData({
      ...formData,
      name,
      slug,
    })
  }

  // Get category code from category name
  const getCategoryCode = (categoryId) => {
    const category = categories.find((c) => c.id === categoryId)
    if (!category) return ''

    // Generate 4-letter code from category name
    const name = category.name.toUpperCase()
    if (name.includes('SUBMERSIBLE')) return 'SUBM'
    if (name.includes('CENTRIFUGAL')) return 'CENT'
    if (name.includes('MONOBLOCK')) return 'MONO'
    if (name.includes('OPENWELL')) return 'OPWL'
    if (name.includes('BOREWELL')) return 'BORE'
    if (name.includes('DOMESTIC')) return 'DOME'
    if (name.includes('AGRICULTURE') || name.includes('AGRICULTURAL')) return 'AGRI'
    if (name.includes('INDUSTRIAL')) return 'INDU'

    // Default: take first 4 characters
    return name.replace(/[^A-Z]/g, '').substring(0, 4)
  }

  // Generate SKU from builder fields
  const generateSKU = () => {
    const categoryCode = getCategoryCode(formData.category_id)
    const power = skuBuilder.power.toUpperCase().replace(/\s/g, '')
    const application = skuBuilder.application.toUpperCase().replace(/\s/g, '')
    const material = skuBuilder.material.toUpperCase().replace(/\s/g, '')
    const flowRate = skuBuilder.flow_rate.toUpperCase().replace(/\s/g, '')
    const pressure = skuBuilder.pressure.toUpperCase().replace(/\s/g, '')

    const parts = [categoryCode, power, application, material, flowRate, pressure].filter(Boolean)
    const sku = parts.join('-')

    setFormData({
      ...formData,
      sku,
    })
  }

  // Handle SKU builder field changes
  const handleSkuBuilderChange = (e) => {
    const { name, value } = e.target
    setSkuBuilder({
      ...skuBuilder,
      [name]: value,
    })
  }

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value,
    })
  }

  const handleFileChange = (e) => {
    const file = e.target.files[0]
    if (file) {
      // Validate file type
      const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
      if (!validTypes.includes(file.type)) {
        setError('Please select a valid image file (JPEG, PNG, or WebP)')
        return
      }

      // Validate file size (5MB max)
      if (file.size > 5 * 1024 * 1024) {
        setError('Image file size must be less than 5MB')
        return
      }

      setSelectedFile(file)
      setError('')

      // Create preview
      const reader = new FileReader()
      reader.onloadend = () => {
        setImagePreview(reader.result)
      }
      reader.readAsDataURL(file)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    try {
      let imageUrl = imagePreview // Keep existing image if editing

      // Upload new image if file is selected
      if (selectedFile) {
        setUploadingImage(true)
        const formDataUpload = new FormData()
        formDataUpload.append('file', selectedFile)

        const uploadResponse = await fetch(`${API_URL}/api/v1/products/upload-image`, {
          method: 'POST',
          headers: getAuthHeaders(),
          body: formDataUpload,
        })

        if (!uploadResponse.ok) {
          const errorData = await uploadResponse.json()
          throw new Error(errorData.detail || 'Failed to upload image')
        }

        const uploadData = await uploadResponse.json()
        imageUrl = uploadData.image_url
        setUploadingImage(false)
      }

      const url = editingProduct
        ? `${API_URL}/api/v1/products/${editingProduct.id}`
        : `${API_URL}/api/v1/products/`

      const method = editingProduct ? 'PUT' : 'POST'

      const payload = {
        ...formData,
        category_id: formData.category_id || null,
        base_price: parseFloat(formData.base_price),
        sale_price: formData.sale_price ? parseFloat(formData.sale_price) : null,
        stock_quantity: parseInt(formData.stock_quantity) || 0,
        warranty_months: parseInt(formData.warranty_months) || 12,
        images: imageUrl ? [imageUrl] : [],
      }

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to save product')
      }

      await fetchData()
      resetForm()
    } catch (err) {
      setError(err.message)
      setUploadingImage(false)
    }
  }

  const resetForm = () => {
    setFormData({
      name: '',
      slug: '',
      sku: '',
      description: '',
      short_description: '',
      category_id: '',
      base_price: '',
      sale_price: '',
      stock_quantity: 0,
      is_in_stock: true,
      is_featured: false,
      is_active: true,
      manufacturer: '',
      model_number: '',
      warranty_months: 12,
    })
    setSkuBuilder({
      power: '',
      application: '',
      material: '',
      flow_rate: '',
      pressure: '',
    })
    setSelectedFile(null)
    setImagePreview(null)
    setShowModal(false)
    setEditingProduct(null)
  }

  const handleEdit = (product) => {
    setEditingProduct(product)
    // Extract first image URL from images array if it exists
    const imageUrl = product.images && product.images.length > 0 ? product.images[0] : ''
    setFormData({
      name: product.name,
      slug: product.slug,
      sku: product.sku || '',
      description: product.description || '',
      short_description: product.short_description || '',
      category_id: product.category_id || '',
      base_price: product.base_price,
      sale_price: product.sale_price || '',
      stock_quantity: product.stock_quantity,
      is_in_stock: product.is_in_stock,
      is_featured: product.is_featured,
      is_active: product.is_active,
      manufacturer: product.manufacturer || '',
      model_number: product.model_number || '',
      warranty_months: product.warranty_months,
    })
    // Set image preview if product has an image
    if (imageUrl) {
      setImagePreview(imageUrl)
    }
    setShowModal(true)
  }

  const handleDelete = async (productId) => {
    if (!confirm('Are you sure you want to delete this product?')) return

    try {
      const response = await fetch(`${API_URL}/api/v1/products/${productId}`, {
        method: 'DELETE',
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to delete product')
      }

      await fetchData()
    } catch (err) {
      setError(err.message)
    }
  }

  const openAddModal = () => {
    resetForm()
    setShowModal(true)
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center">Loading products...</div>
        </div>
      </div>
    )
  }

  return (
    <StaffLayout>
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Product Management</h1>
          <p className="text-gray-600 mt-2">Manage your product catalog</p>
        </div>
        <button
          onClick={openAddModal}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          Add Product
        </button>
      </div>

        {error && (
          <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        {/* Products Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {products.map((product) => (
            <div key={product.id} className="bg-white rounded-lg shadow overflow-hidden">
              {/* Product Image */}
              {product.images && product.images.length > 0 ? (
                <div className="w-full h-48 bg-gray-100">
                  <img
                    src={product.images[0]}
                    alt={product.name}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      e.target.onerror = null
                      e.target.src = 'https://placehold.co/400x300/e5e7eb/6b7280?text=No+Image'
                    }}
                  />
                </div>
              ) : (
                <div className="w-full h-48 bg-gray-100 flex items-center justify-center">
                  <div className="text-center">
                    <div className="text-4xl text-gray-400 mb-2">📦</div>
                    <p className="text-sm text-gray-500">No image</p>
                  </div>
                </div>
              )}

              <div className="p-6">
                <div className="flex justify-between items-start mb-3">
                  <h3 className="text-lg font-semibold text-gray-900">{product.name}</h3>
                  <div className="flex gap-2">
                    {product.is_featured && (
                      <span className="text-yellow-500 text-sm">⭐</span>
                    )}
                    <span
                      className={`px-2 py-1 text-xs font-semibold rounded-full ${
                        product.is_active
                          ? 'bg-green-100 text-green-800'
                          : 'bg-red-100 text-red-800'
                      }`}
                    >
                      {product.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                </div>

                {product.short_description && (
                  <p className="text-sm text-gray-600 mb-3">{product.short_description}</p>
                )}

                <div className="space-y-2 text-sm">
                  {product.sku && (
                    <div className="flex justify-between">
                      <span className="text-gray-500">SKU:</span>
                      <span className="font-medium">{product.sku}</span>
                    </div>
                  )}
                  <div className="flex justify-between">
                    <span className="text-gray-500">Price:</span>
                    <span className="font-bold text-blue-600">₹{product.base_price}</span>
                  </div>
                  {product.sale_price && (
                    <div className="flex justify-between">
                      <span className="text-gray-500">Sale Price:</span>
                      <span className="font-bold text-green-600">₹{product.sale_price}</span>
                    </div>
                  )}
                  <div className="flex justify-between">
                    <span className="text-gray-500">Stock:</span>
                    <span className={product.stock_quantity > 0 ? 'text-green-600' : 'text-red-600'}>
                      {product.stock_quantity} units
                    </span>
                  </div>
                  {product.category_name && (
                    <div className="flex justify-between">
                      <span className="text-gray-500">Category:</span>
                      <span>{product.category_name}</span>
                    </div>
                  )}
                </div>

                <div className="mt-4 pt-4 border-t flex justify-end space-x-2">
                  <button
                    onClick={() => handleEdit(product)}
                    className="px-3 py-1 text-sm text-blue-600 hover:text-blue-800 font-medium"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(product.id)}
                    className="px-3 py-1 text-sm text-red-600 hover:text-red-800 font-medium"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {products.length === 0 && (
          <div className="text-center py-12 bg-white rounded-lg shadow">
            <p className="text-gray-500">No products found. Add your first product!</p>
          </div>
        )}

        {/* Add/Edit Modal */}
        {showModal && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50 overflow-y-auto">
            <div className="bg-white rounded-lg p-8 max-w-3xl w-full mx-4 my-8">
              <h2 className="text-2xl font-bold mb-6">
                {editingProduct ? 'Edit Product' : 'Add New Product'}
              </h2>

              <form onSubmit={handleSubmit} className="space-y-4 max-h-[70vh] overflow-y-auto pr-2">
                {/* Name */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Product Name *
                  </label>
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleNameChange}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                {/* Slug */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Slug *
                  </label>
                  <input
                    type="text"
                    name="slug"
                    value={formData.slug}
                    onChange={handleChange}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  {/* SKU Builder Section */}
                  <div className="col-span-2 bg-blue-50 p-4 rounded-lg border border-blue-200">
                    <h3 className="text-lg font-semibold text-gray-900 mb-3">SKU Builder</h3>
                    <p className="text-sm text-gray-600 mb-4">
                      Build your product SKU using standardized components. Format: CATEGORY-POWER-APPLICATION-MATERIAL-FLOW_RATE-PRESSURE
                    </p>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-4">
                      {/* Power */}
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Power/HP Rating *
                        </label>
                        <input
                          type="text"
                          name="power"
                          value={skuBuilder.power}
                          onChange={handleSkuBuilderChange}
                          placeholder="e.g., 05HP, 1HP, 2HP"
                          required
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        />
                      </div>

                      {/* Application */}
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Application Type *
                        </label>
                        <select
                          name="application"
                          value={skuBuilder.application}
                          onChange={handleSkuBuilderChange}
                          required
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        >
                          <option value="">Select...</option>
                          <option value="DOM">Domestic (DOM)</option>
                          <option value="AGR">Agricultural (AGR)</option>
                          <option value="IND">Industrial (IND)</option>
                          <option value="COM">Commercial (COM)</option>
                        </select>
                      </div>

                      {/* Material */}
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Material/Build *
                        </label>
                        <select
                          name="material"
                          value={skuBuilder.material}
                          onChange={handleSkuBuilderChange}
                          required
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        >
                          <option value="">Select...</option>
                          <option value="SS">Stainless Steel (SS)</option>
                          <option value="CI">Cast Iron (CI)</option>
                          <option value="MS">Mild Steel (MS)</option>
                          <option value="PL">Plastic (PL)</option>
                          <option value="BR">Brass (BR)</option>
                        </select>
                      </div>

                      {/* Flow Rate */}
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Flow Rate *
                        </label>
                        <input
                          type="text"
                          name="flow_rate"
                          value={skuBuilder.flow_rate}
                          onChange={handleSkuBuilderChange}
                          placeholder="e.g., 50LPM, 100LPM"
                          required
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        />
                      </div>

                      {/* Pressure */}
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Pressure/Head *
                        </label>
                        <input
                          type="text"
                          name="pressure"
                          value={skuBuilder.pressure}
                          onChange={handleSkuBuilderChange}
                          placeholder="e.g., 20M, 30M, 50M"
                          required
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        />
                      </div>

                      {/* Generate Button */}
                      <div className="flex items-end">
                        <button
                          type="button"
                          onClick={generateSKU}
                          className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 font-medium"
                        >
                          Generate SKU
                        </button>
                      </div>
                    </div>

                    {/* Generated SKU Display */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Generated SKU *
                      </label>
                      <input
                        type="text"
                        name="sku"
                        value={formData.sku}
                        readOnly
                        required
                        className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-100 font-mono text-lg font-bold"
                        placeholder="SKU will be generated..."
                      />
                      <p className="text-xs text-gray-500 mt-1">
                        This SKU is automatically generated from the components above
                      </p>
                    </div>
                  </div>

                  {/* Category */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Category *
                    </label>
                    <select
                      name="category_id"
                      value={formData.category_id}
                      onChange={handleChange}
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="">Select a category...</option>
                      {categories.map((cat) => (
                        <option key={cat.id} value={cat.id}>
                          {cat.name}
                        </option>
                      ))}
                    </select>
                    <p className="text-xs text-gray-500 mt-1">
                      Required for SKU generation
                    </p>
                  </div>
                </div>

                {/* Product Image Upload */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Product Image
                  </label>

                  {imagePreview && (
                    <div className="mb-3">
                      <img
                        src={imagePreview}
                        alt="Preview"
                        className="w-32 h-32 object-cover rounded border"
                      />
                    </div>
                  )}

                  <input
                    type="file"
                    accept="image/jpeg,image/jpg,image/png,image/webp"
                    onChange={handleFileChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Upload an image file (JPEG, PNG, or WebP). Max size: 5MB
                  </p>
                </div>

                {/* Short Description */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Short Description
                  </label>
                  <input
                    type="text"
                    name="short_description"
                    value={formData.short_description}
                    onChange={handleChange}
                    maxLength="500"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                {/* Description */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Full Description
                  </label>
                  <textarea
                    name="description"
                    value={formData.description}
                    onChange={handleChange}
                    rows="4"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                <div className="grid grid-cols-3 gap-4">
                  {/* Base Price */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Base Price * (₹)
                    </label>
                    <input
                      type="number"
                      name="base_price"
                      value={formData.base_price}
                      onChange={handleChange}
                      required
                      min="0"
                      step="0.01"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>

                  {/* Sale Price */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Sale Price (₹)
                    </label>
                    <input
                      type="number"
                      name="sale_price"
                      value={formData.sale_price}
                      onChange={handleChange}
                      min="0"
                      step="0.01"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>

                  {/* Stock */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Stock Quantity
                    </label>
                    <input
                      type="number"
                      name="stock_quantity"
                      value={formData.stock_quantity}
                      onChange={handleChange}
                      min="0"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  {/* Manufacturer */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Manufacturer
                    </label>
                    <input
                      type="text"
                      name="manufacturer"
                      value={formData.manufacturer}
                      onChange={handleChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>

                  {/* Model Number */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Model Number
                    </label>
                    <input
                      type="text"
                      name="model_number"
                      value={formData.model_number}
                      onChange={handleChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                </div>

                {/* Warranty */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Warranty (months)
                  </label>
                  <input
                    type="number"
                    name="warranty_months"
                    value={formData.warranty_months}
                    onChange={handleChange}
                    min="0"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                {/* Checkboxes */}
                <div className="flex gap-6">
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      name="is_in_stock"
                      checked={formData.is_in_stock}
                      onChange={handleChange}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label className="ml-2 block text-sm text-gray-900">
                      In Stock
                    </label>
                  </div>

                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      name="is_featured"
                      checked={formData.is_featured}
                      onChange={handleChange}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label className="ml-2 block text-sm text-gray-900">
                      Featured Product
                    </label>
                  </div>

                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      name="is_active"
                      checked={formData.is_active}
                      onChange={handleChange}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label className="ml-2 block text-sm text-gray-900">
                      Active
                    </label>
                  </div>
                </div>

                {/* Buttons */}
                <div className="flex justify-end space-x-4 pt-4 sticky bottom-0 bg-white">
                  <button
                    type="button"
                    onClick={resetForm}
                    className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={uploadingImage}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
                  >
                    {uploadingImage ? 'Uploading...' : editingProduct ? 'Update' : 'Create'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
    </StaffLayout>
  )
}
