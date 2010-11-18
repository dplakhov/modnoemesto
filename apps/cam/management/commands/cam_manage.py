from django.core.management.base import BaseCommand, CommandError
from apps.cam.models import Camera, CameraType


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            (driver, host, username, password) = args
        except:
            raise

        import curses
        type = CameraType(name=driver, driver='apps.cam.drivers.%s' % driver)
        camera = Camera(
                type=type,
                host=host,
                username=username,
                password=password
                )
        control = camera.driver.control
        stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        stdscr.keypad(1)
        try:
            while 1:
                c = stdscr.getch()
                if c == curses.KEY_UP:
                    control.move_up()
                elif c == curses.KEY_DOWN:
                    control.move_down()
                elif c == curses.KEY_LEFT:
                    control.move_left()
                elif c == curses.KEY_RIGHT:
                    control.move_right()
                elif c == curses.KEY_NPAGE:
                    control.zoom_in()
                elif c == curses.KEY_PPAGE:
                    control.zoom_out()
                elif c == curses.KEY_HOME:
                    control.home()
                elif c == curses.KEY_END:
                    control.reset()

        except:
            pass

        curses.nocbreak()
        stdscr.keypad(0)
        curses.echo()
        
