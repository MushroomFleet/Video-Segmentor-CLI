# Video-Segmentor-CLI

A command-line tool for segmenting videos into specified lengths and rescaling them to 640x480 resolution.

![Example Screenshot](https://via.placeholder.com/800x400?text=Video+Segmentor+CLI)

## Features

- Segment videos into clips of specified length (in seconds)
- Automatically rescale segments to 640x480 resolution
- Preserve original video format and codec
- Organized output with timestamp-based naming
- Real-time progress bars and colorized terminal output
- Detailed video information display
- Automatic FFMPEG installation (fallback to Python-based alternatives)

## Requirements

- Python 3.6 or higher
- FFMPEG (one of the following options):
  - System-wide FFMPEG installation (recommended for best performance)
  - Python packages will be installed as fallbacks via requirements.txt

**Note about FFMPEG:**
The tool will first try to use system-installed FFMPEG. If not found, it will automatically fall back to Python-based alternatives:
1. First fallback: `ffmpeg-python` package
2. Second fallback: `imageio-ffmpeg` package (can download binaries automatically)

For best performance, we still recommend installing FFMPEG system-wide:
- Download from: https://ffmpeg.org/download.html
- Make sure to add it to your system PATH

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

### Single File Mode

1. Run the segmentor script with the path to your video file and the desired segment length in seconds:
   ```
   segmentor.bat path\to\your\video.mp4 30
   ```
   This will segment the video into 30-second clips.

2. The script will create:
   - A folder with the video's name (spaces replaced with underscores)
   - Original segments in the specified length
   - Rescaled segments (640x480) with "_640" added to the filename

### Batch Directory Mode

1. Run the segmentor script with the `--dir` flag to process all MP4 files in a directory:
   ```
   segmentor.bat --dir path\to\your\directory 30
   ```
   This will segment all MP4 files found in the directory into 30-second clips.

2. The script will create:
   - A timestamped batch output directory (e.g., `batch_output_20231205_143022`)
   - Individual folders for each video (same as single file mode)
   - A batch summary file with processing results and statistics

### Command-line Options

**Single File Mode:**
```
segmentor.bat path\to\video.mp4 segment_length_in_seconds [options]
```

**Batch Directory Mode:**
```
segmentor.bat --dir path\to\directory segment_length_in_seconds [options]
```

Available options:
- `--no-color`: Disable colored terminal output

## Output Format

The segmented files will follow this naming pattern:
- Original segments: `video_name_segmentXXX_YYYYMMDD_HHMMSS.ext`
- Rescaled segments: `video_name_640_segmentXXX_YYYYMMDD_HHMMSS.ext`

Where:
- `XXX` is the segment number (starting from 000)
- `YYYYMMDD_HHMMSS` is the timestamp when the segmentation was performed
- `.ext` is the original file extension

## Progress Tracking

The CLI provides detailed progress information during processing:
- Video information (duration, resolution, bitrate)
- Real-time progress bars for segmentation and rescaling
- Colorized output for better readability
- Summary statistics after completion (file sizes, processing time)

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

### Example 2: Batch process multiple videos
```
segmentor.bat --dir C:\Videos\batch_folder 30
```

This will:
1. Scan `C:\Videos\batch_folder` for all MP4 files
2. Create a timestamped batch output directory (e.g., `batch_output_20231205_143022`)
3. Process each video into 30-second segments
4. Generate individual folders for each video within the batch directory
5. Create a batch summary file with processing statistics

### Example 3: Segment a video with disabled color output
```
segmentor.bat C:\Videos\my video.mp4 60 --no-color
```

This will process the video with 60-second segments and display output without colors (useful for terminals that don't support ANSI colors).

### Example 4: Batch process with disabled color output
```
segmentor.bat --dir C:\Videos\batch_folder 45 --no-color
```

This will batch process all MP4 files in the directory with 45-second segments and disable colored terminal output.

## Batch Processing Features

When using batch directory mode (`--dir`), you get additional features:

- **Robust error handling**: If one video fails, processing continues with the remaining videos
- **Progress tracking**: Shows overall batch progress (e.g., "Processing video 3 of 7") plus individual video progress
- **Comprehensive reporting**: Creates a detailed batch summary file with:
  - Total processing time
  - Success/failure counts
  - List of successfully processed videos
  - List of failed videos (if any)
- **Organized output**: All results are contained in a timestamped batch directory
- **Parallel-friendly**: Each video gets its own subdirectory, preventing file conflicts

## Repository

This project is maintained on GitHub: [https://github.com/MushroomFleet/Video-Segmentor-CLI](https://github.com/MushroomFleet/Video-Segmentor-CLI)
