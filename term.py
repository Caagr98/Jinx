import contextlib
import termios
import fcntl
import sys
import os
import signal
import select

@contextlib.contextmanager
def raw(*, no_signals):
	fd = sys.stdin.fileno()
	attrs_save = termios.tcgetattr(fd)
	attrs = list(attrs_save)
	attrs[3] &= ~termios.ECHO # Don't echo
	attrs[3] &= ~termios.ICANON # Give instantly
	if no_signals:
		attrs[3] &= ~termios.ISIG # Don't send signals
	termios.tcsetattr(fd, termios.TCSANOW, attrs)
	try:
		yield
	finally:
		termios.tcsetattr(fd, termios.TCSAFLUSH, attrs_save)

@contextlib.contextmanager
def wrap(pre, suf):
	print(pre, end="", flush=True)
	try:
		yield
	finally:
		print(suf, end="", flush=True)

def mode(*n):
	n = ";".join(str(n) for n in n)
	return wrap(f"\x1B[?{n}h", f"\x1B[?{n}l")

def umode(*n):
	n = ";".join(str(n) for n in n)
	return wrap(f"\x1B[?{n}l", f"\x1B[?{n}h")

def getch(fds=[]):
	fd = sys.stdin.fileno()
	flags_save = fcntl.fcntl(fd, fcntl.F_GETFL)
	fcntl.fcntl(fd, fcntl.F_SETFL, flags_save | os.O_NONBLOCK)
	while True:
		try:
			os.read(fd, 1024)
		except BlockingIOError:
			break
	fcntl.fcntl(fd, fcntl.F_SETFL, flags_save)
	return os.read(select.select([fd] + fds, [], [])[0][0], 1024)

altbuf_noclear = mode(1047)
altbuf = mode(1049)
hide_cursor = umode(25)

def event_mouse(level=0, scroll=False):
	modes = [1006]
	if level is not None:
		modes.append([1000, 1002, 1003][level])
	if scroll:
		modes.append(1007)
	return mode(*modes)
event_focus = mode(1004)
event_paste = mode(2004)

@contextlib.contextmanager
def on_resize(callback):
	old = signal.getsignal(signal.SIGWINCH)
	signal.signal(signal.SIGWINCH, lambda _, _2: callback())
	callback()
	try:
		yield
	finally:
		signal.signal(signal.SIGWINCH, old)

@contextlib.contextmanager
def resize_pipe(command, w=None):
	def write_pipe():
		os.write(w, command)
	r = None
	if w is None:
		r, w = os.pipe()
	try:
		with on_resize(write_pipe):
			yield r
	finally:
		if r is not None:
			os.close(r)
			os.close(w)
