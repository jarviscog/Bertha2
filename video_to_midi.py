import asyncio, wget, os
from pyppeteer import launch
from pathlib import Path
from youtube_class import YVideo
from global_vars import midi_file_path, audio_file_path, video_file_path


def video_to_midi(youtube_url):
    print("Converting YouTube URL into audio file...")
    file_name = download_video_audio(youtube_url) # store audio file in audio_file_path
    
    print("Converting audio to midi...")
    midi_file_url = asyncio.get_event_loop().run_until_complete(convert_audio_to_link(file_name))
    
    print("Downloading midi file...")
    dl_midi_file(midi_file_url, file_name) # store audio file in midi_file_path

def download_video_audio(youtube_url):
    video_obj = YVideo(youtube_url)
    video_obj.downloadVideo()
    video_obj.convertVideoToMP3()

    return video_obj.file_name

async def convert_audio_to_link(file_name):
    browser = await launch()
    page = await browser.newPage()
    await page.goto('https://www.conversion-tool.com/audiotomidi/')

    filechoose = await page.querySelector('#localfile')
    upload_file = str(audio_file_path / (file_name + ".mp3"))
    print(upload_file)
    await filechoose.uploadFile(upload_file)


    submit = await page.querySelector('#uploadProgress > p > button')
    await submit.click()

    await page.waitForSelector('#post-472 > div.entry-content.clearfix > ul > li:nth-child(1) > a')
    link = await page.querySelectorEval('#post-472 > div.entry-content.clearfix > ul > li:nth-child(1) > a', 'n => n.href')

    await browser.close()
    
    return link

def dl_midi_file(url, file_name):
    wget.download(url, str(midi_file_path / (file_name + ".midi")))

# print(download_video_audio("https://www.youtube.com/watch?v=HHcgTbs7_Os"))
# download_video_audio("https://www.youtube.com/watch?v=HHcgTbs7_Os")
# print(asyncio.get_event_loop().run_until_complete(convert_audio_to_link("HHcgTbs7_Os")))
# dl_midi_file("https://www.conversion-tool.com/downloadfile.php?id=c40c709c32cdfb09af1d4ba9cf1c2ed87a6a994e", "HHcgTbs7_Os")

# video_to_midi("https://www.youtube.com/watch?v=HHcgTbs7_Os")