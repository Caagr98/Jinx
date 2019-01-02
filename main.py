import sys

import term
import jinx
import ui

def __main__():
	buf = open(sys.argv[1], "rb").read()
	u = ui.MainWindow(jinx.Jinx(buf))
	with term.raw(no_signals=True), term.altbuf, term.hide_cursor, term.resize_pipe(b"~resize~") as pipe:
		u.render()
		while True:
			u.input(term.getch([pipe]).decode())

if __name__ == "__main__":
	if not sys.stdout.isatty() and not sys.stdin.isatty():
		raise Exception("Not a tty!")
	__main__()
