# Video-Segmentor-CLI

A command-line tool for segmenting videos into specified lengths and rescaling them to 640x480 resolution.

## Features

- Segment videos into clips of specified length (in seconds)
- Automatically rescale segments to 640x480 resolution
- Preserve original video format and codec
- Organized output with timestamp-based naming

## Requirements

- Python 3.6 or higher
- FFMPEG installed and available in your system PATH

**Note:** This tool requires FFMPEG to be installed separately. It is not included in the installation script.

You can download FFMPEG from: https://ffmpeg.org/download.html

After installation, make sure FFMPEG is added to your system PATH.

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/MushroomFleet/Video-Segmentor-CLI.git
   cd Video-Segmentor-CLI
   ```

2. Run the installation script:
   ```
   install.bat
   ```

## Usage

1. Run the segmentor script with the path to your video file and the desired segment length in seconds:
   ```
   segmentor.bat path\to\your\video.mp4 30
   ```
   This will segment the video into 30-second clips.

2. The script will create:
   - A folder with the video's name (spaces replaced with underscores)
   - Original segments in the specified length
   - Rescaled segments (640x480) with "_640" added to the filename

## Output Format

The segmented files will follow this naming pattern:
- Original segments: `video_name_segmentXXX_YYYYMMDD_HHMMSS.ext`
- Rescaled segments: `video_name_640_segmentXXX_YYYYMMDD_HHMMSS.ext`

Where:
- `XXX` is the segment number (starting from 000)
- `YYYYMMDD_HHMMSS` is the timestamp when the segmentation was performed
- `.ext` is the original file extension

## Examples

### Example 1: Segment a video into 30-second clips
```
segmentor.bat C:\Videos\my video.mp4 30
```

This will:
1. Create a folder named `my_video`
2. Generate segments like:
   - `my_video_segment000_20230405_123456.mp4`
   - `my_video_segment001_20230405_123456.mp4`
   - ...
3. Create rescaled versions:
   - `my_video_640_segment000_20230405_123456.mp4`
   - `my_video_640_segment001_20230405_123456.mp4`
   - ...

## Repository

This project is maintained on GitHub: [https://github.com/MushroomFleet/Video-Segmentor-CLI](https://github.com/MushroomFleet/Video-Segmentor-CLI)