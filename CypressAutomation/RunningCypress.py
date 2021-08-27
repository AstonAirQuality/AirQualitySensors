import os
import subprocess
from pathlib import Path

# my_file = Path("./urls/url.txt")
# # delete the file if it already exists
# if my_file.is_file():
#     my_file.unlink()

# # double backslashes are to escape the '\' character. Otherwise \n gets interpreted as a newline, for example
# e1 = subprocess.run('.\\node_modules\\.bin\\cypress run --spec "cypress\\integration\\examples\\PlumeAutomation.js" ', shell=True, capture_output=True)
# # TODO build more robust and platform-independent file paths into the command string
# if my_file.is_file():
#     print('url has been retrieved, try again')
# else:
#     print('url has not been retrieved')
# #print (e1)  # very verbose if successful!! 


# TODO another subprocess function to download and extract the file (using the command below)
#jupyter nbconvert --execute --clear-output Plume_Dashboard_Download.ipynb
#e2 = subprocess.run('jupyter nbconvert --execute --clear-output ..\\ipynb\\Flows\\Plume_Dashboard_Download.ipynb', shell=True, capture_output=True)