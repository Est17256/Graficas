#Luis Esturban 17256
#Graficas por computadora
#SR4
#05/03/2019
import struct
from random import randint as random
from collections import namedtuple
import cProfile
import re
import pstats
import time
tri1T=[]
tri2T=[]

def char(c):
    return struct.pack("=c", c.encode('ascii'))
def word(c):
    return struct.pack("=h", c)
def dword(c):
    return struct.pack("=l", c)
def color(r, g, b):
    return bytes([b, g, r])


V2 = namedtuple('Vertex2', ['x', 'y'])
V3 = namedtuple('Vertex3', ['x', 'y', 'z'])

def sum(v0, v1):
    return V3(v0.x + v1.x, v0.y + v1.y, v0.z + v1.z)

def res(v0, v1):
    return V3(v0.x - v1.x, v0.y - v1.y, v0.z - v1.z)

def mul(v0, k):
    return V3(v0.x * k, v0.y * k, v0.z *k)

def pun(v0, v1):
    return v0.x * v1.x + v0.y * v1.y + v0.z * v1.z

def cru(v0, v1):
    return V3(
        v0.y * v1.z - v0.z * v1.y,
        v0.z * v1.x - v0.x * v1.z,
        v0.x * v1.y - v0.y * v1.x,
      )

def lon(v0):
    return (v0.x**2 + v0.y**2 + v0.z**2)**0.5

def norm(v0):
    l = lon(v0)
    if (l == 0):
        return V3(0, 0, 0)
    return V3(v0.x/l, v0.y/l, v0.z/l)

def color(r, g, b):
    return bytes([b, g, r])

class Obj(object):
    def __init__(self, filename):
        with open(filename) as f:
            self.lines = f.read().splitlines()

        self.vertex = []
        self.tvertex = []
        self.cars = []
        self.read()
    #Funcion para poder leer los valores de obj
    def read(self):
        for line in self.lines:
            if line:
                prefix, value = line.split(' ', 1)

                if prefix == 'v':
                    self.vertex.append(list(map(float, value.split(' '))))
                if prefix == 'vt':
                    self.tvertex.append(list(map(float, value.split(' ')))) 
                elif prefix == 'f':
                    self.cars.append([list(map(int, car.split('//'))) for car in value.split(' ')])
class Bitmap(object):
    #Contiene los valores de iniciacion 
    def glInit(self):
        self.width = 0
        self.height = 0
        self.color = color(0, 0, 0)
        self.col = color(255, 0, 0)
    #Funcion que asigna el tamano de la escena
    def glCreateWindow(self, width, height):
        self.width = width
        self.height = height
        self.framebuffer = []
        self.glClear()
    #Funcion que crea el punto en el espacio indicado
    def point(self, x, y, color):
	    self.framebuffer[y][x] = color
	#Funcion que crea el limite del area de trabajo permitida
    def glViewPort(self, x, y , width, height):
        self.pX = x
        self.pY = y
        self.vW = width
        self.viewH = height
    #indica la pocicion donde se colocara el punto
    def glVertex(self, x, y):
        xF = int((x+1)*(self.vW/2)+self.pX)
        yF = int((y+1)*(self.viewH/2)+self.pY)
        self.point(xF, yF, self.col)
    #Funcion que crea la escena en la cual se va a trabajar
    def glClear(self):
        self.framebuffer = [
            [
                self.color
                    for x in range(self.width)
	        ]
	        for y in range(self.height)
	    ]
    
        self.zbuffer = [
            [-float('inf') for x in range(self.width)]
            for y in range(self.height)
        ]
    #Funcion que le asigna el color al fondo menores o iguales a 1
    def glClearColor(self, r, g, b):
        if(r<=1 and g<=1 and b<=1):
            self.color = color((r*255), (g*255), (b*255))
            glClear()
    #Asigna el color del punto elegido
    def glColor(self, r, g, b):
       self.col = color(r, g, b)
    #Funcion que calcula el pixel en x
    def pixelX(self,a):
    	resX = 2*((a-self.pX)/self.vW)-1
    	return resX
    #Funcion que calcula el pixel en y
    def pixelY(self,b):
    	resY = 2*((b-self.pY)/self.vH)-1
    	return resY
    #Funcion para poder crear lineas que van de -1 a 1
    def glLine(self,x0, y0, x1, y1):
    	xN0 = round((x0+1)*(self.vW/2)+self.pX)
    	xN1 = round((x1+1)*(self.vW/2)+self.pX)
    	yN0 = round((y0+1)*(self.vH/2)+self.pY)
    	yN1 = round((y1+1)*(self.vH/2)+self.pY)
    	i = 0
    	while i <= 1:
    		x = xN0 + (xN1 - xN0) * i
    		y = yN0 + (yN1 - yN0) * i 
    		self.glVertex(self.pixelX(x),self.pixelY(y))
    		i += 0.01
    def flood(self, x, y, col1, col2):
        if (x < 0 or x >= self.width or y < 0 or y >= self.height):
            return
        if (self.framebuffer[x][y] != col1):
            return
        self.point(x, y, col2)

        self.flood(x+1, y, col1, col2)
        self.flood(x-1, y, col1, col2)
        self.flood(x, y+1, col1, col2)
        self.flood(x, y-1, col1, col2)
    def floodFill(self, x, y, colorN):
        colorO = self.framebuffer[x][y]
        self.flood(x, y, colorO, colorN)
    def transform(self, vertex, tra=(0, 0, 0), sca=(1, 1, 1)):
        return V3(
          round((vertex[0] + tra[0]) * sca[0]),
          round((vertex[1] + tra[1]) * sca[1]),
          round((vertex[2] + tra[2]) * sca[2])
        )
    #Funcion de llenado de triangulos
    def triangle(self, a, b, c, color=None):
        if (a.y > b.y):
            a, b = b, a
        if (a.y > c.y):
            a, c = c, a
        if (b.y > c.y):
            b,c = c, b
        dx_ac = c.x - a.x
        dy_ac = c.y - a.y
        if (dy_ac == 0):
            return
        minv_ac = dx_ac/dy_ac
        dx_ab = b.x - a.x
        dy_ab = b.y - a.y
        tri1S=time.time()
        if (dy_ab != 0):
            minv_ab = dx_ab/dy_ab
            for y in range(a.y, b.y + 1):
                xi = round(a.x - minv_ac * (a.y - y))
                xf = round(a.x - minv_ab * (a.y - y))
                if xi > xf:
                    xi, xf = xf, xi
                for x in range(xi, xf + 1):
                    self.point(x, y, color)
        tri1F=time.time()
        tri1T.append(tri1F-tri1S)
        dx_bc = c.x - b.x
        dy_bc = c.y - b.y
        tri2S=time.time()
        if (dy_bc):
            minv_bc = dx_bc/dy_bc
            for y in range(b.y,c.y + 1):
                xi = round(a.x - minv_ac * (a.y - y))
                xf = round(b.x - minv_bc * (b.y - y))
                if xi > xf:
                    xi, xf = xf, xi
                for x in range(xi, xf + 1):
                    self.point(x, y, color)
        tri2F=time.time()
        tri2T.append(tri2F-tri2S)
    def sumalista(self,listaNumeros):
        laSuma = 0
        for i in listaNumeros:
            laSuma = laSuma + i
        return laSuma
	#Funcion donde se crea la imagen 
    def glFinish(self, filename):
        f = open(filename, 'wb')
        f.write(char('B'))
        f.write(char('M'))
        f.write(dword(14 + 40 + self.width * self.height * 3))
        f.write(dword(0))
        f.write(dword(14 + 40))
        f.write(dword(40))
        f.write(dword(self.width))
        f.write(dword(self.height))
        f.write(word(1))
        f.write(word(24))
        f.write(dword(0))
        f.write(dword(self.width * self.height * 3))
        f.write(dword(0))
        f.write(dword(0))
        f.write(dword(0))
        f.write(dword(0))
        for x in range(self.height):
            for y in range(self.width):
                f.write(self.framebuffer[x][y])
        f.close() 
     #Funcion para cargar el archivo obj y llenarlo 
    def load2(self, filename, tra, sca):
        mod = Obj(filename)

        luz = V3(0, 0, 1)

        for car in mod.cars:
            vcount = len(car)
            if vcount == 3:
                f1 = car[0][0] - 1
                f2 = car[1][0] - 1
                f3 = car[2][0] - 1

                a = V3(*mod.vertex[f1])
                b = V3(*mod.vertex[f2])
                c = V3(*mod.vertex[f3])
                
                nor = norm(cru(res(b, a), res(c, a)))
                inte = pun(nor, luz)
                gray = round(255 * inte)
                
                a = self.transform(mod.vertex[f1], tra, sca)
                b = self.transform(mod.vertex[f2], tra, sca)
                c = self.transform(mod.vertex[f3], tra, sca)
                if gray < 0:
                    continue
                self.triangle(a, b, c, color(gray, gray, gray))
            else:
                f1 = car[0][0] - 1
                f2 = car[1][0] - 1
                f3 = car[2][0] - 1
                f4 = car[3][0] - 1
                ver =  [
                    self.transform(mod.vertex[f1], tra, sca),
                    self.transform(mod.vertex[f2], tra, sca),
                    self.transform(mod.vertex[f3], tra, sca),
                    self.transform(mod.vertex[f4], tra, sca)
                ]
                a, b, c, d = ver
                nor = norm(cru(res(a, b), res(c, d)))
                inte = pun(nor, luz)
                gray = round(255 * inte)
                if gray < 0:
                    continue
                self.triangle(a, b, c, color(gray, gray, gray))
                self.triangle(a, c, d, color(gray, gray, gray))

r = Bitmap()
r.glInit()
r.glCreateWindow(800, 600)
r.load2('mono.obj', (4, 4, 0), (100, 100, 100))
print('pendiente 1 :',r.sumalista(tri1T))
print('pendiente 2 :',r.sumalista(tri2T))
r.glFinish('SR.bmp')

