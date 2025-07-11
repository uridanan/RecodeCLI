# RecodeCLI

**RecodeCLI** is a command-line tool for batch or single-file video recoding using FFmpeg. It automates the process of converting videos to MP4 (H.264/AAC) with customizable audio bitrate, scaling, and output options. Logging is provided to both the console and a file for easy monitoring.

## Features

- Recodes videos to MP4 (H.264/AAC 2.1) using FFmpeg
- Supports single files or entire directories
- Customizable audio bitrate and video scaling (e.g., 1080p, 720p)
- Overwrite control for output files
- Optionally delete input files after successful recoding with `--d`
- Optionally replace surround marking "AAC5.1" with stereo marking "AAC2.1" using `--51`
- Detailed logging to `recode.log` and the console
- Finds subtitles files and renames them to match the new output filename

## Requirements

- Python 3.7+
- [FFmpeg](https://ffmpeg.org/) installed and available in your system PATH, or specify the full path in `recode.py`
    FFmpeg is a powerful multimedia framework for handling video, audio, and other multimedia files and streams.
    It can be used to convert, record, and stream audio and video files.
    For more information on FFmpeg, visit:
    https://ffmpeg.org/download.html
    https://www.wikihow.com/Install-FFmpeg-on-Windows

## Installation

1. Clone this repository:
    ```sh
    git clone https://github.com/yourusername/RecodeCLI.git
    cd RecodeCLI
    ```

2. (Optional) Create a virtual environment:
    ```sh
    python -m venv venv
    venv\Scripts\activate  # On Windows
    ```

3. Install dependencies (if any):
    ```sh
    pip install -r requirements.txt
    ```

## Usage

### Basic Command

```sh
python recode.py <input_file_or_directory> [--t OUTPUT_PATH] [--scale SCALE] [--abr AUDIO_BITRATE] [--no-overwrite] [--d] [--51]
```

### Arguments

- `input_file` (positional): Path to the input video file or directory.
- `--t`: Desired path for the output file or directory.
- `--scale`: Video scale, e.g., `1080p` or `720p`. If omitted, keeps original resolution.
- `--abr`: Audio bitrate (default: `192k`).
- `--no-overwrite`: Do not overwrite output file if it exists.
- `--d`: **Delete input file(s) after successful recoding.**
- `--51`: **Mark output as stereo (AAC2.1) if originally marked as surround (AAC 5.1).**  
  This flag replaces `AAC5.1` with `AAC2.1` in the output filename to indicate stereo audio instead of surround audio.  

### Examples

**Recoding a single file:**
```sh
python recode.py "input.mkv" --scale 720p --abr 128k
```

**Recoding all files in a directory:**
```sh
python recode.py "D:/Videos/ToConvert" --scale 1080p --abr 192k --t "D:/Videos/Converted"
```

**Specifying output file:**
```sh
python recode.py "input.mkv" --t "output.mp4"
```

**Recoding and deleting input file after success:**
```sh
python recode.py "input.mkv" --scale 720p --d
```

**Recoding and marking output as stereo (AAC 2.1):**
```sh
python recode.py "input_AAC5.1.mkv" --51
```

## Logging

- All actions and errors are logged to both the console and `recode.log` in the project directory.

## Testing

Unit tests are provided in the `tests/` directory. To run tests:

```sh
pytest
```

## Notes

- Make sure FFmpeg is installed and accessible. You can set the path in `recode.py` via the `FFMPEG_EXECUTABLE` variable.
- The script will skip files that do not exist or are not valid video files.
- If no output file is specified, it will default to the input file with .mp4 extension.
- If `-t` target dir is specified, it will use that directory.
- If `-t` target dir is not specified, it will use the same directory as the input file.
- Use `--d` to delete input files after successful recoding.
- Use `--51` to mark output as stereo (AAC 2.1) in the filename if originally marked as surround (AAC 5.1)

## License

MIT License

---

**Contributions are welcome!**
