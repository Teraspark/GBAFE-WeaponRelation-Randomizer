import random, glob
from itertools import product
from pathlib import Path
import tkinter as tk
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfilename
from tkinter import messagebox
from string import ascii_letters as Letterlist
from string import digits as Numberlist

GUI = True
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

class Window:
	'''
	UI for the randomizer
	self.master is the tk root
	modes is a tuple of each randomizer modes' name and fuction
	'''
	
	def __init__(self,title="Python GUI"):
		self.modes = (
		('Triangle',triRando),
		('Pair',pairRando),
		('Circular',circleRando),
		('Chaos',chaosRando)
		)
		
		self.master = tk.Tk()
		self.master.title(title)
		self.master.geometry('500x420')
		self.buildUI()
		self.master.mainloop()
		
	def buildUI(self):
		self.mainframe = tk.Frame(self.master)
		self.mainname = tk.Label(self.master,text='Weapon Relation Randomizer')
		self.mainname.pack(side=tk.TOP)
		# self.mainname.grid(row=0,padx=5,columnspan=3,sticky=tk.E+tk.W)
		
		self.topbox = tk.Frame(self.mainframe)
		self.topbox.grid(row=1,column=0,rowspan=2,columnspan=3)
		
		#setup seed ui
		self.seed = tk.StringVar()
		self.seedname = tk.Label(self.topbox,text='Seed:')
		self.seedname.grid(row=0,column=1,sticky=tk.E,padx=2)
		self.seedentry = tk.Entry(self.topbox,textvariable=self.seed)
		self.seedentry.grid(row=0,column=2,columnspan=2,sticky=tk.E+tk.W)
		self.seedchange = tk.Button(self.topbox,text='New Seed',command=self.newseed)
		self.seedchange.grid(row=0,column=4,sticky=tk.W,padx=2,pady=2)
		#setup output file selection ui
		self.outfile = tk.StringVar()
		self.outname = tk.Label(self.topbox,text='File:')
		self.outname.grid(row=1,column=1,sticky=tk.E,padx=2)
		self.outentry = tk.Entry(self.topbox,textvariable=self.outfile)
		self.outentry.grid(row=1,column=2,columnspan=2,sticky=tk.E+tk.W)
		self.outfind = tk.Button(self.topbox,text=' Browse...',command=self.loadfile)
		self.outfind.grid(row=1,column=4,sticky=tk.W,padx=2,pady=3)
			
		self.statbox = tk.Frame(self.mainframe,highlightbackground='black',highlightthickness=1)
		self.poolbox = tk.Frame(self.mainframe)
		self.modebox = tk.Frame(self.mainframe)
		self.statbox.grid(row=3,column=0,rowspan=2,columnspan=3,ipady=5,sticky=(tk.E+tk.W))
		self.modebox.grid(row=5,column=0,rowspan=2,columnspan=3,ipadx=5)
		self.poolbox.grid(row=3,column=3,rowspan=4,columnspan=2,pady=5,padx=5)
		
		#List of weapon types
		self.wpoolname = tk.Label(self.poolbox,text='Weapons Pool')
		self.wpoolname.grid(row=0,column=0,columnspan=3)
		self.wpool = tk.Listbox(self.poolbox)
		self.wpool.grid(row=1,rowspan=3,columnspan=3,sticky=tk.E+tk.W,pady=5)
		self.poolpop = tk.Button(self.poolbox,text='Remove',command=self.wremove)
		self.poolpush = tk.Button(self.poolbox,text='Add',command=self.winsert)
		self.input = tk.Entry(self.poolbox)
		self.poolpop.grid(row=4,column=0,columnspan=3,sticky=tk.E+tk.W)
		self.input.grid(row=5,column=0,columnspan=2)
		self.poolpush.grid(row=5,column=2)
		#add default weapon types to pool
		for w in WeaponList: self.wpool.insert(tk.END,w)
		
		#set range for stat variation
		self.minhit = tk.IntVar()
		self.maxhit = tk.IntVar()
		self.minatk = tk.IntVar()
		self.maxatk = tk.IntVar()
		self.singleroll = tk.IntVar()
		self.statword = tk.Label(self.statbox,text='Weapon Advantage')
		self.maxword = tk.Label(self.statbox,text='Max')
		self.minword = tk.Label(self.statbox,text='Min')
		self.hitword = tk.Label(self.statbox,text='Accuracy')
		self.atkword = tk.Label(self.statbox,text='Damage')
		self.statword.grid(row=0,columnspan=3)
		self.minword.grid(row=1,column=1)
		self.maxword.grid(row=1,column=2)
		self.hitword.grid(row=2,column=0)
		self.atkword.grid(row=3,column=0)
		self.minhitdata = tk.Spinbox(self.statbox,from_=0,to=100,increment=5,textvariable=self.minhit,width=10,command=self.adjustmin)
		self.maxhitdata = tk.Spinbox(self.statbox,from_=5,to=100,increment=5,textvariable=self.maxhit,width=10,command=self.adjustmax)
		self.minhitdata.grid(row=2,column=1)
		self.maxhitdata.grid(row=2,column=2)
		self.minatkdata = tk.Spinbox(self.statbox,from_=0,to=15,textvariable=self.minatk,width=10,command=self.adjustmin)
		self.maxatkdata = tk.Spinbox(self.statbox,from_=0,to=15,textvariable=self.maxatk,width=10,command=self.adjustmax)
		self.minatkdata.grid(row=3,column=1)
		self.maxatkdata.grid(row=3,column=2)
		self.rollcheck = tk.Checkbutton(self.statbox,text='Roll Once',variable=self.singleroll)
		self.rollcheck.grid(row=4,columnspan=3)
		
		self.minhit.set(15)
		self.maxhit.set(15)
		self.minatk.set(1)
		self.maxatk.set(1)
		
		#randomizer mode selection
		self.randomode = tk.IntVar()
		self.modetitle = tk.Label(self.modebox,text='Mode')
		self.modetitle.grid(row=0)
		self.randoptions = []
		for (z,m) in enumerate(self.modes):
			mode = tk.Radiobutton(self.modebox,text=m[0],value=z,variable=self.randomode)
			self.randoptions.append(mode)
			mode.grid(row=z+1,sticky=tk.W)
		
		#button to start randomization
		self.run = tk.Button(self.mainframe,text='Randomize',command=self.randomize)
		self.run.grid(row=7,column=0,columnspan=5,pady=5,sticky=tk.E+tk.W)
		
		self.mainframe.pack()
		
	def adjustmin(self):
		'''ensure the min values never rise above the max values'''
		if self.minhit.get() > self.maxhit.get():
			self.maxhit.set(self.minhit.get())
		if self.minatk.get() > self.maxatk.get():
			self.maxatk.set(self.minatk.get())
	def adjustmax(self):
		'''ensure the max values never fall below the min values'''
		if self.maxhit.get() < self.minhit.get():
			self.minhit.set(self.maxhit.get())
		if self.maxatk.get() < self.minatk.get():
			self.minatk.set(self.maxatk.get())
		
	def wremove(self):
		'''
		remove selected weapon type
		'''
		z = self.wpool.curselection()
		if z: self.wpool.delete(z)
		
	def winsert(self):
		'''
		add weapon type to pool
		'''
		z = self.input.get()
		if z: self.wpool.insert(tk.END,z)
		
	def newseed(self):
		random.seed()
		nseed = ''.join(random.choice(Numberlist+Letterlist) for _ in range(10))
		self.seed.set(nseed)
		
	def loadfile(self):
		file = askForFileOut((('Event File(EA)','*.event'),))
		
		if file != Path():
			if not file.suffix: file = file.with_suffix('.event')
			self.outfile.set(str(file))
		
	def randomize(self):
		'''start randomization for gui'''
		# modes = (triRando,chaosRando)
		weapons = self.wpool.get(0,tk.END)
		wrlist=[]
		
		(min,max) = (self.minatk.get(),self.maxatk.get())
		ratk = range(min,max+1)
		(min,max) = (self.minhit.get(),self.maxhit.get())
		rhit = range(min,max+1,5)
		
		
		#set randomizer seed
		if not self.seed.get(): self.newseed()
		random.seed(self.seed.get())
		
		if self.singleroll.get():
			ratk = random.choices(ratk)
			rhit = random.choices(rhit)
			random.seed(self.seed.get())
			
		m = self.randomode.get()
		if m in range(len(self.modes)):
			wrlist = self.modes[m][1](list(weapons),rhit,ratk)
			# print('WeaponRelations:')
			# for wr in wrlist:
				# print(wr.output())
			# print('WeaponRelationEnd')
			self.writefile(wrlist,weapons,m)
			
			prompt = messagebox.showinfo(title='Randomizing Complete!',message='Randomzing Complete!')
		
	def writefile(self,relations,weapons,mode):
		if not (self.outfile.get()):
			self.loadfile()
		if (self.outfile.get()):
			output = '/* '
			output += 'Weapon Relations Randomizer\n\n'
			output += 'Seed: ' + self.seed.get() + '\n'
			output += 'Mode: ' + self.modes[mode][0] + '\n'
			output += 'Settings:\n'
			output += '\tAccuracy\tMin: ' + str(self.minhit.get())+ '\tMax: ' + str(self.maxhit.get()) + '\n'
			output += '\tDamage\t\tMin: ' + str(self.minatk.get()) + '\tMax: ' + str(self.maxatk.get())+'\n'
			output += '\tSingleRoll: ' + str(bool(self.singleroll.get())) + '\n'
			output += '*/\n\n'
			
			output += '#include "'+defFile+'"\n\n'
			output += 'WeaponRelationships:\n'
			for w in weapons:
				output += '//' +w + ' Relations\n'
				for r in relations:
					if r.isAttacker(w): output+= r.output()+'\n'
				output+='\n'
			output += 'WeaponRelationEnd\n'
			output += '\n// **Any Relation that is not shown here is neutral**\n'
			Path(self.outfile.get()).write_text(output)
			genDefs(Path(self.outfile.get()))
	
class Relation:
	'''
	Set up the relationship for when the
	first weapon type attacks the second
	
	damage = damage modifier
	hit = accuracy modifier
	
	wt1 = first weapon type
	wt2 = second weapon type
	'''
	def __init__(self,w1,w2,hit=0,damage=0):
		self.wt1 = w1
		self.wt2 = w2
		return
	
	def setRelation(self,hit=0,damage=0):
		self.damage = damage
		self.hit = hit
		return
	def isAttacker(self,type):
		'''check if first weapon type matches given value'''
		return self.wt1 == type
	def output(self):
		if self.damage or self.hit:
			return ('WeaponRelation('+self.wt1+','
			+self.wt2+','+str(self.hit)+','
			+str(self.damage) + ')')
		else:
			return ('//'+self.wt1+' vs '+self.wt2+' is a neutral matchup')

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
		app = Window("GBAFE Weapon Relation Randomizer")
	else:
		randoStart()
		input('Press enter to continue \n')
	