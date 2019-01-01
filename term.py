import contextlib
import termios
import fcntl
import sys
import os
import signal

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
	return wrap(f"[?{n}h", f"[?{n}l")

def umode(*n):
	n = ";".join(str(n) for n in n)
	return wrap(f"[?{n}l", f"[?{n}h")

def getch():
	fd = sys.stdin.fileno()
	flags_save = fcntl.fcntl(fd, fcntl.F_GETFL)
	fcntl.fcntl(fd, fcntl.F_SETFL, flags_save | os.O_NONBLOCK)
	while True:
		try:
			os.read(fd, 1024)
		except BlockingIOError:
			break
	fcntl.fcntl(fd, fcntl.F_SETFL, flags_save)
	return os.read(fd, 1024)

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
	signal.signal(signal.SIGWINCH, lambda _, _2: callback(*os.get_terminal_size()))
	callback(*os.get_terminal_size())
	try:
		yield
	finally:
		signal.signal(signal.SIGWINCH, old)