import os
import types
import pytest
from recode import validate_and_interpret_args

def test_validate_and_interpret_args_valid_file(tmp_path):
    # Create a dummy file
    dummy_file = tmp_path / "video.mkv"
    dummy_file.write_text("dummy")

    # Create a mock args object
    args = types.SimpleNamespace(
        input_file=str(dummy_file),
        t=None,
        scale="1080p",
        abr="128k",
        force_overwrite=True
    )

    result = validate_and_interpret_args(args)
    assert result["in"] == str(dummy_file)
    assert result["scale"] == "-1:1080"
    assert result["abr"] == "128k"
    assert result["force_overwrite"] is True

def test_validate_and_interpret_args_invalid_file():
    args = types.SimpleNamespace(
        input_file="not_a_real_file.mkv",
        t=None,
        scale=None,
        abr="192k",
        force_overwrite=True
    )
    with pytest.raises(SystemExit):
        validate_and_interpret_args(args)