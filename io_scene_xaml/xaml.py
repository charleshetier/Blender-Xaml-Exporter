import os
from math import degrees
from math import radians
from math import cos
from math import sin
from mathutils import *

class StreamWriter:
    "A simple xaml stream writer"
    content = ""
    tags = []
    isCurrentNodeOpen = False
    
    # Writes the file
    def commit(self, filePath):
        File = open(filePath, "w")
        File.write(self.content)
        File.close()
        
    # Transforms a vector into xaml format
    def formatVector(self, vector):
        return "%f,%f,%f" % (vector.x, vector.y, vector.z)
    
    # Transforms a vector into xaml format
    def formatPoint(self, point):
        #print(type(point))
        #print(type(point[0]))
        #print(point[0])
        return "%f,%f" % (point[0], point[1])
    
    # Transforms an euler object into xaml format
    def formatEuler(self, euler):
        return "%f,%f,%f" % (degrees(euler.x), degrees(euler.y), degrees(euler.z))
    
    # Transforms a quaternion object into xaml format
    def formatQuaternion(self, quaternion):
        return "%f,%f,%f,%f" % (degrees(quaternion.x), degrees(quaternion.y), degrees(quaternion.z), degrees(quaternion.w))

    # Formats a list
    def formatList(self, list):
        return ",".join([str(item) for item in list])
    
    # Formats a color
    def formatColor(self, color):
        return "#%.2x%.2x%.2x" % (color.r*255, color.g*255, color.b*255)
    
    # Opens a xaml tag
    def openTag(self, name):
        if self.isCurrentNodeOpen:
            self.content += ">\n"
        self.content += "%s<%s" % ("\t"*len(self.tags), name)
        self.isCurrentNodeOpen = True
        self.tags.append(name)
    
    # Adds a new line for the next property
    def newLine(self):
        if self.isCurrentNodeOpen:
            self.content += "\n%s" %("\t"*len(self.tags))
            
    # Adds a property to the current xaml tag
    def addProperty(self, key, value):
        self.content += " %s=\"%s\"" % (key, value)
    
    # Adds a vector list property
    def addVectorListProperty(self, key, vectors):
        formatVectors = " ".join([self.formatVector(vector) for vector in vectors])
        self.addProperty(key, formatVectors)
        
    # Adds a vector list property
    def addPointListProperty(self, key, points):
        #print(points[0])
        #print(points[0][0])
        formatPoints = " ".join([self.formatPoint(point) for point in points])
        self.addProperty(key, formatPoints)
    
    # Adds a vector property to the current xaml tag
    def addVectorProperty(self, key, vector):
        self.addProperty(key, self.formatVector(vector))
    
    # Adds an euler property to the current xaml tag
    def addEulerProperty(self, key, euler):
        self.addProperty(key, self.formatEuler(euler))
        
    # Adds an euler direction property to the current xaml tag
    def addEulerDirectionProperty(self, key, euler):
        self.addVectorProperty(key, euler.to_matrix()*Vector((0,0,-1)))
    
    # Adds a quaternion property to the current xaml tag
    def addQuaternionProperty(self, key, quaternion):
        self.addProperty(key, self.formatQuaternion(quaternion))
    
    # Adds a color property
    def addColorProperty(self, key, color):
        self.addProperty(key, self.formatColor(color))
    
    # Adds a list of lists property
    def addListListProperty(self, key, lists):
        formatLists = " ".join([self.formatList(list) for list in lists])
        self.addProperty(key, formatLists)
                         
    # Close the current xaml tag
    def closeTag(self):
        nodeToClose = self.tags.pop()
        if self.isCurrentNodeOpen:
            self.content += "/>\n" % ()
        else:
            self.content += "%s</%s>\n" % ("\t"*len(self.tags), nodeToClose)
        self.isCurrentNodeOpen = False
        return nodeToClose
    
    # Close until the xaml tag is reached
    def closeTagName(self, name):
        while (name in self.tags):
            if self.closeTag() == name:
                break
    
    # Close all openned tags
    def closeAllTags(self):
        while len(self.tags) > 0:
            self.closeTag()
