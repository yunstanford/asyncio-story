a simple event loop
===================

a simple event loop

How to implement an event loop ?

- coroutine/generator
- a loop and tasks
- I/O
- sleep/timers


-------------------------
Generators and Coroutines
-------------------------

A ``generator`` is a function that produces a sequence of values. It generates a series of values through the ``yield`` statement.

- Generator doesn't produce all values at one time, it only generate value when you "need" it (calling ``.next()``).
- Calling a generator function creates an generator object. However, it does not start running the function, until the ``.next()`` call.
- The function only executes on ``next()``.
- ``yield`` produces a value, but suspends the function.
- If a generator function calls return or reaches the end its definition, a ``StopIteration`` exception is raised.

let's go through simple code snippet.

.. code-block:: python

    def generate_numbers(n):
        for i in range(n):
            yield i


----------------
a loop and tasks
----------------


----------------
a loop and tasks
----------------


----------------
sleep and timers
----------------
