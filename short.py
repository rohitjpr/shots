import streamlit as st
import subprocess
import os
from PIL import Image
import tempfile

# Title of the app
st.set_page_config(page_title="Advanced Video Splitter", layout="wide")
st.title("?? Advanced Video Splitter ??")

# Initialize session state variables
if "input_path" not in st.session_state:
    st.session_state.input_path = None
if "output_path" not in st.session_state:
    st.session_state.output_path = None
if "segment_duration" not in st.session_state:
    st.session_state.segment_duration = 0

# Function to extract thumbnail for video preview
def extract_thumbnail(video_path):
    try:
        temp_dir = tempfile.gettempdir()
        thumbnail_path = os.path.join(temp_dir, "thumbnail.jpg")
        subprocess.run([
            "ffmpeg",
            "-i", video_path,
            "-ss", "00:00:01",  # Extract frame at 1 second
            "-vframes", "1",
            "-y",
            thumbnail_path
        ], check=True)
        return thumbnail_path
    except Exception as e:
        st.error(f"Error extracting thumbnail: {e}")
        return None

# Input Path Selection
st.header("Step 1: Select Input Video")
input_path = st.text_input("Input Video Path")
if st.button("Set Input Path"):
    if os.path.isfile(input_path):
        st.session_state.input_path = input_path
        st.success("Input path set successfully!")
        # Show video preview
        thumbnail = extract_thumbnail(input_path)
        if thumbnail:
            st.image(thumbnail, caption="Video Preview", use_column_width=True)
    else:
        st.error("Invalid input path. Please provide a valid video file.")

# Output Path Selection
st.header("Step 2: Select Output Folder")
output_path = st.text_input("Output Folder Path")
if st.button("Set Output Path"):
    if os.path.isdir(output_path):
        st.session_state.output_path = output_path
        st.success("Output path set successfully!")
    else:
        st.error("Invalid output path. Please provide a valid folder.")

# Segment Duration Selection
st.header("Step 3: Set Segment Duration")
segment_duration = st.number_input("Segment Duration (seconds)", min_value=1, value=300)  # Default 5 minutes
if st.button("Set Segment Duration"):
    st.session_state.segment_duration = segment_duration
    st.success(f"Segment duration set to {segment_duration} seconds.")

# Split Button
st.header("Step 4: Start Splitting")
if st.button("Split Video"):
    if not st.session_state.input_path:
        st.error("Please set a valid input video path.")
    elif not st.session_state.output_path:
        st.error("Please set a valid output folder path.")
    elif st.session_state.segment_duration <= 0:
        st.error("Please set a valid segment duration.")
    else:
        try:
            # Ensure the output path ends with a slash
            output_path = os.path.join(st.session_state.output_path, "")  # Add trailing slash
            output_path = output_path.replace("\\", "/")  # Replace backslashes
            
            # Progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()  # For displaying progress text
            
            # Run FFmpeg command for splitting video into segments
            subprocess.run([
                "ffmpeg",
                "-i", st.session_state.input_path.replace("\\", "/"),
                "-c", "copy",  # Copy codec to maintain quality
                "-map", "0",
                "-segment_time", str(st.session_state.segment_duration),
                "-f", "segment",
                "-reset_timestamps", "1",
                f"{output_path}segment_%03d.mp4"
            ], check=True)
            
            # Update progress bar
            progress_bar.progress(100)
            status_text.text("Processing completed!")
            st.success("Video split successfully! Check the output folder.")
        except subprocess.CalledProcessError as e:
            st.error(f"FFmpeg error: {e}")
        except Exception as e:
            st.error(f"Unexpected error: {e}")

# Advanced Features
st.sidebar.header("Advanced Features")
st.sidebar.markdown("""
- **Fast Processing**: Enabled using `copy` codec in FFmpeg.
- **Quality Maintenance**: Video and audio codecs are copied without re-encoding.
- **Preview**: Thumbnail extracted from the video for preview.
- **Batch Splitting**: Long video is split into multiple segments based on the specified duration.
""")

# Footer
st.markdown("---")
st.markdown("?? **Tip**: Ensure FFmpeg is installed and added to your system's PATH for seamless operation.")