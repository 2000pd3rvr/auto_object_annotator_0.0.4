import sys
from os import walk
import csv
import argparse
from flask import Flask, redirect, url_for, request
from flask import render_template
from flask import send_file
import os  
from datasets import load_dataset
from huggingface_hub import hf_hub_download
from io import BytesIO
from PIL import Image
import tempfile
import shutil
import json
from datetime import datetime
import hashlib
import threading
import requests

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Analytics configuration - Use absolute path to ensure persistence across rebuilds
# In HuggingFace Spaces, files in the workspace root persist across rebuilds
STATS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "analytics_stats.json")
STATS_BACKUP_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "analytics_stats_backup.json")
STATS_LOCK = threading.Lock()

def get_client_ip():
    """Get client IP address from request"""
    try:
        if request.headers.get('X-Forwarded-For'):
            return request.headers.get('X-Forwarded-For').split(',')[0].strip()
        elif request.headers.get('X-Real-IP'):
            return request.headers.get('X-Real-IP')
        else:
            return request.remote_addr or '127.0.0.1'
    except:
        return '127.0.0.1'

def get_country_from_ip(ip):
    """Get country from IP address using free API"""
    try:
        # Using ip-api.com (free, no API key required)
        response = requests.get(f'http://ip-api.com/json/{ip}', timeout=2)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                return data.get('country', 'Unknown')
    except Exception as e:
        print(f"Error getting country for IP {ip}: {e}")
    return 'Unknown'

def get_user_agent_hash():
    """Create a hash of user agent for unique visitor tracking"""
    try:
        ua = request.headers.get('User-Agent', '')
        return hashlib.md5(ua.encode()).hexdigest()[:8]
    except:
        return 'unknown'

def load_stats():
    """Load statistics from JSON file with backup recovery"""
    # Try to load from main file first
    try:
        if os.path.exists(STATS_FILE):
            with open(STATS_FILE, 'r') as f:
                data = json.load(f)
                # Convert unique_visitors list back to set if needed
                if isinstance(data.get('unique_visitors'), list):
                    data['unique_visitors'] = set(data['unique_visitors'])
                print(f"Loaded stats from {STATS_FILE}: {data.get('total_visits', 0)} visits")
                return data
    except Exception as e:
        print(f"Error loading stats from main file: {e}")
        # Try backup file if main file fails
        try:
            if os.path.exists(STATS_BACKUP_FILE):
                print(f"Attempting to load from backup file: {STATS_BACKUP_FILE}")
                with open(STATS_BACKUP_FILE, 'r') as f:
                    data = json.load(f)
                    if isinstance(data.get('unique_visitors'), list):
                        data['unique_visitors'] = set(data['unique_visitors'])
                    print(f"Recovered stats from backup: {data.get('total_visits', 0)} visits")
                    # Restore backup to main file
                    save_stats(data)
                    return data
        except Exception as e2:
            print(f"Error loading stats from backup file: {e2}")
    
    # Return default structure if both files fail
    print("No existing stats found, starting fresh")
    return {
        'total_visits': 0,
        'unique_visitors': set(),
        'countries': {},
        'visits_by_date': {},
        'first_visit': None,
        'last_visit': None,
        'user_agents': {}
    }

def save_stats(stats):
    """Save statistics to JSON file with backup (convert sets to lists for JSON)"""
    try:
        stats_to_save = {
            'total_visits': stats.get('total_visits', 0),
            'unique_visitors': list(stats['unique_visitors']) if isinstance(stats.get('unique_visitors'), set) else stats.get('unique_visitors', []),
            'countries': stats.get('countries', {}),
            'visits_by_date': stats.get('visits_by_date', {}),
            'first_visit': stats.get('first_visit'),
            'last_visit': stats.get('last_visit'),
            'user_agents': stats.get('user_agents', {})
        }
        
        # Save to main file
        with open(STATS_FILE, 'w') as f:
            json.dump(stats_to_save, f, indent=2)
        
        # Create backup copy for redundancy
        try:
            import shutil
            shutil.copy2(STATS_FILE, STATS_BACKUP_FILE)
        except Exception as backup_error:
            print(f"Warning: Could not create backup: {backup_error}")
        
        print(f"Stats saved successfully: {stats_to_save.get('total_visits', 0)} total visits")
    except Exception as e:
        print(f"Error saving stats: {e}")
        import traceback
        traceback.print_exc()

def get_hf_all_time_visits(space_id="0001AMA/auto_object_annotator_0.0.4"):
    """Get HuggingFace Space 'All time visits' from metrics API - returns None if not available"""
    # Get HuggingFace token from environment (automatically provided in Spaces)
    hf_token = os.getenv("HF_TOKEN") or os.getenv("HUGGING_FACE_HUB_TOKEN")
    
    # If no token in env, try to get it from huggingface_hub
    if not hf_token:
        try:
            from huggingface_hub import HfApi
            api = HfApi()
            hf_token = api.token
        except:
            pass
    
    # Prepare headers with authentication if token is available
    headers = {'User-Agent': 'Mozilla/5.0'}
    if hf_token:
        headers['Authorization'] = f'Bearer {hf_token}'
    
    # Try the metrics API endpoint with authentication
    try:
        metrics_url = f"https://huggingface.co/api/spaces/{space_id}/metrics"
        response = requests.get(metrics_url, timeout=2, headers=headers)  # Short timeout to avoid blocking
        if response.status_code == 200:
            data = response.json()
            # Look for "All time visits" in the response
            if isinstance(data, dict):
                # Try various field names for "all time visits"
                for key in ['all_time_visits', 'allTimeVisits', 'total_visits', 'totalVisits', 
                           'all_time_views', 'allTimeViews', 'total_views', 'totalViews',
                           'views', 'visits', 'viewCount', 'visitCount']:
                    if key in data:
                        value = data[key]
                        # Only return if it's a valid number > 0 (not blank/null)
                        if value is not None and value != '' and value != '-':
                            try:
                                count = int(value) if isinstance(value, (int, float, str)) else None
                                if count is not None and count > 0:
                                    return count
                            except (ValueError, TypeError):
                                continue
        elif response.status_code == 401:
            print("HF API: Authentication required but token may be invalid")
        elif response.status_code == 403:
            print("HF API: Access forbidden - may need owner permissions")
    except Exception as e:
        print(f"HF API request failed: {e}")  # Debug logging
        pass  # Silently fail - return None
    
    # Return None if not available (don't fallback to app's tracking)
    return None

def track_visit():
    """Track a visit - cumulative and persistent"""
    try:
        with STATS_LOCK:
            stats = load_stats()
            
            # Convert unique_visitors list back to set if needed
            if isinstance(stats.get('unique_visitors'), list):
                stats['unique_visitors'] = set(stats['unique_visitors'])
            
            # Get visitor information
            ip = get_client_ip()
            ua_hash = get_user_agent_hash()
            visitor_id = f"{ip}_{ua_hash}"
            country = get_country_from_ip(ip)
            current_date = datetime.now().strftime('%Y-%m-%d')
            current_time = datetime.now().isoformat()
            
            # Update statistics
            stats['total_visits'] = stats.get('total_visits', 0) + 1
            if 'unique_visitors' not in stats:
                stats['unique_visitors'] = set()
            stats['unique_visitors'].add(visitor_id)
            
            # Track countries
            if 'countries' not in stats:
                stats['countries'] = {}
            if country not in stats['countries']:
                stats['countries'][country] = 0
            stats['countries'][country] += 1
            
            # Track visits by date
            if 'visits_by_date' not in stats:
                stats['visits_by_date'] = {}
            if current_date not in stats['visits_by_date']:
                stats['visits_by_date'][current_date] = 0
            stats['visits_by_date'][current_date] += 1
            
            # Track first and last visit
            if not stats.get('first_visit'):
                stats['first_visit'] = current_time
            stats['last_visit'] = current_time
            
            # Track user agents
            if 'user_agents' not in stats:
                stats['user_agents'] = {}
            ua = request.headers.get('User-Agent', 'Unknown')
            if ua not in stats['user_agents']:
                stats['user_agents'][ua] = 0
            stats['user_agents'][ua] += 1
            
            # Save statistics
            save_stats(stats)
    except Exception as e:
        # Don't let tracking errors break the app
        print(f"Error tracking visit: {e}")
        import traceback
        traceback.print_exc()

@app.route('/')
def index():
    """Redirect root URL to tagger"""
    # Track visit
    track_visit()
    return redirect(url_for('tagger'))

@app.route('/tagger')
def tagger():
    # Track visit
    track_visit()
    
    # Check if dataset was loaded successfully
    folder_sets = app.config.get("FOLDER_SETS", [])
    if not folder_sets:
        error_msg = app.config.get("DATASET_ERROR", "No folders found with all three required image types (sr_int_full.png, -tr_line.png, -tr_int_full.png)")
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Dataset Loading Error</title>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; background-color: #f0f0f0; }}
                .container {{ background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); max-width: 600px; margin: 0 auto; }}
                h1 {{ color: #dc3545; margin-bottom: 20px; }}
                p {{ font-size: 16px; margin: 15px 0; color: #333; }}
                .error {{ color: #dc3545; font-weight: bold; }}
                .info {{ background: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #ffc107; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>⚠️ Dataset Loading Error</h1>
                <div class="info">
                    <p class="error">{error_msg}</p>
                    <p>This may be due to:</p>
                    <ul style="text-align: left; display: inline-block;">
                        <li>Dataset not fully uploaded yet</li>
                        <li>Network issues loading the dataset</li>
                        <li>Dataset structure doesn't match expected format</li>
                    </ul>
                </div>
                <p>Please check the Space logs for more details.</p>
            </div>
        </body>
        </html>
        """, 500
    
    # Ensure HEAD is initialized and within bounds
    if "HEAD" not in app.config:
        app.config["HEAD"] = 0
    if app.config["HEAD"] < 0:
        app.config["HEAD"] = 0
    if app.config["HEAD"] >= len(folder_sets):
        app.config["HEAD"] = 0
        app.config["IMAGE_SET_INDEX"] = 0
        print("Reached end of folders, looping back to first folder")

    # Safely access current folder set
    try:
        directory = app.config.get('IMAGES', '')
        current_folder_set = folder_sets[app.config["HEAD"]]
        
        # Validate folder set structure
        if not isinstance(current_folder_set, dict) or 'image_sets' not in current_folder_set:
            raise ValueError(f"Invalid folder set structure at index {app.config['HEAD']}")

        # Get current image set index (default to 0 if not set)
        image_set_index = app.config.get("IMAGE_SET_INDEX", 0)
        if image_set_index < 0:
            image_set_index = 0
            app.config["IMAGE_SET_INDEX"] = 0

        # Get image sets for current folder
        image_sets = current_folder_set['image_sets']
        if not isinstance(image_sets, list) or len(image_sets) == 0:
            raise ValueError(f"No image sets found in folder {current_folder_set.get('folder', 'unknown')}")
            
        max_sets = len(image_sets)

        # Ensure image_set_index is within bounds
        if image_set_index >= max_sets:
            image_set_index = 0
            app.config["IMAGE_SET_INDEX"] = 0

        # Get current set of 3 images (all with same file ID prefix)
        current_images = []
        if image_set_index < max_sets:
            current_set = image_sets[image_set_index]
            if not isinstance(current_set, dict):
                raise ValueError(f"Invalid image set structure at index {image_set_index}")
                
            # Validate required keys exist
            required_keys = ['sr_int_full', 'tr_line', 'tr_int_full']
            for key in required_keys:
                if key not in current_set:
                    raise ValueError(f"Missing required image key '{key}' in image set {image_set_index}")
                
            current_images = [
                current_set['sr_int_full'],
                current_set['tr_line'],
                current_set['tr_int_full']
            ]
        else:
            raise ValueError(f"Image set index {image_set_index} out of bounds (max: {max_sets})")
            
    except (IndexError, KeyError, ValueError) as e:
        print(f"Error accessing folder/image data: {e}")
        import traceback
        traceback.print_exc()
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Data Access Error</title>
            <meta charset="UTF-8">
        </head>
        <body>
            <h1>Data Access Error</h1>
            <p>An error occurred while accessing folder/image data.</p>
            <p>Error: {str(e)}</p>
            <p>Please check the Space logs for more details.</p>
        </body>
        </html>
        """, 500

    labels = app.config["LABELS"]
    has_prev_folder = app.config["HEAD"] > 0
    has_next_folder = app.config["HEAD"] + 1 < len(app.config["FOLDER_SETS"])
    has_prev_set = image_set_index > 0
    has_next_set = image_set_index + 1 < max_sets

    # Get statistics for display
    try:
        stats_data = load_stats()
        total_visits = stats_data.get('total_visits', 0)
        unique_count = len(stats_data['unique_visitors']) if isinstance(stats_data.get('unique_visitors'), set) else len(stats_data.get('unique_visitors', []))
        countries_count = len(stats_data.get('countries', {}))
    except Exception as e:
        print(f"Error loading stats: {e}")
        import traceback
        traceback.print_exc()
        total_visits = 0
        unique_count = 0
        countries_count = 0
    
    # Try to get HF Space "All time visits" from analytics
    # Only use HF value if available - don't fallback to app's tracking
    hf_all_time_visits = None
    try:
        hf_all_time_visits = get_hf_all_time_visits()
        # Only use if we got a valid value
        if hf_all_time_visits is not None and hf_all_time_visits > 0:
            pass  # Use the value
        else:
            hf_all_time_visits = None  # Keep blank until HF populates it
    except Exception as e:
        # Silently fail - keep as None (blank)
        print(f"HF All time visits fetch failed (keeping blank): {e}")
        hf_all_time_visits = None

    try:
        return render_template(
        'tagger.html',
        has_prev_folder=has_prev_folder,
        has_next_folder=has_next_folder,
        has_prev_set=has_prev_set,
        has_next_set=has_next_set,
        directory=directory,
        current_folder_set=current_folder_set,
        current_folder=current_folder_set['folder'],
        current_images=current_images,
        labels=labels,
        head=app.config["HEAD"] + 1,
        len=len(app.config["FOLDER_SETS"]),
        image_set_index=image_set_index + 1,
        max_sets=max_sets,
        total_visits=total_visits,
        unique_visitors=unique_count,
        countries_count=countries_count,
        hf_all_time_visits=hf_all_time_visits
        )
    except Exception as e:
        # If template rendering fails, return a simple error page
        print(f"Error rendering template: {e}")
        import traceback
        traceback.print_exc()
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Application Error</title>
            <meta charset="UTF-8">
        </head>
        <body>
            <h1>Application Error</h1>
            <p>An error occurred while rendering the page.</p>
            <p>Error: {str(e)}</p>
            <p>Please check the Space logs for more details.</p>
        </body>
        </html>
        """, 500

def save_annotations_to_csv():
    """Save all labeled annotations to CSV file"""
    # Write CSV with header and all labeled annotations
    with open(app.config["OUT"], 'w') as f:
        # Write header
        f.write("image,id,name,centerX,centerY,width,height\n")

        # Write ALL labeled annotations from current session
        current_count = 0
        for label in app.config["LABELS"]:
            print(f"DEBUG: Checking label - Image: {label['image']}, ID: {label.get('id', 'None')}, Name: {label.get('name', 'None')}")
            if label.get("id") and label.get("name"):
                f.write(
                    label["image"] + "," +
                    label["id"] + "," +
                    label["name"] + "," +
                    str(round(float(label["centerX"]))) + "," +
                    str(round(float(label["centerY"]))) + "," +
                    str(round(float(label["width"]))) + "," +
                    str(round(float(label["height"]))) + "\n"
                )
                current_count += 1
                print(f"DEBUG: Wrote annotation for {label['image']} with class {label['name']} (ID: {label['id']})")
        f.flush()  # Ensure data is written to disk immediately
        print(f"DEBUG: Saved {current_count} labeled annotations to CSV")

@app.route('/save_and_next')
def save_and_next():
    # Get current folder images to identify which annotations to save
    if app.config["HEAD"] < len(app.config["FOLDER_SETS"]):
        current_folder_set = app.config["FOLDER_SETS"][app.config["HEAD"]]
        current_folder_images = set()
        for image_set in current_folder_set['image_sets']:
            current_folder_images.add(image_set['sr_int_full'])
            current_folder_images.add(image_set['tr_line'])
            current_folder_images.add(image_set['tr_int_full'])

        # Read existing CSV content
        existing_lines = []
        if os.path.exists(app.config["OUT"]):
            with open(app.config["OUT"], 'r') as f:
                existing_lines = f.readlines()

        # Write back CSV with header and non-current-folder annotations, plus new current folder annotations
        with open(app.config["OUT"], 'w') as f:
            # Write header
            f.write("image,id,name,centerX,centerY,width,height\n")

            # Write existing annotations that are NOT from current folder
            existing_count = 0
            for line in existing_lines[1:]:  # Skip header
                line = line.strip()
                if line:
                    image_name = line.split(',')[0]
                    if image_name not in current_folder_images:
                        f.write(line + "\n")
                        existing_count += 1
            print(f"DEBUG: Wrote {existing_count} existing annotations from other folders")

            # Write ALL labeled annotations from current session (not just current folder)
            current_count = 0
            for label in app.config["LABELS"]:
                print(f"DEBUG: Checking label - Image: {label['image']}, ID: {label.get('id', 'None')}, Name: {label.get('name', 'None')}")
                if label.get("id") and label.get("name"):
                    f.write(
                        label["image"] + "," +
                        label["id"] + "," +
                        label["name"] + "," +
                        str(round(float(label["centerX"]))) + "," +
                        str(round(float(label["centerY"]))) + "," +
                        str(round(float(label["width"]))) + "," +
                        str(round(float(label["height"]))) + "\n"
                    )
                    current_count += 1
                    print(f"DEBUG: Wrote annotation for {label['image']} with class {label['name']} (ID: {label['id']})")
            print(f"DEBUG: Wrote {current_count} labeled annotations from all folders")

        # Remove current folder annotations from memory but keep others
        app.config["LABELS"] = [label for label in app.config["LABELS"]
                               if label["image"] not in current_folder_images]

        print(f"Saved annotations for folder: {current_folder_set['folder']}")

    # Move to next folder, loop back to start if at the end
    app.config["HEAD"] += 1
    if app.config["HEAD"] >= len(app.config["FOLDER_SETS"]):
        app.config["HEAD"] = 0  # Loop back to first folder
        app.config["IMAGE_SET_INDEX"] = 0  # Reset image set index
        print("Reached end of folders, looping back to first folder")

    return redirect(url_for('tagger'))

@app.route('/next_folder')
def next_folder():
    # Save annotations before moving to next folder
    save_annotations_to_csv()

    # Move to next folder (labels persist)
    app.config["HEAD"] += 1
    if app.config["HEAD"] >= len(app.config["FOLDER_SETS"]):
        app.config["HEAD"] = 0  # Loop back to first folder
        print("Reached end of folders, looping back to first folder")
    app.config["IMAGE_SET_INDEX"] = 0  # Reset to first image set
    
    # Preserve auto-play parameters if present
    autoplay = request.args.get('autoplay')
    interval = request.args.get('interval')
    if autoplay and interval:
        return redirect(url_for('tagger', autoplay=autoplay, interval=interval))
    return redirect(url_for('tagger'))

@app.route('/prev_folder')
def prev_folder():
    # Move to previous folder (labels persist)
    app.config["HEAD"] -= 1
    if app.config["HEAD"] < 0:
        app.config["HEAD"] = len(app.config["FOLDER_SETS"]) - 1  # Loop to last folder
        print("Reached beginning of folders, looping to last folder")
    app.config["IMAGE_SET_INDEX"] = 0  # Reset to first image set
    
    # Preserve auto-play parameters if present
    autoplay = request.args.get('autoplay')
    interval = request.args.get('interval')
    if autoplay and interval:
        return redirect(url_for('tagger', autoplay=autoplay, interval=interval))
    return redirect(url_for('tagger'))

@app.route('/next_set')
def next_set():
    # Save annotations before moving to next set
    save_annotations_to_csv()

    # Move to next image set within current folder
    current_folder_set = app.config["FOLDER_SETS"][app.config["HEAD"]]
    max_sets = len(current_folder_set['image_sets'])

    current_index = app.config.get("IMAGE_SET_INDEX", 0)
    if current_index + 1 < max_sets:
        app.config["IMAGE_SET_INDEX"] = current_index + 1
    else:
        # Reached end of sets in current folder, move to next folder
        if app.config["HEAD"] + 1 < len(app.config["FOLDER_SETS"]):
            app.config["HEAD"] += 1
            app.config["IMAGE_SET_INDEX"] = 0  # Reset to first set in new folder
            print(f"DEBUG: Auto-advanced to next folder: {app.config['FOLDER_SETS'][app.config['HEAD']]['folder']}")
        else:
            # Reached end of all folders, loop back to beginning
            app.config["HEAD"] = 0
            app.config["IMAGE_SET_INDEX"] = 0
            print("DEBUG: Auto-looped back to first folder for continuous play")
    
    # Preserve auto-play parameters if present
    autoplay = request.args.get('autoplay')
    interval = request.args.get('interval')
    if autoplay and interval:
        return redirect(url_for('tagger', autoplay=autoplay, interval=interval))
    return redirect(url_for('tagger'))

@app.route('/prev_set')
def prev_set():
    # Move to previous image set within current folder
    current_index = app.config.get("IMAGE_SET_INDEX", 0)
    if current_index > 0:
        app.config["IMAGE_SET_INDEX"] = current_index - 1
    
    # Preserve auto-play parameters if present
    autoplay = request.args.get('autoplay')
    interval = request.args.get('interval')
    if autoplay and interval:
        return redirect(url_for('tagger', autoplay=autoplay, interval=interval))
    return redirect(url_for('tagger'))

@app.route('/reset_annotations')
def reset_annotations():
    scope = request.args.get('scope', 'folder')

    if scope == 'all':
        # Reset all annotations from all folders
        app.config["LABELS"] = []
        app.config["CLASS_TO_ID"] = {}
        app.config["NEXT_CLASS_ID"] = 1
        print("DEBUG: Reset ALL annotations from ALL folders")
    elif scope == 'folder':
        # Reset annotations only for current folder
        current_folder_set = app.config["FOLDER_SETS"][app.config["HEAD"]]
        folder_name = current_folder_set["folder"]

        # Remove annotations that belong to the current folder
        original_count = len(app.config["LABELS"])
        app.config["LABELS"] = [
            label for label in app.config["LABELS"]
            if not any(label["image"].startswith(f"{folder_name}/") for folder_name in [folder_name])
        ]
        removed_count = original_count - len(app.config["LABELS"])
        print(f"DEBUG: Reset {removed_count} annotations from folder '{folder_name}'")

    # Save the updated annotations to CSV
    save_annotations_to_csv()

    return redirect(url_for('tagger'))

@app.route("/bye")
def bye():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Annotation Complete</title>
        <meta charset="UTF-8">
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background-color: #f0f0f0; }
            .container { background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); max-width: 600px; margin: 0 auto; }
            h1 { color: #28a745; margin-bottom: 20px; }
            p { font-size: 18px; margin: 15px 0; color: #333; }
            .success { color: #28a745; font-weight: bold; }
            .info { background: #e7f3ff; padding: 15px; border-radius: 5px; margin: 20px 0; }
            .restart-btn { background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 20px; }
            .restart-btn:hover { background: #0056b3; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎉 Annotation Complete!</h1>
            <p class="success">All folders have been processed successfully.</p>
            <div class="info">
                <p><strong>Your annotations have been saved to:</strong></p>
                <p><code>out.csv</code></p>
                <p>The CSV file contains all bounding boxes and labels you created.</p>
            </div>
            <p>You can now use this data for training machine learning models or further analysis.</p>
            <a href="/tagger" class="restart-btn">Start Over</a>
        </div>
    </body>
    </html>
    """

@app.route('/stats')
def stats():
    """Display analytics statistics"""
    stats_data = load_stats()
    
    # Convert set to list for display
    unique_count = len(stats_data['unique_visitors']) if isinstance(stats_data['unique_visitors'], set) else len(stats_data.get('unique_visitors', []))
    
    # Sort countries by visits
    sorted_countries = sorted(stats_data.get('countries', {}).items(), key=lambda x: x[1], reverse=True)
    
    # Sort dates
    sorted_dates = sorted(stats_data.get('visits_by_date', {}).items(), reverse=True)[:30]  # Last 30 days
    
    # Get top user agents
    sorted_user_agents = sorted(stats_data.get('user_agents', {}).items(), key=lambda x: x[1], reverse=True)[:10]
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Analytics Statistics</title>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5; }}
            .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            h1 {{ color: #333; border-bottom: 3px solid #6c757d; padding-bottom: 10px; }}
            h2 {{ color: #555; margin-top: 30px; }}
            .stat-box {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #6c757d; }}
            .stat-number {{ font-size: 36px; font-weight: bold; color: #495057; }}
            .stat-label {{ font-size: 14px; color: #666; margin-top: 5px; }}
            .table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            .table th, .table td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            .table th {{ background-color: #6c757d; color: white; }}
            .table tr:hover {{ background-color: #f5f5f5; }}
            .back-link {{ display: inline-block; margin-top: 20px; padding: 10px 20px; background: #6c757d; color: white; text-decoration: none; border-radius: 5px; }}
            .back-link:hover {{ background: #5a6268; }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📊 Analytics Statistics</h1>
            
            <div class="grid">
                <div class="stat-box">
                    <div class="stat-number">{stats_data.get('total_visits', 0):,}</div>
                    <div class="stat-label">Total Visits</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">{unique_count:,}</div>
                    <div class="stat-label">Unique Visitors</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">{len(stats_data.get('countries', {}))}</div>
                    <div class="stat-label">Countries</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">{stats_data.get('first_visit', 'N/A')[:10] if stats_data.get('first_visit') else 'N/A'}</div>
                    <div class="stat-label">First Visit</div>
                </div>
            </div>
            
            <h2>🌍 Visits by Country</h2>
            <table class="table">
                <thead>
                    <tr>
                        <th>Country</th>
                        <th>Visits</th>
                        <th>Percentage</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    total_visits = stats_data.get('total_visits', 1)
    for country, count in sorted_countries:
        percentage = (count / total_visits * 100) if total_visits > 0 else 0
        html += f"""
                    <tr>
                        <td>{country}</td>
                        <td>{count:,}</td>
                        <td>{percentage:.1f}%</td>
                    </tr>
        """
    
    html += """
                </tbody>
            </table>
            
            <h2>📅 Visits by Date (Last 30 Days)</h2>
            <table class="table">
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Visits</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    for date, count in sorted_dates:
        html += f"""
                    <tr>
                        <td>{date}</td>
                        <td>{count:,}</td>
                    </tr>
        """
    
    html += """
                </tbody>
            </table>
            
            <h2>🖥️ Top User Agents</h2>
            <table class="table">
                <thead>
                    <tr>
                        <th>User Agent</th>
                        <th>Visits</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    for ua, count in sorted_user_agents:
        # Truncate long user agents
        ua_display = ua[:80] + '...' if len(ua) > 80 else ua
        html += f"""
                    <tr>
                        <td>{ua_display}</td>
                        <td>{count:,}</td>
                    </tr>
        """
    
    html += f"""
                </tbody>
            </table>
            
            <p><strong>Last Updated:</strong> {stats_data.get('last_visit', 'N/A')}</p>
            
            <a href="/tagger" class="back-link">← Back to Tagger</a>
        </div>
    </body>
    </html>
    """
    
    return html

@app.route('/add/<temp_id>')
def add(temp_id):
    image = request.args.get("image")
    xMin = float(request.args.get("xMin"))
    xMax = float(request.args.get("xMax"))
    yMin = float(request.args.get("yMin"))
    yMax = float(request.args.get("yMax"))

    # Convert to center, width, height format
    centerX = (xMin + xMax) / 2
    centerY = (yMin + yMax) / 2
    width = xMax - xMin
    height = yMax - yMin

    print(f"DEBUG: Coordinates - xMin:{xMin:.1f}, xMax:{xMax:.1f}, yMin:{yMin:.1f}, yMax:{yMax:.1f}")
    print(f"DEBUG: Calculated - centerX:{centerX:.1f}, centerY:{centerY:.1f}, width:{width:.1f}, height:{height:.1f}")

    # Use temporary ID until class is assigned
    app.config["LABELS"].append({
        "image": image,
        "temp_id": temp_id,  # Temporary ID for tracking
        "id": "",  # Will be assigned when class is labeled
        "name": "",
        "centerX": centerX,
        "centerY": centerY,
        "width": width,
        "height": height
    })
    return redirect(url_for('tagger'))

@app.route('/remove/<temp_id>')
def remove(temp_id):
    image = request.args.get("image")
    print(f"DEBUG: Removing - Temp ID: {temp_id}, Image: {image}")

    original_count = len(app.config["LABELS"])
    app.config["LABELS"] = [
        label for label in app.config["LABELS"]
        if not (label["image"] == image and
                (label.get("temp_id") == temp_id or label.get("id") == temp_id))
    ]
    new_count = len(app.config["LABELS"])
    print(f"DEBUG: Removed {original_count - new_count} labels")

    return redirect(url_for('tagger'))

@app.route('/label/<temp_id>')
def label(temp_id):
    image = request.args.get("image")
    name = request.args.get("name").strip().lower()
    print(f"DEBUG: Labeling - Temp ID: {temp_id}, Image: {image}, Name: {name}")

    # Get or assign class ID
    if name not in app.config["CLASS_TO_ID"]:
        app.config["CLASS_TO_ID"][name] = app.config["NEXT_CLASS_ID"]
        app.config["NEXT_CLASS_ID"] += 1
        print(f"DEBUG: Assigned new class ID {app.config['CLASS_TO_ID'][name]} to class '{name}'")

    class_id = app.config["CLASS_TO_ID"][name]

    found = False
    for label in app.config["LABELS"]:
        # Check both temp_id and regular id for compatibility
        label_temp_id = label.get("temp_id", label.get("id"))
        print(f"DEBUG: Checking label - Temp ID: {label_temp_id}, Image: {label['image']}")
        if label["image"] == image and label_temp_id == temp_id:
            label["name"] = name
            label["id"] = str(class_id)  # Assign class-based ID
            if "temp_id" in label:
                del label["temp_id"]  # Remove temp_id once class is assigned
            print(f"DEBUG: Updated label temp_id {temp_id} with name '{name}' and class ID {class_id}")
            found = True
            break

    if not found:
        print(f"DEBUG: Label not found for temp_id: {temp_id}, Image: {image}")

    print(f"DEBUG: Current class mapping: {app.config['CLASS_TO_ID']}")
    return redirect(url_for('tagger'))

@app.route('/image/<path:f>')
def images(f):
    # Check if using HuggingFace dataset
    if app.config.get("USE_HF_DATASET", False):
        # Load image from HuggingFace dataset
        try:
            from huggingface_hub import hf_hub_download
            
            dataset_name = app.config.get("HF_DATASET_NAME", "0001AMA/multimodal_data_annotator_dataset")
            cache_dir = app.config.get("CACHE_DIR", None)
            
            # Try to find the file path
            file_path = f
            dataset_files = app.config.get("HF_DATASET_FILES", {})
            
            # Try exact match first
            if f not in dataset_files:
                # Try to find by matching path
                for path in dataset_files:
                    if path.endswith(f) or f in path:
                        file_path = path
                        break
            
            # Download file from HuggingFace
            try:
                local_path = hf_hub_download(
                    repo_id=dataset_name,
                    filename=file_path,
                    repo_type="dataset",
                    cache_dir=cache_dir
                )
                
                if os.path.exists(local_path):
                    return send_file(local_path)
            except Exception as download_error:
                print(f"Error downloading file {file_path}: {download_error}")
                # Try alternative: download to cache and serve
                try:
                    # Use cache_dir if available
                    cache_file = os.path.join(cache_dir or tempfile.gettempdir(), file_path.replace('/', '_'))
                    if not os.path.exists(cache_file):
                        local_path = hf_hub_download(
                            repo_id=dataset_name,
                            filename=file_path,
                            repo_type="dataset"
                        )
                        # Copy to cache
                        os.makedirs(os.path.dirname(cache_file), exist_ok=True)
                        shutil.copy2(local_path, cache_file)
                    else:
                        local_path = cache_file
                    
                    return send_file(local_path)
                except Exception as e2:
                    print(f"Alternative download also failed: {e2}")
                    
        except Exception as e:
            print(f"Error loading image from dataset: {e}")
            import traceback
            traceback.print_exc()
            # Fallback to local file if available
            pass
    
    # Fallback to local file system
    images_dir = app.config.get('IMAGES', '')
    if images_dir:
        file_path = os.path.join(images_dir, f)
        if os.path.exists(file_path):
            return send_file(file_path)
    
    return "Image not found", 404

def load_from_huggingface_dataset(dataset_name="0001AMA/multimodal_data_annotator_dataset"):
    """Load and process images from HuggingFace dataset"""
    print(f"Loading dataset from HuggingFace: {dataset_name}")
    
    try:
        from huggingface_hub import list_repo_files, hf_hub_download
        
        # List all files in the dataset repository
        print("Listing files in dataset repository...")
        repo_files = list_repo_files(repo_id=dataset_name, repo_type="dataset")
        print(f"Found {len(repo_files)} files in repository")
        
        # Filter PNG files only
        png_files = [f for f in repo_files if f.endswith('.png')]
        print(f"Found {len(png_files)} PNG files")
        
        # Create a cache directory for images
        cache_dir = os.path.join(tempfile.gettempdir(), "hf_dataset_cache")
        os.makedirs(cache_dir, exist_ok=True)
        app.config["CACHE_DIR"] = cache_dir
        
        # Process files to group by folder and file ID
        folder_sets = []
        required_suffixes = ['sr_int_full.png', '-tr_line.png', '-tr_int_full.png']

        # Group files by folder and file ID
        folder_files = {}  # {folder_name: {file_id: {suffix: file_path}}}
        
        for file_path in png_files:
            # Extract folder name and filename
            path_parts = file_path.split('/')
            if len(path_parts) < 2:
                continue
            
            folder_name = path_parts[0]
            filename = path_parts[-1]
            
            # Check if file matches required suffixes
            matched_suffix = None
            for suffix in required_suffixes:
                if filename.endswith(suffix):
                    matched_suffix = suffix
                    break
            
            if not matched_suffix:
                continue
            
            # Extract file ID prefix (everything before the first '-')
            if '-' in filename:
                file_id = filename.split('-')[0]
            else:
                continue
            
            # Initialize folder structure
            if folder_name not in folder_files:
                folder_files[folder_name] = {}
            if file_id not in folder_files[folder_name]:
                folder_files[folder_name][file_id] = {}
            
            # Store file path
            folder_files[folder_name][file_id][matched_suffix] = file_path
        
        # Create folder sets with valid image sets
        for folder_name, file_ids in folder_files.items():
            valid_image_sets = []
            for file_id, images in file_ids.items():
                # Check if all three required suffixes are present
                if all(suffix in images for suffix in required_suffixes):
                    valid_image_sets.append({
                        'file_id': file_id,
                        'sr_int_full': images['sr_int_full.png'],
                        'tr_line': images['-tr_line.png'],
                        'tr_int_full': images['-tr_int_full.png']
                    })
                    print(f"DEBUG: Created valid image set for file_id '{file_id}' in folder '{folder_name}'")
            
            if valid_image_sets:
                folder_sets.append({
                    'folder': folder_name,
                    'image_sets': valid_image_sets
                })
                print(f"DEBUG: Added folder '{folder_name}' with {len(valid_image_sets)} image sets")
        
        # Store file list for image serving
        app.config["HF_DATASET_FILES"] = {f: f for f in png_files}
        app.config["HF_DATASET_NAME"] = dataset_name
        
        print(f"Successfully processed {len(folder_sets)} folders with valid image sets")
        return folder_sets
        
    except Exception as e:
        print(f"Error loading HuggingFace dataset: {e}")
        import traceback
        traceback.print_exc()
        return []

def load_from_local_directory(directory):
    """Load and process images from local directory (original method)"""
    folder_sets = []
    required_suffixes = ['sr_int_full.png', '-tr_line.png', '-tr_int_full.png']

    for (dirpath, dirnames, filenames) in walk(directory):
        if dirpath == directory:  # Skip root directory
            continue

        # Find ALL images with required suffixes in this folder and group by file ID prefix
        found_images = {'sr_int_full.png': [], '-tr_line.png': [], '-tr_int_full.png': []}
        for filename in filenames:
            for suffix in required_suffixes:
                if filename.endswith(suffix):
                    relative_path = os.path.relpath(os.path.join(dirpath, filename), directory)
                    found_images[suffix].append(relative_path)

        # Group images by their file ID prefix (everything before the first '-')
        image_groups = {}
        for suffix in required_suffixes:
            for image_path in found_images[suffix]:
                filename = os.path.basename(image_path)
                # Extract file ID prefix (everything before the first '-')
                if '-' in filename:
                    file_id = filename.split('-')[0]
                    if file_id not in image_groups:
                        image_groups[file_id] = {}
                    image_groups[file_id][suffix] = image_path
                    print(f"DEBUG: Grouped {filename} with file_id '{file_id}' for suffix '{suffix}'")

        # Create image sets only for file IDs that have all three image types
        valid_image_sets = []
        for file_id, images in image_groups.items():
            print(f"DEBUG: Checking file_id '{file_id}' - has suffixes: {list(images.keys())}")
            if all(suffix in images for suffix in required_suffixes):
                valid_image_sets.append({
                    'file_id': file_id,
                    'sr_int_full': images['sr_int_full.png'],
                    'tr_line': images['-tr_line.png'],
                    'tr_int_full': images['-tr_int_full.png']
                })
                print(f"DEBUG: Created valid image set for file_id '{file_id}'")
            else:
                print(f"DEBUG: Skipped file_id '{file_id}' - missing suffixes: {[s for s in required_suffixes if s not in images]}")

        # Only include folders that have at least one complete image set
        if valid_image_sets:
            folder_name = os.path.basename(dirpath)
            folder_sets.append({
                'folder': folder_name,
                'image_sets': valid_image_sets
            })

    return folder_sets

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', type=str, default=None, help='specify the images directory (optional, uses HF dataset if not provided)')
    parser.add_argument("--out")
    args = parser.parse_args()
    
    app.config["LABELS"] = []
    app.config["CLASS_TO_ID"] = {}  # Maps class names to IDs
    app.config["NEXT_CLASS_ID"] = 1  # Next available class ID
    
    # Check if running on HuggingFace Spaces or if no local directory specified
    is_hf_space = os.getenv("SPACE_ID") is not None
    use_hf_dataset = args.dir is None or is_hf_space
    
    if use_hf_dataset:
        print("===== Application Startup at " + str(os.popen('date').read().strip()) + " =====")
        print("Loading from HuggingFace dataset...")
        app.config["USE_HF_DATASET"] = True
        folder_sets = load_from_huggingface_dataset("0001AMA/multimodal_data_annotator_dataset")
        app.config["IMAGES"] = ""  # Not using local directory
    else:
        print("Loading from local directory...")
        app.config["USE_HF_DATASET"] = False
        directory = args.dir
        if directory[-1] != "/":
            directory += "/"
        app.config["IMAGES"] = directory
        folder_sets = load_from_local_directory(directory)

    if not folder_sets:
        error_msg = "No folders found with all three required image types (sr_int_full.png, -tr_line.png, -tr_int_full.png)"
        print(error_msg)
        if use_hf_dataset:
            print("This may be due to:")
            print("1. Dataset not fully uploaded yet")
            print("2. Dataset structure doesn't match expected format")
            print("3. Network issues loading the dataset")
        # Don't exit - allow app to start and show error message in UI
        app.config["FOLDER_SETS"] = []
        app.config["DATASET_ERROR"] = error_msg
    else:
        app.config["FOLDER_SETS"] = folder_sets
        app.config["DATASET_ERROR"] = None
    app.config["HEAD"] = 0
    app.config["IMAGE_SET_INDEX"] = 0
    app.config["OUT"] = args.out if args.out else "out.csv"

    # Check if CSV file exists, create header only if it doesn't exist
    import os
    if not os.path.exists(app.config["OUT"]):
        with open(app.config["OUT"], 'w') as f:
            f.write("image,id,name,centerX,centerY,width,height\n")
        print(f"Created new CSV file: {app.config['OUT']}")
    else:
        print(f"Using existing CSV file: {app.config['OUT']}")
        # Verify the file has the correct header
        with open(app.config["OUT"], 'r') as f:
            first_line = f.readline().strip()
            if first_line != "image,id,name,centerX,centerY,width,height":
                print("Warning: Existing CSV file has different header format!")
                print(f"Expected: image,id,name,centerX,centerY,width,height")
                print(f"Found: {first_line}")
                # Backup the old file and create new one
                backup_name = app.config["OUT"].replace('.csv', '_backup.csv')
                os.rename(app.config["OUT"], backup_name)
                print(f"Backed up old file to: {backup_name}")
                with open(app.config["OUT"], 'w') as f:
                    f.write("image,id,name,centerX,centerY,width,height\n")
                print(f"Created new CSV file with correct header")

    # Load existing annotations from CSV if file exists and has content
    if os.path.exists(app.config["OUT"]):
        try:
            with open(app.config["OUT"], 'r') as f:
                lines = f.readlines()[1:]  # Skip header
                for line in lines:
                    line = line.strip()
                    if line:  # Skip empty lines
                        parts = line.split(',')
                        if len(parts) >= 7:  # Ensure we have all required fields
                            class_name = parts[2].lower() if parts[2] else ""
                            class_id = parts[1] if parts[1] else ""

                            # Rebuild class mapping for labeled annotations
                            if class_name and class_id and class_id.isdigit():
                                class_id_int = int(class_id)
                                if class_name not in app.config["CLASS_TO_ID"]:
                                    app.config["CLASS_TO_ID"][class_name] = class_id_int
                                    if class_id_int >= app.config["NEXT_CLASS_ID"]:
                                        app.config["NEXT_CLASS_ID"] = class_id_int + 1

                            # For unlabeled annotations, assign a temp_id
                            annotation_data = {
                                "image": parts[0],
                                "name": parts[2],
                                "centerX": float(parts[3]),
                                "centerY": float(parts[4]),
                                "width": float(parts[5]),
                                "height": float(parts[6])
                            }

                            if class_id:
                                annotation_data["id"] = class_id
                            else:
                                # Assign temp_id for unlabeled annotations
                                annotation_data["temp_id"] = str(len(app.config["LABELS"]) + 1)

                            app.config["LABELS"].append(annotation_data)
            if len(app.config["LABELS"]) > 0:
                print(f"Loaded {len(app.config['LABELS'])} existing annotations from CSV")
        except Exception as e:
            print(f"Error loading existing annotations: {e}")
            # Don't clear LABELS here, keep them empty if loading fails
    print(f"Found {len(folder_sets)} valid folder sets")
    # For HuggingFace Spaces, use 0.0.0.0 and port 7860
    # For local development, you can use 127.0.0.1 and port 7620
    if os.getenv("SPACE_ID"):  # Running on HuggingFace
        app.run(host="0.0.0.0", port=7860, debug=False)
    else:  # Running locally
        app.run(host="127.0.0.1", port=7620, debug=False)