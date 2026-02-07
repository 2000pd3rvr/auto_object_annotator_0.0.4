# Image Annotation Tool

A professional web-based annotation application for multi-view image datasets with advanced features for efficient labeling and quality assurance.

## 🎯 Overview

This tool is designed for annotating image datasets that contain multiple views of the same objects. Each image set consists of three related images with the same file ID prefix:
- **Surface Reflection Internal Full** (`-sr_int_full.png`)
- **Transmission Line** (`-tr_line.png`) 
- **Transmission Internal Full** (`-tr_int_full.png`)

## 🚀 Key Features

### 📁 **Dataset Management**
- **Multi-folder support**: Automatically processes all folders containing valid image sets
- **File ID grouping**: Images grouped by prefix before '-' character (e.g., `teddy__1-sr_int_full.png`, `teddy__1-tr_line.png`, `teddy__1-tr_int_full.png`)
- **Smart validation**: Only includes folders with complete image sets (all three image types)
- **Continuous workflow**: Seamless navigation through entire dataset

### 🖼️ **Image Display**
- **Optimized layout**: Two images side-by-side (50% width each) at top, one full-width image below
- **Smart scaling**: 
  - `sr_int_full.png` images scaled to 416px width
  - `tr_int_full.png` images use original size with 150px cropping from top/bottom
- **Reduced whitespace**: Optimized spacing for better scale number visibility
- **Professional presentation**: Clean, focused image display

### 🏷️ **Annotation System**
- **Bounding box annotations**: Click and drag to create rectangular annotations
- **Class-based labeling**: Assign objects to predefined classes
- **Class-based ID system**: Sequential IDs per class (1,2,3... for each class separately)
- **Center-point format**: Annotations saved as x,y center coordinates plus width/height
- **Multi-canvas support**: Annotate any of the three images in each set

### 🎨 **User Interface**
- **Orange color scheme**: Professional orange theme throughout interface
- **Thinner annotation lines**: 2px line width for clean, precise annotations
- **Compact labels**: 60% smaller font size for unobtrusive labeling
- **Transparent buttons**: Outline-only buttons with 50% smaller size
- **Elegant sidebar**: Garamond font, regular weight, gray color
- **Full-height layout**: Sidebar utilizes 100% height efficiently

### 🔍 **Zoom & Navigation**
- **Individual zoom controls**: Separate zoom buttons for each image canvas
- **Smart zoom behavior**: 
  - Starts at 100% fitting display canvas
  - Scroll enabled only when zooming over 100%
  - Allows magnification beyond 100% for detailed work
- **Gray transparent icons**: Subtle, non-intrusive zoom button appearance
- **Per-canvas positioning**: Zoom buttons positioned on left side of each canvas

### 💾 **Data Management**
- **Auto-save functionality**: Automatically saves annotations on navigation
- **CSV export format**: Standard CSV with image path, class, coordinates, and dimensions
- **Update-safe saving**: Updates existing CSV files or creates new ones
- **Class-based ID assignment**: Maintains separate ID sequences for each class

### 🎮 **Auto-Play Feature**
- **Complete dataset coverage**: Cycles through ALL images in entire dataset
- **Infinite loop playback**: Automatically restarts from beginning when complete
- **Customizable timing**: Set any interval from 1 second to minutes
- **Smart navigation**: 
  - Advances through all sets in current folder
  - Automatically moves to next folder when current is complete
  - Loops back to first folder for continuous operation
- **User control**: Pause/resume at any time, manual override available

### 🔄 **Reset & Management**
- **Flexible reset options**: Clear annotations by folder/class or globally
- **Clean slate capability**: Start fresh when needed
- **Non-destructive workflow**: Reset doesn't affect saved CSV data

## 🛠️ **Installation & Setup**

### Prerequisites
- Python 3.7+
- Flask
- Modern web browser

### Installation
```bash
# Clone or download the project
cd your-project-directory

# Install dependencies
pip install flask

# Ensure your image dataset is organized in folders with the required image types
```

### Dataset Structure
```
images/
├── folder1/
│   ├── object1-sr_int_full.png
│   ├── object1-tr_line.png
│   ├── object1-tr_int_full.png
│   ├── object2-sr_int_full.png
│   ├── object2-tr_line.png
│   └── object2-tr_int_full.png
├── folder2/
│   └── ... (similar structure)
└── ...
```

## 🚀 **Usage**

### Starting the Application
```bash
python "anno4 copy.py"
```
Access the application at: `http://127.0.0.1:6700/tagger`

### Basic Workflow
1. **Navigate**: Use "Next Set" and "Next Folder" buttons to browse images
2. **Annotate**: Click and drag on images to create bounding boxes
3. **Classify**: Click class buttons to assign labels to annotations
4. **Auto-save**: Annotations automatically save when navigating
5. **Review**: Use auto-play feature for quality assurance

### Auto-Play Usage
1. Click the ▶️ **Play** button (green outline)
2. Enter desired interval (e.g., "3" for 3 seconds between images)
3. Watch the complete dataset cycle through all folders and sets
4. Use ⏸️ **Pause** to stop, or click any navigation button to take manual control

### Zoom Controls
- Click **🔍+** to zoom in on specific image
- Click **🔍-** to zoom out
- Zoom starts at 100% (fit-to-screen)
- Scroll bars appear only when zoomed over 100%

### Reset Options
- **By Folder**: Clear annotations for current folder only
- **By Class**: Clear annotations for specific class across all images
- **Global**: Clear all annotations (use with caution)

## 📊 **Output Format**

Annotations are saved to `out.csv` with the following format:
```csv
image_path,class_name,class_id,center_x,center_y,width,height
toy/object1-sr_int_full.png,teddy,1,150.5,200.3,45.2,67.8
```

## 🎯 **Advanced Features**

### File ID Grouping
- Images automatically grouped by file ID prefix (everything before first '-')
- Ensures related images stay together in annotation sets
- Maintains data integrity across different image types

### Class-Based ID System
- Each class maintains its own ID sequence
- Example: teddy class gets IDs 1,2,3... while cup class gets separate 1,2,3...
- Prevents ID conflicts between different object types

### Continuous Loop Workflow
- Application never "ends" - automatically loops back to beginning
- Perfect for ongoing annotation projects
- Supports multiple annotation sessions

## 🔧 **Configuration**

The application automatically detects and configures:
- Image folders and valid image sets
- Required image suffixes (`sr_int_full.png`, `-tr_line.png`, `-tr_int_full.png`)
- CSV file location and format
- Navigation state and progress

## 📝 **Notes**

- Only folders containing all three required image types are included
- Images must follow the naming convention: `prefix-suffix.png`
- Auto-save occurs on every navigation action
- Zoom and annotation state is maintained per canvas
- Application supports unlimited classes and annotations

## 🎨 **Design Philosophy**

This tool prioritizes:
- **Efficiency**: Streamlined workflow for rapid annotation
- **Accuracy**: Clear visual presentation and precise controls
- **Consistency**: Standardized format and behavior
- **Usability**: Intuitive interface with professional appearance
- **Quality**: Built-in review and validation features

---

**Built for professional image annotation workflows with focus on multi-view datasets and quality assurance.**
