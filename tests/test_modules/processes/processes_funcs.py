

def get_process(process_name: str):
    """
    Runs: ps aux | grep $process_name | grep -v grep
    """
    fake_process_list = ["vim", "pymetrics"]
    if process_name in fake_process_list:
        return {
            "process": process_name,
            "exit_code": 0
        }
    return {
        "process": process_name,
        "exit_code": 1
    }


def kill_process(process_name: str, signal: str):
    """
    Runs: kill -s $signal $process_name
    """
    fake_process_list = ["vim", "pymetrics"]
    fake_signal_dict = {
        "SIGHUP": 1,
        "SIGINT": 2,
    }
    if process_name in fake_process_list and signal in fake_signal_dict.keys():
        return {
            "process": process_name,
            "signal": signal,
            "exit_code": 0
        }
    return {
        "process": process_name,
        "signal": signal,
        "exit_code": 1
    }
