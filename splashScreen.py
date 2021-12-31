from tkinter import *

def splashScreen():
    splash = Tk()
    splash.overrideredirect(True)
    splash.geometry("{0}x{1}+0+0".format(splash.winfo_screenwidth(), splash.winfo_screenheight()))
    splash.configure(background='black')
    splash.after(2000, splash.destroy)
    bg = PhotoImage(file = "splash.png")
    lab = Label(splash, image = bg)
    lab.pack()

    splash.mainloop()