#!/usr/bin/python3
# -*- coding: iso-8859-15 -*-
"""
This file is part of the cintruder project, https://cintruder.03c8.net

Copyright (c) 2012/2020 psy <epsylon@riseup.net>

cintruder is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free
Software Foundation version 3 of the License.

cintruder is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
details.

You should have received a copy of the GNU General Public License along
with cintruder; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import os, traceback, hashlib, sys, time, socket
import platform, subprocess, re, webbrowser, shutil
from core.options import CIntruderOptions
from core.crack import CIntruderCrack
from core.ocr import CIntruderOCR
from core.curl import CIntruderCurl
from core.xml_export import CIntruderXML
from core.update import Updater
try:
    from urlparse import urlparse
except:
    import urllib.request, urllib.parse, urllib.error
    from urllib.parse import urlparse

# set to emit debug messages about errors (0 = off).
DEBUG = 0

class cintruder():
    """
    CIntruder application class
    """
    def __init__(self):
        self.captcha = ""
        self.optionOCR = []
        self.optionCrack = []
        self.optionParser = None
        self.optionCurl = None
        self.options = None
        self.word_sug = None
        self.train == 0
        self.crack == 0
        self.ignoreproxy = 1  
        self.isurl = 0
        self.os_sys = platform.system()
        self._webbrowser = webbrowser
        self.GIT_REPOSITORY = 'https://code.03c8.net/epsylon/cintruder' # oficial code source [OK! 26/01/2019]
        self.GIT_REPOSITORY2 = 'https://github.com/epsylon/cintruder' # mirror source [since: 04/06/2018]

    def set_options(self, options):
        """
        Set cintruder options
        """
        self.options = options

    def create_options(self, args=None):
        """
        Create the program options for OptionParser.
        """
        self.optionParser = CIntruderOptions()
        self.options = self.optionParser.get_options(args)
        if not self.options:
            return False
        return self.options

    def set_webbrowser(self, browser):
        self._webbrowser = browser

    def banner(self):
        print('='*75)
        print("")
        print("        o8%8888,    ")
        print("       o88%8888888. ")
        print("      8'-    -:8888b   ")
        print("     8'         8888  ")
        print("    d8.-=. ,==-.:888b  ")
        print("    >8 `~` :`~' d8888   ")
        print("    88         ,88888   ")
        print("    88b. `-~  ':88888  ")
        print("    888b \033[1;31m~==~\033[1;m .:88888 ")
        print("    88888o--:':::8888      ")
        print("    `88888| :::' 8888b  ")
        print("    8888^^'       8888b  ")
        print("   d888           ,%888b.   ")
        print("  d88%            %%%8--'-.  ")
        print(" /88:.__ ,       _%-' ---  -  ")
        print("     '''::===..-'   =  --.  `\n")
        print(self.optionParser.description, "\n")
        print('='*75)

    def get_attack_captchas(self):
        """
        Get captchas to brute force
        """
        captchas = []
        options = self.options
        p = self.optionParser
        if options.train:
            print(('='*75))
            print((str(p.version)))
            print(('='*75))
            print("Starting to 'train'...")
            print(('='*75))
            captchas = [options.train]
        if options.crack:
            print(('='*75))
            print((str(p.version)))
            print(('='*75))
            print("Starting to 'crack'")
            print(('='*75))
            captchas = [options.crack]
        if options.track:
            print(('='*75))
            print((str(p.version)))
            print(('='*75))
            print("Tracking captchas from url...")
            print(('='*75))
            captchas = [options.track]
        return captchas

    def train(self, captcha):
        """
        Learn mode:
            + Add words to the brute forcing dictionary
        """
        self.train_captcha(captcha)

    def train_captcha(self, captcha):
        """
        Learn mode:
            1- Apply OCR to captcha/image and split into unities
            2- Human-Recognize that unities like alphanumeric words (gui supported)
            3- Move that words into dictionary (gui supported)
        """
        options = self.options
        # step 1: applying OCR techniques
        if options.name: # with a specific OCR module
            print("[Info] Loading module: [ "+ options.name + " ]\n")
            try:
                sys.path.append('mods/%s/'%(options.name))
                exec("from " + options.name + "_ocr" + " import CIntruderOCR") # import module
            except Exception:
                print("\n[Error] '"+ options.name+ "' module not found!\n")
                return #sys.exit(2)
            if options.setids: # with a specific colour ID
                setids = int(options.setids)
                if setids >= 0 and setids <= 255:
                    self.optionOCR = CIntruderOCR(captcha, options)
                else:
                    print("\n[Error] You must enter a valid RGB colour ID number (between 0 and 255)\n")
                    return #sys.exit(2)
            else:
                self.optionOCR = CIntruderOCR(captcha, options)
        else: # using general OCR algorithm
            if options.setids: # with a specific colour ID
                setids = int(options.setids)
                if setids >= 0 and setids <= 255:
                    self.optionOCR = CIntruderOCR(captcha, options)
                else:
                    print("\n[Error] You must enter a valid RGB colour ID number (between 0 and 255)\n")
                    return #sys.exit(2)
            else:
                self.optionOCR = CIntruderOCR(captcha, options)

    def crack(self, captcha):
        """
        Crack mode:
            + Brute force target's captcha against a dictionary
        """
        self.crack_captcha(captcha)

    def crack_captcha(self, captcha):
        """
        Crack mode: bruteforcing...
        """
        options = self.options
        if options.name:
            print("[Info] Loading module: ["+ str(options.name) + "] \n")
            try:
                sys.path.append('mods/%s/'%(options.name))
                exec("from " + options.name + "_crack" + " import CIntruderCrack")
            except Exception:
                print("\n[Error] '"+ options.name+ "' module not found!\n")
                return #sys.exit(2)
            self.optionCrack = CIntruderCrack(captcha)
            w = self.optionCrack.crack(options)
            self.word_sug = w
        else:
            self.optionCrack = CIntruderCrack(captcha)
            w = self.optionCrack.crack(options)
            self.word_sug = w

    def remote(self, captchas, proxy):
        """
        Get remote captchas 
        """
        l = []
        if not os.path.exists("inputs/"):
            os.mkdir("inputs/")
        for captcha in captchas:
            c = self.remote_captcha(captcha, proxy)
            if c:
                l.append(c)
                return l
            else:
                return

    def remote_captcha(self, captcha, proxy):
        """
        Get remote captcha
        """
        if proxy:
            self.ignoreproxy=0
        self.optionCurl = CIntruderCurl(captcha, self.ignoreproxy, proxy)
        buf = self.optionCurl.request()
        if buf != "exit":
            m = hashlib.md5()
            m.update(captcha.encode('utf-8'))
            c = "%s.gif"%(m.hexdigest())
            h = "inputs/" + str(c)
            f = open(h, 'wb')
            f.write(buf.getvalue())
            f.close
            buf.close
            return h
        else:
            return #sys.exit(2)

    def export(self, captchas):
        """
        Export results
        """
        if self.options.xml and not (self.options.train):
            self.optionXML = CIntruderXML(captchas)
            if self.word_sug == None:
                print("[Info] XML NOT created!. There are not words to suggest...")
            else:
                self.optionXML.print_xml_results(captchas, self.options.xml, self.word_sug)
                print("[Info] XML created: "+str(self.options.xml)+ "\n")

    def track(self, captchas, proxy, num_tracks):
        """
        Download captchas from url
        """
        for captcha in captchas:
            self.track_captcha(captcha, proxy, num_tracks)

    def track_captcha(self, captcha, proxy, num_tracks):
        """
        This technique is useful to create a dictionary of 'session based' captchas
        """
        options = self.options
        urlp = urlparse(captcha)
        self.domain = urlp.hostname
        if not os.path.exists("inputs/%s"%(self.domain)):
            os.mkdir("inputs/%s"%(self.domain))
        if proxy:
            self.ignoreproxy = 0
        buf = ""
        i=0
        while i < int(num_tracks) and buf != "exit":
            self.optionCurl = CIntruderCurl(captcha, self.ignoreproxy, proxy)
            buf = self.optionCurl.request()
            if options.verbose:
                print("\n[-]Connection data:")
                out = self.optionCurl.print_options()
                print('-'*45)
            if buf != "exit":
                m = hashlib.md5()
                m.update(captcha.encode('utf-8'))
                h = "inputs/%s/%s.gif"%(self.domain, m.hexdigest())
                f = open(h, 'wb')
                f.write(buf.getvalue())
                f.close
                buf.close
                print("[Info] Saved: "+ str(h))
                print("------------")
            i=i+1
        if buf != "exit":
            print("\n=================")
            print("Tracking Results:")
            print("=================")
            print("\nNumber of tracked captchas: [ "+ str(num_tracks)+" ] \n")

    def run(self, opts=None):
        """ 
        Run cintruder
        """ 
        if opts:
            options = self.create_options(opts)
            self.set_options(options)
        options = self.options
        #step -1: run GUI/Web interface
        if options.web:
            self.create_web_interface()
            return
        #step -1: check/update for latest stable version
        if options.update:
            self.banner()
            try:
                print("\nTrying to update automatically to the latest stable version\n")
                Updater() 
            except:
                print("Not any .git repository found!\n")
                print("="*30)
                print("\nTo have working this feature, you should clone CIntruder with:\n")
                print("$ git clone %s" % self.GIT_REPOSITORY)
                print("\nAlso you can try this other mirror:\n")
                print("$ git clone %s" % self.GIT_REPOSITORY2 + "\n")
        #step 0: list output results and get captcha targets
        if options.listmods:
            print("=====================================")
            print("Listing specific OCR exploit modules:")
            print("=====================================\n")
            top = 'mods/'
            for root, dirs, files in os.walk(top, topdown=False):
                for name in files:
                    if name == 'DESCRIPTION':
                        if self.os_sys == "Windows": #check for win32 sys
                            subprocess.call("type %s/%s"%(root, name), shell=True)
                        else:
                            subprocess.call("cat %s/%s"%(root, name), shell=True)

            print("\n[Info] List end...\n")
            return
        if options.track_list:
            print("==============================")
            print("Listing last tracked captchas:")
            print("==============================\n")
            top = 'inputs/'
            tracked_captchas = []
            for root, dirs, files in os.walk(top, topdown=False):
                for name in files:
                    path = os.path.relpath(os.path.join(root, name))
                    if self.os_sys == "Windows": #check for win32 sys
                        atime = os.path.getatime(path)
                    else:
                        date = os.stat(path)
                        atime = time.ctime(date.st_atime)
                    tracked_captchas.append([atime,str(" + "+name),str("   |-> "+path)])
            tracked_captchas=sorted(tracked_captchas,key=lambda x:x[0]) # sorted by accessed time
            ca = 0 # to control max number of results
            for t in tracked_captchas:
                ca = ca + 1
                print("-------------------------")
                for c in t:
                    if ca < 26:
                        print(c)
                    else:
                        break
                print("-------------------------")
            print("\n[Info] List end...\n")
            return 
        captchas = self.get_attack_captchas()
        captchas = self.sanitize_captchas(captchas)
        captchas2track = captchas
        if self.isurl == 1 and (options.train or options.crack):
            if options.proxy:
                captchas = self.remote(captchas, options.proxy)
            else:
                captchas = self.remote(captchas, "")
            if options.verbose:
                print("\n[-] Connection data:")
                out = self.optionCurl.print_options()
                print('-'*45)
        #step 0: track
        if options.track:
            if options.s_num:
                num_tracks = int(options.s_num) # tracking number defined by user
            else:
                num_tracks = int(5) # default track connections
            if options.proxy:
                self.track(captchas2track, options.proxy, num_tracks)
            else:
                self.track(captchas2track, "", num_tracks)
        #step 1: train
        if options.train:
            try:
                if len(captchas) == 1:
                    for captcha in captchas:
                        if captcha is None:
                            print("\n[Error] Applying OCR algorithm... Is that captcha supported?\n")
                            if os.path.exists('core/images/previews'):
                                shutil.rmtree('core/images/previews') # remove last OCR
                        else:
                            print("\n[Info] Target: "+ options.train+"\n")
                            self.train(captcha)
                else:
                    for captcha in captchas:
                        if len(captchas) > 1 and captcha is None:
                            pass
                        else:
                            print("\n[Info] Target: "+ options.train+"\n")
                            self.train(captcha)
            except:
                print("[Error] Something wrong getting captcha. Aborting...\n")
            if options.xml:
                print("[Info] You don't need export to XML on this mode... File not generated!\n")
        #step 2: crack
        if options.crack:
            if len(captchas) == 1:
                for captcha in captchas:
                    if captcha is None:
                        print("\n[Error] Trying to bruteforce... Is that captcha supported?\n")
                        if os.path.exists('core/images/previews'):
                            shutil.rmtree('core/images/previews') # remove last OCR
                    else:
                        print("\n[Info] Target: "+ options.crack+"\n")
                        self.crack(captcha)
            else:
                for captcha in captchas:
                    if len(captchas) > 1 and captcha is None:
                        pass
                    else:
                        print("\n[Info] Target: "+ options.crack+"\n")
                        self.crack(captcha)
            if options.command:
                print("[Info] Executing tool connector... \n")
                if self.word_sug is not None:
                    print("[Info] This is the word suggested by CIntruder: [ "+ str(self.word_sug)+ " ] \n")
                else:
                    print("[Error] CIntruder hasn't any word to suggest... Handlering tool process aborted! ;(\n")
                    sys.exit(2)
                if "CINT" in options.command: # check parameter CINT on command (*)
                    # change cintruder suggested word for the users captchas input form parameter
                    # and execute handlered tool with it.
                    if self.word_sug is not None:      
                        cmd = options.command.replace("CINT", self.word_sug)
                        subprocess.call(cmd, shell=True)
                    else:
                        cmd = options.command
                        subprocess.call(cmd, shell=True)
                else:
                    print("[Error] Captcha's parameter flag: 'CINT' is not present on: "+ str(options.command)+ "\n")
        #step 3: export
        if options.xml:
            self.export(captchas)

    def sanitize_captchas(self, captchas):
        """
        Sanitize correct input of source target(s)
        """
        options = self.options
        all_captchas = set()
        for captcha in captchas:
            # captcha from url
            if "http://" in captcha or "https://" in captcha:
                all_captchas.add(captcha)
                self.isurl = 1
            elif self.isurl == 0: # captcha from file
                (root, ext) = os.path.splitext(captcha)       
                if ext != '.gif' and ext != '.jpg' and ext != '.jpeg' and ext != '.png': # by the moment                    
                    captcha = None
                    all_captchas.add(captcha)
                else:
                    all_captchas.add(captcha)
                self.isurl = 0
        return all_captchas

    def create_web_interface(self):
        # launch webserver+gui
        from .webgui import ClientThread
        import webbrowser
        host = '0.0.0.0'
        port = 9999
        try:
            webbrowser.open('http://127.0.0.1:9999', new=1)
            tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            tcpsock.bind((host,port))
            while True:
                tcpsock.listen(4)
                (clientsock, (ip, port)) = tcpsock.accept()
                newthread = ClientThread(ip, port, clientsock)
                newthread.start()
        except (KeyboardInterrupt, SystemExit):
            sys.exit()

if __name__ == "__main__":
    app = cintruder()
    options = app.create_options()
    if options:
        app.set_options(options)
        app.run()
