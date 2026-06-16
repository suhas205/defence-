import streamlit as st
import pandas as pd
import geocoder
import os
from PIL import Image
from mail import send_email, send_alert_image
from ultralytics import YOLO
from pothole_detection import detect_from_image, detect_from_video
import streamlit.components.v1 as components
import subprocess

# Create uploads directory if missing
os.makedirs('uploads', exist_ok=True)

# ----------------------------
# Model selection (Normal vs SAR)
# ----------------------------
MODEL_PATHS = {
    "Normal": r"C:\Users\suhas_t9klwz0\Downloads\best (1).pt",
    "SAR": r"C:\Users\suhas_t9klwz0\Downloads\best (6).pt"
}

@st.cache_resource(show_spinner=False)
def load_model(path):
    return YOLO(path)

# Sidebar menu
page = st.sidebar.selectbox(
    "Pages Menu",
    options=['Home', 'Using Image', 'Using Video', 'Live Camera']
)

# Alert flags
if 'alert_sent_image' not in st.session_state:
    st.session_state.alert_sent_image = False

if 'alert_sent_video' not in st.session_state:
    st.session_state.alert_sent_video = False

# ----------------------------
# Utility Functions
# ----------------------------
def register(location, highway_type, size, position, is_video=False):
    """Send email report."""
    if isinstance(highway_type, (list, tuple)):
        highway_type_str = ", ".join(highway_type) if highway_type else "Unknown"
    else:
        highway_type_str = str(highway_type)

    data = {
        "location": location,
        "highway_type": highway_type_str,
        "size": size,
        "position": position
    }

    send_email(data, 'suhastms2004@gmail.com', is_video)
    st.info("Reported successfully.")

def get_fallback_location():
    g = geocoder.ip('me')
    return g.latlng if g.latlng else [0, 0]

def get_pothole_info():
    location = get_fallback_location()
    st.sidebar.markdown("---")

    highway_type = st.sidebar.multiselect(
        "Target Type(s):",
        ["Ship", "Aircraft", "Tank", "Unknown"]
    )
    size = st.sidebar.selectbox("Approx. Size", ["Small", "Medium", "Large"])
    position = st.sidebar.selectbox("Position in Frame", ["Center", "Edge"])

    return location, highway_type, size, position

def load_image(image_file):
    img = Image.open(image_file)
    img.save("uploads/image.jpg")
    return img

def load_video(video_file):
    with open("uploads/video.mp4", 'wb') as f:
        f.write(video_file.read())

# ----------------------------
# Using Image Page
# ----------------------------
if page == 'Using Image':
    st.title("Image Detection")

    model_choice = st.radio(
        "Select Model",
        list(MODEL_PATHS.keys()),
        index=0,
        horizontal=True
    )

    model = load_model(MODEL_PATHS[model_choice])

    image_file = st.file_uploader("Upload Image", type=['png', 'jpg', 'jpeg'])

    if image_file:
        st.session_state.alert_sent_image = False

        col1, col2 = st.columns(2)
        col1.image(load_image(image_file))

        detections = detect_from_image("uploads/image.jpg", model)
        col2.image("results/image_result.jpg")

        if detections and detections > 0:
            if not st.session_state.alert_sent_image:
                send_alert_image(
                    "results/image_result.jpg",
                    'suhastms2004@gmail.com',
                    subject="Immediate Detection Alert (Image)",
                    body=f"Detected {detections} object(s)."
                )
                st.session_state.alert_sent_image = True

            location, highway_type, size, position = get_pothole_info()
            if st.sidebar.button("Send Mail"):
                register(location, highway_type, size, position)
        else:
            st.warning("No detections found.")

# ----------------------------
# Using Video Page
# ----------------------------
elif page == 'Using Video':
    st.title("Video Detection")

    model_choice = st.radio(
        "Select Model",
        list(MODEL_PATHS.keys()),
        index=0,
        horizontal=True
    )

    model = load_model(MODEL_PATHS[model_choice])

    video_file = st.file_uploader("Upload Video", type=["mp4", "avi", "mkv"])

    if video_file:
        st.session_state.alert_sent_video = False
        load_video(video_file)

        detected = detect_from_video("uploads/video.mp4", model)

        os.system(
            'ffmpeg -i results/video_result.avi '
            '-vcodec libx264 results/processed.mp4 -y'
        )

        st.video("results/processed.mp4")

        if detected:
            if not st.session_state.alert_sent_video:
                send_alert_image(
                    "results/video_alert.jpg",
                    'suhastms2004@gmail.com',
                    subject="Immediate Detection Alert (Video)",
                    body="Detection found in uploaded video."
                )
                st.session_state.alert_sent_video = True

            location, highway_type, size, position = get_pothole_info()
            if st.sidebar.button("Send Mail"):
                register(location, highway_type, size, position, is_video=True)
        else:
            st.warning("No detections found.")

# ----------------------------
# Live Camera Page
# ----------------------------
elif page == 'Live Camera':
    st.title("Live Camera Detection")

    model_choice = st.radio(
        "Select Model",
        list(MODEL_PATHS.keys()),
        index=0,
        horizontal=True
    )

    model_path = MODEL_PATHS[model_choice]

    if 'process' not in st.session_state:
        st.session_state.process = None

    if st.button("Start Detection"):
        if st.session_state.process is None:
            st.session_state.process = subprocess.Popen(
                ["python", "test.py", model_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            st.info("Detection started")

    if st.button("Stop Detection"):
        if st.session_state.process:
            st.session_state.process.terminate()
            st.session_state.process = None
            st.success("Detection stopped")

# ----------------------------
# Home Page
# ----------------------------
else:
    st.title("Military Defense Detection System")
    st.image("image.png", use_column_width=True)
    st.write(
        "AI-powered detection using YOLO for SAR and optical imagery."
    )
