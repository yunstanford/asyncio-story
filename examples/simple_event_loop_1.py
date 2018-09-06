from types import coroutine


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
		return [ready_streams.append(self._map[stream]) for stream in self._map if stream.ready()]

	def register(self, stream, listen_event, task):
		self._map[stream] = (listen_event, task)

	def unregister(self, stream):
		self._map.pop(stream)


class MyLoop:

	def __init__(self):
		self.selector = MySelect()

    def run_until_complete(self, task):
    	tasks = [(task, None)]
        try:
            while tasks or self.selector.get_map():
            	
                task.send(None)
        except StopIteration:
            pass


# Utilities control flow functions
##################################
@coroutine
def spawn(task):
	child = yield ('spawn', task)
	return child


@coroutine
def join(task):
	yield ('join', task)


async def gather(tasks):
	children_tasks = []
	for t in tasks:
		child = await spawn(t)
		children_tasks.append(t)

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
	stream = MyStream("A", wait_cycles=2)
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
