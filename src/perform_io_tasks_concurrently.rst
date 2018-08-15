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

Running this snippet of code,

.. code-block::

    $ time python3 examples/perform_io_tasks_sequentially.py
    2018-08-14 22:33:04,604 Started io bound task 0...
    2018-08-14 22:33:04,991 Finished io bound task 0...
    2018-08-14 22:33:04,992 Started io bound task 1...
    2018-08-14 22:33:05,125 Finished io bound task 1...
    2018-08-14 22:33:05,125 Started io bound task 2...
    2018-08-14 22:33:05,220 Finished io bound task 2...
    2018-08-14 22:33:05,220 Started io bound task 3...
    2018-08-14 22:33:05,470 Finished io bound task 3...
    2018-08-14 22:33:05,470 Started io bound task 4...
    2018-08-14 22:33:05,569 Finished io bound task 4...
    2018-08-14 22:33:05,569 Started io bound task 5...
    2018-08-14 22:33:05,669 Finished io bound task 5...
    2018-08-14 22:33:05,670 Started io bound task 6...
    2018-08-14 22:33:05,846 Finished io bound task 6...
    2018-08-14 22:33:05,846 Started io bound task 7...
    2018-08-14 22:33:05,935 Finished io bound task 7...
    2018-08-14 22:33:05,935 Started io bound task 8...
    2018-08-14 22:33:06,006 Finished io bound task 8...
    2018-08-14 22:33:06,007 Started io bound task 9...
    2018-08-14 22:33:06,092 Finished io bound task 9...

    real    0m1.895s
    user    0m0.398s
    sys     0m0.063s

We can see, the program runs like sequential manner, it starts and finishes tasks one by one. Can we run tasks concurrently ? Yep, `asyncio.gather` is your friend.

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

Running this snippet of code again, with improvement,

.. code-block::

    $ time python3 examples/perform_io_tasks_concurrently.py
    2018-08-14 22:37:03,553 Started io bound task 0...
    2018-08-14 22:37:03,568 Started io bound task 1...
    2018-08-14 22:37:03,568 Started io bound task 2...
    2018-08-14 22:37:03,569 Started io bound task 3...
    2018-08-14 22:37:03,569 Started io bound task 4...
    2018-08-14 22:37:03,570 Started io bound task 5...
    2018-08-14 22:37:03,570 Started io bound task 6...
    2018-08-14 22:37:03,570 Started io bound task 7...
    2018-08-14 22:37:03,571 Started io bound task 8...
    2018-08-14 22:37:03,572 Started io bound task 9...
    2018-08-14 22:37:03,738 Finished io bound task 0...
    2018-08-14 22:37:03,741 Finished io bound task 2...
    2018-08-14 22:37:03,748 Finished io bound task 8...
    2018-08-14 22:37:03,749 Finished io bound task 6...
    2018-08-14 22:37:03,752 Finished io bound task 3...
    2018-08-14 22:37:03,755 Finished io bound task 5...
    2018-08-14 22:37:03,757 Finished io bound task 1...
    2018-08-14 22:37:03,758 Finished io bound task 4...
    2018-08-14 22:37:03,758 Finished io bound task 9...
    2018-08-14 22:37:03,759 Finished io bound task 7...

    real    0m0.625s
    user    0m0.413s
    sys     0m0.068s

With `asyncio.gather`, tasks have been executed concurrently, the program runs much faster. `asyncio.gather` won’t necessarily run your coroutines in order, but it will return a list of results in the same order as its input.
