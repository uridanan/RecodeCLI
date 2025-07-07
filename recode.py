import subprocess
import os
import time
import argparse
import logging

# Set up logger to output to a file
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("recode.log", mode="a", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Ensure FFmpeg is installed and available in the system PATH
# If FFmpeg is not in PATH, provide the full path to the ffmpeg executable
# Example: FFMPEG_EXECUTABLE = "C:/Program Files/ffmpeg/bin/ffmpeg.exe"
# Example: FFMPEG_EXECUTABLE = "ffmpeg" (if it's in your PATH)
FFMPEG_EXECUTABLE = "C:/Program Files/ffmpeg/bin/ffmpeg.exe"  # Ensure ffmpeg is in your PATH or provide full path

def recode_with_ffmpeg(input_file, output_file, audio_bitrate="192k", scale=None, force_overwrite=True, quality_crf=23, preset="medium"):
    """
    Recodes a video to MP4 (H.264/AAC 2.1) using FFmpeg.

    Args:
        input_file (str): Path to the input video file.
        output_file (str): Path for the output recoded video file.
        quality_crf (int): Constant Rate Factor for video quality (lower is better, e.g., 18-24).
        audio_bitrate (str): Audio bitrate (e.g., "192k", "128k").
        preset (str): x264 preset (e.g., "medium", "slow", "fast").
        force_overwrite (bool): If True, overwrite output file without prompt.
    """
    if not os.path.exists(input_file):
        logger.error(f"Error: Input file not found at {input_file}")
        return
    
    # Check if input_file is a video file by extension
    video_extensions = ('.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv', '.webm', '.mpeg', '.mpg', '.m4v')
    if not input_file.lower().endswith(video_extensions):
        logger.debug(f"Skipped: {input_file} is not a recognized video file.")
        return


    # Base FFmpeg command
    command = [
        "ffmpeg",
        "-i", input_file,
        "-c:v", "libx264",
        "-crf", str(quality_crf),
        "-preset", preset,
        "-c:a", "aac",
        "-ac", "2", # 2 audio channels (stereo)
        "-b:a", audio_bitrate
    ]

    # Video filter for scaling
    if scale is not None:
        command.append("-vf")
        command.append("scale="+scale)
        logger.debug(f"Scaling video to: {scale}")

    command.append(output_file)

    if force_overwrite:
        command.insert(1, "-y") # Insert -y right after 'ffmpeg'

    logger.debug(f"Starting recoding for: {input_file}")
    logger.debug(f"Output file will be: {output_file}")
    command_str = ""
    for c in command: 
        command_str += c + ' '   

    try:
        logger.debug(f"{ command_str.strip() }")
        logger.info(f"START: { input_file } -> { output_file }  ")
        start = time.time()
        subprocess.run(command, check=True)
        end = time.time()
        elapsed_time = format_time(end - start)
        logger.info(f"Recoding completed in: {elapsed_time}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error during FFmpeg recoding for {input_file}:")
        logger.error(f"Command: {' '.join(e.cmd)}")
        logger.error(e.stderr.decode() if e.stderr else "")
    except FileNotFoundError:
        logger.error("Error: FFmpeg executable not found.")
        logger.error("Please ensure FFmpeg is installed and its executable is in your system's PATH.")

def format_time(x):
    elapsed_time = int(x)
    hours = elapsed_time // 3600
    minutes = (elapsed_time % 3600) // 60
    seconds = elapsed_time % 60

    elapsed_time_str = f"{hours:02}:{minutes:02}:{seconds:02}"
    return elapsed_time_str

def parse_arguments():
    parser = argparse.ArgumentParser(description="Automate video recoding to MP4/AAC with FFmpeg.")
    parser.add_argument("input_file", help="Path to the input video file.")
    parser.add_argument("--t", help="Desired path for the output recoded video file.")
    parser.add_argument("--scale", help="scale (e.g., '1080p', '720p').")
    parser.add_argument("--abr", default="192k",
                        help="Audio bitrate (e.g., '128k', '192k', '256k'). Default: 192k")
    parser.add_argument("--no-overwrite", action="store_false", dest="force_overwrite",
                        help="Do not overwrite output file if it exists (FFmpeg will prompt).")
    parser.add_argument("--d", action="store_true", dest="delete_input",
                        help="Delete source file when done.")
    parser.add_argument("--51", action="store_true", dest="surround",
                        help="Delete source file when done.")
    args = parser.parse_args()
    return args

def validate_and_interpret_args(args):
    final_args = {}

    # Make sure there is a valid input file
    if args.input_file is None or args.input_file == "":
        logger.error("Error: Input file path cannot be empty.")
        exit(1)
    if not os.path.exists(args.input_file):
        logger.error(f"Error: Input file or directory does not exist at {args.input_file}")
        exit(1)
    
    final_args["in"] = args.input_file
    final_args["out"] = args.t
    if args.scale is None or args.scale not in ["1080p", "720p"]:
        final_args["scale"] = None  # Use scale of original video
    elif args.scale == "1080p":
        final_args["scale"] = "-1:1080"
    elif args.scale == "720p":
        final_args["scale"] = "-1:720"
    final_args["abr"] = args.abr
    final_args["suffix"] = f"_{args.abr}"
    if args.scale is not None: final_args["suffix"] += f"_{args.scale}"
    final_args["force_overwrite"] = args.force_overwrite
    final_args["delete"] = args.delete_input
    final_args["surround"] = args.surround
    if args.surround:
        final_args["suffix"] = "AAC2.1"
    return final_args

def get_output_file(input_file, suffix, target=None):
    """
    Determines the output file path based on the input file and target directory.
    If target is None, it uses the same directory as the input file.
    If target is a directory, it uses that directory.
    If target is a file, it uses the file name with .mp4 extension.

    """
    output_file = ""
    if not target is None and os.path.isfile(target):
        # If target is a file, use that file name 
        output_file = target
    elif not target is None and os.path.isdir(target):
        # If target is a directory, use that directory
        output_file = os.path.join(target, os.path.basename(input_file))
    else:  
        # If target is None or not a valid directory, use the input file's name and directory
        output_file = input_file
        
    # If suffix is AAC2.1, replace the end of the file name starting at AAC5.1
    if suffix == "AAC2.1":
        if output_file.lower().find("aac5.1") != -1:
            output_file = output_file[:output_file.lower().find("aac5.1")] + suffix + ".mp4"
    else:
        # If suffix is not AAC2.1, just add the suffix to the file name
        output_file = os.path.splitext(output_file)[0] + suffix + ".mp4"    

    return output_file


def recode_video(file_in, file_out, abr, suffix, scale=None, force_overwrite=True, delete_input=False):
    output_file = get_output_file(file_in, suffix, file_out)
    recode_with_ffmpeg(
        file_in,
        output_file,
        audio_bitrate=abr,
        scale=scale,
        force_overwrite=force_overwrite
    )
    if delete_input:
        try:
            os.remove(file_in)
            logger.info(f"Deleted input file: {file_in}")
        except Exception as e:
            logger.error(f"Error deleting input file {file_in}: {e}")

    # Move and rename subtitles file 
    # Find the subtitle file: input_file.srt or input_file.en.srt or input_file-en.srt or input_file.sub or input_file.en.sub  
    move_and_rename_subtitles(file_in, output_file)


def move_and_rename_subtitles(input_file, output_file):
    """
    Finds subtitle files associated with the input video file.
    Looks for .srt or .sub files with the same base name as the input file.
    Returns a list of found subtitle files.
    """
    base_name_src = os.path.splitext(input_file)[0]
    base_name_tgt = os.path.splitext(output_file)[0]
    for ext in ['.srt', '.en.srt', '-en.srt', '.heb.srt', '.sub']:
        subtitle_file_src = base_name_src + ext
        subtitle_file_tgt = base_name_tgt + ext
        if os.path.exists(subtitle_file_src):
            try:
                os.rename(subtitle_file_src, subtitle_file_tgt)
                logger.info(f"Renamed subtitle file from {subtitle_file_src} to {subtitle_file_tgt}")   
            except Exception as e:
                logger.error(f"Error renaming subtitle file {subtitle_file_src} to {subtitle_file_tgt}: {e}")



if __name__ == "__main__":

    args = parse_arguments()

    args = validate_and_interpret_args(args)

    if os.path.isfile(args["in"]):
        logger.debug(f"Input is a file: {args['in']}")
        recode_video(args["in"], args["out"], args["abr"], args["suffix"], args["scale"], args["force_overwrite"], args["delete"])
        # output_file = get_output_file(args["in"], args["suffix"], args["out"])
        # recode_with_ffmpeg(
        #     args["in"],
        #     output_file,
        #     args["abr"],
        #     args["scale"],
        #     force_overwrite=args["force_overwrite"]
        # )
    elif os.path.isdir(args["in"]):
        logger.debug(f"Input is a directory: {args['in']}")
        for file in os.listdir(args["in"]):
            file_path = os.path.join(args["in"], file)
            if os.path.isfile(file_path):
                recode_video(file_path, args["out"], args["abr"], args["suffix"], args["scale"], args["force_overwrite"], args["delete"])
                # output_file = get_output_file(file_path, args["suffix"], args["out"])
                # recode_with_ffmpeg(
                #     file_path,
                #     output_file,
                #     audio_bitrate=args["abr"],
                #     scale=args["scale"],
                #     force_overwrite=args["force_overwrite"]
                # )        
    else:
        logger.error(f"Error: Input path '{args['in']}' is neither a file nor a directory.")
        exit(1)
