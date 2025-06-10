from config import YOLO_CONFIG, VIDEO_CONFIG, SHOW_PROCESSING_OUTPUT, DATA_RECORD_RATE, FRAME_SIZE, TRACK_MAX_AGE

if FRAME_SIZE > 1920:
	print("Frame size is too large!")
	quit()
elif FRAME_SIZE < 480:
	print("Frame size is too small! You won't see anything")
	quit()

import datetime
import time
import numpy as np
import imutils
import cv2
import os
import csv
import json
import sys 
import threading
import queue
from video_process import video_process
from deep_sort import nn_matching
from deep_sort.detection import Detection
from deep_sort.tracker import Tracker
from deep_sort import generate_detections as gdet

# Thread-safe CSV writer class
class ThreadSafeCSVWriter:
    def __init__(self, filepath, headers):
        self.filepath = filepath
        self.headers = headers
        self.data_queue = queue.Queue()
        self.should_stop = threading.Event()
        self.writer_thread = None
        self._ensure_file_exists()
        
    def _ensure_file_exists(self):
        """Ensure the CSV file exists with proper headers"""
        if not os.path.exists(self.filepath) or os.path.getsize(self.filepath) == 0:
            with open(self.filepath, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(self.headers)
    
    def start(self):
        """Start the background writer thread"""
        self.writer_thread = threading.Thread(target=self._writer_worker)
        self.writer_thread.daemon = True
        self.writer_thread.start()
    
    def _writer_worker(self):
        """Background thread that writes data to CSV"""
        while not self.should_stop.is_set():
            try:
                # Get data from queue with timeout
                data = self.data_queue.get(timeout=1.0)
                
                # Write to file immediately and close
                with open(self.filepath, 'a', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(data)
                    file.flush()  # Ensure data is written immediately
                
                self.data_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error writing to CSV: {e}")
                continue
    
    def writerow(self, data):
        """Add data to the write queue"""
        self.data_queue.put(data)
    
    def stop(self):
        """Stop the writer thread and flush remaining data"""
        # Write any remaining data
        while not self.data_queue.empty():
            try:
                data = self.data_queue.get_nowait()
                with open(self.filepath, 'a', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(data)
                    file.flush()
                self.data_queue.task_done()
            except queue.Empty:
                break
            except Exception as e:
                print(f"Error during final write: {e}")
        
        # Signal thread to stop
        self.should_stop.set()
        if self.writer_thread and self.writer_thread.is_alive():
            self.writer_thread.join(timeout=2.0)

# Check if directory argument is passed
if len(sys.argv) > 1:
    cam_dir = sys.argv[1]
    print(f"Running with directory: {cam_dir}")

    # Optional: switch video input based on cam_dir
    if cam_dir == "cam1":
        VIDEO_CONFIG["VIDEO_CAP"] = 0  # Laptop cam
    elif cam_dir == "cam2":
        VIDEO_CONFIG["VIDEO_CAP"] = "video2.mp4"
    elif cam_dir == "cam3":
        VIDEO_CONFIG["VIDEO_CAP"] = "video3.mp4"
    VIDEO_CONFIG["IS_CAM"] = (cam_dir == "cam1")
else:
    cam_dir = None
    print("No camera directory specified. Using default config.")

# Read from video
IS_CAM = VIDEO_CONFIG["IS_CAM"]
cap = cv2.VideoCapture(VIDEO_CONFIG["VIDEO_CAP"])

# Load YOLOv3-tiny weights and config
WEIGHTS_PATH = YOLO_CONFIG["WEIGHTS_PATH"]
CONFIG_PATH = YOLO_CONFIG["CONFIG_PATH"]

# Load the YOLOv3-tiny pre-trained COCO dataset 
net = cv2.dnn.readNetFromDarknet(CONFIG_PATH, WEIGHTS_PATH)
# Set the preferable backend to CPU since we are not using GPU
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

# Get the names of all the layers in the network
ln = net.getLayerNames()
# Filter out the layer names we dont need for YOLO
ln = [ln[i - 1] for i in net.getUnconnectedOutLayers()]

# Tracker parameters
max_cosine_distance = 0.7
nn_budget = None

#initialize deep sort object
if IS_CAM: 
	max_age = VIDEO_CONFIG["CAM_APPROX_FPS"] * TRACK_MAX_AGE
else:
	max_age=DATA_RECORD_RATE * TRACK_MAX_AGE
	if max_age > 30:
		max_age = 30

script_dir = os.path.dirname(os.path.abspath(__file__))
model_filename = os.path.join(script_dir, "model_data", "mars-small128.pb")

encoder = gdet.create_box_encoder(model_filename, batch_size=1)
metric = nn_matching.NearestNeighborDistanceMetric("cosine", max_cosine_distance, nn_budget)
tracker = Tracker(metric, max_age=max_age)

# Ensure processed_data directory exists
if not os.path.exists('processed_data'):
	os.makedirs('processed_data')

# Initialize thread-safe CSV writers
movement_writer = ThreadSafeCSVWriter(
    'processed_data/movement_data.csv',
    ['Track ID', 'Entry time', 'Exit Time', 'Movement Tracks']
)

crowd_writer = ThreadSafeCSVWriter(
    'processed_data/crowd_data.csv',
    ['Time', 'Human Count', 'Social Distance violate', 'Restricted Entry', 'Abnormal Activity']
)

# Start the writer threads
movement_writer.start()
crowd_writer.start()

START_TIME = time.time()

try:
    processing_FPS = video_process(cap, FRAME_SIZE, net, ln, encoder, tracker, movement_writer, crowd_writer)
    cv2.destroyAllWindows()
except KeyboardInterrupt:
    print("\nInterrupted by user. Cleaning up...")
except Exception as e:
    print(f"Error during processing: {e}")
finally:
    # Ensure proper cleanup
    movement_writer.stop()
    crowd_writer.stop()

END_TIME = time.time()
PROCESS_TIME = END_TIME - START_TIME
print("Time elapsed: ", PROCESS_TIME)

if IS_CAM:
	print("Processed FPS: ", processing_FPS)
	VID_FPS = processing_FPS
	DATA_RECORD_FRAME = 1
else:
	print("Processed FPS: ", round(cap.get(cv2.CAP_PROP_FRAME_COUNT) / PROCESS_TIME, 2))
	VID_FPS = cap.get(cv2.CAP_PROP_FPS)
	DATA_RECORD_FRAME = int(VID_FPS / DATA_RECORD_RATE)
	START_TIME = VIDEO_CONFIG["START_TIME"]
	time_elapsed = round(cap.get(cv2.CAP_PROP_FRAME_COUNT) / VID_FPS)
	END_TIME = START_TIME + datetime.timedelta(seconds=time_elapsed)

cap.release()

video_data = {
	"IS_CAM": IS_CAM,
	"DATA_RECORD_FRAME" : DATA_RECORD_FRAME,
	"VID_FPS" : VID_FPS,
	"PROCESSED_FRAME_SIZE": FRAME_SIZE,
	"TRACK_MAX_AGE": TRACK_MAX_AGE,
	"START_TIME": START_TIME.strftime("%d/%m/%Y, %H:%M:%S"),
	"END_TIME": END_TIME.strftime("%d/%m/%Y, %H:%M:%S")
}

# Write video data with proper encoding
with open('processed_data/video_data.json', 'w', encoding='utf-8') as video_data_file:
	json.dump(video_data, video_data_file, indent=2)

print("Processing completed. Data saved to processed_data directory.")