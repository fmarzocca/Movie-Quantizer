from urllib.request import urlopen, urlretrieve
from urllib.error import URLError, HTTPError
import os
import stat
import tkinter.messagebox as mbox


FFMPEG_URL = "https://github.com/imageio/imageio-binaries/raw/master/ffmpeg/ffmpeg-osx-v3.2.4"


def get_ffmpeg(mqapp):
    if internet_on() == False:
        mqapp.popup.destroy()
        mbox.showinfo("Error!", "No internet connection or File not Found.\n\n"
                      "Please provide manual installation of ffmpeg.")
        return False
    # get the file
    try:
        urlretrieve(FFMPEG_URL, "/tmp/ffmpeg.osx")
    except URLError as e:
        mqapp.popup.destroy()
        mbox.showinfo("Error!", e.reason)
        return False
    except HTTPError as e:
        mqapp.popup.destroy()
        mbox.showinfo("Error!", e.msg)
        return False

    # move the file
    try:
        os.makedirs(mqapp.path_OSX)
    except:
        pass
    try:
        os.rename("/tmp/ffmpeg.osx", mqapp.path_OSX+"/ffmpeg.osx")
    except OSError as e:
        mqapp.popup.destroy()
        mbox.showinfo("Error!", e.output)
        return False
    # make the file executable
    st = os.stat(mqapp.path_OSX+"/ffmpeg.osx")
    os.chmod(mqapp.path_OSX+"/ffmpeg.osx", st.st_mode | stat.S_IEXEC)
    mqapp.set_ffmpegversion()
    mqapp.popup.destroy()


# check if we are connected to internet
def internet_on():
    try:
        urlopen(FFMPEG_URL, timeout=2)
        return True
    except URLError as err:
        return False
    except HTTPError as e:
        return False
