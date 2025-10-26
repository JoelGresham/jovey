# Supabase Storage Setup for Product Images

## Overview
This document explains how to set up Supabase Storage for product image uploads.

## Steps to Configure Storage Bucket

### 1. Access Supabase Dashboard
1. Go to https://supabase.com/dashboard
2. Select your Jovey project
3. Navigate to **Storage** in the left sidebar

### 2. Create Storage Bucket
1. Click **New bucket**
2. Enter the following details:
   - **Name**: `product-images`
   - **Public bucket**: ✅ **Check this** (images need to be publicly accessible)
   - **File size limit**: 5MB (optional, for optimization)
   - **Allowed MIME types**: Leave default or specify: `image/jpeg`, `image/png`, `image/webp`

3. Click **Create bucket**

### 3. Configure Bucket Policies (Important!)
After creating the bucket, you need to set up policies for secure access:

1. Click on the `product-images` bucket
2. Go to **Policies** tab
3. Create the following policies:

#### Policy 1: Allow Staff to Upload
```sql
-- Policy name: Allow authenticated staff to upload
-- Allowed operation: INSERT

CREATE POLICY "Allow authenticated staff to upload"
ON storage.objects
FOR INSERT
TO authenticated
WITH CHECK (
  bucket_id = 'product-images'
  AND (storage.foldername(name))[1] = 'products'
);
```

#### Policy 2: Allow Public Read Access
```sql
-- Policy name: Allow public to read product images
-- Allowed operation: SELECT

CREATE POLICY "Allow public to read product images"
ON storage.objects
FOR SELECT
TO public
USING (bucket_id = 'product-images');
```

### 4. Verify Setup
Test the configuration:
1. Try uploading an image through the staff portal
2. Verify the image appears in **Storage** > **product-images** > **products** folder
3. Test that the public URL is accessible

## Image Upload Flow

1. **Staff member** selects an image file in the product form
2. **Frontend** validates file type and size (max 5MB)
3. **Frontend** sends file to `/api/v1/products/upload-image` endpoint
4. **Backend** validates and uploads to Supabase Storage bucket `product-images/products/{uuid}.{ext}`
5. **Backend** returns the public URL
6. **Frontend** includes the URL in the product's `images` array
7. **Product** is saved with the image URL

## Troubleshooting

### Error: "Failed to upload image"
- Check that the `product-images` bucket exists
- Verify bucket is marked as **public**
- Ensure policies are created correctly
- Check that the Supabase service role key is set in backend `.env`

### Error: "Image not displaying"
- Verify the bucket is **public**
- Check the SELECT policy allows public access
- Confirm the image URL format is correct

### Error: "Permission denied"
- Ensure the user is authenticated as staff
- Verify the INSERT policy allows authenticated users
- Check that `get_current_staff_user` dependency is working

## Security Notes

- Images are stored with UUID filenames to prevent naming conflicts
- File type and size validation happens on both frontend and backend
- Only staff members can upload images (enforced by authentication)
- Images are publicly readable (required for e-commerce functionality)
- The `products/` folder structure helps organize images

## File Limits

- **Max file size**: 5MB
- **Allowed types**: JPEG, JPG, PNG, WebP
- **Storage path**: `product-images/products/{uuid}.{ext}`

## Next Steps

After setting up storage:
1. Test image upload through staff portal at `/staff/products`
2. Verify images display on public product pages
3. Check that image URLs are saved correctly in database
4. Monitor storage usage in Supabase dashboard
