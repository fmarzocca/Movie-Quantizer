application_title = "Movie Quantizer" 
main_python_file = "mq.py"

import sys

from cx_Freeze import setup, Executable

base = None
if sys.platform == "win32":
	base = "Win32GUI"

includes = ["tkinter"]
excludes = ['tcl', 'ttk', 'Tkinter']

build_options = {'bdist_mac':
                    {'iconfile': "icons/mq.icns"
                    },
                }

target= Executable(
    script="mq.py",
    base=base,
    )
    
setup(
    name = application_title,
    version = "1.0.0",
    description = "A movie Frame Grabber",
    options = build_options,
    executables = [target]
)

