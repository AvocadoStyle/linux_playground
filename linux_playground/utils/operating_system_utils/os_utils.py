import os


WIN_OS = 'nt'

def is_windows_os():
    return os.name == WIN_OS

def is_linux_os():
    return not is_windows_os()