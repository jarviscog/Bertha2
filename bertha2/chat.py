#!/usr/bin/env python

""" Reads commands from Twitch chat, and adds the parsed video links to a queue """

import socket
from typing import Tuple 
from pytube import YouTube
from multiprocessing import Queue
from pprint import pprint

from bertha2.settings import CHANNEL, NICKNAME, TOKEN, MAX_VIDEO_LENGTH_SECONDS
from bertha2.utils.logs import initialize_module_logger, log_if_in_debug_mode

logger = initialize_module_logger(__name__)


def is_valid_youtube_video(link: str) -> bool:

    try:
        yt = YouTube(link)
    except Exception as e:
        logger.info(f"CHAT: link is invalid {e}")
        return False

    try:
        # this will return None if it's available, and an error if it's not
        yt.check_availability() 
    except Exception as e: 
        # Will raise an exception if members only, live stream. etc.
        logger.info(f"Invaid video: {e}")
        return False

    if yt.age_restricted:
        logger.info(f"Invalid video: {link} is age restricted")
        return False

    if yt.length >= MAX_VIDEO_LENGTH_SECONDS:
        logger.info(f"Invalid video: {link} is too long")
        return False

    return True


def send_privmsg(sock: socket.socket, message, twitch_channel, reply_id=None) -> None:
    if reply_id is not None:
        msg = f"@reply-parent-msg-id={reply_id} PRIVMSG #{twitch_channel} :{message}\r\n"
        sock.send(msg.encode("utf-8"))
        logger.debug(msg)
    else:
        msg = f"PRIVMSG #{twitch_channel} :{message}\r\n"
        sock.send(msg.encode("utf-8"))
        logger.debug(msg)


def parse_privmsg(msg: str) -> dict | None:
    if not msg or msg == '':
        return None

    # Looks like this:
    # ('@badge-info=;badges=...user-id=142;user-type= :user!user@user.tmi.twitch.tv '
    # 'PRIVMSG #berthatwo :!play https://www.youtube.com/watch?v=B_i743apHLs&t=12s')]
    logger.debug(msg)
    pprint(msg.strip().split(" :"))
    pprint(msg.strip().split(" :"))
    pprint(len(msg.strip().split(" :")))
    message_parts = msg.strip().split(" :");

    # check if privmsg
    if "PRIVMSG" not in message_parts[1]:

        return None

    # TODO: This could be a regex
    tags = message_parts[0].split(";")
    msg_id = tags[8].split("=")[1].strip()
    username = tags[4].split("=")[1].strip()

    msg_content = message_parts[2].strip()
    command, command_arg = None, None
    if msg_content[:1] == "!":
        command = msg_content.split(" ")[0].strip()
        command_arg = msg_content.split(" ")[1].strip()

    return {
        'msg_id': msg_id,
        'username': username,
        'msg_content': msg_content,
        'command': command,
        'command_arg': command_arg,
    }


def connect_to_twitch_irc() -> Tuple[socket.socket, str] | None:
    """
    Connects to a Twitch channel through IRC
    :return: Socket and response if success | None
    """

    sock = socket.socket()
    sock.connect(("irc.chat.twitch.tv", 6667))  # connect to server
    sock.send(f"CAP REQ :twitch.tv/tags\n".encode("utf-8"))  # req capabilities
    resp = sock.recv(2048).decode("utf-8")  # check if cap req was successful
    logger.debug(resp)
    if "CAP * NAK" in resp:
        logger.critical("Capabilities couldn't be requested.")
        raise ConnectionRefusedError
    # Authenticate user
    sock.send(f"PASS {TOKEN}\n".encode("utf-8"))  
    sock.send(f"NICK {NICKNAME}\n".encode("utf-8"))
    resp = sock.recv(2048).decode("utf-8")  # check if auth was successful
    # TODO: More test cases
    if "Improperly formatted auth" in resp:
        logger.critical("Improperly formatted auth.")
        return None
    if "Login authentication failed" in resp:
        logger.critical("Login authentication failed.")
        return None
    sock.send(f"JOIN #{CHANNEL}\n".encode("utf-8"))  # join channel
    response = sock.recv(2048).decode("utf-8")  # get join messages
    return (sock, response)


def chat_process(link_q: Queue):
    """
    Reads through twitch chat and parses out commands

    :param: link_q: The queue that the YouTube links from chat should be added to
    :return:
    """
    log_if_in_debug_mode(logger, __name__)

    logger.debug(f"Twitch token, nickname: {TOKEN}, {NICKNAME}")

    # https://dev.twitch.tv/docs/irc

    connection_response = connect_to_twitch_irc()
    if not connection_response:
        logger.critical(f"Could not connect to Twitch chat.")
        return
    
    (sock, response) = connection_response 
    logger.debug(response)

    logger.info(f"Ready and waiting for twitch commands in [{CHANNEL}]...")

    while True:
        try:
            resp = sock.recv(2048).decode("utf-8")

            # this code ensures the IRC server knows the bot is still listening
            if resp.startswith("PING"):
                sock.send("PONG\n".encode("utf-8"))
                continue
            
            message_object = parse_privmsg(resp)
            if not message_object:
                logger.warning("Could not parse message")
                continue

            logger.debug(message_object)

            # TODO: Should this be it's own function?
            if message_object["command"] == "!play":

                logger.debug(message_object["msg_content"])
                if not is_valid_youtube_video(message_object["command_arg"]):
                    logger.debug(f"invalid youtube video")

                    send_privmsg(sock,
                                 f"Sorry, {message_object['command_arg']} is not a valid YouTube link. \
                                 It's either an invalid link or it's age restricted.",
                                 CHANNEL,
                                 reply_id=message_object["msg_id"])
                    continue


                # Queue.put adds command_arg to the global Queue variable, not a local Queue. See
                #   multiprocessing.Queue for more info.
                # TODO: we can add video_name_q.put() here instead. just use
                #   the youtube link that we have here and create a youtube object
                link_q.put(message_object["command_arg"])
                logger.info(f"The video follow video has been queued: {message_object['command_arg']}")
                send_privmsg(
                        sock, 
                        f"Your video ({message_object['command_arg']}) has been queued.", 
                        CHANNEL,
                        reply_id=message_object["msg_id"])

        except Exception as e:
            logger.critical(f"Error{e}")
            pass

if __name__ == "__main__":
    print("Running chat.py as main")
    # TODO: Be able to run this independently