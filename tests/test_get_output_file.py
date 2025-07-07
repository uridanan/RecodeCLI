import os
import tempfile
import pytest
import types
from unittest.mock import patch
from recode import RecodeCLI

def test_get_output_file_with_target_file(tmp_path):
    args = types.SimpleNamespace(
        input_file=None,
        t=None,
        scale=None,
        abr="128k",
        force_overwrite=True,
        delete_input=False,
        surround=False
    )
    cli = RecodeCLI(args)
    input_file = tmp_path / "input.mkv"
    input_file.write_text("dummy")
    target_file = tmp_path / "output.mp4"
    with patch("os.path.isfile", return_value=True), patch("os.path.isdir", return_value=False):
        result = result = cli.get_output_file(str(input_file), str(target_file))
        assert result.endswith("_128k.mp4")
        assert os.path.basename(result) == "output_128k.mp4"

def test_get_output_file_with_target_dir(tmp_path):
    args = types.SimpleNamespace(
        input_file=None,
        t=None,
        scale=None,
        abr="128k",
        force_overwrite=True,
        delete_input=False,
        surround=False
    )
    cli = RecodeCLI(args)
    input_file = tmp_path / "input.mkv"
    input_file.write_text("dummy")
    target_dir = tmp_path / "outdir"
    target_dir.mkdir()
    with patch("os.path.isfile", return_value=False), patch("os.path.isdir", return_value=True):
        result = cli.get_output_file(str(input_file), str(target_dir))
        assert result.startswith(str(target_dir))
        assert result.endswith("_128k.mp4")
        assert os.path.basename(result) == "input_128k.mp4"

def test_get_output_file_with_no_target(tmp_path):
    args = types.SimpleNamespace(
        input_file=None,
        t=None,
        scale=None,
        abr="128k",
        force_overwrite=True,
        delete_input=False,
        surround=False
    )
    cli = RecodeCLI(args)
    input_file = tmp_path / "input.mkv"
    input_file.write_text("dummy")
    with patch("os.path.isfile", return_value=False), patch("os.path.isdir", return_value=False):
        result = cli.get_output_file(str(input_file))
        assert result.startswith(str(tmp_path))
        assert result.endswith("_128k.mp4")
        assert os.path.basename(result) == "input_128k.mp4"

def test_get_output_file_suffix_aac21(tmp_path):
    # Prepare args with surround flag for AAC2.1
    args = types.SimpleNamespace(
        input_file=None,
        t=None,
        scale=None,
        abr="192k",
        force_overwrite=True,
        delete_input=False,
        surround=True
    )
    cli = RecodeCLI(args)

    # Case where filename contains 'AAC5.1'
    input_file = tmp_path / "video_AAC5.1.mkv"
    input_file.write_text("dummy")
    suffix = "AAC2.1"
    result = cli.get_output_file(str(input_file))
    assert result.endswith("AAC2.1.mp4")
    assert "AAC5.1" not in result
    assert "AAC2.1" in result

    # Case where filename contains 'AAC5.1'
    input_file = tmp_path / "Vashti_002_AAC5.1_192k.mp4"
    input_file.write_text("dummy")
    suffix = "AAC2.1"
    result = cli.get_output_file(str(input_file))
    assert result.endswith("AAC2.1.mp4")
    assert "AAC5.1" not in result
    assert "AAC2.1" in result 

    # Case where filename does not contain 'AAC5.1' is irrelevant.
    # We wouldn't replace it with AAC2.1 but it could have been in the filename to begin with.