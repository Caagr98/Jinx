import term
import sys
import jinx
import ui

def __main__():
	buf = open("/home/yuki/anime/eou2/formal/mo2r00_game.sav", "rb").read()
	u = ui.MainWindow(jinx.Jinx(buf))
	with term.raw(no_signals=True), term.altbuf, term.hide_cursor:
		u.render()
		while True:
			k = term.getch().decode()
			u.input(k)
			u.render()
def enc(s):
	return "".join(c if c.isprintable() else '·' for c in s.decode("latin1"))

if __name__ == "__main__":
	if not sys.stdout.isatty() and not sys.stdin.isatty():
		raise Exception("Not a tty!")
	__main__()
