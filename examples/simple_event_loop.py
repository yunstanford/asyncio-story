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
my_loop.run_until_complete(task)

import asyncio
loop = asyncio.get_event_loop()
task = hello_world()
loop.run_until_complete(task)