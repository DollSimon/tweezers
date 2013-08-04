from IPython.core.display import *

# code from http://williewong.wordpress.com/2012/07/27/ipython-notebook-take-2/
def add(x,y): return x+y
def MDPL(string): display(Math(string))
def comp_str(listofstrings): return reduce(add,listofstrings)

# code from http://williewong.wordpress.com/2012/07/27/ipython-notebook-take-2/
class math_expr(object):
   '''''Math Expression object'''''

   def __init__(self,atomslist, labeldefault = True, highlight = []):
      '''''init takes arg: list of atoms, each atom being a compilable chunck of LaTeX expression'''''
      self.listofatoms = atomslist
      self.labels = labeldefault
      MDPL(comp_str(self.__colouratoms(highlight)))

   def _repr_latex_(self):
      '''''Returns a latex expression of the object. Will be parsed by MathJax'''''
      self.__labelatoms()
      latexstring = comp_str(self.labeledatoms) if self.labels else comp_str(self.listofatoms)
      return "$" + latexstring + "$"

   @property
   def labeled(self):
      '''''Tells you whether labelling is turned on by default'''''
      return self.labels

   @labeled.setter
   def label(self,boolean):
      '''''Sets the default labelling'''''
      self.labels = boolean

   @property
   def latex(self):
      '''''Accesses the LaTeX code snip for the expression'''''
      display(Latex(comp_str(self.listofatoms)))

   def __labelatoms(self):
      '''''Label atoms by adding underbraces'''''
      self.labeledatoms = [ "\underbrace{" + self.listofatoms[i] + "}_{" + str(i) + "}" for i in range(len(self.listofatoms)) ]

   def replace(self,pos,newstr):
      '''''Replaces an atom with another atom'''''
      MDPL(comp_str(self.__colouratoms([pos])))
      newstrings = list(self.listofatoms)
      newstrings[pos] = newstr
      return math_expr(newstrings,self.labels,[pos])

   def merge(self,positions):
      '''''Merges atoms: the input is a list of positions. The new atom is placed at the position of the foremost of the positions'''''
      MDPL(comp_str(self.__colouratoms(positions)))
      newstrings = list(self.listofatoms)
      temp = [ newstrings[i] for i in positions ]
      positions.sort()
      positions.reverse()
      for i in positions: del newstrings[i]
      newstrings.insert(positions[-1],comp_str(temp))
      return math_expr(newstrings,self.labels,[positions[-1]])

   def split(self,pos,newatoms):
      '''''Splits atoms: replaces an atom in place with multiple sub atoms'''''
      MDPL(comp_str(self.__colouratoms([pos])))
      newstrings = list(self.listofatoms)
      del newstrings[pos]
      templen = len(newatoms)
      while len(newatoms) > 0:
         newstrings.insert(pos,newatoms.pop())
      return math_expr(newstrings,self.labels,range(pos,pos+templen))

   def cancel(self,positions):
      '''''Cancels a bunch of terms: input a list of positions'''''
      MDPL(comp_str(self.__colouratoms(positions)))
      positions.sort()
      positions.reverse()
      newstrings = list(self.listofatoms)
      for i in positions: del newstrings[i]
      return math_expr(newstrings,self.labels)

   def move(self,posini,posfin):
      '''''Move atom at posini to posfin, pushing all others back'''''
      MDPL(comp_str(self.__colouratoms([posini])))
      newstrings = list(self.listofatoms)
      temp = newstrings.pop(posini)
      newstrings.insert(posfin if posfin < posini else posfin-1, temp)
      return math_expr(newstrings,self.labels,[posfin if posfin < posini else posfin - 1])

   def __colouratoms(self,positions,labelled=False):
      '''''Returns the list of atoms, but with selected terms coloured'''''
      temp = list(self.listofatoms)
      if labelled:
         self.labelatoms()
         temp = list(self.labeledatoms)
      for i in positions: temp[i] = "\color{red}{"+temp[i]+"}"
      return temp
