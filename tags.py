'''List of stuff to add later on
check if i need to implement support for
-	input/form tags
-	all the canvas stuff
'''

BR = '<br>' #line break

class Tag:
	'''attempt to create a system for html tags
	name = tagname
	info = tag attributes
	space = indent
	'''
	
	name = ''
	space = 0
	
	def __init__(self,tagname):
		self.name = tagname
		self.content = []
		self.info = {}
	
	def indent(self):
		return '  '*self.space
	
	def __str__(self):
		text = self.indent() + '<' + self.name
		for a in self.info:
			text += ' ' + a + '="' + str(self.info[a]) +'"'
		text += '>'
		
		if all(type(c) == str for c in self.content):
			text += ' '.join(self.content)
			text += '</'+self.name+'>\n'
		else:
			for c in self.content:
				text += '\n'+ str(c) +'\n'
			text += self.indent() + '</'+self.name+'>\n'
		
		return text
	
	def set_tag_attr(self,attr,val):
		self.info[attr] = val
	
	def get_tag_attr(self,attr):
		if attr in self.info:
			return self.info[attr]
		else:
			return None
	def add_content(self,stuff):
		'''content added is expected to be str or Tag'''
		self.content.append(stuff)
		if type(stuff) == Tag:
			stuff.space = self.space + 1

class Comment(Tag):
	def __str__(self):
		return '<!--' + str(self.content) + '-->'

class Style(Tag):
	'''made to represent the <style> html tag'''
	def __init__(self):
		self.name = 'style'
		self.info = {}
		
	def __str__(self):
		text = self.indent() + '<' + self.name + '>'
		for a in self.info:
			text += '\n'+self.indent()+a+' {'
			for c in self.info[a]:
				text += '\n'+c+': '+self.info[a][c]+';'
			text += '\n'+self.indent()+'}\n'
		text += self.indent() + '</'+self.name+'>\n'
		return text
		
	def add_class(self,sclass):
		'''add class to <style>'''
		self.info['.'+sclass] = {}
	def edit_class(self,sclass,cssp,val):
		'''edit class in <style>'''
		self.info['.'+sclass][cssp] = val
	def add_tag(self,stags):
		'''add style for given tags'''
		self.info[stags] = {}
	def edit_tag(self,stags,cssp,val):
		'''edit style for tags'''
		self.info[stags][cssp] = val
		
	

class HTML(Tag):
	'''create a new html page
	generates <html>, <head>, and <body> html tags'''
	
	def __init__(self):
		self.name = 'html'
		self.content = []
		self.head = Tag('head')
		self.body = Tag('body')
		self.add_content(self.head)
		self.add_content(self.body)
		self.info = {}
	
	def __str__(self):
		text = '<!DOCTYPE html>\n<html>'
		for c in self.content:
			text += '\n'+str(c)
		text += '</html>\n\n'
		return text
