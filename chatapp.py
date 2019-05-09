import tkinter as tk
import random
import _thread
import socket
from datetime import datetime


name = 'Somebody'
discrim = ''.join([str(random.randint(1, 9)) for _ in range(0, 4)])
print(f'{name}#{discrim}')


class MainApp(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.textbox = tk.Text(state=tk.DISABLED)
        self.textbox.pack(side='top', fill=tk.BOTH, expand=True)
        self.entrybox = tk.Entry()
        self.entrybox.pack(fill='x', expand=True)
        self.sendbutton = tk.Button(text='Send your message', command=self.send_text, cursor='exchange')
        self.sendbutton.pack(side='bottom', fill='x', expand=False)
        self.winfo_toplevel().title('Communicator')  # App name
        self.client = None

    def add_text(self, text: str, after: int=25):
        self.textbox.config(state=tk.NORMAL)
        if after < len(self.textbox_text.split('\n')):
            self.textbox_removefirstline(after=after)  # This is so we can reduce the amount of lines
        self.textbox.insert(tk.END, f'\n{text}')
        self.textbox.update()
        self.textbox.config(state=tk.DISABLED)

    def send_text(self):
        text = self.entrybox_text
        now = datetime.now()
        timestamp = f'{now.hour}:{now.minute}'
        self.add_text(f'[{timestamp}] {name}#{discrim}: {text}')
        self.client.send(f'[{timestamp}] {name}#{discrim}: {text}')
        self.clear_entryboxtext()

    def clear_entryboxtext(self):
        self.entrybox.delete(0, tk.END)

    def textbox_removefirstline(self, after: int=25):
        self.textbox.config(state=tk.NORMAL)
        text = self.textbox_text
        if after < len(text.split('\n')):
            end = text.find('\n')
            text = text[end + 1:]  # + 1 to remove the newline
            self.textbox.replace(1.0, tk.END, text)
        self.textbox.config(state=tk.DISABLED)

    @property
    def entrybox_text(self):
        return self.entrybox.get()

    @property
    def textbox_text(self):
        text = self.textbox.get(1.0, tk.END)
        return text


class Client:
    def __init__(self, app: MainApp):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.port = 6666
        self.address = 'ADDRESS'
        self.addr = (self.address, self.port)
        self.id = self.connect()
        self.app = app

    def connect(self):
        try:
            self.client.connect(self.addr)
            self.client.send(f'{name},{discrim}'.encode())  # Initial payload
            return self.client.recv(4096)
        except Exception as _:
            raise _

    def send(self, text: str):
        try:
            self.client.send(text.encode())
        except Exception as _:
            raise _

    def on_receive(self):
        while True:
            try:
                data = self.client.recv(4096)
                decoded = data.decode('utf-8')
                if not data:
                    break
                print(f'Data received: {decoded}')
                _thread.start_new_thread(self.app.add_text, (decoded,))
            except Exception as _:
                raise _


if __name__ == '__main__':
    root = tk.Tk()
    root.geometry = (600, 600)
    app = MainApp(root)
    app.pack(side='top', fill='both', expand=True)

    c = Client(app)
    app.client = c
    _thread.start_new_thread(c.on_receive, ())

    root.mainloop()
