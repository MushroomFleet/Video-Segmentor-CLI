import os
import sys
import subprocess
import argparse
import re
from datetime import datetime

def check_ffmpeg():
    """Check if FFMPEG is installed and available"""
    try:
        subprocess.run(['ffmpeg', '-version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
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
        print(f"Created output directory: {dir_name}")
    else:
        print(f"Using existing directory: {dir_name}")
    
    return dir_name

def segment_video(input_file, segment_length, output_dir):
    """Segment the video into specified lengths"""
    # Get file extension
    _, file_extension = os.path.splitext(input_file)
    
    # Get base filename without extension
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    base_name = sanitize_filename(base_name)
    
    # Generate output pattern for segmented files
    # Format: output_dir/base_name_segment%03d_timestamp.extension
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    segment_pattern = f"{output_dir}/{base_name}_segment%03d_{timestamp}{file_extension}"
    
    print(f"Segmenting video into {segment_length}-second chunks...")
    print(f"Output pattern: {segment_pattern}")
    
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
    
    # Run the command
    try:
        subprocess.run(ffmpeg_segment_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Video segmented successfully.")
        
        # Return list of segmented files
        segmented_files = []
        pattern = f"{re.escape(base_name)}_segment\\d+_{timestamp}{re.escape(file_extension)}"
        for file in os.listdir(output_dir):
            if re.match(pattern, file):
                segmented_files.append(os.path.join(output_dir, file))
        
        print(f"Created {len(segmented_files)} segments.")
        return segmented_files, timestamp
    
    except subprocess.CalledProcessError as e:
        print(f"Error segmenting video: {e}")
        sys.exit(1)

def rescale_segments(segmented_files, output_dir):
    """Rescale the segmented videos to 640x480"""
    rescaled_files = []
    
    print(f"Rescaling {len(segmented_files)} segments to 640x480...")
    
    for file in segmented_files:
        # Get the directory and full filename
        dirname = os.path.dirname(file)
        basename = os.path.basename(file)
        
        # Get the base name and the part containing segment information
        parts = basename.split('_segment')
        if len(parts) >= 2:
            base_part = parts[0]
            segment_part = '_segment'.join(parts[1:])
            
            # Create the new filename with _640 inserted
            new_basename = f"{base_part}_640_segment{segment_part}"
            output_file = os.path.join(dirname, new_basename)
            
            # Command to rescale the video
            ffmpeg_rescale_cmd = [
                'ffmpeg',
                '-i', file,
                '-vf', 'scale=640:480',
                '-c:a', 'copy',  # Copy audio codec
                output_file
            ]
            
            # Run the command
            try:
                subprocess.run(ffmpeg_rescale_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                rescaled_files.append(output_file)
                print(f"Rescaled: {os.path.basename(output_file)}")
            
            except subprocess.CalledProcessError as e:
                print(f"Error rescaling segment {file}: {e}")
    
    return rescaled_files

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Segment and rescale videos using FFMPEG')
    parser.add_argument('input_file', help='Path to the input video file')
    parser.add_argument('segment_length', type=int, help='Length of each segment in seconds')
    
    args = parser.parse_args()
    
    # Check if FFMPEG is installed
    if not check_ffmpeg():
        print("Error: FFMPEG is not installed or not found in the system PATH.")
        print("Please install FFMPEG and make sure it's in your PATH before running this script.")
        sys.exit(1)
    
    # Validate input file
    if not os.path.isfile(args.input_file):
        print(f"Error: The input file '{args.input_file}' does not exist.")
        sys.exit(1)
    
    # Validate segment length
    if args.segment_length <= 0:
        print("Error: Segment length must be a positive integer.")
        sys.exit(1)
    
    print(f"\nVideo Segmentor CLI")
    print(f"===================")
    print(f"Input file: {args.input_file}")
    print(f"Segment length: {args.segment_length} seconds")
    
    # Create output directory
    output_dir = create_output_dir(args.input_file)
    
    # Segment the video
    segmented_files, timestamp = segment_video(args.input_file, args.segment_length, output_dir)
    
    # Rescale the segmented videos
    rescaled_files = rescale_segments(segmented_files, output_dir)
    
    print("\nProcess completed successfully!")
    print(f"Original segments: {len(segmented_files)}")
    print(f"Rescaled segments: {len(rescaled_files)}")
    print(f"All files saved in the '{output_dir}' directory.")
    print(f"Timestamp used for this batch: {timestamp}")

if __name__ == "__main__":
    main()