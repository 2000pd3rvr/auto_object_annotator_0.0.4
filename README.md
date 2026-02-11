---
title: Auto Object Annotator 0.0.4
emoji: 🚀
colorFrom: yellow
colorTo: green
sdk: docker
sdk_version: "4.0.0"
python_version: "3.9"
app_file: app.py
pinned: false
---

# Spatiotemporal Object Detection Visualizer & Annotator

A professional web-based dual-function application for visualizing and annotating spatiotemporal image datasets. This tool serves as both a **visualizer** for RGB spatially resolved images with their corresponding transient signals, and an **annotator** for creating bounding box annotations with minimal user input.

## 🎯 Overview

This application provides **dual functionality** for spatiotemporal object detection datasets:

### 📊 **Visualizer Function**
The tool visualizes RGB spatially resolved images alongside their corresponding transient signals:
- **RGB Spatially Resolved Image** (`-sr_int_full.png`): Surface reflection internal full view showing spatial RGB information
- **Transient Intensity Map** (`-tr_int_full.png`): Transmission internal full view displaying transient signal intensity across all pixels
- **Transient Line Plots** (`-tr_line.png`): Transmission line plots showing transient signal resolved as line plots across pixels

Each image set consists of three related images with the same file ID prefix, allowing synchronized visualization of spatial and temporal information.

### ✏️ **Annotator Function**
The annotation system requires only **2 coordinates** (points) made by the user to generate bounding boxes:
- **Point-to-Point Annotation**: Click two points on any image to automatically create a bounding box
- **Minimal Input**: No dragging required - just two clicks define the bounding box corners
- **Multi-View Support**: Annotate on any of the three synchronized views (RGB, intensity, or line plots)

### 📤 **Export for Model Training**
The application enables export of:
- **RGB images** with their corresponding **bounding boxes**
- **Transient signals** (intensity maps and line plots) associated with each annotation
- **Spatiotemporal data** formatted for object detection model training

This dual functionality makes it ideal for preparing datasets for **spatiotemporal object detection model training**, where both spatial (RGB) and temporal (transient) information are crucial.

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
- **Two-point bounding box creation**: Simply click two points to generate rectangular annotations (no dragging required)
- **Point-to-point annotation**: First click sets one corner, second click sets the opposite corner
- **Class-based labeling**: Assign objects to predefined classes
- **Class-based ID system**: Sequential IDs per class (1,2,3... for each class separately)
- **Center-point format**: Annotations saved as x,y center coordinates plus width/height
- **Multi-canvas support**: Annotate on any of the three synchronized views (RGB spatial, transient intensity, or line plots)

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

### 💾 **Data Management & Export**
- **Auto-save functionality**: Automatically saves annotations on navigation
- **CSV export format**: Standard CSV with image path, class, coordinates, and dimensions
- **Spatiotemporal export**: Export RGB images with bounding boxes and their corresponding transient signals
- **Model training ready**: Formatted output suitable for spatiotemporal object detection model training
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
python app.py
```
Access the application at: `http://127.0.0.1:6700/tagger`

### Basic Workflow

#### As a Visualizer:
1. **Navigate**: Use "Next Set" and "Next Folder" buttons to browse through image sets
2. **View synchronized data**: Observe RGB spatially resolved images alongside their transient intensity maps and line plots
3. **Compare views**: Analyze spatial and temporal information simultaneously across the three synchronized views

#### As an Annotator:
1. **Create bounding boxes**: Click two points on any image (first click = corner 1, second click = opposite corner)
2. **Classify**: Enter class name to assign labels to annotations
3. **Multi-view annotation**: Annotate on RGB spatial view, transient intensity, or line plots - all synchronized
4. **Auto-save**: Annotations automatically save when navigating
5. **Review**: Use auto-play feature for quality assurance
6. **Export**: Export RGB images with bounding boxes and corresponding transient signals for model training

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
image,id,name,centerX,centerY,width,height
toy/object1-sr_int_full.png,1,teddy,150.5,200.3,45.2,67.8
toy/object1-tr_int_full.png,1,teddy,150.5,200.3,45.2,67.8
toy/object1-tr_line.png,1,teddy,150.5,200.3,45.2,67.8
```

Each annotation includes:
- **Image path**: Path to the annotated image (RGB spatial, transient intensity, or line plot)
- **Class ID**: Sequential ID per class
- **Class name**: User-assigned class label
- **Bounding box coordinates**: Center point (centerX, centerY) and dimensions (width, height)

The exported data can be used to:
- Train spatiotemporal object detection models
- Associate RGB spatial information with transient temporal signals
- Create datasets with synchronized spatial and temporal annotations

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

## 🔬 **Use Cases**

### Spatiotemporal Object Detection
- **Visualize** RGB spatially resolved images with their corresponding transient signals
- **Annotate** objects using simple two-point bounding box creation
- **Export** synchronized RGB and transient data for model training
- **Train** spatiotemporal object detection models with both spatial and temporal information

### Research Applications
- Material analysis with spatial and temporal resolution
- Object detection in time-resolved imaging
- Multi-modal dataset preparation
- Spatiotemporal pattern recognition

---

**Built for professional spatiotemporal object detection workflows, combining visualization and annotation capabilities for RGB spatial and transient temporal data.**
