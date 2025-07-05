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
    echo Please provide either a video file or use --dir for batch processing.
    echo.
    echo Usage:
    echo   Single file: segmentor.bat path\to\video.mp4 segment_length_in_seconds [options]
    echo   Batch mode:  segmentor.bat --dir path\to\directory segment_length_in_seconds [options]
    echo.
    echo Options:
    echo   --no-color    Disable colored output
    echo.
    echo Examples:
    echo   segmentor.bat C:\Videos\my_video.mp4 30
    echo   segmentor.bat --dir C:\Videos\batch_folder 30
    goto :end
)

REM Check if first argument is --dir (batch mode)
if "%~1"=="--dir" (
    if "%~2"=="" (
        echo Please provide the directory path for batch processing.
        echo.
        echo Usage:
        echo   segmentor.bat --dir path\to\directory segment_length_in_seconds
        echo.
        echo Example:
        echo   segmentor.bat --dir C:\Videos\batch_folder 30
        goto :end
    )
    if "%~3"=="" (
        echo Please provide the segment length in seconds.
        echo.
        echo Usage:
        echo   segmentor.bat --dir path\to\directory segment_length_in_seconds
        echo.
        echo Example:
        echo   segmentor.bat --dir C:\Videos\batch_folder 30
        goto :end
    )
) else (
    REM Single file mode validation
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
)

REM Pass all arguments to the Python script
python segmentor.py %*

:end
pause
