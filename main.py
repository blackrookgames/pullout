import asyncio
import sys

from pathlib import Path

from src import *

result = False

def test():
    task = cry.CryTaskTest()
    cry.queuetask(task)
    yield cry.CryTaskWait(task)
    print("Test")
    global result
    result = True

async def loop():
    looping = True
    error = None
    loop = asyncio.get_running_loop()
    time = loop.time()
    coroutine.create(test())
    while looping: # TODO: Change to app.looping or something
        _time = time
        time = loop.time()
        coroutine._m_update(time - _time)
        print(time - _time)
        await cry._m_update(loop)
        await asyncio.sleep(0.1)
    if error is None: return
    raise error

def main():
    if len(sys.argv) == 0: return 1
    try:
        apipath = Path(sys.argv[0]).resolve()\
            .parent\
            .joinpath("SECRET")\
            .joinpath("cdp_api_key.json")
        coroutine._m_init()
        cry._m_init(apipath)
        asyncio.run(loop())
    except helper.CLIError as _e:
        print(f"ERROR: {_e}", file = sys.stderr)
        return 1
    finally:
        cry._m_final()
        coroutine._m_final()
    return 0

if __name__ == "__main__":
    sys.exit(main())