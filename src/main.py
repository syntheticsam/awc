"""
This is the program that runs on the computer that is also running Audacity.
To communicate between computers it uses the websockets library.
Setup code and basis code comes from Audacity's test script:
https://github.com/audacity/audacity/blob/release-3.7.2/scripts/piped-work/pipe_test.py
"""

import sys
import os
import asyncio
from websockets.asyncio.server import serve

def check_setup() -> list:
    """This function checks the users current operating system and returns
    the correct values needed for communication through Audacity.
    This is bad code. """
    if sys.platform == 'win32':
        print("Hello world! Starting setup.")
        TONAME = '\\\\.\\pipe\\ToSrvPipe'
        FROMNAME = '\\\\.\\pipe\\FromSrvPipe'
        EOL = '\r\n\0'
        return [TONAME, FROMNAME, EOL]
    else:
        print("Hello world! Starting setup.")
        TONAME = '/tmp/audacity_script_pipe.to.' + str(os.getuid())
        FROMNAME = '/tmp/audacity_script_pipe.from.' + str(os.getuid())
        EOL = '\n'
        return [TONAME, FROMNAME, EOL]

def record_command(TOFILE, EOL) -> None:
    """Send the record command to Audacity."""
    print("Attempting to toggle recording.")
    TOFILE.write("Record1stChoice:" + EOL)
    TOFILE.flush()

def pause_command(TOFILE, EOL) -> None:
    """Send the pause command to Audacity."""
    print("Attempting to pause recording.")
    TOFILE.write("Pause:" + EOL)
    TOFILE.flush()

def audacity_check(TONAME, FROMNAME) -> None:
    """Check Audacity is set up and working correctly."""
    print("Write to  \"" + TONAME + "\"")
    if not os.path.exists(TONAME):
        print(" ..does not exist.  Ensure Audacity is running with mod-script-pipe.")
        sys.exit()

    print("Read from \"" + FROMNAME + "\"")
    if not os.path.exists(FROMNAME):
        print(" ..does not exist.  Ensure Audacity is running with mod-script-pipe.")
        sys.exit()


async def commander(websocket):
    global TOFILE, FROMFILE, EOL
    async for message in websocket:
        a = message.split()
        if a[0] == "recStop":
            print("Pausing!")
            pause_command(TOFILE, EOL)
        elif a[0] == "recStart":
            print("Recording")
            record_command(TOFILE, EOL)
        else:
            print(message)


async def main():
    """Main function. This checks for new commands asyncronusly and runs them
    if so."""
    async with serve(commander, "localhost", 8001) as server:
        await server.serve_forever()


# The following is bad code. But ahh well.
setup_list = check_setup()
TONAME = setup_list[0]
FROMNAME = setup_list[1]
EOL = setup_list[2]

audacity_check(TONAME, FROMNAME)

TOFILE = open(TONAME, 'w')
print("-- File to write to has been opened")
FROMFILE = open(FROMNAME, 'rt')
print("-- File to read from has now been opened too\r\n")


asyncio.run(main())
# GG <3
# Made By Sam with Love and no gen ai :)
