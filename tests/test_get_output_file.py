import os
import tempfile
import pytest
from unittest.mock import patch
from recode import get_output_file

def test_get_output_file_with_target_file(tmp_path):
    input_file = tmp_path / "input.mkv"
    input_file.write_text("dummy")
    target_file = tmp_path / "output.mp4"
    suffix = "_recode"
    with patch("os.path.isfile", return_value=True), patch("os.path.isdir", return_value=False):
        result = get_output_file(str(input_file), suffix, str(target_file))
        assert result.endswith("_recode.mp4")
        assert os.path.basename(result) == "output_recode.mp4"

def test_get_output_file_with_target_dir(tmp_path):
    input_file = tmp_path / "input.mkv"
    input_file.write_text("dummy")
    target_dir = tmp_path / "outdir"
    target_dir.mkdir()
    suffix = "_recode"
    with patch("os.path.isfile", return_value=False), patch("os.path.isdir", return_value=True):
        result = get_output_file(str(input_file), suffix, str(target_dir))
        assert result.startswith(str(target_dir))
        assert result.endswith("_recode.mp4")
        assert os.path.basename(result) == "input_recode.mp4"

def test_get_output_file_with_no_target(tmp_path):
    input_file = tmp_path / "input.mkv"
    input_file.write_text("dummy")
    suffix = "_recode"
    with patch("os.path.isfile", return_value=False), patch("os.path.isdir", return_value=False):
        result = get_output_file(str(input_file), suffix)    
        assert result.startswith(str(tmp_path))
        assert result.endswith("_recode.mp4")
        assert os.path.basename(result) == "input_recode.mp4"