import requests
from tkinter import *
import socket
import time
from tkinter import messagebox
from configparser import ConfigParser

class MyFrame(Frame):
    def __init__(self):
        Frame.__init__(self)
        self.master.title("Barcode Tubes")
        self.master.rowconfigure(5, weight=1)
        self.master.columnconfigure(5, weight=1)
        self.grid(sticky=W + E + N + S)
        self.itemnameText = StringVar()
        self.ldfidText = StringVar()
        self.itemdescriptionText = StringVar()

        # tube barcode
        self.guitubebarcodelabel = Label(self, text="Tube Barcode:")
        self.guitubebarcode = Label(self, text="Waiting For Read")
        self.guitubebarcodelabel.grid(row=1, column=0, sticky=W)
        self.guitubebarcode.grid(row=1, column=1, sticky=W)

        #item name
        self.guiitemnamelabel = Label(self, text="Item Name")
        self.guiitemname = Entry(self, textvariable=self.itemnameText)
        self.guiitemnamelabel.grid(row=2, column=0, sticky=W)
        self.guiitemname.grid(row=2, column=1, sticky=W)

        # LDF id text
        self.guildfidlabel = Label(self, text="LDF ID")
        self.guildfid = Entry(self, textvariable=self.ldfidText)
        self.guildfidlabel.grid(row=3, column=0, sticky=W)
        self.guildfid.grid(row=3, column=1, sticky=W)

        #text description
        self.guiitemdescriptionlabel = Label(self, text="Desciption")
        self.guiitemdescription = Text(self, height=3)
        self.guiitemdescriptionlabel.grid(row=4, column=0, sticky=W)
        self.guiitemdescription.grid(row=4, column=1, sticky=W)

        self.read_barcode = Button(self, text="Query", command=self.read)
        self.read_barcode.grid(row=6, column=0, sticky=W)

        self.read_barcode2 = Button(self, text="Read", command=self.read2)
        self.read_barcode2.grid(row=5, column=0, sticky=W)

        self.update_entry_button = Button(self, text="Update Entry", command=self.update_entry_in_amos)
        self.update_entry_button.grid(row=7, column=0, sticky=W)

        self.close_button = Button(self, text="Quit", command=Frame.quit)
        self.close_button.grid(row=8, column=0, sticky=W)

    def request_json_of_barcode(self, barcode_id):

        try:
            r = requests.get(parser.get('config_file', 'amos_url')+ 'amos/api/v1.0/request_tube/',
                         headers={'tube_barcode': barcode_id})

            if r.json():
                self.update_gui_with_result(r.json())

            else:
                messagebox.showinfo("Error", "AMOS Error")
        except:
            messagebox.showinfo("Error", "AMOS Error")

    def read(self):

        if self.guitubebarcode['text'] == 'Waiting For Read':
            messagebox.showinfo('Error','Sorry Barcode not read. Have you put only one in the rack?')
        else:
            self.request_json_of_barcode(barcode_id=self.guitubebarcode['text'])



    def read2(self):

        list_of_barcodes = self.read_the_barcode()

        if len(list_of_barcodes) == 1:
            self.guitubebarcode['text'] = list_of_barcodes[0]
        else:
            print('Sorry Barcode not read. Have you put only one in the rack?')

    def read_the_barcode(self):
        host = parser.get('config_file', 'vision_mate_ip')  # set to IP address of target computer
        port = int(parser.get('config_file', 'vision_mate_port'))
        addr = (host, port)

        s = socket.socket()

        s.connect(addr)

        # scan the barcode
        s.send(b'S\r')
        print(s.recv(1024))

        # wait until the barcode has been scanned
        waiting = True
        while waiting == True:
            time.sleep(2)
            s.send(b'L\r')
            result = s.recv(1024)
            result = result.decode("utf-8")
            print(result)
            if result == 'OKL45':
                waiting = False

        # get the data
        s.send(b'L\r')
        result = s.recv(1024)
        s.send(b'D\r')
        result = s.recv(1024)
        result = result.decode("utf-8")

        my_list = result.split(",")

        list_of_barcodes = []

        for x in my_list:
            if 'No Tube' in x or x == '':
                pass
            else:
                list_of_barcodes.append(x)
        print(list_of_barcodes)
        s.close()
        return(list_of_barcodes)

    def update_gui_with_result(self, json_object):
        print(json_object)
        self.guitubebarcode['text'] = json_object['tube_barcode']
        self.itemnameText.set(json_object['item_name'])
        self.guiitemdescription.insert("1.0", json_object['item_description'])

    def update_entry_in_amos(self):
        variable = messagebox.askquestion('Update Entry In Amos', 'Are you sure you want to update this entry in AMOS?')
        if variable == 'yes':
            if self.guitubebarcode['text'] == 'Not Found':
                messagebox.showinfo("Error", "Please Scan a Barcode")

            elif self.guitubebarcode['text'] == 'Waiting For Read':
                messagebox.showinfo("Error", "Please Scan a Barcode")
            else:
                r = requests.get(parser.get('config_file', 'amos_url') + 'amos/api/v1.0/register_tube/',
                                 headers={'tube_barcode': self.guitubebarcode['text'], 'item_name': str(self.itemnameText.get()), 'ldf_id': str(self.ldfidText.get()),
                                          'item_description': str(self.guiitemdescription.get("1.0",'end-1c'))})
                messagebox.showinfo("Info", r.text)
        else:
            pass


if __name__ == "__main__":
    parser = ConfigParser()
    parser.read('tubes_config.cfg')
    print(parser.get('config_file', 'vision_mate_ip'))
    MyFrame().mainloop()
