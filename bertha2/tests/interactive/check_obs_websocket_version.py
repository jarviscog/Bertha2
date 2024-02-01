import logging

import asyncio
import simpleobsws


# TODO: This is caused because we are grabbing the default logger
# This is to prevent messy debug logs from pyppeteer
simpleobsws_logger = logging.getLogger("simpleobsws")
simpleobsws_logger.setLevel(50)
simpleobsws_logger.addHandler(logging.StreamHandler())

parameters = simpleobsws.IdentificationParameters(
    ignoreNonFatalRequestChecks=False)  # Create an IdentificationParameters object (optional for connecting)

ws = simpleobsws.WebSocketClient(url='ws://127.0.0.1:4444',
                                 identification_parameters=parameters)  # Every possible argument has been passed, but none are required. See lib code for defaults.


async def make_request():
    await ws.connect()  # Make the connection to obs-websocket
    await ws.wait_until_identified()  # Wait for the identification handshake to complete

    request = simpleobsws.Request('GetVersion')  # Build a Request object

    ret = await ws.call(request)  # Perform the request
    if ret.ok():  # Check if the request succeeded
        print("Request succeeded! Response data: {}".format(ret.responseData))

    await ws.disconnect()  # Disconnect from the websocket server cleanly


loop = asyncio.get_event_loop()
loop.run_until_complete(make_request())
