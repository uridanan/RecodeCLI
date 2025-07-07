import os
import types
import pytest
from recode import RecodeCLI

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
        force_overwrite=True,
        delete_input=False,
        surround=False
    )
    cli = RecodeCLI(args)
    assert cli.input_path == str(dummy_file)
    assert cli.scale == "-1:1080"
    assert cli.abr == "128k"
    assert cli.force_overwrite is True
    assert cli.delete_input is False
    assert cli.surround is False
    assert cli.suffix == "_128k_1080p"