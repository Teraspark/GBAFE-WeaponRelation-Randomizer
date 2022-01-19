#!/usr/bin/python3

# GBA Fire Emblem Weapon Relation Randomizer
# v1.2
# by Teraspark

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
import tags

GUI = True #command line version not implemented yet
def_file = "WeaponRelationDefs.event"

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
		('Triangle',tri_rando,\
			'Create weapon triangles'),
		# ('Pair',pairRando,\
			# 'generate random relationship pairs.\n If A is set to have an advantage against B, then B will be set to have an equal disadvantage against A'),
		('Circular',circle_rando,\
			"create a circular relationship where every weapon has \n an advantage against in the next one in the sequence"),
		('Chaos',chaos_rando,\
			'generate completely random relationships')
		)
		
		self.master = tk.Tk()
		self.master.title(title)
		self.master.geometry('500x400')
		self.build_ui()
		self.master.mainloop()
		
	def build_ui(self):
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
		self.values['minrel'].set(2)
		self.values['maxrel'].set(2)
		
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
		self.values['pair'] = tk.IntVar(value=1)
		paircheck = ttk.Checkbutton(modeconfig,variable=self.values['pair'],text='Symmetry')
		paircheck.grid(row=1,sticky=tk.W)
		CreateToolTip(paircheck,'When checked, ensure that all relations go both ways\n(If Swords beat Axes, Axes will lose to Swords)')
		self.values['selfnull'] = tk.IntVar(value=1)
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
		z = self.widgets['minreldata']['to']
		if self.values['minrel'].get() > z:
			self.values['minrel'].set(z)
		if self.values['minhit'].get() > self.values['maxhit'].get():
			self.values['maxhit'].set(self.values['minhit'].get())
		if self.values['minatk'].get() > self.values['maxatk'].get():
			self.values['maxatk'].set(self.values['minatk'].get())
		if self.values['minrel'].get() > self.values['maxrel'].get():
			self.values['maxrel'].set(self.values['minrel'].get())
	def adjustmax(self):
		'''ensure the max values never fall below the min values'''
		z = self.widgets['maxreldata']['to']
		if self.values['maxrel'].get() > z:
			self.values['maxrel'].set(z)
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
		if z:
			self.widgets['wpool'].delete(z)
			z = len(self.widgets['wpool'].get(0,tk.END))
			self.widgets['minreldata']['to']=z
			self.widgets['maxreldata']['to']=z
			self.adjustmax()
		
	def winsert(self):
		'''
		add weapon type to pool
		'''
		z = self.values['pooladd'].get()
		z = z.strip()
		if z: 
			self.widgets['wpool'].insert(tk.END,z)
			z = len(self.widgets['wpool'].get(0,tk.END))
			self.widgets['minreldata']['to']=z
			self.widgets['maxreldata']['to']=z
		
	def newseed(self):
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
		
		
		if not self.values['outfile'].get():
			self.loadfile()
		m = self.values['randomode'].get()
		if m in range(len(self.modes)):
			self.modes[m][1](wrlist,settings)
			self.writetable(wrlist,settings,m)
			self.writefile(wrlist,settings,m)
		return
	
	def writefile(self,relations,settings,mode):
		'''create the output randomizer event file'''
		def printMacro(rw1,rw2,wr):
			return 'WeaponRelation('+rw1+','+rw2+\
			','+str(wr['hit'])+','+str(wr['atk'])+')'
		if self.values['outfile'].get():
			#write seed and settings to file
			output = '/* '
			output += 'Weapon Relations Randomizer\n\n'
			output += 'Seed:\t' + settings['seed'] + '\n'
			output += 'Mode:\t' + self.modes[mode][0] + '\n'
			output += 'Settings:\n'
			output += '\tAccuracy\tMin: ' + str(min(settings['rhit']))+ '\tMax: ' + str(max(settings['rhit']))+'\n'
			output += '\tDamage\t\tMin: ' + str(min(settings['ratk']))+ '\tMax: ' + str(max(settings['ratk']))+'\n'
			output += '\tCount\t\tMin: ' + str(min(settings['rcnt']))+ '\tMax: ' + str(max(settings['rcnt']))+'\n'
			output += '\tSingleRoll: ' + str(settings['rollonce']) + '\n'
			output += '\tSymmetry: ' + str(settings['symmetry']) + '\n'
			output += '\tSelf Neutral: ' + str(settings['selfnull']) + '\n'
			output += '*/\n\n'
			output += '#include "'+def_file+'"\n\n'
			output += 'WeaponRelationships:\n'
			#print relations
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
	
	def writetable(self,relations,settings,mode):
		'''generate html relations table'''
		def print_value(wrv):
			# tcol = tags.Tag('td')
			# trow.add_content(tcol)
			sp = tags.Tag('span')
			# tcol.add_content(s1)
			# tcol.add_content(tags.BR)
			# s2 = tags.Tag('span')
			# tcol.add_content(s2)
			if wrv < 0:
				sp.add_content(str(wrv))
				sp.set_tag_attr('class','minus')
			elif wrv > 0:
				sp.add_content('+'+str(wrv))
				sp.set_tag_attr('class','plus')
			# if wr['hit'] < 0:
				# s1.add_content(str(wr['hit']))
				# s1.set_tag_attr('class','minus')
			# else:
				# s1.add_content('+'+str(wr['hit']))
				# s1.set_tag_attr('class','plus')
			# if wr['atk'] < 0:
				# s2.add_content(str(wr['atk']))
				# s2.set_tag_attr('class','minus')
			# else:
				# s2.add_content('+'+str(wr['atk']))
				# s2.set_tag_attr('class','plus')
			return sp
		#create new html page
		if not self.values['outfile'].get():
			#do nothing if no output file path
			return
		output = tags.HTML()
		z = tags.Tag('title')
		z.add_content('Weapon Relations Randomizer')
		output.head.add_content(z)
		#set up the style information
		style = tags.Style()
		output.head.add_content(style)
		style.add_tag('table, th, td')
		style.edit_tag('table, th, td','border','1px solid black')
		style.add_class('plus')
		style.add_class('minus')
		style.edit_class('minus','color','red')
		style.edit_class('plus','color','blue')
		#generate body
		z = tags.Tag('h1')
		z.add_content('Weapon Relations Randomizer')
		output.body.add_content(z)
		#output settings
		
		#generate table
		table = tags.Tag('table')
		output.body.add_content(table)
		#generate table
		#header row
		row = tags.Tag('tr')
		table.add_content(row)
		col = tags.Tag('th')
		row.add_content(col)
		col.add_content('Weapons')
		for w in settings['weaponlist']:
			col = tags.Tag('th')
			row.add_content(col)
			col.add_content(w)
		for w1 in settings['weaponlist']:
			# new row
			row = tags.Tag('tr')
			table.add_content(row)
			#first column is weapon type
			col = tags.Tag('th')
			row.add_content(col)
			col.add_content(w1)
			for w2 in settings['weaponlist']:
				col = tags.Tag('td')
				row.add_content(col)
				r = relations.getRelation(w1,w2)
				span = print_value(r['hit'])
				col.add_content(span)
				col.add_content(tags.BR)
				span = print_value(r['atk'])
				col.add_content(span)
				
		#write to file
		z = Path(self.values['outfile'].get())
		z = z.with_suffix('.html')
		output = str(output)
		z.write_text(output)
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
	x = defpath.with_name(def_file)
	if not glob.glob(str(x),recursive=False):
		x.write_text(z)

def circle_rando(relations,settings):
	'''Circular Randomization'''
	def build_circle(hit,atk):
		weapons = list(settings['weaponlist'])
		wc = [random.choice(weapons)]
		weapons.remove(wc[-1])
		while weapons:
			wlist = list(weapons)
			for w in wlist:
				if not relations.isNeutral(wc[-1],w):
					wlist.remove(w)
			wc.append(random.choice(wlist))
			weapons.remove(wc[-1])
		# atk = random.choice(ratk)
		# hit = random.choice(rhit)
		for (n,w) in enumerate(wc):
			relations.setRelation(wc[n-1],wc[n],hit,atk)
			if settings['symmetry']:
				relations.setRelation(wc[n],wc[n-1],-hit,-atk)
		return
	
	random.seed(settings['seed'])
	rhit = settings['rhit']
	ratk = settings['ratk']
	rcnt = settings['rcnt']
	
	if settings['rollonce']:
		ratk = [random.choice(ratk)]
		rhit = [random.choice(rhit)]
		rcnt = [random.choice(rcnt)]
		random.seed(settings['seed'])
	
	circles = random.choice(rcnt)
	for c in range(circles):
		z = random.choice(rhit)
		x = random.choice(ratk)
		build_circle(z,x)
		if not settings['symmetry']:
			z = random.choice(rhit)
			x = random.choice(ratk)
			build_circle(-z,-x)
	return
	
def chaos_rando(relations,settings):
	'''Chaotic Randomization'''
	random.seed(settings['seed'])
	rhit = settings['rhit']
	ratk = settings['ratk']
	rcnt = settings['rcnt']
	
	if settings['rollonce']:
		ratk = [random.choice(ratk)]
		rhit = [random.choice(rhit)]
		rcnt = [random.choice(rcnt)]
		random.seed(settings['seed'])
	
	weapons = list(settings['weaponlist'])
	rc = {}
	for w in weapons: rc[w]=0
	
	for w1 in weapons:
		count = random.choice(rcnt)
		c = 0
		wlist = list(weapons)
		if settings['selfnull']: wlist.remove(w1)
		for w in wlist:
			if not relations.isNeutral(w1,w):
				wlist.remove(w)
				c += 1
			elif rc[w] >= max(rcnt):
				wlist.remove(w)
		while c < count and wlist:
			w2 = random.choice(wlist)
			wlist.remove(w2)
			neg = random.choice([1,-1])
			hit = random.choice(rhit) * neg
			atk = random.choice(ratk) * neg
			relations.setRelation(w1,w2,hit,atk)
			if settings['symmetry'] and w1 != w2:
				relations.setRelation(w2,w1,-hit,-atk)
			c += 1
		rc[w1] = c
	return
	
def tri_rando(relations,settings):
	'''Triangular Randomization'''
	random.seed(settings['seed'])
	rhit = settings['rhit']
	ratk = settings['ratk']
	rcnt = settings['rcnt']
	
	if settings['rollonce']:
		ratk = [random.choice(ratk)];
		rhit = [random.choice(rhit)];
		rcnt = [random.choice(rcnt)];
		random.seed(settings['seed'])
	
	weapons = list(settings['weaponlist'])
	tc = {}
	for w in weapons: tc[w]=0
	
	for w1 in weapons:
		weapons = list(settings['weaponlist'])
		weapons.remove(w1)
		wlist = list(weapons)
		
		count = random.choice(rcnt)
		
		for w in weapons:
			if not relations.isNeutral(w1,w):
				wlist.remove(w)
			elif tc[w] >= max(rcnt):
				wlist.remove(w)
		
		while tc[w1] < count and len(wlist) >= 2:
			w2 = random.choice(wlist)
			wlist.remove(w2)
			w3 = random.choice(wlist)
			wlist.remove(w3)
			neg = random.choice([1,-1])
			hit = random.choice(rhit) * neg
			atk = random.choice(ratk) * neg
			relations.setRelation(w1,w2,hit,atk)
			relations.setRelation(w2,w3,hit,atk)
			relations.setRelation(w3,w1,hit,atk)
			
			if settings['symmetry']:
				relations.setRelation(w2,w1,-hit,-atk)
				relations.setRelation(w3,w2,-hit,-atk)
				relations.setRelation(w1,w3,-hit,-atk)
				tc[w1]+=2
				tc[w2]+=2
				tc[w3]+=2
			else:
				tc[w1]+=1
				tc[w2]+=1
				tc[w3]+=1
	return

def rando_start():
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

if __name__ == '__main__':
	if GUI:
		app = App("GBAFE Weapon Relation Randomizer")
	else:
		rando_start()
		input('Press enter to continue \n')

