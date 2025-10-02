# How to Share UMD Audit Analysis on Google Colab

## Method 1: Google Drive Upload (RECOMMENDED)

### Step 1: Upload to Google Drive

1. **Create a folder structure in Google Drive:**
   ```
   My Drive/
     └── UMD_Audit_Project/
         ├── notebooks/
         ├── data/
         └── outputs/
   ```

2. **Upload folders:**
   - Upload entire `notebooks/` folder to Drive
   - Upload entire `data/` folder to Drive
   - Upload `outputs/` folder (optional - will be regenerated)

### Step 2: Access in Google Colab

At the top of each notebook, teammates should add this code cell:

```python
# Mount Google Drive
from google.colab import drive
drive.mount('/content/drive')

# Navigate to project directory
import os
os.chdir('/content/drive/My Drive/UMD_Audit_Project')

# Verify files are accessible
!ls -la data/
!ls -la notebooks/
```

### Step 3: Install Required Packages

Add this cell at the beginning of each notebook in Colab:

```python
# Install required packages
!pip install pandas numpy openpyxl matplotlib seaborn plotly -q

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

print("✓ Libraries loaded successfully")
```

### Step 4: Update File Paths

The notebooks currently use `../data/` paths. In Colab with Drive, update to:

```python
# OLD (local):
# data_dir = Path('../data')

# NEW (Colab with Drive):
data_dir = Path('/content/drive/My Drive/UMD_Audit_Project/data')
```

---

## Method 2: Direct Upload to Colab Session

### For Quick Testing (files lost when session ends)

```python
from google.colab import files
import zipfile

# 1. Upload ZIP file
uploaded = files.upload()  # Click to upload your ZIP

# 2. Extract
!unzip ACG6697.zip
!ls -la

# 3. Navigate
import os
os.chdir('ACG6697')
```

### How to Create the ZIP:

On your Mac terminal:
```bash
cd /Users/sethgoldstein/ACG6697
zip -r ACG6697_for_colab.zip notebooks/ data/ outputs/ *.md -x "*.pyc" -x "*__pycache__*" -x "*.git*"
```

---

## Method 3: GitHub Repository (Best for Version Control)

### Setup:

```bash
cd /Users/sethgoldstein/ACG6697
git init
git add notebooks/ data/ outputs/ PROJECT_CONTEXT.md umdcase.md README.md
git commit -m "UMD audit analysis"
git push origin main
```

### In Colab:

```python
# Clone repository
!git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
%cd YOUR_REPO

# Install packages
!pip install -r requirements.txt
```

---

## Quick Start Template for Teammates

**Add this as the FIRST cell in each notebook for Colab:**

```python
# ========================================
# GOOGLE COLAB SETUP
# Run this cell first!
# ========================================

# Check if running in Colab
try:
    import google.colab
    IN_COLAB = True
    print("Running in Google Colab")
except:
    IN_COLAB = False
    print("Running locally")

if IN_COLAB:
    # Mount Google Drive
    from google.colab import drive
    drive.mount('/content/drive')
    
    # Install packages
    !pip install openpyxl -q
    
    # Set working directory
    import os
    os.chdir('/content/drive/My Drive/UMD_Audit_Project')
    
    # Update paths for Colab
    import sys
    from pathlib import Path
    data_dir = Path('data')
    output_tables = Path('outputs/tables')
    output_figures = Path('outputs/figures')
    
    # Create output directories
    output_tables.mkdir(parents=True, exist_ok=True)
    output_figures.mkdir(parents=True, exist_ok=True)
    
    print("✓ Colab setup complete")
    print(f"✓ Working directory: {os.getcwd()}")
    print(f"✓ Data files: {list(data_dir.glob('*.xlsx'))}")
else:
    # Local setup
    from pathlib import Path
    data_dir = Path('../data')
    output_tables = Path('../outputs/tables')
    output_figures = Path('../outputs/figures')
    
    print("✓ Local setup complete")

# Standard imports
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Display settings
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.float_format', '{:.2f}'.format)

print("✓ All libraries loaded")
```

---

## Sharing Options Summary

| Method | Pros | Cons | Best For |
|--------|------|------|----------|
| **Google Drive** | Easy sharing, persistent, teammates can edit | Manual upload | Team collaboration |
| **Direct Upload** | Quick, no setup | Lost on disconnect, repetitive | Quick demos |
| **GitHub** | Version control, professional | Setup required, data files large | Long-term projects |

---

## Recommended Workflow for Your Team:

1. **You (Analyst):** Upload `notebooks/` and `data/` to a shared Google Drive folder
2. **Share the folder** with your teammates (view or edit access)
3. **Teammates:** 
   - Open Google Colab
   - Mount Drive
   - Navigate to the shared folder
   - Open `.ipynb` files directly from Drive
4. **To run notebooks:**
   - Add the "Colab Setup" cell at the top of each notebook
   - Run all cells
   - Outputs will save to Drive (persistent)

---

## Testing Checklist

Before sharing with teammates, verify:

- [ ] All data files are in `data/` folder
- [ ] All notebooks run top-to-bottom without errors
- [ ] Output directories exist (`outputs/tables/`, `outputs/figures/`)
- [ ] Paths are updated for Colab (if using Drive method)
- [ ] Required packages listed (pandas, numpy, openpyxl, matplotlib, seaborn)

---

## Troubleshooting

**"No such file or directory"**
- Check that Drive is mounted: `!ls "/content/drive/My Drive"`
- Verify folder name matches exactly (case-sensitive)

**"ModuleNotFoundError"**
- Run: `!pip install [package_name]`
- Add to setup cell

**"Permission denied"**
- Ensure Drive folder is shared with teammates
- Check folder permissions in Google Drive

---

## Questions?

See `PROJECT_CONTEXT.md` for full project guidelines.

