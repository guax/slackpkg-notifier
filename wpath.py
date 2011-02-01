""" Path and system configuration for slackpkg-notifier

chdir() -- Change directory to the location of the current file.

"""

import os

# The path containing the wpath.py file.
current = os.path.dirname(os.path.realpath(__file__)) + '/'

# These paths can easily be modified to handle system wide installs, or
# they can be left as is if all files remain with the source directory
# layout.
# All of these paths *MUST* end in a /
# except the python one, of course as it is an executable

images = current + "/images/"

# time for periodically check updates
checker_time = 2 # in hours

#slackpkg-notifier version
version = "1.0"

def chdir(file):
    """Change directory to the location of the specified file.

    Keyword arguments:
    file -- the file to switch to (usually __file__)

    """
    os.chdir(os.path.dirname(os.path.realpath(file)))

