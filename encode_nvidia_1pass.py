import os
import subprocess
import time

# Set your source folder here
source_folder = r"Z:\fast_channels\OTERRA\ENCODE"

# Codec configurations and settings
vcodec = "h264_nvenc"
acodec = "aac"
minrate = "12M"
bitrate = "14M"
maxrate = "15M"
bufsize = "14M"
audio_rate = "320k"
sample_rate = "44100"
frame_size = "1920x1080"
logo_path = "1plus1_wm_2.png"

# Infinite loop to keep the script running
while True:
    # Check every file in the source folder recursively
    for root, _, files in os.walk(source_folder):
        for file in files:
            if file.lower().endswith((".mkv", ".avi", ".mxf", ".mpg")):
                source_file = os.path.join(root, file)
                dest_file = os.path.splitext(source_file)[0] + "_nvidia_1pass_encoded.mp4"
                base_name = os.path.splitext(os.path.basename(source_file))[0]

                # Check if the .mp4 file already exists (meaning another instance is processing it)
                if not os.path.exists(dest_file):
                    print(dest_file)
                    # Get initial file size
                    file_size1 = os.path.getsize(source_file)

                    # Wait for a bit to see if the file is still being written to
                    time.sleep(5)

                    # Get file size again to see if it changed
                    file_size2 = os.path.getsize(source_file)
                    print(file_size1, file_size2)

                    # Check if file size has changed
                    if file_size1 == file_size2:
                        print(f"File {source_file} is ready for processing.")

                        # Check the number of audio streams using ffprobe
                        ffprobe_output = subprocess.check_output(["ffprobe", "-i", source_file, "-show_streams"],
                                                                  stderr=subprocess.STDOUT,
                                                                  universal_newlines=True)
                        audio_streams = sum(1 for line in ffprobe_output.splitlines() if "codec_type=audio" in line)

                        # Check if there is only one audio stream
                        if audio_streams == 1:
                            subprocess.run(["ffmpeg", "-hwaccel", "cuda", "-hwaccel_output_format", "cuda", "-i", source_file,"-write_tmcd", "false",
                                            "-c:v", vcodec, "-b:v", bitrate, "-minrate", minrate, "-maxrate", maxrate, "-bufsize", bufsize,
                                            "-c:a", acodec, "-b:a", audio_rate, "-ar", sample_rate, "-ac", "2", "-n", "-passlogfile",
                                            os.path.join(source_folder, f"{base_name}_ffmpeglog"), dest_file], check=True)
                        else:
                            subprocess.run(["ffmpeg", "-hwaccel", "cuda", "-hwaccel_output_format", "cuda", "-i", source_file,
                                            "-filter_complex", "[0:a:0][0:a:1]amerge=inputs=2[a]", "-write_tmcd", "false", "-map", "0:v",
                                            "-c:v", vcodec, "-b:v", bitrate, "-minrate", minrate, "-maxrate", maxrate, "-bufsize", bufsize,
                                            "-map", "[a]", "-c:a", acodec, "-b:a", audio_rate, "-ar", sample_rate, "-ac", "2", "-n",
                                            "-passlogfile", os.path.join(source_folder, f"{base_name}_ffmpeglog"), dest_file], check=True)

                        print(f"Finished processing: {source_file}")
                    else:
                        print(f"File {source_file} is still uploading.")

    # Wait before checking the folder again
    time.sleep(60)
