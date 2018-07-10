How do you perform a CPU intensive operation ?
==============================================

The CPU-intensive working is blocking task from an event loop perspective, because the main loop will be blocked from dealing other tasks. Say, we have an event loop that is processing a cpu intensive task that doesn't involve any I/O, then we enqueue some I/O bound tasks. However, those enqueued I/O bound tasks will never been started/waited, until the cpu intensive task finished, because loop is ``blocked``. Let's take a look a small piece of code.


.. code-block:: python

    import asyncio
    import logging
    import sys
    import time

    loop = asyncio.get_event_loop()

    log = logging.getLogger(__name__)
    out_hdlr = logging.StreamHandler(sys.stdout)
    out_hdlr.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
    out_hdlr.setLevel(logging.INFO)
    log.addHandler(out_hdlr)
    log.setLevel(logging.INFO)

    async def cpu_bound_ops():
        """
        Simulation of a long-running CPU-bound operation
        """
        log.info("Started cpu intensive task...")
        time.sleep(10)
        log.info("Finished cpu intensive task...")

    async def io_bound_ops():
        """
        Simulation of a I/O-bound operation
        """
        log.info("Started io bound task...")
        await asyncio.sleep(6.0)
        log.info("Finished io bound task...")

    async def tasks():
        await asyncio.gather(*[
                cpu_bound_ops(),
                io_bound_ops(),
                io_bound_ops(),
            ])

    def main():
        loop.run_until_complete(tasks())

    main()


Running this snippet of code,

.. code-block::

    2018-07-09 20:56:34,360 Started io bound task...
    2018-07-09 20:56:34,360 Started cpu intensive task...
    2018-07-09 20:56:44,364 Finished cpu intensive task...
    2018-07-09 20:56:44,365 Started io bound task...
    2018-07-09 20:56:44,365 Finished io bound task...
    2018-07-09 20:56:50,368 Finished io bound task...

We can see, ``asyncio.gather`` only started one io-bound task and one cpu intensive task,
it hasn't started all tasks, because the cpu intensive one has blocked event loop.
The other io-bound task has been started after the cpu intensive one finished.


Can we improve it ? we could fire off processes for the CPU-intensive tasks and have them report back to the main loop when done.

.. code-block:: python

    import asyncio
    import logging
    import sys
    import time
    import multiprocessing

    loop = asyncio.get_event_loop()

    CPU_COUNT = multiprocessing.cpu_count()
    executor = ProcessPoolExecutor(max_workers=CPU_COUNT)

    log = logging.getLogger(__name__)
    out_hdlr = logging.StreamHandler(sys.stdout)
    out_hdlr.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
    out_hdlr.setLevel(logging.INFO)
    log.addHandler(out_hdlr)
    log.setLevel(logging.INFO)

    def cpu_bound_ops():
        """
        Simulation of a long-running CPU-bound operation
        """
        log.info("Started cpu intensive task...")
        time.sleep(10)
        log.info("Finished cpu intensive task...")

    async def io_bound_ops():
        """
        Simulation of a I/O-bound operation
        """
        log.info("Started io bound task...")
        await asyncio.sleep(6.0)
        log.info("Finished io bound task...")

    async def tasks():
        await asyncio.gather(*[
                loop.run_in_executor(executor, cpu_bound_ops),
                io_bound_ops(),
                io_bound_ops(),
            ])

    def main():
        loop.run_until_complete(tasks())

    main()


Running this snippet of code again, with improvement,

.. code-block::

    2018-07-09 20:56:24,354 Started io bound task...
    2018-07-09 20:56:24,354 Started io bound task...
    2018-07-09 20:56:24,356 Started cpu intensive task...
    2018-07-09 20:56:30,358 Finished io bound task...
    2018-07-09 20:56:30,358 Finished io bound task...
    2018-07-09 20:56:34,357 Finished cpu intensive task...

you can see io bound tasks and cpu intensive task started almost at same time, and io bound tasks (6 sec) finished earlier than the cpu intensive task (10 sec) as expected, because event loop has not been blocked this time.
