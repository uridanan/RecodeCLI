import subprocess
import os
import time
import argparse
import logging


# TODO
# Add modes for AMF and libx265?
#   I've managed to get AMF to produce good quality with faster speed and smaller size
#   libx265 gives smaller files, but takes longer. Check if it works with Emby

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

FFMPEG_EXECUTABLE = "C:/Program Files/ffmpeg/bin/ffmpeg.exe"  # Ensure ffmpeg is in your PATH or provide full path

def format_time(x):
    elapsed_time = int(x)
    hours = elapsed_time // 3600
    minutes = (elapsed_time % 3600) // 60
    seconds = elapsed_time % 60
    elapsed_time_str = f"{hours:02}:{minutes:02}:{seconds:02}"
    return elapsed_time_str

class RecodeCLI:
    def __init__(self, args):
        self.input_path = args.input_file
        self.output_path = args.t
        self.scale = None if args.scale not in ["1080p", "720p"] else ("-1:1080" if args.scale == "1080p" else "-1:720")
        self.abr = args.abr
        self.force_overwrite = args.force_overwrite
        self.delete_input = args.delete_input
        self.surround = args.surround
        self.suffix = self._determine_suffix(args)
        self.codec = args.c.lower()
    
    def _determine_suffix(self, args):
        if args.surround:
            return "AAC2.1"
        suffix = f"_{args.abr}"
        if args.scale in ["1080p", "720p"]:
            suffix += f"_{args.scale}"
        return suffix

    def _get_command(self, input_file, output_file):
        command = [
            "ffmpeg",
            "-i", input_file,
        ]
        
        if self.codec == "amf":
            command = command + self._amf()            
        elif self.codec == "libx264":
            command = command + self._libx264()
        else: # self.codec == "libx265"
            command = command + self._libx265()
        
        # Sound codec and bitrate, always use AAC 2.1
        command = command + [
            "-c:a", "aac",
            "-ac", "2",
            "-b:a", self.abr,
        ]

        if self.scale is not None:
            command.append("-vf")
            command.append("scale=" + self.scale)
            logger.debug(f"Scaling video to: {self.scale}")

        command.append(output_file)

        if self.force_overwrite:
            command.insert(1, "-y")

        return command
        
    def _amf(self):
         # The updated command to use VBR for file size control
        target_bitrate = "2M"  # You can adjust this value to control the file size
        max_bitrate = "3M"     # A reasonable maxrate is often 1.5x the target bitrate
        buffer_size = "3M"     # Usually the same as maxrate

        amf_command = [                       
            "-pix_fmt", "yuv420p", # Explicitly set the pixel format to 8-bit YUV420P immediately after input
            "-c:v", "h264_amf",
            "-quality", "balanced",
            
            # Rate control options for AMF
            "-rc", "vbr_peak",
            "-b:v", target_bitrate,
            "-maxrate", max_bitrate,
            "-bufsize", buffer_size, 
        ]   
        return amf_command
    
    def _libx264(self):
        libx264_command = [
            "-c:v", "libx264",
            "-crf", "23",
            "-preset", "medium",
        ]
        return libx264_command
    
    def _libx265(self):
        libx265_command = [
            "-c:v", "libx265",
            "-crf", "28",
            "-preset", "medium",
        ]
        return libx265_command
        
    def recode_with_ffmpeg(self, input_file, output_file):
        if not os.path.exists(input_file):
            logger.error(f"Error: Input file not found at {input_file}")
            return

        video_extensions = ('.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv', '.webm', '.mpeg', '.mpg', '.m4v')
        if not input_file.lower().endswith(video_extensions):
            logger.debug(f"Skipped: {input_file} is not a recognized video file.")
            return

        command = self._get_command(input_file, output_file)

        logger.debug(f"Starting recoding for: {input_file}")
        logger.debug(f"Output file will be: {output_file}")
        command_str = " ".join(command)

        try:
            logger.debug(f"{command_str.strip()}")
            logger.info(f"START: {input_file} -> {output_file}")
            start = time.time()
            subprocess.run(command, check=True)
            end = time.time()
            elapsed_time = format_time(end - start)
            logger.info(f"Recoding completed in: {elapsed_time}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Error during FFmpeg recoding for {input_file}:")
            logger.error(f"Command: {' '.join(e.cmd)}")
            logger.error(e.stderr.decode() if e.stderr else "")
            return False
        except FileNotFoundError:
            logger.error("Error: FFmpeg executable not found.")
            logger.error("Please ensure FFmpeg is installed and its executable is in your system's PATH.")
            return False

    def get_output_file(self, input_file, target=None):
        output_file = ""
        suffix = self.suffix
        if target is not None and os.path.isfile(target):
            output_file = target
        elif target is not None and os.path.isdir(target):
            output_file = os.path.join(target, os.path.basename(input_file))
        else:
            output_file = input_file

        if suffix == "AAC2.1":
            if output_file.lower().find("aac5.1") != -1:
                output_file = output_file[:output_file.lower().find("aac5.1")] + suffix + ".mp4"
            else:
                output_file = os.path.splitext(output_file)[0] + suffix + ".mp4"
        else:
            output_file = os.path.splitext(output_file)[0] + suffix + ".mp4"
        return output_file

    def recode_video(self, file_in, file_out):
        output_file = self.get_output_file(file_in, file_out)
        if self.recode_with_ffmpeg(file_in, output_file):
            if self.delete_input:
                try:
                    os.remove(file_in)
                    logger.info(f"Deleted input file: {file_in}")
                except Exception as e:
                    logger.error(f"Error deleting input file {file_in}: {e}")
            self.move_and_rename_subtitles(file_in, output_file)

    def move_and_rename_subtitles(self, input_file, output_file):
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

    def run(self):
        if os.path.isfile(self.input_path):
            logger.debug(f"Input is a file: {self.input_path}")
            self.recode_video(self.input_path, self.output_path)
        elif os.path.isdir(self.input_path):
            logger.debug(f"Input is a directory: {self.input_path}")
            for file in os.listdir(self.input_path):
                file_path = os.path.join(self.input_path, file)
                if os.path.isfile(file_path):
                    self.recode_video(file_path, self.output_path)
        else:
            logger.error(f"Error: Input path '{self.input_path}' is neither a file nor a directory.")
            exit(1)

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
                        help="Mark output as surround (AAC 5.1) in the filename.")
    parser.add_argument("--c", default="amf",
                        help="Video codec to use (default: 'amf'). Options: 'amf', 'libx264', 'libx265'.")
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_arguments()
    cli = RecodeCLI(args)
    cli.run()



# Example usage:
# python c:\\Github\\RecodeCLI\\recode.py "D:\Downloads\Karate Kid Legends.AAC5.1-[YTS.MX].mp4" --t D:\Movies\ --abr 256k --51