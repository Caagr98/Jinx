class Jinx:
	__slots__ = ["buffer", "fname", "written", "insert", "char", "half", "_undo", "_redo", "encoding", "_start", "_end", "_edit", "_lastWrite"]
	def __init__(self, buffer, position=0, fname=None):
		self.buffer = bytearray(buffer)
		self.fname = fname

		self.written = None
		self.insert = self.char = False
		self.half = False
		self._undo = []
		self._redo = []
		self._edit = self._lastWrite = 0

		self.position = position

		self.encoding = "latin1"

	@property
	def start(self):
		return self._start
	@start.setter
	def start(self, v):
		self._start = max(0, min(v, len(self.buffer)))
	@property
	def end(self):
		return self._end
	@end.setter
	def end(self, v):
		self._end = max(0, min(v, len(self.buffer)))

	@property
	def position(self):
		return self.start + self._nwritten - self.half
	@position.setter
	def position(self, pos):
		self.start = self.end = pos

	def __getitem__(self, idx):
		if idx < self.start: return self.buffer[idx]
		if idx < self.start + self._nwritten: return self.written[idx - self.start]
		return self.buffer[idx - self._nwritten + (self.end - self.start)]
	def __len__(self):
		return len(self.buffer) + self._nwritten - (self.end - self.start)
	@property
	def _nwritten(self):
		if self.written is None: return 0
		return len(self.written)

	@property
	def modified(self):
		print(self._edit, self._lastWrite)
		return self._edit != self._lastWrite or self.written is not None

	def begin(self):
		if self.written is None:
			self.written = bytearray()

	def commit(self):
		if self.written is not None:
			self._undo.append((self.start, self.start+self._nwritten, self.buffer[self.start:self.end], self._edit))
			self._redo.clear()
			self._edit = self._edit + 1

			self.buffer[self.start:self.end] = self.written

			self.position = self.start + self._nwritten
			self.written = None
		if self.half:
			self.half = False
			self.position -= 1

	def _undoredo(self, undo, redo):
		if undo:
			start, end, text, edit = undo.pop()
			redo.append((start, start+len(text), self.buffer[start:end], self._edit))
			self.buffer[start:end] = text
			self.position = end
			self._edit = edit

	def undo(self): self._undoredo(self._undo, self._redo)
	def redo(self): self._undoredo(self._redo, self._undo)

	def write_key(self, key):
		if self.char:
			if key.isprintable():
				try:
					ch = key.encode(self.encoding)
				except:
					pass
				else:
					self.begin()
					self.written.extend(ch)
					self.end += (not self.insert) * len(ch)
					return True
		else:
			if key in "0123456789abcdefABCDEF":
				self.begin()
				if self.half:
					self.written[-1] = (self.written[-1] << 4) | int(key, 16)
					self.half = False
				else:
					self.written.append(int(key, 16))
					self.end += not self.insert
					self.half = True
				return True
		return False

	def erase(self):
		if self.written:
			del self.written[-1]
		else:
			self.start -= 1
		self.end -= not self.insert
