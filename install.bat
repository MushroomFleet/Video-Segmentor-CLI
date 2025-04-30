@echo off
echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing required packages...
pip install -r requirements.txt

echo.
echo Installation complete!
echo.
echo NOTE: For best performance, a system FFMPEG installation is recommended.
echo If you don't have FFMPEG installed, the tool will attempt to:
echo 1. Use system FFMPEG if available (fastest)
echo 2. Fall back to ffmpeg-python package
echo 3. Fall back to imageio-ffmpeg (which can download binaries automatically)
echo.
echo If you want to install FFMPEG system-wide, download it from:
echo https://ffmpeg.org/download.html
echo and make sure it's added to your system PATH.
echo.
echo You can now use segmentor.bat to segment and rescale your videos.
pause