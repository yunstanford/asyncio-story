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
