a simple event loop
===================

You might ask yourself while using asyncio, what does asyncio do under the hood, and how could I implement an event loop ? Consider,

- coroutine/generator
- asyncio task
- event loop
- I/O
- sleep/timers


-------------------------
Generators and Coroutines
-------------------------

A ``generator`` is a function that produces a sequence of values. It generates a series of values through the ``yield`` statement.

- Generator doesn't produce all values at one time, it only generate value when you "need" it (calling ``.next()`` in python2 or ``next(generator)`` in python3). it doesn't waste memory.
- Calling a generator function creates an generator object. However, it does not start running the function, until the ``.next()`` call.
- The function only executes on ``next()``.
- ``yield`` produces a value, but suspends the function.
- Function resumes on next call to `next()`.
- If a generator function calls return or reaches the end its definition, a ``StopIteration`` exception is raised.

let's go through simple code snippet.

.. code-block:: python

    def generate_numbers(n):
        print("starting generating numbers...")
        for i in range(n):
            yield i

    # python2.7
    >>> g = generate_numbers(3)
    >>> g
    <generator object generate_numbers at 0x108808a50>
    # generator has not been started, it didn't print anything
    >>> g.next()
    starting generating numbers...
    0
    >>> g.next()
    1
    >>> g.next()
    2
    >>> g.next()
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    StopIteration


In `python 2.5`, `PEP342 <https://www.python.org/dev/peps/pep-0342/>`_ introduced a feature of sending stuff into a paused ``generator``, python has the concept of ``coroutines`` then. Among other things, ``PEP342`` introduced the ``send()`` method on generators. This allowed one to not only pause generators, but to send a value back into a generator where it paused.

- ``coroutine`` do more than pause function and generate value, it can also consume values sent to it
- Sent values are returned by ``(yield)``
- Execution is the same as for a generator
- When you call a coroutine, nothing happens, they only run in response to ``next()`` and ``send()`` methods

.. code-block:: python

    def compare_numbers(n):
        print("Does input number less than {} ?".format(n))
        while True:
            i = (yield)
            if i < n:
                print("yes!")
            else:
                print("no!")

    >>> c = compare_numbers(5)
    # did not print anything
    >>> c.next()
    # coroutine starts running after first .next() call
    Does input number less than 5 ?
    >>> c.send(3)
    yes!
    >>> c.send(10)
    no!

------------
asyncio task
------------

What do we actually do when defining ``async def`` function in ``> Python 3.5`` ? Let's see,

.. code-block:: python

    async def hello_world():
        print("hey, hello world!")

    # create coroutine
    coro = hello_world()

    >>> type(coro)
    <class 'coroutine'>
    >>> type(coro.send)
    <class 'builtin_function_or_method'>
    >>> type(coro.throw)
    <class 'builtin_function_or_method'>

Note that the code above never printed our "hey, hello world!" message. That's because nothing happened, we never actually executed statements inside the coroutine function, we simply created the coroutine object.


But, how can we execute the coroutine ? We can schedule it by calling ``.send(None)``.

.. code-block:: python

    >>> coro.send(None)
    hey, hello world!
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    StopIteration


As we can see, a couroutine object's ``.send(None)`` method raises ``StopIteration``. We can try schedule the coroutine and catch
``StopIteration``.

.. code-block:: python

    >>> try:
    >>>     coro.send(None)
    >>> except StopIteration:
    >>>     pass
    hey, hello world!


We've seen how task runs, but what happens if task raises ``Exception`` ?

.. code-block:: python

    async def hello_world():
        raise ValueError("hey, hello world!")

    # create coroutine
    coro = hello_world()

    >>> try:
    >>>     coro.send(None)
    >>> except Exception as e:
    >>>     print("Catch coroutine's exception {}".format(str(e)))


Next, you may wonder how ``.throw()`` come into place ?


----------
Event Loop
----------

In our previous discussion, we know that ``.send(None)`` could resume coroutine, but in reality, we may not know how many times that
a coroutine could yield control beforehand. WE NEED A LOOP.


.. code-block:: python

    async def say_hello():
        print("hey, hello world!")

    async def hello_world():
        print("Resume coroutine.")
        for i in range(3):
            await say_hello()
        print("Finished coroutine.")


    # create coroutine
    coro = hello_world()

    >>> try:
    >>>     while 1:
    >>>         coro.send(None)
    >>> except StopIteration:
    >>>     print("Exit the Loop..")

    Resume coroutine.
    hey, hello world!
    hey, hello world!
    hey, hello world!
    Finished coroutine.
    Exit the Loop..


Does it look familar ? Yep! You guessed it, it's basically ``loop.run_until_complete``.

.. code-block:: python

    async def say_hello():
        print("hey, hello world!")

    async def hello_world():
        print("Resume coroutine.")
        for i in range(3):
            await say_hello()
        print("Finished coroutine.")

    class MyLoop:

        def run_until_complete(self, task):

            try:
                while 1:
                    task.send(None)
            except StopIteration:
                pass

    my_loop = MyLoop()
    task = hello_world()
    my_loop.run_until_complete()

    import asyncio
    loop = asyncio.get_event_loop()
    task = hello_world()
    loop.run_until_complete(task)

    # console logs
    $ python3 examples/simple_event_loop.py
    Resume coroutine.
    hey, hello world!
    hey, hello world!
    hey, hello world!
    Finished coroutine.
    Resume coroutine.
    hey, hello world!
    hey, hello world!
    hey, hello world!
    Finished coroutine.

Oh, we've just implemented a simple event loop!

Wait... In reality, task could be suspended (not ready) due to I/O operations, and event loop should push it back to the queue. Let's consider,

- ``Suspend`` the task when involves I/O, so it doesn't block the main thread.
- ``Resume`` the task when stream I/O is ready (epoll, kqueue).

As such, our async python process could fully utilize CPU, and something like ``asyncio.gather`` for running tasks concurrently. Considering these factors, let's take a look a little bit more complicated event loop.


.. code-block:: python

    from types import coroutine
    from collections import defaultdict


    # customized Stream class for demo purpose
    class MyStream:

        def __init__(self, name, wait_cycles=1):
            self.name = name
            self.wait_cycles = wait_cycles

        def ready(self):
            self.wait_cycles = self.wait_cycles - 1
            return self.wait_cycles <= 0

        def write(self, data):
            print("Stream {} writing {}...".format(self.name, data))

        def read(self):
            print("Stream {} is reading...".format(self.name))


    EVENT_READ = "EVENT_READ"
    EVENT_WRITE = "EVENT_WRITE"


    # simplied select for demo purpose
    class MySelect:

        def __init__(self):
            # Map: stream => (event_type, task)
            self._map = {}

        def get_map(self):
            return self._map

        def select(self):
            """ check if I/O is ready """
            return {stream: self._map[stream] for stream in self._map if stream.ready()}

        def register(self, stream, listen_event, task):
            self._map[stream] = (listen_event, task)

        def unregister(self, stream):
            self._map.pop(stream)


    class MyLoop:

        def __init__(self):
            self.selector = MySelect()

        def run_until_complete(self, task):
            tasks = [(task, None)]
            watch = defaultdict(list)

            while tasks or self.selector.get_map():

                # fetch ready streams
                ready_streams = []
                selected = self.selector.select()
                for stream, data in selected.items():
                    event, task = data
                    tasks.append((task, None))
                    ready_streams.append(stream)
                    # unregister ready_streams
                    self.selector.unregister(stream)

                queue, tasks = tasks, []

                for task, data in queue:
                    try:
                        data = task.send(data)
                    except StopIteration: # finished the task
                        tasks.extend((t, None) for t in watch.pop(task, []))
                    else:
                        if data and data[0] == SPAWN:
                            tasks.append((data[1], None))
                            tasks.append((task, data[1]))
                        elif data and data[0] == JOIN:
                            watch[data[1]].append(task)
                        elif data and data[0] == EVENT_READ:
                            self.selector.register(data[1], EVENT_READ, task)
                        elif data and data[0] == EVENT_WRITE:
                            self.selector.register(data[1], EVENT_WRITE, task)
                        else:
                            tasks.append((task, None))


    # Utilities control flow functions
    ##################################
    SPAWN = "spawn"
    JOIN = "join"


    @coroutine
    def spawn(task):
        child = yield (SPAWN, task)
        return child


    @coroutine
    def join(task):
        yield (JOIN, task)


    async def gather(tasks):
        children_tasks = []
        for t in tasks:
            child = await spawn(t)
            children_tasks.append(child)
        for t in children_tasks:
            await join(t)


    # Async Read and Write:
    # Return control to main thread (parent task) after task being scheduled
    ########################################################################
    @coroutine
    def read(stream):
        yield (EVENT_READ, stream)
        return stream.read()


    @coroutine
    def write(stream, data):
        yield (EVENT_WRITE, stream)
        return stream.write(data)


    async def hello_world_read():
        stream = MyStream("A", wait_cycles=20)
        await read(stream)


    async def hello_world_write():
        stream = MyStream("B", wait_cycles=1)
        await write(stream, "Hello World!")


    # Main
    ######
    async def hello_world():
        await gather([
            hello_world_read(), hello_world_write(),
        ])

    main = hello_world()
    my_loop = MyLoop()
    my_loop.run_until_complete(main)

    # console logs
    $ python3 examples/simple_event_loop_1.py
    Stream B writing Hello World!...
    Stream A is reading...


Apparently, task A doesn't block task B, and it finishes earlier than task B.


----------------
sleep and timers
----------------

`sleep/timer` is another interesting topic in `asyncio`, because we can not call `time.sleep` as it'll block the event loop from running tasks.


WIP
...
...


------------
Handling I/O
------------



----------
References
----------

Here are some references that might help you understand more.

-
-
-

