

def read_file_line(path: str, line_no: int):
    """
    runs: cat $path | sed -n "$line_no{p;q;}" "$1"
    """
    fake_data = "the text on the line specified of the file at the path provided"
    return {
        "path": path,
        "line": line_no,
        "data": fake_data,
    }


def write_file_line(path: str, line_no: int, data: str):
    """
    runs: sed -i "s/`head -$line_no $path | tail -1 `/$data/" $path
    """
    if path and line_no and data:
        return {"status": "success"}
    else:
        return {"status": "failed"}
