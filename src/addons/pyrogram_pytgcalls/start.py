import os
import asyncio

import pytgcalls
import pyrogram

import config as cfg


class RadioMesa():
    _init = False
    client = pyrogram.Client(
        cfg.USERBOT_SESSION,
        api_hash=cfg.USERBOT_API_HASH,
        api_id=cfg.USERBOT_API_ID,
    )

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(RadioMesa, cls).__new__(cls)
        return cls.instance
    
    def __init__(self) -> None:
        pass
    
    async def init(self):
        if self._init == True:
            raise "Alredy init"

        await self.client.start()
        while not self.client.is_connected:
            await asyncio.sleep(1)
        self.group_call = pytgcalls.GroupCall(self.client, '')
        self._init = True
    
    def get_group_call(self):
        return self.group_call


    # to change audio file you can do this:
    # group_call.input_filename = 'input2.raw'

    # to change output file:
    # group_call.output_filename = 'output2.raw'

    # to restart play from start:
    # group_call.restart_playout()

    # to stop play:
    # group_call.stop_playout()

    # same with output (recording)
    # .restart_recording, .stop_output

    # to mute yourself:
    # group_call.set_is_mute(True)

    # to leave a VC
    # group_call.stop()

    # to rejoin
    # group_call.rejoin()
