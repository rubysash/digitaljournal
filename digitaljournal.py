'''
Author: James  https://rubysash.com

encrypted journal (plain text version)

Clear TX Word+date is filename
Summary and Entry are encrypted
Can Load previous entries
Can Save Current
Has "Insipre me" option for fun


Todo:
pep 8 format

To install modules:
python -m pip install --upgrade pip
pip3 install tkinter
pip3 install base64
pip3 install hashlib
pip3 install pycrypttodome

'''

# gui stuff
import tkinter as tk
import tkinter.messagebox as mb                             # to make the popup

from tkinter import Tk, Text, BOTH, W, N, E, S, DISABLED
from tkinter.ttk import Frame, Button, Label, Style
from tkinter import filedialog                              # for file selector

# file i/o stuff
import json

# for date time filename
from datetime import datetime
import time                                                 # for run timer

# for the inspiration randoms
import random


# encryption stuff, not needed version 1.x
from base64 import b64encode, b64decode
import hashlib
from Cryptodome.Cipher import AES
import os
from Cryptodome.Random import get_random_bytes



# globals
debug = 0

# default start open directory
startDir = "C:/git/jourknell"

title = "James' Encrypted Thought Pre-Processor V 1.00"

# general appearances
# todo: fix up fonts and bold stuff, hard to read
opts1 = { 'ipadx': 5, 'ipady': 5 , 'sticky': 'nswe' } # centered
opts2 = { 'ipadx': 5, 'ipady': 5 , 'sticky': 'e' } # right justified
opts3 = { 'ipadx': 5, 'ipady': 5 , 'sticky': 'w' } # left justified
bgcolor = '#ECECEC'
white = '#FFFFFF'

class App(Frame):

    startTime = time.time()

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        # we are making a grid that is 12 colums across
        # colum 1 and colum 12 are just space holders.

        self.master.title(title)
        self.pack(fill=BOTH, expand=True)


        # variables we are using/looking for
        self.word = tk.StringVar()

        # set the file name and DTS
        self.date = tk.StringVar()
        self.date.set(datetime.now().strftime("%Y-%m-%d_%I%M%S%p"))

        self.key1 = tk.StringVar()
        self.key2 = tk.StringVar()

        # the plan is to encrypt this stuff below
        self.summary = tk.StringVar()
        self.perception = tk.Text(self, width=50, height=10, bg=white)
        self.reality = tk.Text(self, width=50, height=10, bg=white)
        self.opportunity = tk.Text(self, width=50, height=10, bg=white)


        # corners for spacing/layout
        self.label_nw = tk.Label(self, text=" ", bg=bgcolor)
        self.label_nw.grid(row=0, column=0, **opts1)
        self.label_ne = tk.Label(self, text=" ", bg=bgcolor)
        self.label_ne.grid(row=0, column=12, **opts1)

        # first header
        self.label_a = tk.Label(self, text="Plain Text: (Word+Date Makes File Name)", bg=bgcolor)
        self.label_a.grid(row=0, column=1, columnspan=8, **opts1)

        # Clear button
        btn_clear = tk.Button(self, text=" Clear ",command=self.clear, bg=bgcolor)
        btn_clear.grid(row=1,column=11,  **opts1)

        # Build File Name:
        tk.Label(self, text="One Word").grid(row=1, column=1, columnspan=2, **opts2)
        tk.Entry(self, textvariable=self.word).grid(row=1, column=3, columnspan=2, **opts3)

        tk.Label(self, text="Date").grid(row=1, column=5, columnspan=2, **opts2)
        tk.Entry(self, textvariable=self.date, state=DISABLED).grid(row=1, column=7, columnspan=2, **opts3)

        # Load button and file entry (disabled)
        self.loadfile = tk.StringVar()
        self.btn_load = tk.Button(self, text="LOAD",command=self.load, bg=bgcolor)
        self.btn_load.grid(row=2,column=11, **opts1)
        tk.Entry(self, textvariable=self.loadfile, state=DISABLED).grid(row=2, column=1, columnspan=8, **opts1)

        # header
        self.label_c = tk.Label(self, text="Everything below should be encrypted (in V2)", bg=bgcolor)
        self.label_c.grid(row=3, column=1, columnspan=11, **opts1)

        # save button
        btn_save = tk.Button(self, text=" Save ",command=self.save, bg=bgcolor)
        btn_save.grid(row=3,column=11,  **opts1)

        # Event Summary field
        tk.Label(self, text="Event Summary").grid(row=4, column=1, columnspan=2, **opts2)
        tk.Entry(self, textvariable=self.summary).grid(row=4, column=3, columnspan=7, **opts1)

        # inspire button
        btn_inspire = tk.Button(self, text=" Inspire ",command=self.inspire, bg=bgcolor)
        btn_inspire.grid(row=4, column=11,  **opts1)

        # go ahead and focus on the inspire button
        btn_inspire.focus_set()

        # header
        self.label_d = tk.Label(self, text="My Perceptions and Feelings", bg=bgcolor)
        self.label_d.grid(row=5, column=1, columnspan=11, **opts1)

        # What did I think happened
        self.perception.grid(row=6, column=1, columnspan=11, rowspan=5, **opts1)

        # header
        self.label_e = tk.Label(self, text="Objective, Verifiable - Facts", bg=bgcolor)
        self.label_e.grid(row=11, column=1, columnspan=11, **opts1)

        # how did things actually go down, 
        self.reality.grid(row=12, column=1, columnspan=11, rowspan=5, **opts1)

        # header
        self.label_f = tk.Label(self, text="Opportunties for Improvement", bg=bgcolor)
        self.label_f.grid(row=17, column=1, columnspan=11, **opts1)

        # how can I fix my thinking or prevent this problem?
        self.opportunity.grid(row=18, column=1, columnspan=11, rowspan=5, **opts1)

        # Encrypt Keys, fields for V2
        tk.Label(self, text="Key").grid(row=23, column=1, columnspan=3, **opts2)
        tk.Entry(self, textvariable=self.key1).grid(row=23, column=4, columnspan=8, **opts1)
        tk.Label(self, text="Verify").grid(row=24, column=1, columnspan=3, **opts2)
        tk.Entry(self, textvariable=self.key2).grid(row=24, column=4, columnspan=8, **opts1)

        # final header/spacer
        self.label_h = tk.Label(self, text=" ", bg=bgcolor)
        self.label_h.grid(row=25, column=1, columnspan=11, **opts1)


    """
    Check if file is readable
    """
    def isReadable(self,fnm):
        if os.path.exists(fnm):
        # path exists
            # is it a file or a dir?
            if os.path.isfile(fnm): 
                # also works when file is a link and the target is writable
                return os.access(fnm, os.W_OK)
            else:
                # path is a dir, so cannot write as a file
                return False
        
        # target does not exist, check perms on parent dir
        pdir = os.path.dirname(fnm)
        if not pdir: pdir = '.'
        
        # target is creatable if parent dir is writable
        return os.access(pdir, os.W_OK)


    """
    Clear the screen
    """
    def clear(self):
        # clear out the trash
        self.perception.delete("1.0", tk.END)
        self.reality.delete("1.0", tk.END)
        self.opportunity.delete("1.0", tk.END)
        self.word.set("")
        self.date.set(datetime.now().strftime("%Y-%m-%d_%I%M%S%p"))
        self.summary.set("")
        self.key1.set("")
        self.key2.set("")

        # load sample data
        perception = "- How did you feel? What do you think happened?\n- What's the worst that it could be?\n- What emotions are you feeling?\n- What reasons do you have for these emotions?"
        reality = "- What are the verifiable facts?\n- If you cannot prove it, do not put it here!\n- Why do you feel this way?"
        opportunity = "- How can you do it better next time?\n- What would someone who knows what to do, do?\n- How can you prevent this in the future?\n- Are there any steps, even incomplete, that might help?"

        # clear out and insider the loaded data
        self.word.set("Keyword")
        self.summary.set("Summarize Succinctly")
        self.perception.insert(tk.INSERT, perception)
        self.reality.insert(tk.INSERT, reality)
        self.opportunity.insert(tk.INSERT, opportunity)
        print("Sample data loaded")

    """
    Shut Down Function, and message
    """
    def shudIdDown(self,msg):
        # ok, give us a final time report
        runtime = float("%0.2f" % (time.time() - self.startTime))
        print("Run Time (Since Start): ", runtime, "seconds")
        
        # and then tell us what we want to see
        print(msg)
        sys.exit(0)


    """
    Load an older, saved entry
    todo: try except json.decoder to verify valid JSON
    todo: if no file is selected and they cancel it spits out error
    FileNotFoundError: [Errno 2] No such file or directory: ''
    use try/except for the load to hide the error
    todo: currently it's detecting cp1252, might want to force utf-8 for all
    """
    def load(self):
        if debug:
            print("DEBUG: Attempting to load file in loadFile()")

        # the file selector dialogue
        # https://effbot.org/tkinterbook/tkinter-file-dialogs.htm
        loadfile =  filedialog.askopenfilename(
            initialdir = startDir,
            title = "Select file",
            filetypes = (("JSON files","*.json"),("all files","*.*")))

        # put it in the entry field
        self.loadfile.set(loadfile)

        # run the file through the basic read tests
        if self.isReadable(loadfile):
            if debug:
                print("File exists, readable, proceed")

            # clear the fields first so it doesn't auto concatenate existing data
            self.perception.delete("1.0", tk.END)
            self.reality.delete("1.0", tk.END)
            self.opportunity.delete("1.0", tk.END)
            self.word.set("")
            self.date.set("")
            self.summary.set("")
            self.key1.set("")
            self.key2.set("")
           
            # build our dictionary of data and load it from json
            data = ''
            with open(loadfile, 'r') as infile:
                data = json.load(infile)

            # repopulate to existing form
            self.word.set(data['word'])
            self.date.set(data['date'])
            self.summary.set(data['summary'])
            self.perception.insert(tk.INSERT, data['perception'])
            self.reality.insert(tk.INSERT, data['reality'])
            self.opportunity.insert(tk.INSERT, data['opportunity'])
            
            if debug:
                print("Data loaded from '" + str(infile) + "'")
        else:
            self.shudIdDown("Cannot read from file, check permissions, exiting #278")


    """
    Save this entry
    todo: add pycryptodome methods here
    todo: told user "1 word", but you know they are going to type a file name like: ../../whatever
    todo: force 1 word, ascii safe characters only
    """
    def save(self):
        if debug:
            print("DEBUG: Attempting to save file in save()")

        # if error detected, flag will set to 0
        flag = 1
        word = self.word.get()
        date = self.date.get()
        summary = self.summary.get()
        perception = self.perception.get("1.0", tk.END)
        reality = self.reality.get("1.0", tk.END)
        opportunity = self.opportunity.get("1.0", tk.END)

        if (len(word) < 3):
            mb.showinfo("Information", "Word Field Empty?")
            flag = 0
        if (len(summary) < 3):
            mb.showinfo("Information", "Summary Field Empty?")
            flag = 0

        # no errors detected, so get data
        if (flag == 1):
            data = {
                "word": self.word.get(),
                "date": self.date.get(),
                "summary": self.summary.get(),
                "perception": self.perception.get("1.0", tk.END),
                "reality": self.reality.get("1.0", tk.END),
                "opportunity": self.opportunity.get("1.0", tk.END),
            }

            # build our json file name
            file = self.date.get() + "-" + self.word.get() + ".json"

            # dump to json, clobber existing file of same name
            with open(file, 'w') as outfile:
                json.dump(data, outfile, indent=2)

            # explain to user what happened
            print(file + " updated")
            runtime = float("%0.2f" % (time.time() - self.startTime))
            print("Run Time (Since Start): ", runtime, "seconds")
        else:
            # or don't
            mb.showinfo("Information", "FILE NOT SAVED, FIELDS MIGHT BE EMPTY")

    """
    Pull up a random quote for inspiration
    todo: research the unknowns
    todo: separate out data like this into json instead of code
    """
    def inspire(self):
        inspirations = [
"Focus on getting it done.|Unknown",
"What is the most important thing to accomplish right now?  Do it.|Unknown",
"I keep things simple.|Unknown",
"Opposition will become opportunity.|Unknown",
"Count your blessings, one by one.|Unknown",
"Don't let the fear of time it takes to do something stop you from doing it.  The time will pass anyway.|Unknown",
"The best way to predict your future is to create it.|Unknown",
"Where the heart is willing, it will find 1000 ways.  Where it is unwilling, it will find a 1000 excuses.|Unknown",
"Don't blame your circumstances, create them.|Unknown",
"Motivation gets you started - habit keeps you going.|Unknown",
"You will never find time for anything - you must make time.|Unknown",
"Astonish yourself today - do what you are capable of.|Unknown",
"Your character is what you really are, your reputation is what people think you are.|Unknown",
"You cannot make a brand new start, only a brand new ending.|Unknown",
"Nothing on earth can stop the man with right attitude; Nothing on earth can help the man with the wrong attitude.|Unknown",
"If you think you can or think you can't, you are right.|Henry Ford",
"I am a dealer of hope.|Me",
"My words create life.|Me",
"I provide value to the life of everyone I meet.|Me",
"I inspire others to see the good in themselves.|Me",
"The ultimate measure of a man is where he stands at times of challenge and controversy.|Unknown",
"Anyone can hold the helm when the sea is calm.|Unknown",
"Where there is no vision, the people perish.  Create vision.|Proverbs 29:18",
"Misfortunes, untoward events, lay open, disclose the skill of a general.|Unknown",
"I am decisive and take action.|Me",
"I know the value of 5 minutes.|Me",
"A bold onset is half the battle|Giuseppe Garibaldi",
"A good general not only sees the way to victory; he also knows when victory is impossible.|Unknown",
"Integrity is what you do when nobody is watching.|Unknown",
"We are what we repeatedly do - therefore, excellence is not an act, but a habit.|Unknown",
"Work spares us from three evils: boredom, vice, need.|Unknown",
"If the wind will not serve, take to the oars.|Unknown",
"You cannot plow a field by turning it over in your mind.|Unknown",
"Do not wait until the iron is hot to strike; but make it hot by striking.|Unknown",
"Nothing will be attempted if all possible objections must first be overcome.|Unknown",
"What are you waiting for ?|Unknown",
"Fortune favors the brave.|Unknown",
"Great spirits have always encountered violent opposition from mediocre minds.|Unknown",
"I have been blessed with a great spirit.|Unknown",
"For hope is but the dream of those that wake.|Unknown",
"Constant dripping hollows out a stone.|Unknown",
"Every artist was first an amateur.  Every master was once a disaster.|Unknown",
"I accept the challenge.|Me",
"I am a warrior. My blade is sharp, my armor is strong, my action is fierce.|Unknown",
"Strike Hard! Strike Fast! Strike First!  Strike Last!|Scott",
"The journey of a thousand miles begins with a single step.|Lao Tzu",
"Failure is not learning from the blunder.|Unknown",
"You cannot dream yourself into a character; you must hammer and forge yourself one.|Unknown",
"A good name will shine forever.|Unknown",
"If you don't know where you are going, you'll end up someplace else.|CS Lewis",
"Who aims at excellence will be above mediocrity; who aims at mediocrity will be far short of it.|Unknown",
"The art of being wise is knowing what to overlook.|Unknown",
"Chance favors the prepared mind.|Unknown",
"Of all parts of wisdom, the practice is the best.|John Tillotson",
"Play for more than you can afford to lose and you will learn the game.|Unknown",
"Never say more than is necessary.|Unknown",
"It is better to light one candle than to curse the darkness.|Unknown",
"If you want the same results, do what you just did.|Unknown",
"Never part without loving words to think of during your absence.  It may be that you will not meet them again in this life.|Unknown",
"I do not forget small kindnesses, and I do not remember small faults.|Unknown",
"If you love what you do, you'll never have to work another day in your life.|Unknown",
"You don't get paid for the hour.  You get paid for the value you bring to the hour.|Unknown",
"What can I do?  What can I read?  Who could I ask ?|Unknown",
"Don't wish it were easier, strive to be better.|Unknown",
"Discipline is the bridge between goals and accomplishments.|Unknown",
"Don't talk, just ACT! Don't say, just SHOW! Don't promise, just DELIVER !|Unknown",
"It's a slow process, but quitting won't speed it up.|Unknown",
"Set a goal that makes you want to jump out of bed in the morning.|Unknown",
"Discipline is the bridge between goals and accomplishment.|Unknown",
"When you want to succeed as bad as you want to breathe, then you'll be successful.|Unknown",
"Hard work beats talent when talent doesn't work hard.|Unknown",
"Champions train, losers complain.|Unknown",
"What did I do today that was better than yesterday ?|Unknown",
"Discipline is doing what needs to be done, even if you don't want to do it.|Unknown",
"The one who falls and gets up is so much stronger than the one who never fell.|Unknown",
"Hustle until your haters ask if you're hiring.|Unknown",
"If your dreams don't scare you, they aren't big enough.|Unknown",
"You didn't come this far to only come this far.|Unknown",
"Work so hard that one day your signature will be called an autograph.|Unknown",
"There may be people that have more talent than you, but there's no excuse for anyone to work harder than you do.|Unknown",
"It's hard to beat a person that never gives up.|Unknown",
"Don't stop when you're tired, stop when you're done.|Unknown",
"Today I will do what others won't, so tomorrow I can do what others can't.|Unknown",
"Income seldom exceeds personal development.|Unknown",
"During the darkest of nights is when the stars shine the brightest.|Unknown",
"The night is darkest just before the sun lights the sky.|Unknown",
"Keep working, even when nobody is watching.|Unknown",
"If you do not believe in yourself, no one will do it for you.|Unknown",
"Champions don't show up to get everything they want; they show up to give everything they have.|Unknown",
"If you want to be the best, you have to do what other people won't.|Unknown",
"Throw me to the wolves, and I will return - leading the pack.|Unknown",
"If they say it's impossible, remember that it's impossible for THEM, not YOU !|Unknown",
"You cannot change your destination overnight, but you can change your direction.|Unknown",
"Learn how to be happy with what you have while you pursue all that you want.|Unknown",
"If you are not willing to risk the unusual, you will have to settle for the ordinary.|Unknown",
"We can have more than we've got because we can become more than we are.|Unknown",
"Affirmation without discipline is the beginning of delusion.|Unknown",
"I look for the greatness in all man.|Unknown",
"Winning isn't everything, but wanting to win is. |Vince Lombardi",
"If you have to eat that frog, no sense in looking at it. |Mark Twain",
"Forgiveness is the fragrance the violet sheds on the heel that has crushed it. |Mark Twain",
"Thunder is good, thunder is impressive; but it is the lightning that does the work. |Mark Twain",
"Laws control the lesser man.. Right conduct controls the greater one. |Mark Twain",
"The secret of getting ahead is getting started. |Mark Twain",
"A person who won't read has no advantage over a person who can't read. |Mark Twain",
"If you quit once, it becomes a habit - never quit. |Michael Jordan",
"You don't drown by falling into water.  You only drown if you stay there. |Zig Ziglar",
"People often say that motivation doesn't last.  Well, neither does bathing - that's why we reocmmend it daily. |Zig Ziglar",
"Remember that failure is an event, not a person. |Zig Ziglar",
"You don't have to be great to start, but you have to start to be great. |Zig Ziglar",
"A goal properly set is halfway reached. |Zig Ziglar",
"Be careful not to compromise what you want most for what you want now. |Zig Ziglar",
"Do more than you are being paid to do, and you'll eventually be paid more for what you do. |Zig Ziglar",
"If you go looking for a friend, you're going to find they're very scarce.  If you go out to be a friend, you'll find them everywhere. |Zig Ziglar",
"Expect the best.  Prepare for the worst.   Capitalize on what comes.  |Zig Ziglar",
"If you treat your wife like a thoroughbred, you'll never end up with a nag. |Zig Ziglar",
"It's not what you've got, it's what you use that makes a difference. |Zig Ziglar",
"The limits of tyrants are prescribed by the endurance of those whom they oppress. |Frederick Douglas",
"The thing worse than rebellion is the thing that causes rebellion. |Frederick Douglas",
"It's not what you look at that matters, it's what you see. |Henry David Thoreau",
"Men go fishing all of their lives without knowing that it is not hte fish they are after. |Henry David Thoreau",
"It's not enough to be busy.  So are the ants.  The question is:  What are we busy about? |Henry David Thoreau",
"Success usually comes to those who are too busy to be looking for it. |Henry David Thoreau",
"The price of anything is the amount of life you are willing to exchange for it. |Henry David Thoreau",
"What is once well done is done forever. |Henry David Thoreau",
"It takes two to speak the truth: one to speak, and another to hear. |Henry David Thoreau",
"The man who goes alone can start today; but he who travels with another must wait till that other is ready. |Henry David Thoreau",
"Do not hire a man who does your work for money, but him who does it for the love of it. |Henry David Thoreau",
"It is best to avoid the beginnings of evil. |Henry David Thoreau",
"Love all, trust a few, do wrong to none. | Shakespear",
"How far that little candle throws it's beams! So shines a good dead in a naughty world. |Shakespear",
"The empty vessel makes the loudest sound. |Shakespear",
"I wasted time, and now doth time waste me. |Shakespear",
"Cowards die many times before their deaths; the valiant never taste of death but once. |Shakespear",
"The opportunity to secure ourselves against default lies in our own hands, but the opportunity of defeating the enemy is provided by the enemy himself. |Sun Tzu",
"Pretend inferiority and encourage his arrogance. |Sun Tzu",
"Secret operation are essential in war; upon them the army relies to make its every move. |Sun Tzu",
"Thus, what is of supreme importance in war is to attack the enemy's strategy. |Sun Tzu",
"Prohibit the taking of omens, and do away with superstitious doubts.  Then, until death itself comes, no calamity need be feared. |Sun Tzu",
"There are no secrets to success.  It is the result of preparation, hard work, and learning from failure. |Colin Powell",
"Success isn't always about greatness.  It's about consistency.  Consistent hard work leads to success.  Greatness will come. |Dwayne Johnson",
"Perseverance is the hard work you do after you get tired of doing the hard work you already did. |Newt Gingrich",
"Pray as though everything depended on God.  Work as though everything depeneded on you. |St. Augustine",
"If I am walking with two other men, each of them will serve as my teacher.  I will pick out the good points of one and imitate them, and the bad points of the other and correct them in myself. |Confucius",
"Ability will never catch up with the demand for it. |Confucious",
"It is more shameful to distrust your friends than to be deceived by them. |Confucious",
"Look at the means which a man employs, consider his motives, observe his pleasures.  A man simply cannot conceal himself. |Confucious",
"Those who realize their folly are not true fools. |Zhuangzi",
"When the well is dry, they know the worth of water. |Benjamin Franklin",
"It's easier to prevent bad habits than to break them. |Benjamin Franklin",
"You may delay, but time will not. |Benjamin Franklin",
"A false friend and a shadow attend only while the sun shines. |Benjamin Franklin",
"Necessity never made a good bargain. |Benjamin Franklin",
"Observe all men, thyself most. |Benjamin Franklin",
"If you could kick the person in the pants responsible for most of your trouble, you wouldn't sit for a month. |Theodore Roosevelt",
"For God gave us a spirit not of fear but of power and love and self-control. |2 Timothy 1:7",
"Behold, I have given you authority to tread on serpents and scorpions, and over all the power of the enemy, and nothing shall hurt you. |Luke 10:19",
"He gives power to the faint, and to him who has no might he increases strength. Even youths shall faint and be weary, and young men shall fall exhausted; but they who wait for the Lord shall renew their strength; they shall mount up with wings like eagles; they shall run and not be weary; they shall walk and not faint. |Isaiah 40:29-31",
"Finally, brothers, rejoice. Aim for restoration, comfort one another, agree with one another, live in peace; and the God of love and peace will be with you. |2 Corinthians 13:11",
"But Jesus looked at them and said, 'With man this is impossible, but with God all things are possible.'|Matthew 19:26",
"Fear not, for I am with you; be not dismayed, for I am your God; I will strengthen you, I will help you, I will uphold you with my righteous right hand. |Isaiah 41:10",
"Death and life are in the power of the tongue, and those who love it will eat its fruits. |Proverbs 18:21",
"But be doers of the word, and not hearers only, deceiving yourselves. |James 1:22",
"Ah, Lord God! It is you who have made the heavens and the earth by your great power and by your outstretched arm! Nothing is too hard for you. |Jeremiah 32:17",
"Therefore I tell you, whatever you ask in prayer, believe that you have received it, and it will be yours. |Mark 11:24",
"A soft answer turns away wrath, but a harsh word stirs up anger. |Proverbs 15:1",
"Let no corrupting talk come out of your mouths, but only such as is good for building up, as fits the occasion, that it may give grace to those who hear. |Ephesians 4:29",
"Gracious words are like a honeycomb, sweetness to the soul and health to the body.  |Proverbs 16:24",
"A gentle tongue is a tree of life, but perverseness in it breaks the spirit. |Proverbs 15:4",
"A slack hand causes poverty, but the hand of the diligent makes rich. |Proverbs 10:4",
"The hand of the diligent will rule, while the slothful will be put to forced labor. |Proverbs 12:24",
"Do your best to present yourself to God as one approved, a worker who has no need to be ashamed, rightly handling the word of truth.  |2 Timothy 2:15",
"Whatever your hand finds to do, do it with your might, for there is no work or thought or knowledge or wisdom in Sheol, to which you are going. |Ecclesiastes 9:10",
"Go to the ant, O sluggard; consider her ways, and be wise. Without having any chief, officer, or ruler, she prepares her bread in summer and gathers her food in harvest.  |Proverbs 6:6-8",
"Keep your heart with all vigilance, for from it flow the springs of life. |Proverbs 4:23",
"Know well the condition of your flocks, and give attention to your herds, |Proverbs 27:23",
"The blessing of the Lord makes rich, and he adds no sorrow with it. |Proverbs 10:22",
"In all toil there is profit, but mere talk tends only to poverty. |Proverbs 14:23",
"I love those who love me, and those who seek me diligently find me. |Proverbs 8:17",
"Set your minds on things that are above, not on things that are on earth. |Colossians 3:2",
"Call to me and I will answer you, and will tell you great and hidden things that you have not known. |Jeremiah 33:3",
"Do not present your members to sin as instruments for unrighteousness, but present yourselves to God as those who have been brought from death to life, and your members to God as instruments for righteousness. |Romans 6:13",
"For even when we were with you, we would give you this command: If anyone is not willing to work, let him not eat. |2 Thessalonians 3:10",
"So put away all malice and all deceit and hypocrisy and envy and all slander. |1 Peter 2:1",
"The rich rules over the poor, and the borrower is the slave of the lender. |Proverbs 22:7",
"Be not one of those who give pledges, who put up security for debts. If you have nothing with which to pay, why should your bed be taken from under you? |Proverbs 22:26-27",
"Owe no one anything, except to love each other, for the one who loves another has fulfilled the law. |Romans 13:8",
"On the first day of every week, each of you is to put something aside and store it up, as he may prosper, so that there will be no collecting when I come. |1 Corinthians 16:2",
"Give to the one who begs from you, and do not refuse the one who would borrow from you. |Matthew 5:42",
"Whoever is greedy for unjust gain troubles his own household, but he who hates bribes will live. |Proverbs 15:27",
"You shall not oppress your neighbor or rob him. The wages of a hired servant shall not remain with you all night until the morning. |Leviticus 19:13",
"As for the rich in this present age, charge them not to be haughty, nor to set their hopes on the uncertainty of riches, but on God, who richly provides us with everything to enjoy. |1 Timothy 6:17",
"Give a portion to seven, or even to eight, for you know not what disaster may happen on earth. |Ecclesiastes 11:2",
"Prepare your work outside; get everything ready for yourself in the field, and after that build your house. |Proverbs 24:27",
"Better is a little with righteousness than great revenues with injustice.  |Proverbs 16:8",
"Therefore do not be anxious about tomorrow, for tomorrow will be anxious for itself. Sufficient for the day is its own trouble. |Matthew 6:34",
"Without counsel plans fail, but with many advisers they succeed. |Proverbs 15:22",
"By wisdom a house is built, and by understanding it is established; by knowledge the rooms are filled with all precious and pleasant riches. |Proverbs 24:3-4",
"Be kind to one another, tenderhearted, forgiving one another, as God in Christ forgave you. |Ephesians 4:32",
"And whenever you stand praying, forgive, if you have anything against anyone, so that your Father also who is in heaven may forgive you your trespasses. |Mark 11:25",
"If we confess our sins, he is faithful and just to forgive us our sins and to cleanse us from all unrighteousness. |1 John 1:9",
"But if you do not forgive others their trespasses, neither will your Father forgive your trespasses. |Matthew 6:15",
"Judge not, and you will not be judged; condemn not, and you will not be condemned; forgive, and you will be forgiven |Luke 6:37",
"Bearing with one another and, if one has a complaint against another, forgiving each other; as the Lord has forgiven you, so you also must forgive. |Colossians 3:13",
"But I say to you who hear, Love your enemies, do good to those who hate you |Luke 6:27",
"And forgive us our debts, as we also have forgiven our debtors. |Matthew 6:12",
"Whoever conceals his transgressions will not prosper, but he who confesses and forsakes them will obtain mercy. |Proverbs 28:13",
"Let the wicked forsake his way, and the unrighteous man his thoughts; let him return to the Lord, that he may have compassion on him, and to our God, for he will abundantly pardon. |Isaiah 55:7",
"If your enemy is hungry, give him bread to eat, and if he is thirsty, give him water to drink, |Proverbs 25:21",
"A new commandment I give to you, that you love one another: just as I have loved you, you also are to love one another. |John 13:34",
"Therefore, if anyone is in Christ, he is a new creation. The old has passed away; behold, the new has come. |2 Corinthians 5:17",
"And as they continued to ask him, he stood up and said to them, 'Let him who is without sin among you be the first to throw a stone at her.' |John 8:7",
"Do you see a man skillful in his work? He will stand before kings; he will not stand before obscure men. |Proverbs 22:29",
"And he has filled him with the Spirit of God, with skill, with intelligence, with knowledge, and with all craftsmanship |Exodus 35:31",
"If any of you lacks wisdom, let him ask God, who gives generously to all without reproach, and it will be given him. |James 1:5",
"Look carefully then how you walk, not as unwise but as wise, making the best use of the time, because the days are evil. Therefore do not be foolish, but understand what the will of the Lord is. Ephesians |5:15-17",
"Listen to advice and accept instruction, that you may gain wisdom in the future. |Proverbs 19:20",
"Whoever restrains his words has knowledge, and he who has a cool spirit is a man of understanding. Even a fool who keeps silent is considered wise; when he closes his lips, he is deemed intelligent. |Proverbs 17:27-28",
"When pride comes, then comes disgrace, but with the humble is wisdom. |Proverbs 11:2",
"A fool gives full vent to his spirit, but a wise man quietly holds it back. |Proverbs 29:11",
"By insolence comes nothing but strife, but with those who take advice is wisdom. |Proverbs 13:10",
"Whoever walks with the wise becomes wise, but the companion of fools will suffer harm. |Proverbs 13:20",
"Walk in wisdom toward outsiders, making the best use of the time. Let your speech always be gracious, seasoned with salt, so that you may know how you ought to answer each person. |Colossians 4:5-6",
"Whoever is slow to anger has great understanding, but he who has a hasty temper exalts folly. |Proverbs 14:29"
        ]

        # how many total in our list
        counted = len(inspirations)

        # pick a random one
        chosenJuan = str(inspirations[random.randint(1,counted)])
        
        # show the popup
        mb.showinfo("Information", chosenJuan)
        print("Inspired")

def main():
    root = Tk()
    app = App()
    root.mainloop()

# ok, do the stuff above
if __name__ == "__main__":
    main()
