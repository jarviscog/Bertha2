import asyncio
import logging
import random
import os

import wget
from moviepy.editor import VideoFileClip
from pyppeteer import launch
from pytube import YouTube
from pytube.extract import video_id

from bertha2.settings import (
    MIDI_FILE_PATH,
    AUDIO_FILE_PATH,
    PROXY_PORT,
    PROXY_USERNAME,
    PROXY_PASSWORD,
    VIDEO_FILE_PATH
)
from bertha2.utils.logs import initialize_module_logger, log_if_in_debug_mode

logger = initialize_module_logger(__name__)

# This is to prevent messy debug logs from pyppeteer
pptr_logger = logging.getLogger("pyppeteer")
pptr_logger.setLevel(50)
pptr_logger.addHandler(logging.StreamHandler())


def download_video_audio(youtube_url):
    logger.debug(f"Converting YouTube URL into audio file...")

    yt = YouTube(youtube_url)
    file_name = video_id(youtube_url)

    # download video
    logger.debug(f"Starting video download")
    yt.streams.first().download(
        output_path=VIDEO_FILE_PATH, filename=f"{file_name}.mp4"
    )

    # convert to mp3
    # str conversion + brackets are necessary
    video_clip = VideoFileClip(str(VIDEO_FILE_PATH / (file_name + ".mp4")))

    audio_clip = video_clip.audio
    # str conversion + brackets are necessary
    audio_clip.write_audiofile(str(AUDIO_FILE_PATH / (file_name + ".mp3")), verbose=False, logger=None)

    audio_clip.close()
    video_clip.close()

    return file_name


# TODO: get this function working
async def convert_audio_to_midi(file_name):
    log_if_in_debug_mode(logger, __name__)
    logger.debug(f"converting audio to midi")
    # TODO: put some try catches in here to prevent timeouts

    proxy_num = random.randrange(0, 100000)

    logger.debug(f"ATTEMPTING TO GET LINK")
    browser = await launch(
        {
            "logLevel": 0,
            "args": [f"--proxy-server=zproxy.lum-superproxy.io:{PROXY_PORT}"],
            # "headless": False,
        }
    )
    page = await browser.newPage()
    await page.authenticate(
        {
            "username": f"{PROXY_USERNAME}-session-{proxy_num}",
            "password": PROXY_PASSWORD,
        }
    )

    # proxy is working!!!

    try:  # TODO: finish the error checking on this function
        await page.goto("https://www.conversion-tool.com/audiotomidi/", timeout=30000)
        # await page.goto("https://whatmyuseragent.com")

    except Exception as e:
        logger.critical(f"goto timed out!")
        logger.critical(f"{e}")  # error -> Navigation Timeout Exceeded: 1000 ms exceeded.
        # return asyncio.get_event_loop().run_until_complete(
        #     convert_audio_to_link(file_name)
        # )
        # TODO: restart function from the top!

    logger.debug(f"Opened the webpage successfully")

    filechoose = await page.querySelector("#localfile")
    upload_file = str(AUDIO_FILE_PATH / (file_name + ".mp3"))
    await filechoose.uploadFile(upload_file)

    submit = await page.querySelector("#uploadProgress > p > button")
    await submit.click()

    await page.waitForSelector(
        "#post-472 > div.entry-content.clearfix > ul > li:nth-child(1) > a", timeout=0
    )
    link = await page.querySelectorEval(
        "#post-472 > div.entry-content.clearfix > ul > li:nth-child(1) > a",
        "n => n.href",
    )

    await browser.close()
    logger.debug(f"Got the link!")

    # os.remove(str(audio_file_path / (file_name + ".mp3")))  # remove unneeded mp3 file
    logger.debug(f"{link}")

    logger.debug(f"Downloading midi file...")
    wget.download(link, str(MIDI_FILE_PATH / (file_name + ".midi")))


def video_to_midi(youtube_url):
    # TODO: add a feature that checks if the YouTube video has already been converted

    yt = YouTube(youtube_url)
    video_name = yt.vid_info['videoDetails']['title']

    logger.info(f"Converting YouTube video \"{video_name}\" to a MIDI file")

    # video_name = yt.vid_info
    # file_name = video_id(youtube_url)

    # if it's been converted and found in files, return filepath (temporarily disabled for testing)
    # if os.path.isfile(str(midi_file_path / (file_name + ".midi"))):
    #     return str(midi_file_path / (file_name + ".midi"))

    # TODO: can we convert multiple files at the same time? or can we convert them faster?
    file_name = download_video_audio(youtube_url)  # store audio file in audio_file_path

    # TODO: if this fails, rerun the function
    asyncio.run(convert_audio_to_midi(file_name))

    file_name += ".midi"
    filepath = os.path.join(MIDI_FILE_PATH,  file_name)

    return filepath, video_name


def converter_process(sigint_e, conn, link_q, play_q,):
    logger.info(f"Converter process has been started.")
    while not sigint_e.is_set():
        try:
            link = link_q.get(timeout=10)

            filepath, video_title = video_to_midi(link)
            logger.info(f"Successfully converted {video_title} to a MIDI file")

            conn.send({"title": video_title,
                       "filepath": f"{os.getcwd()}/files/video/{YouTube(link).video_id}.mp4"})  # This should be here. As soon as a video is finished converting, it should be added to the queue because we know it's safe

            play_q.put(filepath)
        except:  # this will occur when link_q is empty. not the best way to implement.
            pass

    else:
        logger.info(f"Converter process has been shut down.")
