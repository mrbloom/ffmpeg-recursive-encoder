@echo off
setlocal enabledelayedexpansion

:: Set your source folder here
set "sourceFolder=Z:\fast_channels\OTERRA\ENCODE"

:: Codec configurations and settings
set "vCodec=h264"
set "aCodec=aac"
set "bitrate=15M"
set "audioRate=320k"
set "sampleRate=44100"
set "frameSize=1920x1080"

:: Infinite loop to keep the script running
:loop

:: Check every file in the source folder recursively
for /R "%sourceFolder%" %%i in (*.mkv, *.avi, *.mxf) do (
    :: Construct the output file path
    set "destFile=%%~dpni_cpu_encoded.mp4"
    
    
    :: Check if the .mp4 file already exists (meaning another instance is processing it)
    if not exist "!destFile!" (
        echo !destFile!
        :: Get initial file size
        set fileSize1=%%~zi

        :: Wait for a bit to see if the file is still being written to
        timeout /t 5 /nobreak > nul


        :: Get file size again to see if it changed
        set fileSize2=%%~zi

        echo !fileSize1! !fileSize2!
        
        :: Check if file size has changed
        if !fileSize1! equ !fileSize2! (
            echo File "%%i" is ready for processing.            
           
            ffmpeg -i "%%i" -c:v %vCodec% -b:v %bitrate% -map 0:v:0 -filter_complex "[0:a:0][0:a:1]amerge=inputs=2[a]" -map "[a]" -c:a %aCodec% -b:a %audioRate% -ar %sampleRate% -ac 2 "!destFile!"


            echo Finished processing: "%%i"
        ) else (
            echo File "%%i" is still uploading.
        )


    )
)

:: Wait before checking the folder again
timeout /t 60

goto loop
