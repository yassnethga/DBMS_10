import tkinter as tk
import api
from connection_dialog import ConnectionDialog
from ui import App


def main():
    root = tk.Tk()
    root.withdraw()

    dialog = ConnectionDialog(root)
    if not dialog.confirmed:
        root.destroy()
        return

    api.BASE_URL = dialog.url
    api.HEADERS = {"X-API-Key": dialog.key}

    root.destroy()
    App().mainloop()


if __name__ == "__main__":
    main()
