#!/bin/bash
# Script to prepare UMD audit project for Google Colab sharing

echo "========================================="
echo "UMD Audit - Prepare for Google Colab"
echo "========================================="
echo ""

# Create a clean copy for sharing
echo "Creating clean copy for Colab..."

# Create temporary directory
mkdir -p temp_colab_export

# Copy necessary files
echo "Copying notebooks..."
cp -r notebooks temp_colab_export/

echo "Copying data files..."
cp -r data temp_colab_export/

echo "Copying outputs..."
cp -r outputs temp_colab_export/

echo "Copying documentation..."
cp PROJECT_CONTEXT.md temp_colab_export/ 2>/dev/null || echo "PROJECT_CONTEXT.md not found (optional)"
cp umdcase.md temp_colab_export/ 2>/dev/null || echo "umdcase.md not found (optional)"
cp GOOGLE_COLAB_SETUP.md temp_colab_export/README.md

# Create ZIP file
echo ""
echo "Creating ZIP file..."
cd temp_colab_export
zip -r ../UMD_Audit_for_Colab.zip . -x "*.pyc" -x "*__pycache__*" -x "*.git*" -x ".DS_Store"
cd ..

# Cleanup
echo "Cleaning up..."
rm -rf temp_colab_export

echo ""
echo "========================================="
echo "✓ SUCCESS!"
echo "========================================="
echo ""
echo "Created: UMD_Audit_for_Colab.zip"
echo ""
echo "Next steps:"
echo "1. Upload this ZIP to Google Drive"
echo "2. Share the Drive folder with teammates"
echo "3. Teammates can extract and run in Colab"
echo ""
echo "OR"
echo ""
echo "1. Create folder 'UMD_Audit_Project' in Google Drive"
echo "2. Upload notebooks/ and data/ folders directly"
echo "3. Share with teammates"
echo ""
echo "See GOOGLE_COLAB_SETUP.md for detailed instructions"
echo "========================================="

