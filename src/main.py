"""
This is the program that runs on the computer that is also running Audacity.
To communicate between computers it uses the websockets library.
Setup code and basis code comes from Audacity's test script:
https://github.com/audacity/audacity/blob/release-3.7.2/scripts/piped-work/pipe_test.py
"""

import sys
import os
import asyncio
from websockets.asyncio.client import connect

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

def offline_test(TOFILE, FROMFILE, EOL) -> None:
    """This is here to test that audacity does infact accept my recordings
    Also crashes it :3 """
    while True:
        r = 0
        match r:
            case 0:
                record_command(TOFILE, EOL)
                r = 1
            case 1:
                pause_command(TOFILE, EOL)
                r = 0

async def client(ip:str, port:int, TOFILE, FROMFILE, EOL):
    """Main function. This checks for new commands asyncronusly and runs them
    if so."""
    is_recording = False
    async with connect(f'ws://{ip}:{port}') as websocket:
        await websocket.send("Client Connected!")
        message = await websocket.recv()
        if message == 'rec' and is_recording:
            pause_command(TOFILE, EOL)
            await websocket.send("rcFalse")
        else:
            record_command(TOFILE, EOL)
            await websocket.send("rcTrue")



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

ip = input("ip> ")
noPort= True
while noPort:
    try:
        port = int(input("port> "))
        noPort = False
    except Exception:
        print("Bruh that is not an int.")
client(ip, port, TOFILE, FROMFILE, EOL)
# GG <3
# Made By Sam with Love and no gen ai :)
