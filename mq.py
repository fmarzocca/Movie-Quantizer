#!/usr/bin/env python3

#
# Movie Quantizer
# © Fabio Marzocca - 2017
#
# Notes: requires ffmpeg


import tkinter
from tkinter import ttk, filedialog, StringVar, Spinbox, Frame, Message, Toplevel
import tkinter.messagebox as mbox
import sys
import subprocess
import os
import threading
from get_ffmpeg import get_ffmpeg

 
VERSION = '1.0.0'
FFMPEG_BIN = "ffmpeg"

class MQ(ttk.Frame):
    #The  gui and functions.
    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        self.movieLabeltext=StringVar()
        self.moviefile = ""
        self.outfolder=""
        self.fileloaded=False
        self.folderloaded=False
        self.movieLabeltext.set("<none>")
        self.movieDuration=0.0
        self.root = parent
        self.init_gui()
        
        
        
    def on_quit(self):
		#Exits program.
        sys.exit()
     
    #Get the movie file    
    def loadmovie(self):
    	#check if ffmpeg is installed
        if (self.checkifffmpeg()==False):
            #self.answer_label['text'] = "ERROR: this application needs ffmpeg installed in the system!"
            answer = mbox.askyesno("ERROR","This application needs ffmpeg "
                          "installed in the system!\n\n"
                          "Do you want to install it?")
            if answer==True:
                root.update();
                self.tryGettingffmpeg()
                return
            root.update();
            return
        opts = {}
        opts['filetypes'] = [('Supported types',("*.mov","*.mp4","*.mpg","*.avi","*.h264","*.mpeg","*.mkv","*.m4a","*.3gp","*.ogg","*.wmv","*.vob"))]       
        self.moviefile = filedialog.askopenfilename(**opts)
        if self.moviefile != "":
            self.movie_button['text']=os.path.basename(self.moviefile)
            self.fileloaded=True        
            self.checkDuration()
            self.interval_spin['state'] = 'normal'
            self.calculate_images()
        if (self.fileloaded and self.folderloaded)==True:
            self.action_button['state'] = 'normal'

 	#Get informations and duration of the movie	
    def checkDuration(self):
        c = os.popen(FFMPEG_BIN+" -i "+"'"+self.moviefile+"'"+" 2>&1 | grep Duration")
        out = c.read()
        self.answer_label['text'] ="Movie info:"+out
        c.close()
        dur = out.index("Duration:")
        duration = out[dur+10:dur+out[dur:].index(",")]
        hh, mm, ss = map(float, duration.split(":"))
        self.movieDuration = (hh*60 + mm)*60 + ss


    def selectFolder(self):
        self.outfolder = filedialog.askdirectory()
        if self.outfolder != "":
            self.folder_button['text']=os.path.basename(self.outfolder)
            self.folderloaded=True 
        if (self.fileloaded and self.folderloaded)==True:
            self.action_button['state'] = 'normal'
            
 		  
    def checkifffmpeg(self):
        try:
            devnull = open(os.devnull)
            subprocess.call(['ffmpeg',  '-version'], stderr=subprocess.STDOUT,
                stdout=devnull)
            FFMPEG_BIN = "ffmpeg"
        except (OSError, ValueError, subprocess.CalledProcessError):
            try:
                subprocess.call(['ffmpeg.osx',  '-version'], 
                        stderr=subprocess.STDOUT,stdout=devnull)
                FFMPEG_BIN = "ffmpeg.osx"
            except (OSError, ValueError, subprocess.CalledProcessError):           
                return False
        return True

    def tryGettingffmpeg(self):
        self.progLabelText="Downloading ffmpeg. Please wait.."
        self.progress_win()
        root.update()
        t1=threading.Thread(target=get_ffmpeg, args=(self,))
        t1.start() 
        FFMPEG_BIN = "ffmpeg.osx"

                
                  
    def calculate_images(self):
        images = int(float(self.movieDuration)/float(self.interval_spin.get()))
        self.images_nrs['state']='normal'
        self.images_nrs.delete(0,'end')
        self.images_nrs.insert(0,images)
        self.images_nrs['state']='disabled'

            
    def execute(self):
        #Grab the images
        format = self.image_formatbox.get()
        result=(os.system('ls "'+self.outfolder+'"/img*.'+format))

        if result ==0:
        	answer = mbox.askyesno("Warning","Folder already contains image files, that will be overwritten. Proceed?")
        	if answer==False:
        		return
        	root.update();
        self.progLabelText="Processing images. Please wait.."
        self.progress_win()
        t1=threading.Thread(target=self.exec_thread)
        t1.start() 
        
    def exec_thread(self):
        format = self.image_formatbox.get()
        if format == "tiff":
            pixformat=" -pix_fmt rgb565 " 
        else: 
        	pixformat=" "
        fps = float(1/float(self.interval_spin.get()))
        cmd = FFMPEG_BIN+" -i '"+self.moviefile+"'"+pixformat+ "-vf fps="+\
            str(fps)+" '"+self.outfolder+"'/img%04d."+format+" 2>&1"
        try:
            subprocess.check_call(cmd,shell=True)
            self.popup.destroy()
            cnt = subprocess.check_output('ls "'+self.outfolder+'"/img*.'+format+' | wc -l', shell=True)
            self.answer_label['text'] = "Result: "+\
                (cnt.decode('ascii').strip())+\
                " image files have been successfully created in "+self.outfolder
            return
        except subprocess.CalledProcessError as e:
            self.answer_label['text'] =e.output   
            self.popup.destroy()
            return 
        
    
    def progress_win(self):
        self.popup=Toplevel(self)
        progress_bar = ttk.Progressbar(self.popup,orient='horizontal',
            mode='determinate',takefocus=True, length=400)
        progress_bar.grid(row=1,column=0,sticky="we")
        
        self.progLabel=ttk.Label(self.popup, text=self.progLabelText).grid(column=0, row=0,
             sticky="we")
        self.popup.attributes('-topmost',True)
        progress_bar.start(50)

    def init_gui(self):
        #Builds GUI.
        self.root.title('Movie Quantizer')
        self.root.option_add('*tearOff', 'FALSE')
 
        self.grid(column=0, row=0, sticky='nsew')
 
        self.menubar = tkinter.Menu(self.root)
 
        self.menu_file = tkinter.Menu(self.menubar)
        self.menu_file.add_command(label='Open Movie File...',
            command=self.loadmovie)
        self.menu_file.add_command(label='Select Output Folder...', 
            command=self.selectFolder)
        self.menu_file.add_command(label='Exit', command=self.on_quit)
 
 
        self.menubar.add_cascade(menu=self.menu_file, label='File')
 
        self.root.config(menu=self.menubar)
 

        self.movie_button = ttk.Button(self, text='Select',
  		    command=self.loadmovie)
        self.movie_button.grid(column=1, row = 2)

        self.interval_spin = Spinbox(self, from_=0.5, to=20.0, 
            increment=0.5, width=4, fg="red", command=self.calculate_images,
            state='disabled')
        self.interval_spin.grid(column=1, row=3, sticky="e")
        
        self.folder_button = ttk.Button(self, text='Select',
            command=self.selectFolder)
        self.folder_button.grid(column=3, row=2)
        
        self.images_nrs = ttk.Entry(self,text='', width=5,
            state='disabled')
        self.images_nrs.grid(column=3, row=3, sticky="e")
        
        self.box_value=StringVar()
        self.image_formatbox = ttk.Combobox(self, textvariable=self.box_value,
              state='readonly', width=4, justify='center')
        self.image_formatbox['values'] = ("jpg","tiff")
        self.image_formatbox.current(0)
        self.image_formatbox.grid(column=1, row=4, sticky="w")
        
        self.action_button = ttk.Button(self, text='Grab Images',
                command=self.execute, state='disabled')
        self.action_button.grid(column=0, row=5, columnspan=4)
 
        
        self.answer_frame = Frame(self, height=300, background="white")

        self.answer_frame.grid(column=0, row=6, columnspan=4, sticky='nesw')
 
        self.answer_label = Message(self.answer_frame, text='', justify='center', width=600)
        self.answer_label.grid(column=0, row=0)
 
        # Labels that remain constant throughout execution.
        ttk.Label(self, text=' ').grid(column=0, row=0,
                columnspan=4)
        ttk.Label(self, text='Movie File:').grid(column=0, row=2,
                sticky='w')
        ttk.Label(self, text='Output Folder:').grid(column=2, row=2,
                sticky='w')
        ttk.Label(self, text="Grab a frame each (sec.):").grid(column=0, row=3,
                sticky='w')
        ttk.Label(self, text="Nr. of images:").grid(column=2, row=3,
                sticky='w')
        ttk.Label(self, text="Images format:").grid(column=0, row=4,
                sticky='w')

        for child in self.winfo_children():
            child.grid_configure(padx=7, pady=7)
        
        
 

def about_dialog():
        mbox.showinfo("About Movie Quatizer", "A movie Frame Grabber\n©2017 - Fabio Marzocca\n\nVersion: "+VERSION, parent=root)
        
if __name__ == '__main__':
    root = tkinter.Tk()
    MQ(root)
    root.resizable(False, False)
    root.createcommand('tkAboutDialog', about_dialog)
    os.environ['PATH'] += '/usr/local/bin'
    root.mainloop()
