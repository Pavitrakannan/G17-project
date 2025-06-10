import datetime

# Video Path
#VIDEO_CONFIG = {
#	"VIDEO_CAP" : "kapaleshwar.mp4",
#	"IS_CAM" : False,
#	"CAM_APPROX_FPS": 3,
#	"HIGH_CAM": False,
#	"START_TIME": datetime.datetime(2020, 11, 5, 0, 0, 0, 0)
#}
# Configuration file for crowd monitoring system
import datetime

# YOLO Configuration
YOLO_CONFIG = {
    "WEIGHTS_PATH": "yolo_weights/yolov3-tiny.weights",
    "CONFIG_PATH": "yolo_config/yolov3-tiny.cfg",
    "CONFIDENCE_THRESHOLD": 0.5,
    "NMS_THRESHOLD": 0.4
}

# Video Configuration
VIDEO_CONFIG = {
    "IS_CAM": False,
    "VIDEO_CAP": "sample_video.mp4",  # Default video file
    "CAM_APPROX_FPS": 30,
    "START_TIME": datetime.datetime(2020, 5, 11, 0, 0, 0),
    "END_TIME": datetime.datetime(2020, 5, 11, 0, 0, 9)
}

# Processing Configuration
SHOW_PROCESSING_OUTPUT = True
DATA_RECORD_RATE = 5  # Records per second
FRAME_SIZE = 1080     # Processing frame size
TRACK_MAX_AGE = 3     # Maximum age for tracking objects

# File encoding settings
FILE_ENCODING = 'utf-8'

# Dashboard Configuration
DASHBOARD_CONFIG = {
    "UPDATE_INTERVAL": 2,  # seconds
    "CROWD_ALERT_THRESHOLD": 10,
    "PORT": 5000,
    "HOST": "0.0.0.0"
}

# Safety thresholds
SAFETY_THRESHOLDS = {
    "MAX_CROWD_COUNT": 15,
    "SOCIAL_DISTANCE_LIMIT": 5,
    "ABNORMAL_ACTIVITY_LIMIT": 3
}

# Video Path
VIDEO_CONFIG = {
    "VIDEO_CAP" : 0,  # 0 for default webcam, 1 for external webcam if available
    "IS_CAM" : True,
    "CAM_APPROX_FPS": 30,  # Adjust based on your webcam's capabilities
    "HIGH_CAM": False,  # Set to True if camera is mounted overhead
    "START_TIME": datetime.datetime.now()  # Use current time
}

# Load YOLOv3-tiny weights and config
YOLO_CONFIG = {
	"WEIGHTS_PATH" : "YOLOv4-tiny/yolov4-tiny.weights",
	"CONFIG_PATH" : "YOLOv4-tiny/yolov4-tiny.cfg"
}
# Show individuals detected
SHOW_PROCESSING_OUTPUT = True
# Show individuals detected
SHOW_DETECT = True
# Data record
DATA_RECORD = True
# Data record rate (data record per frame)
DATA_RECORD_RATE = 5
# Check for restricted entry
RE_CHECK = False
# Restricted entry time (H:M:S)
RE_START_TIME = datetime.time(0,0,0) 
RE_END_TIME = datetime.time(23,0,0)
# Check for social distance violation
SD_CHECK = False
# Show violation count
SHOW_VIOLATION_COUNT = False
# Show tracking id
SHOW_TRACKING_ID = False
# Threshold for distance violation
SOCIAL_DISTANCE = 50
# Check for abnormal crowd activity
ABNORMAL_CHECK = True
# Min number of people to check for abnormal
ABNORMAL_MIN_PEOPLE = 5
# Abnormal energy level threshold
ABNORMAL_ENERGY = 1866
# Abnormal activity ratio threhold
ABNORMAL_THRESH = 0.66
# Threshold for human detection minumun confindence
MIN_CONF = 0.3
# Threshold for Non-maxima surpression
NMS_THRESH = 0.2
# Resize frame for processing
FRAME_SIZE = 1080
# Tracker max missing age before removing (seconds)
TRACK_MAX_AGE = 3