import argparse
from os import getenv, getcwd
import os
from pathlib import Path

from dotenv import load_dotenv
load_dotenv("secrets.env")


# Bertha2 Details
cwd = getcwd()
TEMPORARY_FILES_PATH = Path("temp")
MIDI_FILE_PATH = os.path.join(cwd, TEMPORARY_FILES_PATH, "midi")
AUDIO_FILE_PATH = os.path.join(cwd, TEMPORARY_FILES_PATH, "audio")
VIDEO_FILE_PATH = os.path.join(cwd, TEMPORARY_FILES_PATH, "video")

DIRS = [MIDI_FILE_PATH, AUDIO_FILE_PATH, VIDEO_FILE_PATH]  # add any other file paths to this variable

CUSS_WORDS_FILE_NAME = os.path.join(cwd, "cuss_words.txt")
QUEUE_SAVE_FILE = "saved_queues"

SOLENOID_COOLDOWN_S = 30

def import_cuss_words():
    global cuss_words

    try:
        with open(CUSS_WORDS_FILE_NAME) as f:
            words = f.read()
            word_list = words.split("\n")
            word_list = list(filter(None, word_list))  # Remove blank elements (e.g. "") from array
            return word_list
    except Exception as e:
        print(f"CUSS WORDS NOT ENABLED {e}")
        return []

CUSS_WORDS = import_cuss_words()


# Initialize arguments
parser = argparse.ArgumentParser(prog='Bertha2')
parser.add_argument('--disable_hardware', action='store_true')  # checks if the `--disable_hardware` flag is used
parser.add_argument("--log", action="store")
parser.add_argument("--debug_visuals", action='store_true')
parser.add_argument("--debug_converter", action='store_true')
parser.add_argument("--debug_hardware", action='store_true')
parser.add_argument("--debug_chat", action='store_true')
cli_args = parser.parse_args()


# Logging Formatter
# Easily create ANSI escape codes here: https://ansi.gabebanks.net
MAGENTA = "\x1b[35;49;1m"
BLUE = "\x1b[34;49;1m"
GREEN = "\x1b[32;49;1m"
RESET = "\x1b[0m"
LOG_FORMAT = f"{BLUE}[%(levelname)s]{MAGENTA}[%(name)s]{RESET} %(message)s     {GREEN}[%(filename)s:%(lineno)d]{RESET}"


# Twitch Details
CHANNEL = 'berthatwo'  # the channel of which chat is being monitored

# Twitch Login Details
NICKNAME = getenv("NICKNAME")
TOKEN = getenv("TOKEN")
CLIENT_ID = getenv("CLIENT_ID")

PROXY_PORT = getenv("PROXY_PORT")
PROXY_USERNAME = getenv("PROXY_USERNAME")
PROXY_PASSWORD = getenv("PROXY_PASSWORD")


# OBS
OBS_WEBSOCKET_URL = 'ws://127.0.0.1:4444'
SCENE_NAME = 'Scene'
MEDIA_NAME = 'Video'
MAX_VIDEO_TITLE_LENGTH_QUEUE = 45
MAX_VIDEO_TITLE_LENGTH_CURRENT = 45
VIDEO_WIDTH = 1280
VIDEO_HEIGHT = 720

NO_VIDEO_PLAYING_TEXT = "Nothing currently playing."
VISUALS_EMPTY_QUEUE_NEXT_UP_MESSAGE = "Nothing queued."
VISUALS_NONEMPTY_QUEUE_HEADER_MESSAGE = "Next Up:"
STATUS_TEXT_OBS_SOURCE_ID = "current_song"
PLAYING_VIDEO_OBS_SOURCE_ID = "playing_video"


DEFAULT_VISUALS_STATE = {
    "currently_displayed_status_text": NO_VIDEO_PLAYING_TEXT,
    "currently_playing_video_path": "",
    "currently_displayed_next_up": "",
    "queued_video_metadata_objects": [],  # 0th subscript in this list is the currently playing video
    "is_video_currently_playing": False,
    "is_bertha_on_cooldown": False,
    "does_next_up_need_update": True,
    "does_status_text_need_update": True
}

