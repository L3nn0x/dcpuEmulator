import curses

def main(stdsrc):
	stdsrc.addstr(0, 0, "Current mode test", curses.A_REVERSE);
	stdsrc.refresh()
	c = stdsrc.getch()

#curses.wrapper(main)

