import tkinter as tk
from tkinter import Label
from  tkinter import ttk
import DataQuery


def GENRE_SELECTOR(tracks):
    content = DataQuery.getAllFieldValues(tracks, "genre")
    Window = tk.Toplevel()
    canvas = tk.Canvas(Window, height=600, width=100)

    tbl_genre = ttk.Treeview(Window, height=600)
    tbl_genre['columns'] = ('', 'Genre', 'track count')

    vsb = ttk.Scrollbar(Window, orient="vertical", command=tbl_genre.yview)
    vsb.pack(side='right', fill='y')
    tbl_genre.configure(yscrollcommand=vsb.set)

    text_lbl = ""
    content = dict(sorted(content.items()))
    content = dict(sorted(content.items(), key= lambda item: item[1], reverse=True))
    for c in content.keys():
        #text_lbl += c + " (" + str(content[c]) + ")\n"
        tbl_genre.insert(parent='', index='end', values=('', c, content[c]))
    lbl_genres = Label(Window, text=text_lbl, padx=2, pady=5)
    #lbl_genres.pack()

    tbl_genre.pack()
    canvas.pack()