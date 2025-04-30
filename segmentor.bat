@echo off
echo Video Segmentor CLI
echo -----------------
echo.

call venv\Scripts\activate.bat

if "%~1"=="" (
    echo Please provide the path to the video file and segment length in seconds.
    echo.
    echo Usage:
    echo   segmentor.bat path\to\video.mp4 segment_length_in_seconds
    echo.
    echo Example:
    echo   segmentor.bat C:\Videos\my_video.mp4 30
    goto :end
)

if "%~2"=="" (
    echo Please provide the segment length in seconds.
    echo.
    echo Usage:
    echo   segmentor.bat path\to\video.mp4 segment_length_in_seconds
    echo.
    echo Example:
    echo   segmentor.bat C:\Videos\my_video.mp4 30
    goto :end
)

python segmentor.py "%~1" %~2

:end
pause