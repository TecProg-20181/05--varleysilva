from . import diskspace
import subprocess


def test_bytes():
    blocks = 0
    output = '0.00B'
    result = diskspace.bytes_to_readable(blocks)
    assert result == output

def test_subprocess():
    cmd = 'pwd'
    subprocess_output = diskspace.subprocess_check_output(cmd)
    assert subprocess_output == subprocess.check_output(cmd)
