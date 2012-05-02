from isobar.pattern.core import *

import inspect
import math

class PStaticViaOSC (Pattern):
	initialised = False
	
	def __init__(self, default = 0, address = "/value", port = 9900):
		if not PStaticViaOSC.initialised:
			import osc

			osc.init()
			osc.listen(port = port)

		self.value = default
		self.address = address
		osc.bind(self.recv, address)

	def recv(self, msg, source = None):
		address = msg[0]
		signature = msg[1][1:]
		print "(%s) %s" % (address, signature)
		self.value = msg[2]

	def next(self):
		return self.value

class PStaticTimeline (Pattern):
	""" PStaticTimeline: Returns the position (in beats) of the current timeline. """

	def __init__(self):
		pass

	def next(self):
		beats = self.get_beats()
		return round(beats, 5)

	def get_beats(self):
		#------------------------------------------------------------------------
		# determine the Timeline object we are embedded within and return
		# its current number of beats.
		#------------------------------------------------------------------------
		"""
		stack = inspect.stack()
		for frame in stack:
			frameobj = frame[0]
			args, _, _, value_dict = inspect.getargvalues(frameobj)
			if len(args) and args[0] == 'self':
				instance = value_dict.get('self', None)
				classname = instance.__class__.__name__
				if classname == "Timeline":
					#------------------------------------------------------------------------
					# round to 5 DP to prevent rounding errors which may give us 
					# a value of N.9999999....
					#------------------------------------------------------------------------
					return instance.beats
		"""
		timeline = self.timeline
		if timeline:
			return timeline.beats

		return 0

class PStaticGlobal(Pattern):
	""" PStaticGlobal: Static global value identified by a string, with OSC listener """
	dict = {}
	listening = False

	def __init__(self, name, value = None):
		self.name = name
		if value is not None:
			PStaticGlobal.set(name, value)

	def next(self):
		name = Pattern.value(self.name)
		return PStaticGlobal.dict[name]

	@classmethod
	def set(self, key, value):
		print "setting %s to %s" % (key, value)
		PStaticGlobal.dict[key] = value

	@classmethod
	def listen(self, prefix = "/global", port = 9900):
		if not PStaticGlobal.listening:
			import osc

			osc.init()
			osc.listen(port = port)
			PStaticGlobal.listening = True

		self.prefix = prefix
		osc.bind(self.recv, prefix)

	@classmethod
	def recv(self, msg, source = None):
		address = msg[0]
		signature = msg[1][1:]
		print "(%s) %s" % (address, signature)
		key = msg[2]
		value = msg[3]
		PStaticGlobal.set(key, value)

class PStaticTimelineSine(PStaticTimeline):
	def __init__(self, period):
		self.period = period

	def next(self):
		period = Pattern.value(self.period)
		# self.phase += math.pi * 2.0 / period

		beats = self.get_beats()
		rv = math.sin(2 * math.pi * beats / self.period)
		return rv


class PStaticSeq(Pattern):
	def __init__(self, sequence, duration):
		self.sequence = sequence
		self.duration = duration
		self.start = None
	
	def next(self):
		timeline = self.timeline
		if self.start is None:
			self.start = round(timeline.beats, 5)

		now = round(timeline.beats, 5)
		if now - self.start >= self.duration:
			self.sequence.pop(0)
			self.start = now
			if len(self.sequence) == 0:
				raise StopIteration
		return self.sequence[0]
