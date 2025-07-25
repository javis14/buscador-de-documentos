try:
    from tkinter import *
    import fitz
    from tkinter.ttk import Progressbar
    from threading import Thread
    import math
except Exception as e:
    print(
        f"This error occured while importing neccesary modules or library {e}")


class ShowPdf():

    img_object_li = []

    def pdf_view(self, master, width=1200, height=600, pdf_location="", bar=True, load="after"):

        self.frame = Frame(master, width=width, height=height, bg="white")

        scroll_y = Scrollbar(self.frame, orient="vertical")
        scroll_x = Scrollbar(self.frame, orient="horizontal")

        scroll_x.pack(fill="x", side="bottom")
        scroll_y.pack(fill="y", side="right")

        percentage_view = 0
        percentage_load = StringVar()

        if bar == True and load == "after":
            self.display_msg = Label(textvariable=percentage_load)
            self.display_msg.pack(pady=10)

            loading = Progressbar(
                self.frame, orient=HORIZONTAL, length=100, mode='determinate')
            loading.pack(side=TOP, fill=X)

        self.text = Text(self.frame, yscrollcommand=scroll_y.set,
                         xscrollcommand=scroll_x.set, width=width, height=height)
        self.text.pack(side="left")

        scroll_x.config(command=self.text.xview)
        scroll_y.config(command=self.text.yview)

        def add_img():
            precentage_dicide = 0
            open_pdf = fitz.open(pdf_location)
            self.img_object_li.clear()

            for page in open_pdf:
                pix = page.get_pixmap()
                pix1 = fitz.Pixmap(pix, 0) if pix.alpha else pix
                img = pix1.tobytes("ppm")
                timg = PhotoImage(data=img)
                self.img_object_li.append(timg)
                if bar == True and load == "after":
                    precentage_dicide = precentage_dicide + 1
                    percentage_view = (
                        float(precentage_dicide)/float(len(open_pdf))*float(100))
                    loading['value'] = percentage_view
                    percentage_load.set(
                        f"Please wait!, your pdf is loading {int(math.floor(percentage_view))}%")
            if bar == True and load == "after":
                loading.pack_forget()
                self.display_msg.pack_forget()

            for i in self.img_object_li:
                self.text.image_create(END, image=i)
                self.text.insert(END, "\n\n")
            self.text.configure(state="disabled")

        def start_pack():
            t1 = Thread(target=add_img)
            t1.start()

        if load == "after":
            master.after(250, start_pack)
        else:
            start_pack()

        return self.frame


def main():
    root = Tk()
    root.geometry("700x780")
    d = ShowPdf().pdf_view(
        root, pdf_location=r"D:\DELL\Documents\Encyclopedia GUI.pdf", width=50, height=200)
    d.pack()
    root.mainloop()


if __name__ == '__main__':
    main()
