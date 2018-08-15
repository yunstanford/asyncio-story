import asyncio
import logging
import aiohttp
import sys
import time

loop = asyncio.get_event_loop()

log = logging.getLogger(__name__)
out_hdlr = logging.StreamHandler(sys.stdout)
out_hdlr.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
out_hdlr.setLevel(logging.INFO)
log.addHandler(out_hdlr)
log.setLevel(logging.INFO)

async def io_bound_ops(task_name, session):
    """
    Simulation of a I/O-bound operation
    """
    log.info("Started io bound task %s...", task_name)
    async with session.get("https://www.google.com") as rsp:
        await rsp.text()
    log.info("Finished io bound task %s...", task_name)

async def run_sequentially(n):
    """
    Run tasks sequentially.
    """
    session = aiohttp.ClientSession()
    for i in range(n):
        await io_bound_ops(i, session)
    await session.close()

def main():
    loop.run_until_complete(run_sequentially(10))

main()