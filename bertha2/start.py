#!/usr/bin/env python

""" The main runner for Bertha2
Opens up multiple processes that run coresponding tasks. 
- Reading commands from Twitch chat
- Converting videos to mp4 and MIDI
- Controlling hardware to play MIDI files
- Reflecing the state of the system in OBS

"""

import json
import os
import signal
from multiprocessing import Process, Queue, Event, Pipe
from pathlib import Path

# Get all of the processes that will run async
from bertha2.chat import chat_process
from bertha2.converter import converter_process
from bertha2.hardware import hardware_process
from bertha2.visuals import visuals_process

from bertha2.settings import DIRS, QUEUE_SAVE_FILENAME
from bertha2.utils.logs import initialize_root_logger

os.environ['IMAGEIO_VAR_NAME'] = 'ffmpeg'

logger = initialize_root_logger(__name__)


def create_dirs(DIRS):
    for dir in DIRS:
        file_dir = Path(dir)
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)

    logger.info(f"Created directories")


def save_queues(link_q: Queue, play_q: Queue):
    logger.info(f"Saving queues to database.")

    ll = []
    pl = []
    
    while not link_q.empty():
        ll.append(link_q.get())

    while not play_q.empty():
        pl.append(play_q.get())

    # save q to json file
    backup_file_contents = {
        "play_q": pl,
        "link_q": ll
    }

    logger.debug(backup_file_contents)

    with open(QUEUE_SAVE_FILENAME, 'w', encoding='utf-8') as file:
        json.dump(backup_file_contents, file, ensure_ascii=False, indent=4)

    logger.info(f"Saved queues to database.")


def load_queue(queue_name: str):
    logger.info(f"Loading queue: {queue_name}")

    q = Queue()

    try:
        with open(QUEUE_SAVE_FILENAME) as f:
            contents = json.load(f)

        logger.debug(contents[queue_name])

        # save it into a queue
        for item in contents[queue_name]:
            q.put(item)
    except Exception as ee:
        logger.critical(f"Queue could not be loaded. {ee}")

    return q


if __name__ == '__main__':

    logger.info(f"Initializing Bertha2...")
    create_dirs(DIRS)

    # Set signal handling of SIGINT to ignore mode.
    default_handler = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    link_q = load_queue("link_q")  # Queue of YouTube links to convert
    play_q = load_queue("play_q")  # Queue of ready-to-play videos

    # Pipe: converter -> visuals connection
    cv_parent_conn, cv_child_conn = Pipe()
    # Pipe: hardware -> visuals connection. Used for the hardware process to tell the visuals process when its doing things
    hv_child_conn, hv_parent_conn = Pipe()

    sigint_e = Event()
    
    # Connect each process that can be. After, it is the process's responsibility to not crash
    # TODO: Write a fuction for each to see if it can be booted up
    #   e.g. Is b2 connected, can we connect to obs?
    # TODO: why does visuals have the parent and child conns, when it is only receiving data?
    chat_p = Process(target=chat_process, args=(link_q,))
    converter_p = Process(target=converter_process, args=(sigint_e, cv_child_conn, link_q, play_q,))
    hardware_p = Process(target=hardware_process, args=(sigint_e, hv_parent_conn, play_q,))
    visuals_p = Process(target=visuals_process, args=(cv_parent_conn, hv_child_conn,))

    processes = [chat_p, converter_p, hardware_p, visuals_p]

    # Start all of the processes
    for process in processes:
        process.daemon = True
        process.start()

    # Since we spawned all the necessary processes already,
    #   restore default signal handling for the parent process.
    signal.signal(signal.SIGINT, default_handler)

    try:
        signal.pause()
    except KeyboardInterrupt:
        logger.info(f"Shutting down gracefully...")
        sigint_e.set()
        converter_p.join()
        hardware_p.join()
    except Exception as e:
        logger.critical(f"Error has occurred. {e}")
    finally:
        save_queues(link_q, play_q)
        logger.info(f"Shut down.")
