# v2.0 roadmap

* Have the option to play either series, or parallel
  * Parallel will play midi files as soon as they are queued.
  * Series will play the videos one after another
* Easy and consistent testing (even without hardware connected)
* Better logging, some way of enabling different levels of information without constantly commenting out print statements
  * Make sure the log levels are accurate to what they are. Document how to level logs.
  * Change log level while program is running? https://towardsdatascience.com/how-to-add-a-debug-mode-for-your-python-logging-mid-run-3c7330dc199d
  * Save logs to files
* Add some better explanations for what is going on
  * Why does your video not immediately appear in next up?
* More stability and consistency. Should not crash, but handle unexpected behavior
  * Add some serious try catches to this code so things don't go wrong

# Testing

* Write some unit tests (non-interactive testing)
* Is this queueing every video?
* Will the queue save videos even if it's in the process of shutting down?
* Breaking down into smaller, testable functions.
* Writing tests for these functions.

# Some bigger things to implement

* Be able to pause the program when certain conditions aren't met to prevent undefined behaviours.
  * In the following cases, the program should pause but not crash or stop running:
    * OBS isn't open / crashes / can't be accessed
    * OBS can't find elements that need to be accessed
    * Cannot connect to Twitch chat
    * Cannot connect to hardware / hardware emulator
  * In the following cases the program should stop running:
    * Can't access important secret keys / keys are not valid
* There should be more information displayed on stream as to what is happening with the program and robot

# Bugs / Needed Improvements

* If a link that doesn't work gets past initial filter, make sure it doesn't mess everything up.
* Why are other users seeing messages from berthatwo? All responses to !play commands should be whispers
* Doesn't always save the play queue (like when the hardware isn't working)
* check for the existence of needed files on launch (cuss_wrds.txt, secrets.env)
* "next up" onscreen element doesn't properly render after a restart. 
* Doesn't play the first video that's requested (on startup, or on restart)
* It currently plays image files (!play https://i.ytimg.com/vi/QNQQGO2WJbM/hqdefault.jpg?sqp=-oaymwE2CNACELwBSFXyq4qpAygIARUAAIhCGAFwAcABBvABAfgBvgSAAoAIigIMCAAQARhyIFooQDAP&rs=AOn4CLCaDbi7K59Dw3oIoKaZXVtCsKV8Nw)
* Implement a better peak and hold system. Solenoids shouldn't get so hot all the time.
* Make sure all solenoids turn off once done. There are often still signals left on after everything is done playing.
* The load and save queues features need to be repaired
* Ensure data transmission between Arduino and PC is reliable (https://github.com/beneater/error-detection-videos)
* Create a start message for visuals process
* If visuals.py can't connect to OBS after some time, the program will crash entirely.
  * What should the desired behaviour here be? If it can't connect, should it just wait until it can connect?
* Enable a GitHub action that cleans up python code?

# Notes

* Use this for mocking API's: https://requests-mock.readthedocs.io/en/latest/index.html (if needed)
* READ THIS: https://go.snyk.io/rs/677-THP-415/images/Python_Cheatsheet_whitepaper.pdf
