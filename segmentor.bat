@echo off
echo Video Segmentor CLI
echo -----------------
echo.

REM Enable ANSI color codes in Windows console
reg query HKCU\Console /v VirtualTerminalLevel >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    reg add HKCU\Console /v VirtualTerminalLevel /t REG_DWORD /d 1 /f >nul 2>&1
)

call venv\Scripts\activate.bat

if "%~1"=="" (
    echo Please provide the path to the video file and segment length in seconds.
    echo.
    echo Usage:
    echo   segmentor.bat path\to\video.mp4 segment_length_in_seconds [options]
    echo.
    echo Options:
    echo   --no-color    Disable colored output
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

REM Pass all arguments to the Python script
python segmentor.py %*

:end
pause