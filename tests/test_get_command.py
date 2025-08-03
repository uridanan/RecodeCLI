import types
from recode import RecodeCLI

def test_get_command_amf():
    args = types.SimpleNamespace(
        input_file="input.mkv",
        t=None,
        scale=None,
        abr="192k",
        force_overwrite=True,
        delete_input=False,
        surround=False,
        c="amf"
    )
    cli = RecodeCLI(args)
    command = cli._get_command("input.mkv", "output.mp4")
    assert "ffmpeg" in command[0]
    assert "-c:v" in command
    assert "h264_amf" in command
    assert "-b:a" in command
    assert "192k" in command
    assert "output.mp4" == command[-1]

def test_get_command_libx264():
    args = types.SimpleNamespace(
        input_file="input.mkv",
        t=None,
        scale="1080p",
        abr="128k",
        force_overwrite=True,
        delete_input=False,
        surround=False,
        c="libx264"
    )
    cli = RecodeCLI(args)
    command = cli._get_command("input.mkv", "output.mp4")
    assert "-c:v" in command
    assert "libx264" in command
    assert "-crf" in command
    assert "-preset" in command
    assert "-b:a" in command
    assert "128k" in command
    assert "-vf" in command
    assert "scale=-1:1080" in command
    assert "output.mp4" == command[-1]

def test_get_command_libx265():
    args = types.SimpleNamespace(
        input_file="input.mkv",
        t=None,
        scale="720p",
        abr="256k",
        force_overwrite=False,
        delete_input=False,
        surround=False,
        c="libx265"
    )
    cli = RecodeCLI(args)
    command = cli._get_command("input.mkv", "output.mp4")
    assert "-c:v" in command
    assert "libx265" in command
    assert "-crf" in command
    assert "-preset" in command
    assert "-b:a" in command
    assert "256k" in command
    assert "-vf" in command
    assert "scale=-1:720" in command
    assert "output.mp4" == command[-1]
    # Should not have '-y' since force_overwrite is False
    assert "-y"