#!/bin/bash
# Export notebooks as HTML for easy sharing

echo "Converting notebooks to HTML..."

# Create export directory
mkdir -p exports_for_teammates

# Convert each notebook to HTML
for notebook in notebooks/*.ipynb; do
    filename=$(basename "$notebook" .ipynb)
    echo "Converting $filename..."
    jupyter nbconvert --to html "$notebook" --output-dir exports_for_teammates/
done

# Copy outputs
echo "Copying output files..."
cp -r outputs exports_for_teammates/

echo ""
echo "✓ Done! Share the 'exports_for_teammates' folder"
echo ""
echo "Teammates can:"
echo "  1. Open HTML files in any browser (double-click)"
echo "  2. See all findings, charts, and tables"
echo "  3. No Python/Jupyter needed!"

