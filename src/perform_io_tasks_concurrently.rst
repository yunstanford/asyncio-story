How do you perform IO tasks concurrently in asyncio ?
=====================================================

Python3’s asyncio module and the async and await keywords combine to allow us to do cooperative concurrent programming, where a code path voluntarily yields control to a scheduler, trusting that it will get control back when some resource has become available (or just when the scheduler feels like it).


.. code-block:: python

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



.. code-block:: python

    import asyncio
    import logging
    import sys
    import time
    import aiohttp

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

    async def run_concurrently(n):
        """
        Run tasks concurrently.
        """
        session = aiohttp.ClientSession()
        tasks = [asyncio.ensure_future(io_bound_ops(i, session)) for i in range(n)]
        await asyncio.gather(*tasks)
        await session.close()

    def main():
        loop.run_until_complete(run_concurrently(10))

    main()

