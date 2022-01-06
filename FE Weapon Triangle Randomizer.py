import random, glob
from itertools import product
from pathlib import Path
import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfilename
from tkinter import messagebox
from string import ascii_letters as Letterlist
from string import digits as Numberlist

GUI = True #command line version not implemented yet
defFile = "WeaponRelationDefs.event"

#defualt List of weapon types
WeaponList = ('Sword','Lance','Axe','Bow','Light','Anima','Dark','Monster')

#File loading/saving functions
def askForFileIn(filedata=()):
	filedata += (("all files","*.*"),)
	file = askopenfilename(title="Open",filetypes=filedata)
	return Path(file)

def askForFileOut(filedata=()):
	filedata += (("all files","*.*"),)
	file = asksaveasfilename(title="Save As",filetypes=filedata)
	return Path(file)

def isValidFile(file):
	if not file:
		return False
	return file.is_file()

class App:
	'''
	UI for the randomizer
	self.master is the tk root
	modes is a tuple of each randomizer modes' name and fuction
	'''
	
	def __init__(self,title="Python GUI"):
		self.modes = (
		('Triangle',triRando,\
			'Create weapon triangles'),
		('Pair',pairRando,\
			'generate random relationship pairs.\n If A is set to have an advantage against B, then B will be set to have an equal disadvantage against A'),
		('Circular',circleRando,\
			"create a circular relationship where every weapon has \n an advantage against in the next one in the sequence"),
		('Chaos',chaosRando,\
			'generate completely random relationships')
		)
		
		self.master = tk.Tk()
		self.master.title(title)
		self.master.geometry('500x500')
		self.buildUI()
		self.master.mainloop()
		
	def buildUI(self):
		self.frames = {}
		self.values = {}
		self.widgets = {} #hold widgets we might access later
		
		self.mainframe = ttk.Frame(self.master)
		self.mainname = ttk.Label(self.master,text='Weapon Relation Randomizer')
		self.mainname.pack(side=tk.TOP)
		
		
		topbox = ttk.Frame(self.mainframe)
		topbox.grid(row=1,column=0,rowspan=2,columnspan=3)
		self.frames['topbox'] =  topbox
		
		#setup seed ui
		self.values['seed'] = tk.StringVar()
		seedname = ttk.Label(topbox,text='Seed:')
		seedname.grid(row=0,column=1,sticky=tk.E,padx=2)
		seedentry = ttk.Entry(topbox,textvariable=self.values['seed'])
		seedentry.grid(row=0,column=2,columnspan=2,sticky=tk.E+tk.W)
		seedchange = ttk.Button(topbox,text='New Seed',command=self.newseed)
		seedchange.grid(row=0,column=4,sticky=tk.W,padx=2,pady=2)
		
		CreateToolTip(seedchange,'Generate a new seed')
		
		#setup output file selection ui
		self.values['outfile'] = tk.StringVar()
		outname = ttk.Label(topbox,text='File:')
		outname.grid(row=1,column=1,sticky=tk.E,padx=2)
		outentry = ttk.Entry(topbox,textvariable=self.values['outfile'])
		outentry.grid(row=1,column=2,columnspan=2,sticky=tk.E+tk.W)
		outfind = ttk.Button(topbox,text=' Browse...',command=self.loadfile)
		outfind.grid(row=1,column=4,sticky=tk.W,padx=2,pady=3)
		
		statbox = ttk.Frame(self.mainframe)
		poolbox = ttk.Frame(self.mainframe)
		modebox = ttk.Frame(self.mainframe)
		modeconfig = ttk.Frame(self.mainframe)
		statbox.grid(row=3,column=0,rowspan=2,columnspan=3,ipady=5,sticky=(tk.E+tk.W))
		modebox.grid(row=5,column=0,rowspan=2,columnspan=1,ipadx=5,sticky=tk.N)
		poolbox.grid(row=3,column=3,rowspan=4,columnspan=2,pady=5,padx=5)
		modeconfig.grid(row=5,column=1,rowspan=2,sticky=tk.N)
		
		#List of weapon types
		self.frames['poolbox'] = poolbox
		self.values['pooladd'] = tk.StringVar()
		wpoolname = ttk.Label(poolbox,text='Weapons Pool')
		wpoolname.grid(row=0,column=0,columnspan=3)
		wpool = tk.Listbox(poolbox)
		wpool.grid(row=1,rowspan=3,columnspan=3,sticky=tk.E+tk.W,pady=5)
		poolpop = ttk.Button(poolbox,text='Remove',command=self.wremove)
		poolpush = ttk.Button(poolbox,text='Add',command=self.winsert)
		poolinput = ttk.Entry(poolbox,textvariable=self.values['pooladd'])
		poolpop.grid(row=4,column=0,columnspan=3,sticky=tk.E+tk.W)
		poolinput.grid(row=5,column=0,columnspan=2)
		poolpush.grid(row=5,column=2)
		poolscroll = ttk.Scrollbar(poolbox, orient=tk.VERTICAL, command=wpool.yview)
		poolscroll.grid(row=1,column=3,rowspan=3,sticky=tk.N+tk.S+tk.W)
		wpool['yscrollcommand'] = poolscroll.set
		
		#add default weapon types to pool
		for w in WeaponList: wpool.insert(tk.END,w)
		self.widgets['wpool'] = wpool
		
		#set range for stat variation
		self.frames['statbox'] = statbox
		self.values['minatk'] = tk.IntVar()
		self.values['maxatk'] = tk.IntVar()
		self.values['minhit'] = tk.IntVar()
		self.values['maxhit'] = tk.IntVar()
		self.values['minrel'] = tk.IntVar()
		self.values['maxrel'] = tk.IntVar()
		self.values['singleroll'] = tk.IntVar()
		statword = ttk.Label(statbox,text='Weapon Advantage')
		maxword = ttk.Label(statbox,text='Max')
		minword = ttk.Label(statbox,text='Min')
		hitword = ttk.Label(statbox,text='Accuracy')
		atkword = ttk.Label(statbox,text='Damage')
		statword.grid(row=0,columnspan=4)
		minword.grid(row=1,column=2)
		maxword.grid(row=1,column=3)
		hitword.grid(row=2,column=0)
		atkword.grid(row=3,column=0)
		minhitdata = ttk.Spinbox(statbox,from_=0,to=100,increment=5,textvariable=self.values['minhit'],width=10,command=self.adjustmin)
		maxhitdata = ttk.Spinbox(statbox,from_=5,to=100,increment=5,textvariable=self.values['maxhit'],width=10,command=self.adjustmax)
		minhitdata.grid(row=2,column=2)
		maxhitdata.grid(row=2,column=3)
		minatkdata = ttk.Spinbox(statbox,from_=0,to=15,textvariable=self.values['minatk'],width=10,command=self.adjustmin)
		maxatkdata = ttk.Spinbox(statbox,from_=0,to=15,textvariable=self.values['maxatk'],width=10,command=self.adjustmax)
		minatkdata.grid(row=3,column=2)
		maxatkdata.grid(row=3,column=3)
		relword = ttk.Label(statbox,text='Count')
		relword.grid(row=4,column=0)
		minreldata = ttk.Spinbox(statbox,from_=1,to=len(WeaponList),textvariable=self.values['minrel'],width=10,command=self.adjustmin)
		maxreldata = ttk.Spinbox(statbox,from_=1,to=len(WeaponList),textvariable=self.values['maxrel'],width=10,command=self.adjustmax)
		minreldata.grid(row=4,column=2)
		maxreldata.grid(row=4,column=3)
		
		self.widgets['minreldata']=minreldata
		self.widgets['maxreldata']=maxreldata
		CreateToolTip(relword,'Amount of relations to give to each weapon')
		
		rollcheck = ttk.Checkbutton(statbox,text='Roll Once',variable=self.values['singleroll'])
		rollcheck.grid(row=5,columnspan=4)
		
		CreateToolTip(rollcheck,'roll once and use the same \n values for every relation')
		
		#set default values
		self.values['minhit'].set(15)
		self.values['maxhit'].set(15)
		self.values['minatk'].set(1)
		self.values['maxatk'].set(1)
		self.values['minrel'].set(1)
		self.values['maxrel'].set(1)
		
		#randomizer mode selection
		self.frames['modebox'] = modebox
		self.frames['modeconfig'] = modeconfig
		self.values['randomode'] = tk.IntVar()
		modetitle = ttk.Label(modebox,text='Mode')
		modetitle.grid(row=0)
		
		for (z,m) in enumerate(self.modes):
			mode = ttk.Radiobutton(modebox,text=m[0],value=z,variable=self.values['randomode'])
			mode.grid(row=z+1,sticky=tk.W)
			CreateToolTip(mode,m[2])
		
		#randomizer settings
		configtitle = ttk.Label(modeconfig,text='Options')
		configtitle.grid(row=0)
		self.values['pair'] = tk.IntVar()
		paircheck = ttk.Checkbutton(modeconfig,variable=self.values['pair'],text='Symmetry')
		paircheck.grid(row=1,sticky=tk.W)
		CreateToolTip(paircheck,'When checked, ensure that all relations go both ways\n(If Swords beat Axes, Axes will lose to Swords)')
		self.values['selfnull'] = tk.IntVar()
		selfneutral = ttk.Checkbutton(modeconfig,variable=self.values['selfnull'],text='Self Neutrality')
		selfneutral.grid(row=2,sticky=tk.W)
		CreateToolTip(selfneutral,'When checked, even weapon vs itself matchup will be neutral')
		
		#button to start randomization
		run = ttk.Button(self.mainframe,text='Randomize',command=self.randomize)
		run.grid(row=7,column=0,columnspan=5,pady=5,sticky=tk.E+tk.W)
		CreateToolTip(run,"Start the randomizer")
		
		
		self.mainframe.pack()
		
	def adjustmin(self):
		'''ensure the min values never rise above the max values'''
		if self.values['minhit'].get() > self.values['maxhit'].get():
			self.values['maxhit'].set(self.values['minhit'].get())
		if self.values['minatk'].get() > self.values['maxatk'].get():
			self.values['maxatk'].set(self.values['minatk'].get())
		if self.values['minrel'].get() > self.values['maxrel'].get():
			self.values['maxrel'].set(self.values['minrel'].get())
	def adjustmax(self):
		'''ensure the max values never fall below the min values'''
		if self.values['maxhit'].get() < self.values['minhit'].get():
			self.values['minhit'].set(self.values['maxhit'].get())
		if self.values['maxatk'].get() < self.values['minatk'].get():
			self.values['minatk'].set(self.values['maxatk'].get())
		if self.values['maxrel'].get() < self.values['minrel'].get():
			self.values['minrel'].set(self.values['maxrel'].get())
	def wremove(self):
		'''
		remove selected weapon type from pool
		'''
		z = self.widgets['wpool'].curselection()
		if z: self.widgets['wpool'].delete(z)
		
	def winsert(self):
		'''
		add weapon type to pool
		'''
		z = self.values['pooladd'].get()
		if z: self.widgets['wpool'].insert(tk.END,z)
		
	def newseed(self):
		random.seed()
		nseed = ''.join(random.choice(Numberlist+Letterlist) for _ in range(10))
		self.values['seed'].set(nseed)
		
	def loadfile(self):
		file = askForFileOut((('Event File(EA)','*.event'),))
		
		if file != Path():
			if not file.suffix: file = file.with_suffix('.event')
			self.values['outfile'].set(str(file))
	
	def randomize(self):
		'''start randomization for gui'''
		settings = {}
		settings['weaponlist'] = self.widgets['wpool'].get(0,tk.END)
		wrlist = RelationList(settings['weaponlist'])
		
		(min,max) = (self.values['minatk'].get(),self.values['maxatk'].get())
		settings['ratk'] = range(min,max+1)
		(min,max) = (self.values['minhit'].get(),self.values['maxhit'].get())
		settings['rhit'] = range(min,max+1,5)
		(min,max) = (self.values['minrel'].get(),self.values['maxrel'].get())
		settings['rcnt'] = range(min,max+1)
		
		settings['symmetry'] = bool(self.values['pair'].get())
		settings['rollonce'] = bool(self.values['singleroll'].get())
		settings['selfnull'] = bool(self.values['selfnull'].get())
		
		#set randomizer seed
		if not self.values['seed'].get(): self.newseed()
		settings['seed'] = self.values['seed'].get()
		
		# if self.values['singleroll'].get():
			# ratk = [random.choice(ratk)]
			# rhit = [random.choice(rhit)]
			# random.seed(self.values['seed'].get())
		
		
		m = self.values['randomode'].get()
		if m in range(len(self.modes)):
			self.modes[m][1](wrlist,settings)
			self.writefile(wrlist,settings,m)
		return
	
	def writefile(self,relations,settings,mode):
		def printMacro(rw1,rw2,wr):
			return 'WeaponRelation('+rw1+','+rw2+\
			','+str(wr['hit'])+','+str(wr['atk'])+')'
		if not self.values['outfile'].get():
			self.loadfile()
		if self.values['outfile'].get():
			#write seed and settings to file
			output = '/* '
			output += 'Weapon Relations Randomizer\n\n'
			output += 'Seed: ' + settings['seed'] + '\n'
			output += 'Mode: ' + self.modes[mode][0] + '\n'
			output += 'Settings:\n'
			output += '\tAccuracy\tMin: ' + str(min(settings['rhit']))+ '\tMax: ' + str(max(settings['rhit']))+'\n'
			output += '\tDamage\t\tMin: ' + str(min(settings['ratk']))+ '\tMax: ' + str(max(settings['ratk']))+'\n'
			output += '\tSingleRoll: ' + str(settings['rollonce']) + '\n'
			output += '\tSymmetry: ' + str(settings['symmetry']) + '\n'
			output += '\tSelf Neutral: ' + str(settings['selfnull']) + '\n'
			output += '*/\n\n'
			output += '#include "'+defFile+'"\n\n'
			#print relations
			weapons = self.widgets['wpool'].get(0,tk.END)
			for w1 in settings['weaponlist']:
				output += '//' +w1 + ' Relations\n'
				for w2 in settings['weaponlist']:
					r = relations.getRelation(w1,w2)
					if r['atk'] or r['hit']:
						output += printMacro(w1,w2,r)+'\t  '
					output +='//'+relations.matchup(w1,w2)+'\n'
				output+= '\n'
			output += 'WeaponRelationEnd\n'
			output += '\n// **Any Relation that is not shown here is neutral**\n'
			#generate file
			Path(self.values['outfile'].get()).write_text(output)
			genDefs(Path(self.values['outfile'].get()))
			prompt = messagebox.showinfo(title='Randomizing Complete!',message='Randomzing Complete!')
			return

class ToolTip(object):
	'''create a tooltip for a given widget'''
	def __init__(self, widget):
		self.widget = widget
		self.tipwindow = None
		self.id = None
		self.x = self.y = 0

	def showtip(self, text):
		"Display text in tooltip window"
		self.text = text
		if self.tipwindow or not self.text:
			return
		x, y, cx, cy = self.widget.bbox("insert")
		x = x + self.widget.winfo_rootx() + 57
		y = y + cy + self.widget.winfo_rooty() +27
		self.tipwindow = tw = tk.Toplevel(self.widget)
		tw.wm_overrideredirect(1)
		tw.wm_geometry("+%d+%d" % (x, y))
		label = tk.Label(tw, text=self.text, justify=tk.LEFT,
					  background="#ffffe0", relief=tk.SOLID, borderwidth=1,
					  font=("tahoma", "8", "normal"))
		label.pack(ipadx=1)

	def hidetip(self):
		tw = self.tipwindow
		self.tipwindow = None
		if tw:
			tw.destroy()

def CreateToolTip(widget, text):
	toolTip = ToolTip(widget)
	def enter(event):
		toolTip.showtip(text)
	def leave(event):
		toolTip.hidetip()
	widget.bind('<Enter>', enter)
	widget.bind('<Leave>', leave)
	
class RelationList:
	'''
	pow = damage modifier
	hit = accuracy modifier
	
	
	'''
	
	def __init__(self,wlist):
		'''
		wlist is the list of weapon types
		'''
		self.rlist = dict()
		for w1 in wlist:
			self.rlist[w1] = dict()
		for (w1,w2) in product(wlist,wlist):
			self.rlist[w1][w2] = {'atk':0,'hit':0}
		
	def setRelation(self,w1,w2,accuracy=0,damage=0):
		self.rlist[w1][w2]['atk'] = damage
		self.rlist[w1][w2]['hit'] = accuracy
		return
	
	def getRelation(self,w1,w2):
		return self.rlist[w1][w2]
	
	def isNeutral(self,w1,w2):
		r = self.rlist[w1][w2]
		a = r['atk']
		h = r['hit']
		z = not (a or h)
		return z
	
	def matchup(self,w1,w2):
		text = ''
		# if self.rlist[w1][w2]['atk'] or self.rlist[w1][w2]['hit']:
			# text += ('WeaponRelation('+self.wt1+','
			# +self.wt2+','+str(self.rlist[w1][w2]['hit'])+','
			# +str(self.rlist[w1][w2]['atk']) + ')  \t')
			
		if self.rlist[w1][w2]['hit'] > 0 or (not self.rlist[w1][w2]['hit'] and self.rlist[w1][w2]['atk'] > 0):
			text += (w1+' vs '+w2 + ': Advantage')
		elif self.rlist[w1][w2]['hit'] < 0 or (not self.rlist[w1][w2]['hit'] and self.rlist[w1][w2]['atk'] < 0):
			text += (w1+' vs '+w2+ ': Disadvantage')
		else:
			text += (w1+' vs '+w2 +': Neutral')
		
		return text
		
def genDefs(defpath):
	'''
	generate the definitions file if it 
	does not exist in the given directory
	'''
	z= '''#ifndef FreeSpace
	#ifdef _FE6_
	#define FreeSpace 0xE08000
	ORG FreeSpace
	#endif
	#ifdef _FE7_
	#define FreeSpace 0xD20000
	ORG FreeSpace
	#endif
	#ifdef _FE8_
	#define FreeSpace 0xb2a610
	ORG FreeSpace
	#endif
#endif

#ifndef WeaponRelationDefs
	#define WeaponRelationDefs
	//repoint to new weapon table
	#ifdef _FE6_
	PUSH
	ORG $25A9C
	POIN WeaponRelationships
	// orginal at $5C61C0
	POP
	#endif

	#ifdef _FE7_
	PUSH
	ORG $2A17C 
	POIN WeaponRelationships 
	// original at $B9426C
	POP
	#endif

	#ifdef _FE8_
	PUSH
	ORG $2C7CC
	POIN WeaponRelationships 
	// original at $59BA90
	POP
	#endif
	
	#define WeaponRelation(awtype,dwtype,hit,damage) "BYTE awtype dwtype (hit) (damage)"
	#define WeaponRelationEnd "BYTE 0xFF 0x0 0x0 0x0"
	
	//define weapon types
	#ifndef WeaponTypes
		
		#define WeaponTypes
		
		//Define Weapon Types here
		//These are already defined in EAstlib
		#define Sword 0x0
		#define Lance 0x1
		#define Axe 0x2
		#define Bow 0x3
		#define Staff 0x4
		#define Anima 0x5
		#define Light 0x6
		#define Dark 0x7
		
		//used by monsters in FE8 and probably also the final bosses
		#define Monster 0xB
		//add new weapon types here
		
	#endif

#endif
	'''
	x = defpath.with_name(defFile)
	if not glob.glob(str(x),recursive=False):
		x.write_text(z)
		
def randoStart():
	'''prepare for randomization without gui'''
	weapons = WeaponList
	#Get list of weapon types from ui
	#otherwise use the default
	ratk = range(1,5+1)	#range for damage bonus randomization
	rhit = range(10,25+1,5)	#range for accuracy bonus randomization
	#call a rando function based on settings
	wtalist = triRando(weapons,rhit,ratk)
	#write output to file
	print('WeaponRelations:')
	for wr in wtalist:
		print(wr.output())
	print('WeaponRelationEnd')
	return

def pairRando(weapons,rhit,ratk):
	'''weapon relations are random pairings
	if weapon 1 beats weapon 2 then 2 will lose to 1
	'''
	wtalist = []
	pairings = []
	for (z,x) in product(weapons,weapons):
		#skip if pairing already exists
		if (x,z) in pairings:
			continue
		if (z,x) in pairings:
			continue
		#decide whether this is
		#an advantage or disadvantage
		# or neutral
		neg = random.choice([1,0,-1])
		hit = random.choice(rhit) * neg
		atk = random.choice(ratk) * neg
		wr = Relation(z,x)
		wr.setRelation(hit,atk)
		wtalist.append(wr)
		if z != x:
			wr = Relation(x,z)
			wr.setRelation(-hit,-atk)
			wtalist.append(wr)
		pairings.append((z,x))
	return wtalist

def triRando(weapons,rhit,ratk):
	'''randomize to make weapon triangles
	return list of weapon relations'''
	wtalist = []
	
	while(len(weapons) >= 3):
		#grab 3 random weapon types
		w = [None] * 3
		for x in range(3):
			w[x] = random.choice(weapons)
			#remove them from the pool
			weapons.remove(w[x])
		#roll for hit and/or damage bonuses if necessary
		hit = random.choice(rhit)
		atk = random.choice(ratk)
		#create weapon triangle
		for (z,x) in ((w[0],w[1]),(w[1],w[2]),(w[2],w[0])):
			#z has advantage over x
			wr = Relation(z,x)
			wr.setRelation(hit,atk)
			wtalist.append(wr)
			#x has disadvantage to z
			wr = Relation(x,z)
			wr.setRelation(-hit,-atk)
			wtalist.append(wr)
	return wtalist

def circleRando(weapons,rhit,ratk):
	'''randomize all weapon types into a circle
	where each type beats one other type and loses to another'''
	wtalist = []
	pairings = []
	random.shuffle(weapons)
	for v,weapon in enumerate(weapons):
		(z,x) = (weapons[v-1],weapons[v])
		#prevent the same pairing from happening twice
		if (z,x) in pairings: continue
		if (x,z) in weapons: continue
		hit = random.choice(rhit)
		atk = random.choice(ratk)
		wr = Relation(z,x)
		wr.setRelation(hit,atk)
		wtalist.append(wr)
		if z!= x:
			wr = Relation(x,z)
			wr.setRelation(-hit,-atk)
			wtalist.append(wr)
		pairings.append((z,x))
	return wtalist

def chaosRando(weapons,rhit,ratk):
	'''weapon relations are completely random
	return list of one sided weapon relations'''
	wtalist=[]
	for (z,x) in product(weapons,weapons):
		wr = Relation(z,x)
		#decide whether this is
		#an advantage or disadvantage
		# or neutral
		neg = random.choice([1,0,-1])
		# if neg: #skip if 0
		hit = random.choice(rhit) * neg
		atk = random.choice(ratk) * neg
		wr.setRelation(hit,atk)
		wtalist.append(wr)
	return wtalist

if __name__ == '__main__':
	if GUI:
		app = App("GBAFE Weapon Relation Randomizer")
	else:
		randoStart()
		input('Press enter to continue \n')
	