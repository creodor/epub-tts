
##check pydub for wav -> mp3 conversion

## Using SAPI tts wrapper from https://github.com/DeepHorizons/tts
import tts.sapi

#offer gtts as an optional engine/voice
from gtts import gTTS

## wxpython: https://www.wxpython.org/pages/overview/#hello-world
## pip install -U wxPython
import wx

## subprocess, to allow the conversion to process while other things happen
import subprocess
import re

## ebooklib, should consider replacing with a xml parser instead.
## epub is well documented
## pip install ebooklib
import ebooklib
from ebooklib import epub



def convert_book(book, voiceEngine):
    bookTitle = str(book.get_metadata('DC', 'title'))
    sIndex = bookTitle.find('\'')
    eIndex = bookTitle.find('\',')
    bookTitle = bookTitle[sIndex+1:eIndex]
    counter = 1
    for item in book.get_items():
            #this needs:
            #1. strip out or utilize markup for voice modulation
            #2. convert to using ffmpeg for mp3 output
            #3. put whole book into one mp3? can mp3 have chapters? maybe some container file?
            segment = str(item.get_content())
            
            reg = '<.*?>'
            cleanedWords = clean_markup(reg, segment)
            reg = '{.*?}'
            cleanedWords = clean_markup(reg, cleanedWords)
            cleanedWords = cleanedWords.replace('\\n', ' ')
            cleanedWords = cleanedWords.replace('\\', '')

            outputFile = bookTitle + '-' + str(counter)

            makeVoiceFile(outputFile, cleanedWords, voiceEngine)
            #voice.create_recording(outputFile, cleanedWords)
            
            #voice.create_recording('./working/')
            counter += 1

def clean_markup(regEx, words):
        #want this to be able to detect portions of a book (ie, title/author/etc) and adjust voice
        #accordingly. might even use the winston tts with its xml variant.
        #for now, it just dumps out all of the xml/html tags and leaves whatever's left.
        #fails in some cases.
        #this will need to become a class for all of the above.
        clean = re.compile(regEx)
        return re.sub(clean, "", words)
        #words.replace("\\n", "")

def makeVoiceFile(outputFile, cleanedWords, engine):
    if engine == 'SAPI':
        voice = tts.sapi.Sapi()
        outputFile = outputFile + '.wav'
        voice.create_recording(outputFile, cleanedWords)
    elif engine == 'gTTS':
        voice = gTTS(cleanedWords, lang='en')
        outputFile = outputFile + '.mp3'
        voice.save(outputFile)

    
    
    #this uses ffmpeg to output mp3 files
    #ffmpeg in path or probably in workingdir
    #Command = "ffmpeg -y -i ./working/" + outputFile + ".wav ./working/" + outputFile + ".mp3"
    #subprocess.call(Command, shell=True)

class TTSFrame(wx.Frame):
    """
    A Frame that says Hello World
    """

    def __init__(self, *args, **kw):
        # ensure the parent's __init__ is called
        super(TTSFrame, self).__init__(*args, **kw)  

        # basic variables
        self.dirName = ''
        self.voiceEngines = ['SAPI', 'gTTS']
        self.voiceEngine = 'gTTS'     

        # create panel
        self.makeMainPanel()

        # create a menu bar
        self.makeMenuBar()

        # and a status bar
        self.CreateStatusBar()
        self.SetStatusText("Welcome to wxPython!")



    def makeMainPanel(self):

        # primary panel
        pnl = wx.Panel(self)
        
        st = wx.StaticText(pnl, label="Choose ePub file and convert", pos=(25,25))
        font = st.GetFont()
        font.PointSize += 8
        st.SetFont(font)

        # make the open button
        # calls the OnOpen method, used in the menu too
        selectEpubButton = wx.Button(pnl, label="Choose ePub", pos=(25,75))
        selectEpubButton.Bind(wx.EVT_BUTTON, self.OnOpen) 

        convertEpubButton = wx.Button(pnl, label = "Convert To Speech", pos = (25, 100))
        convertEpubButton.Bind(wx.EVT_BUTTON, self.OnConvert)

        self.voiceEngineSelectionCombo = wx.ComboBox(pnl, choices=self.voiceEngines, pos=(200, 75))

        self.voiceEngineSelectionCombo.Bind(wx.EVT_COMBOBOX, self.OnEngineChoice)

    def makeMenuBar(self):
        """
        A menu bar is composed of menus, which are composed of menu items.
        This method builds a set of menus and binds handlers to be called
        when the menu item is selected.
        """

        # Make a file menu with Hello and Exit items
        fileMenu = wx.Menu()
        # The "\t..." syntax defines an accelerator key that also triggers
        # the same event

        openItem = fileMenu.Append(wx.ID_OPEN)


        fileMenu.AppendSeparator()
        # When using a stock ID we don't need to specify the menu item's
        # label
        exitItem = fileMenu.Append(wx.ID_EXIT)

        # Now a help menu for the about item
        helpMenu = wx.Menu()
        aboutItem = helpMenu.Append(wx.ID_ABOUT)

        # Make the menu bar and add the two menus to it. The '&' defines
        # that the next letter is the "mnemonic" for the menu item. On the
        # platforms that support it those letters are underlined and can be
        # triggered from the keyboard.
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&File")
        menuBar.Append(helpMenu, "&Help")

        # Give the menu bar to the frame
        self.SetMenuBar(menuBar)

        # Finally, associate a handler function with the EVT_MENU event for
        # each of the menu items. That means that when that menu item is
        # activated then the associated handler function will be called.
        self.Bind(wx.EVT_MENU, self.OnExit,  exitItem)
        self.Bind(wx.EVT_MENU, self.OnAbout, aboutItem)
        self.Bind(wx.EVT_MENU, self.OnOpen, openItem)

    def OnExit(self, event):
        """Close the frame, terminating the application."""
        self.Close(True)

    
    def OnOpen(self, event):
        #Opening the book or content to parse

        #ask user what file to open
        with wx.FileDialog(self, "Choose ePub", wildcard="ePub files (*.epub)|*.epub", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            
            self.dirName = fileDialog.GetPath()

    def OnAbout(self, event):
        """Display an About Dialog"""
        wx.MessageBox("This is a wxPython Hello World sample",
                      "About Hello World 2",
                      wx.OK|wx.ICON_INFORMATION)

    def OnConvert(self, event):
        convert_book(epub.read_epub(self.dirName), self.voiceEngine)

    def OnEngineChoice(self, event):
        self.voiceEngine =  self.voiceEngineSelectionCombo.GetValue()

if __name__ == '__main__':
    # When this module is run (not imported) then create the app, the
    # frame, show it, and start the event loop.
    app = wx.App()
    frm = TTSFrame(None, title='ePub To Speech')
    frm.Show()
    app.MainLoop()