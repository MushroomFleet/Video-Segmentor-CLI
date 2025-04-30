import os
import sys
import subprocess
import argparse
import re
import importlib
import shutil
import time
from datetime import datetime
from pathlib import Path
from tqdm import tqdm
import colorama
from colorama import Fore, Back, Style

# Initialize colorama
colorama.init(autoreset=True)

# Global variables
USE_SYSTEM_FFMPEG = True
FFMPEG_PYTHON = None
IMAGEIO_FFMPEG = None

def print_header():
    """Print a stylish header for the application"""
    print(f"\n{Fore.CYAN}{'=' * 60}")
    print(f"{Fore.CYAN}{Style.BRIGHT}                 VIDEO SEGMENTOR CLI")
    print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}\n")

def print_success(message):
    """Print a success message"""
    print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")

def print_info(message):
    """Print an info message"""
    print(f"{Fore.BLUE}ℹ {message}{Style.RESET_ALL}")

def print_warning(message):
    """Print a warning message"""
    print(f"{Fore.YELLOW}⚠ {message}{Style.RESET_ALL}")

def print_error(message):
    """Print an error message"""
    print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")

def print_step(step_number, total_steps, description):
    """Print a step indicator"""
    print(f"{Fore.CYAN}[{step_number}/{total_steps}] {description}{Style.RESET_ALL}")

def check_ffmpeg():
    """Check if FFMPEG is installed and available, setup fallbacks if needed"""
    global USE_SYSTEM_FFMPEG, FFMPEG_PYTHON, IMAGEIO_FFMPEG
    
    print_info("Checking for FFMPEG installation...")
    
    # First, check if system FFMPEG is available
    try:
        result = subprocess.run(['ffmpeg', '-version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        version_output = result.stdout.decode('utf-8').split('\n')[0]
        print_success(f"System FFMPEG found: {version_output}")
        USE_SYSTEM_FFMPEG = True
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_warning("System FFMPEG not found. Checking for Python alternatives...")
        USE_SYSTEM_FFMPEG = False
    
    # Try to import ffmpeg-python
    try:
        import ffmpeg
        FFMPEG_PYTHON = ffmpeg
        
        # Verify ffmpeg-python can find an ffmpeg binary
        try:
            # Try to get ffmpeg version through ffmpeg-python
            ffmpeg.input(os.devnull).output('-', f='null').run(capture_stdout=True, capture_stderr=True)
            print_success("Using ffmpeg-python package as fallback.")
            return True
        except ffmpeg.Error as e:
            print_warning("ffmpeg-python found but couldn't access FFMPEG binary.")
    except ImportError:
        print_warning("ffmpeg-python package not found.")
    
    # Try to use imageio-ffmpeg which can download binaries
    try:
        import imageio_ffmpeg
        IMAGEIO_FFMPEG = imageio_ffmpeg
        
        # This will trigger download if needed
        with tqdm(total=1, desc="Setting up imageio-ffmpeg", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}") as pbar:
            ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
            pbar.update(1)
        
        if os.path.exists(ffmpeg_path):
            print_success(f"Using imageio-ffmpeg at: {ffmpeg_path}")
            
            # Add the directory containing ffmpeg to the PATH
            os.environ["PATH"] = os.path.dirname(ffmpeg_path) + os.pathsep + os.environ["PATH"]
            USE_SYSTEM_FFMPEG = True  # We'll use subprocess with the updated PATH
            return True
    except ImportError:
        print_warning("imageio-ffmpeg package not found.")
    
    # If we got here, we couldn't find any working FFMPEG
    print_error("No working FFMPEG installation found.")
    print_info("Please either:")
    print(f"{Fore.YELLOW}  1. Install FFMPEG system-wide and add it to your PATH")
    print(f"{Fore.YELLOW}  2. Ensure ffmpeg-python or imageio-ffmpeg packages are installed with pip")
    return False

def sanitize_filename(filename):
    """Replace spaces with underscores in the filename"""
    return filename.replace(' ', '_')

def create_output_dir(input_file):
    """Create an output directory based on the input filename"""
    # Get the base filename without extension
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    
    # Create a directory name by sanitizing the base filename
    dir_name = sanitize_filename(base_name)
    
    # Create the directory if it doesn't exist
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
        print_success(f"Created output directory: {dir_name}")
    else:
        print_info(f"Using existing directory: {dir_name}")
    
    return dir_name

def get_video_info(input_file):
    """Get video duration and other information"""
    try:
        # Get duration
        duration_cmd = [
            'ffprobe', 
            '-v', 'error', 
            '-show_entries', 'format=duration', 
            '-of', 'default=noprint_wrappers=1:nokey=1', 
            input_file
        ]
        duration = float(subprocess.check_output(duration_cmd).decode('utf-8').strip())
        
        # Get resolution
        resolution_cmd = [
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height',
            '-of', 'csv=s=x:p=0',
            input_file
        ]
        resolution = subprocess.check_output(resolution_cmd).decode('utf-8').strip()
        
        # Get bitrate
        bitrate_cmd = [
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=bit_rate',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            input_file
        ]
        try:
            bitrate = int(subprocess.check_output(bitrate_cmd).decode('utf-8').strip()) // 1000
            bitrate_str = f"{bitrate} kbps"
        except:
            bitrate_str = "Unknown"
        
        return {
            'duration': duration,
            'resolution': resolution,
            'bitrate': bitrate_str
        }
    except:
        # Return defaults if we can't get info
        return {
            'duration': 0,
            'resolution': 'Unknown',
            'bitrate': 'Unknown'
        }

def segment_video(input_file, segment_length, output_dir):
    """Segment the video into specified lengths"""
    global USE_SYSTEM_FFMPEG, FFMPEG_PYTHON
    
    # Get file extension
    _, file_extension = os.path.splitext(input_file)
    
    # Get base filename without extension
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    base_name = sanitize_filename(base_name)
    
    # Generate output pattern for segmented files
    # Format: output_dir/base_name_segment%03d_timestamp.extension
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    segment_pattern = f"{output_dir}/{base_name}_segment%03d_{timestamp}{file_extension}"
    
    print_step(1, 2, f"Segmenting video into {segment_length}-second chunks")
    print_info(f"Output pattern: {segment_pattern}")
    
    # Get video info
    print_info("Analyzing video file...")
    with tqdm(total=1, desc="Reading video metadata", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}") as pbar:
        video_info = get_video_info(input_file)
        pbar.update(1)
    
    # Display video information
    duration = video_info['duration']
    if duration > 0:
        hours, remainder = divmod(duration, 3600)
        minutes, seconds = divmod(remainder, 60)
        duration_str = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
        expected_segments = int(duration / segment_length) + 1
        
        print(f"\n{Fore.CYAN}Video Information:{Style.RESET_ALL}")
        print(f"  {Fore.CYAN}Duration:{Style.RESET_ALL} {duration_str}")
        print(f"  {Fore.CYAN}Resolution:{Style.RESET_ALL} {video_info['resolution']}")
        print(f"  {Fore.CYAN}Bitrate:{Style.RESET_ALL} {video_info['bitrate']}")
        print(f"  {Fore.CYAN}Expected segments:{Style.RESET_ALL} ~{expected_segments}")
        print()
    else:
        expected_segments = None
        print_warning("Could not determine video duration. Proceeding without progress estimation.")
    
    # Create a custom progress class for FFMPEG output
    class FFmpegProgressBar:
        def __init__(self, total_duration):
            self.total_duration = total_duration
            self.pbar = tqdm(total=100, desc="Segmenting video", unit="%", 
                             bar_format="{l_bar}{bar}| {n:.1f}% [{elapsed}<{remaining}]")
            self.last_time = 0
            
        def update(self, time_position):
            if self.total_duration > 0:
                progress = min(100, (time_position / self.total_duration) * 100)
                self.pbar.update(progress - self.last_time)
                self.last_time = progress
                
        def close(self):
            self.pbar.close()
    
    # Function to parse FFMPEG output for progress
    def parse_ffmpeg_progress(line, progress_bar):
        if "time=" in line:
            time_match = re.search(r'time=(\d+):(\d+):(\d+)', line)
            if time_match:
                h, m, s = map(int, time_match.groups())
                time_seconds = h * 3600 + m * 60 + s
                progress_bar.update(time_seconds)
    
    # Segment the video
    if USE_SYSTEM_FFMPEG:
        # Command to segment the video using ffmpeg
        ffmpeg_segment_cmd = [
            'ffmpeg',
            '-i', input_file,
            '-c', 'copy',  # Copy codecs to avoid re-encoding
            '-map', '0',
            '-segment_time', str(segment_length),
            '-f', 'segment',
            '-reset_timestamps', '1',
            segment_pattern
        ]
        
        # Run the command with progress tracking
        try:
            print_info("Starting segmentation. This may take a while for large videos...")
            
            if duration > 0:
                progress_bar = FFmpegProgressBar(duration)
                
                process = subprocess.Popen(
                    ffmpeg_segment_cmd, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    bufsize=1
                )
                
                # Read the output line by line and update progress
                for line in iter(process.stdout.readline, ''):
                    parse_ffmpeg_progress(line, progress_bar)
                
                # Ensure the progress bar finishes at 100%
                progress_bar.last_time = 0
                progress_bar.update(duration)
                progress_bar.close()
                process.wait()
                
                if process.returncode != 0:
                    print_error(f"Error during segmentation (return code {process.returncode})")
                    sys.exit(1)
            else:
                # If we couldn't determine duration, run without progress tracking
                with tqdm(total=0, desc="Segmenting video", bar_format="{desc}: {elapsed}") as pbar:
                    process = subprocess.run(ffmpeg_segment_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            print_success("Video segmented successfully.")
            
        except subprocess.CalledProcessError as e:
            print_error(f"Error segmenting video: {e}")
            sys.exit(1)
    
    elif FFMPEG_PYTHON is not None:
        # Use ffmpeg-python as fallback
        try:
            import ffmpeg
            
            # Create the segment command with ffmpeg-python
            stream = ffmpeg.input(input_file)
            stream = ffmpeg.output(
                stream, 
                segment_pattern,
                c='copy',
                map='0',
                segment_time=str(segment_length),
                f='segment',
                reset_timestamps=1
            )
            
            print_info("Starting segmentation using ffmpeg-python. This may take a while...")
            
            # With ffmpeg-python, we can't easily track progress, so use an indeterminate progress bar
            with tqdm(total=0, desc="Segmenting with ffmpeg-python", bar_format="{desc}: {elapsed}") as pbar:
                ffmpeg.run(stream, capture_stdout=True, capture_stderr=True)
            
            print_success("Video segmented successfully using ffmpeg-python.")
            
        except Exception as e:
            print_error(f"Error segmenting video with ffmpeg-python: {e}")
            sys.exit(1)
    
    else:
        print_error("No FFMPEG implementation available for segmentation.")
        sys.exit(1)
    
    # Return list of segmented files
    segmented_files = []
    pattern = f"{re.escape(base_name)}_segment\\d+_{timestamp}{re.escape(file_extension)}"
    
    # Find segmented files with progress bar
    with tqdm(desc="Collecting segment files", unit="files") as pbar:
        for file in os.listdir(output_dir):
            if re.match(pattern, file):
                segmented_files.append(os.path.join(output_dir, file))
                pbar.update(1)
    
    print_success(f"Created {len(segmented_files)} segments.")
    return segmented_files, timestamp

def rescale_segments(segmented_files, output_dir):
    """Rescale the segmented videos to 640x480"""
    global USE_SYSTEM_FFMPEG, FFMPEG_PYTHON
    
    rescaled_files = []
    
    print_step(2, 2, f"Rescaling {len(segmented_files)} segments to 640x480")
    
    # Custom progress formatting for tqdm
    bar_format = "{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]"
    
    # Calculate total file size for progress tracking
    total_size = sum(os.path.getsize(file) for file in segmented_files)
    print_info(f"Total size to process: {total_size / (1024*1024):.2f} MB")
    
    success_count = 0
    error_count = 0
    
    # Use progress bar for better user experience
    with tqdm(segmented_files, desc="Rescaling segments", unit="file", bar_format=bar_format) as pbar:
        for file in pbar:
            # Get the directory and full filename
            dirname = os.path.dirname(file)
            basename = os.path.basename(file)
            
            # Set the current filename in the progress bar description
            pbar.set_description(f"Rescaling {basename}")
            
            # Get the base name and the part containing segment information
            parts = basename.split('_segment')
            if len(parts) >= 2:
                base_part = parts[0]
                segment_part = '_segment'.join(parts[1:])
                
                # Create the new filename with _640 inserted
                new_basename = f"{base_part}_640_segment{segment_part}"
                output_file = os.path.join(dirname, new_basename)
                
                if USE_SYSTEM_FFMPEG:
                    # Command to rescale the video using system FFMPEG
                    ffmpeg_rescale_cmd = [
                        'ffmpeg',
                        '-i', file,
                        '-vf', 'scale=640:480',
                        '-c:a', 'copy',  # Copy audio codec
                        '-y',  # Overwrite output files
                        '-v', 'quiet',  # Reduce output verbosity
                        '-stats',       # Show stats
                        output_file
                    ]
                    
                    # Run the command
                    try:
                        process = subprocess.run(ffmpeg_rescale_cmd, check=True, 
                                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        rescaled_files.append(output_file)
                        success_count += 1
                    except subprocess.CalledProcessError as e:
                        print_warning(f"\nError rescaling segment {basename}: {e}")
                        error_count += 1
                
                elif FFMPEG_PYTHON is not None:
                    # Use ffmpeg-python as fallback
                    try:
                        import ffmpeg
                        
                        # Create the rescale command with ffmpeg-python
                        stream = ffmpeg.input(file)
                        stream = ffmpeg.output(
                            stream,
                            output_file,
                            vf='scale=640:480',
                            **{'c:a': 'copy'}  # Copy audio codec
                        )
                        
                        ffmpeg.run(stream, capture_stdout=True, capture_stderr=True, overwrite_output=True, quiet=True)
                        rescaled_files.append(output_file)
                        success_count += 1
                    except Exception as e:
                        print_warning(f"\nError rescaling segment {basename} with ffmpeg-python: {e}")
                        error_count += 1
                
                else:
                    print_warning(f"\nSkipping rescale of {basename} - no FFMPEG implementation available")
                    error_count += 1
    
    # Print summary
    if success_count == len(segmented_files):
        print_success(f"Successfully rescaled all {success_count} segments.")
    else:
        print_info(f"Rescaling complete: {success_count} successful, {error_count} failed.")
    
    return rescaled_files

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Segment and rescale videos using FFMPEG')
    parser.add_argument('input_file', help='Path to the input video file')
    parser.add_argument('segment_length', type=int, help='Length of each segment in seconds')
    parser.add_argument('--no-color', action='store_true', help='Disable colored output')
    
    args = parser.parse_args()
    
    # Check if we should disable color output
    if args.no_color:
        colorama.deinit()
    
    # Print the header
    print_header()
    
    # Check if FFMPEG is installed
    if not check_ffmpeg():
        print_error("FFMPEG is not installed or not found.")
        print_info("Please install FFMPEG and make sure it's in your PATH before running this script.")
        sys.exit(1)
    
    # Validate input file
    if not os.path.isfile(args.input_file):
        print_error(f"The input file '{args.input_file}' does not exist.")
        sys.exit(1)
    
    # Validate segment length
    if args.segment_length <= 0:
        print_error("Segment length must be a positive integer.")
        sys.exit(1)
    
    # Display input information
    input_size_mb = os.path.getsize(args.input_file) / (1024*1024)
    
    print(f"\n{Fore.CYAN}Input Information:{Style.RESET_ALL}")
    print(f"  {Fore.CYAN}File:{Style.RESET_ALL} {args.input_file}")
    print(f"  {Fore.CYAN}Size:{Style.RESET_ALL} {input_size_mb:.2f} MB")
    print(f"  {Fore.CYAN}Segment length:{Style.RESET_ALL} {args.segment_length} seconds")
    
    # Record start time
    start_time = time.time()
    
    # Create output directory
    output_dir = create_output_dir(args.input_file)
    
    # Segment the video
    segmented_files, timestamp = segment_video(args.input_file, args.segment_length, output_dir)
    
    # Rescale the segmented videos
    rescaled_files = rescale_segments(segmented_files, output_dir)
    
    # Calculate processing time
    elapsed_time = time.time() - start_time
    minutes, seconds = divmod(elapsed_time, 60)
    
    # Print the final summary with styling
    print(f"\n{Fore.GREEN}{Style.BRIGHT}Process completed successfully!{Style.RESET_ALL}")
    print(f"\n{Fore.CYAN}Summary:{Style.RESET_ALL}")
    print(f"  {Fore.CYAN}Original segments:{Style.RESET_ALL} {len(segmented_files)}")
    print(f"  {Fore.CYAN}Rescaled segments:{Style.RESET_ALL} {len(rescaled_files)}")
    print(f"  {Fore.CYAN}Processing time:{Style.RESET_ALL} {int(minutes)}m {int(seconds)}s")
    print(f"  {Fore.CYAN}Output location:{Style.RESET_ALL} {os.path.abspath(output_dir)}")
    print(f"  {Fore.CYAN}Timestamp used:{Style.RESET_ALL} {timestamp}")
    
    # Calculate total output size
    try:
        original_size = sum(os.path.getsize(f) for f in segmented_files) / (1024*1024)
        rescaled_size = sum(os.path.getsize(f) for f in rescaled_files) / (1024*1024)
        total_size = original_size + rescaled_size
        
        print(f"  {Fore.CYAN}Original segments size:{Style.RESET_ALL} {original_size:.2f} MB")
        print(f"  {Fore.CYAN}Rescaled segments size:{Style.RESET_ALL} {rescaled_size:.2f} MB")
        print(f"  {Fore.CYAN}Total output size:{Style.RESET_ALL} {total_size:.2f} MB")
        
        # Calculate compression/expansion ratio
        ratio = total_size / input_size_mb
        print(f"  {Fore.CYAN}Size ratio (output/input):{Style.RESET_ALL} {ratio:.2f}x")
    except:
        # Skip size calculation if there's an error
        pass
    
    print(f"\n{Fore.BLUE}Files saved in: {Style.BRIGHT}{os.path.abspath(output_dir)}{Style.RESET_ALL}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Process interrupted by user.{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Fore.RED}An unexpected error occurred: {e}{Style.RESET_ALL}")
        sys.exit(1)