import sys

import term
import jinx
import ui

def __main__():
	buf = open(sys.argv[1], "rb").read()
	u = ui.MainWindow(jinx.Jinx(buf))
	with term.raw(no_signals=True), term.altbuf, term.resize_pipe(b"~resize~") as pipe:
		while True:
			input = term.getch([pipe]).decode()
			u.input(input)
			print("\x1B[1;150H" + repr(input))
			print("\x1B[u", end="", flush=True)

if __name__ == "__main__":
	if not sys.stdout.isatty() and not sys.stdin.isatty():
		raise Exception("Not a tty!")
	__main__()
