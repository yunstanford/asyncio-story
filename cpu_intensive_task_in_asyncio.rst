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
