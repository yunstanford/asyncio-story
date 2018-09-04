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
            while 1:
                task.send(None)
        except StopIteration:
            pass


@coroutine
def spawn(task):
	child = yield ('spawn', task)
	return child


@coroutine
def join(task):
	yield ('join', task)


@coroutine
def read(stream):
	yield (EVENT_READ, stream)
	return stream.read()


@coroutine
def write(stream, data):
	yield (EVENT_WRITE, stream)
	return stream.write(data)


def gather(tasks):
	pass


async def hello_world():
	read_stream = MyStream("A", wait_cycles=2)
	write_stream = MyStream("B", wait_cycles=1)
