'''
This tool is meant to be used to produce animated particle trails.
It can be used on existing animations or it can be used to generate the animation 
of the agent along a chosen curve
'''

__author__ = 'Amalia Filip'
__version__= '1.0'


for name in dir():
    if not name.startswith('_'):
        try:
            del globals()[name]
        except:
            pass


import maya.cmds as cmds
from maya.OpenMaya import MVector
import math as math
import random as rand
from functools import partial

def okButtonHandler(userMenu, *pArgs):
	'''pressing the OK button executes the code and closes the UI window'''
	print("Start action")
	animateAgent(userMenu)
	createParticleTrail(userMenu)
	cmds.deleteUI("particleTrailWindow")

def applyButtonHandler(userMenu, *pArgs):
	'''pressing the Apply button executes the code, but leaves the UI window open'''
	print("Start action")
	animateAgent(userMenu)
	createParticleTrail(userMenu)

def cancelButtonHandler(*pArgs):
	'''pressing the Cancel button closes the UI window'''
	print("Action is cancelled")
	cmds.deleteUI("particleTrailWindow")
	

class Menu:
	'''data structure created to store user input'''
	def __init__(self):
		print("Initialised")
	def createUI (self):
		self.windowID = "particleTrailWindow"
		windowID = self.windowID
		
		if cmds.window(windowID, exists=True):
			cmds.deleteUI(windowID)

		# make a new window 
		winControl = cmds.window(windowID, title="Particle Trail", widthHeight=(400, 650), s = False )
		
		cmds.columnLayout( adjustableColumn = True, co = ['both', 5], rs = 5, h = 5 )
		
		image_path = 'C:\Users\Ama\Desktop\uniWork\python\S2_pythonProject\particleTrail_UI.png'
		
		cmds.image( image=image_path, h = 220 )
		
		cmds.text(label = 'Agent Name', align = 'left')
		self.agentName = cmds.textField(w = 350)	
		cmds.text(label='Number of Animated Frames', align = 'left')
		self.numOfFrames = cmds.intField(minValue = 1, maxValue = 1000, step = 1, value = 100)
		self.ratioOfObjectToParticle = cmds.floatSliderGrp(label = 'Ratio of Object to Particles', minValue = 20.0, maxValue = 150.0, value = 70.0, field = True)
		self.trailDensity = cmds.intSliderGrp(label='Trail Density', minValue=1, maxValue=20, value=3, field=True)
		self.trailLength = cmds.intSliderGrp(label='Trail Length', minValue=1, maxValue=50, value=7, field=True)
		
		#cmds.setParent('..')
		
		
		cmds.frameLayout(label = "Animate Along Curve", cll = True, cl = False, mh = 10, mw = 50 )
		cmds.text( label='Curve Name', align = 'left' )
		self.curveName = cmds.textField(w = 338, en = True)
		
		cmds.setParent('..')
		cmds.rowLayout( numberOfColumns=3, columnWidth3=(170, 170, 170))
		
		cmds.button(label = "OK", command = partial(okButtonHandler, self))
		cmds.button(label = "Apply", command = partial(applyButtonHandler, self))
		cmds.button(label = "Cancel", command = cancelButtonHandler)

		cmds.showWindow( winControl )

#source code from Dr. Xiaosong Yang starts here
def findSizeofParticle(transNodeName, ratioOfObjectToParticles):
	''' find a good size of particle to fill the surface of the object
	transNodeName: the transform name of the mesh
	ratioOfObjectToParticles: user input for adjusting the size of the particles (the higher the ratio, the smaller the particles)
	
	return		: size for particles, it can be tuned by user from user interface
	'''
	bbox = cmds.exactWorldBoundingBox(transNodeName)
	diagDist = math.sqrt((bbox[3]-bbox[0])*(bbox[3]-bbox[0]) + (bbox[4]-bbox[1])*(bbox[4]-bbox[1]) + (bbox[5]-bbox[2])*(bbox[5]-bbox[2]))
	
	return diagDist/ratioOfObjectToParticles
	
def getCoordinatesOfAllVertices(transNodeName, numVertices):
	'''get the coordinates of all the vertices on the mesh

	objectName	: the name of the first 3D object
	numVertices	: the number of vertices on the first mesh
	
	return		: the array of all the vertices coordinates
	'''
	coordinatesArray = []
	for i in range(numVertices):
		vertexPosition = cmds.xform(transNodeName + ".vtx[" + str(i) + "]", q=True, t=True, worldSpace=True)
		coordinatesArray.append(vertexPosition)

	return coordinatesArray
#source code from Dr. Xiaosong Yang ends here
	
class ReturnValueOfFillShape():
	'''data structure for storing return data from the 'fillShapeWithParticles' function'''
	def __init__(self, particleGrp, numberOfParticles, particleTest):
		self.particleGrp = particleGrp
		self.numberOfParticles = numberOfParticles
		self.particleTest = particleTest

def fillShapeWithParticles(transNodeName, coordArray, numVertices, ratioOfParticles):
	'''function 'fillShapeWithParticles' from Dr. Xiaosong Yang, ammended to pick random vertices 
	to place the particles on
	
	return		: the particleGrp, the numberOfParticles created and a list 'particleTest' which 
				  stores on which vertex the particle was created (1 for particle created, 0 for empty vertex)
	'''

	# determine the size of particle
	size = findSizeofParticle(transNodeName, ratioOfParticles)
	# create sphere particles
	tempSphere = cmds.sphere(radius = size)
	
	particleTest = []
	numberOfParticles = 0 
	particleGrp = []

	# place particles at vertices position
	for i in range(numVertices):
		
		#for every vertex it chooses randomly whether to place a particle there or not
		vertFlag = rand.randint(0, 1)
		if vertFlag == 0:
			particleTest.append(0)
			continue

		newParticles = cmds.instance(tempSphere[0])
		cmds.move(coordArray[i][0], coordArray[i][1], coordArray[i][2], newParticles)

		particleGrp.append(newParticles[0])
		numberOfParticles += 1
		particleTest.append(1)
		
	particleGrpName = cmds.group(particleGrp, n="particlesGrp")

	cmds.delete(tempSphere[0])
	
	return ReturnValueOfFillShape(particleGrp, numberOfParticles, particleTest)

#source from Constantinos Glynos starts here
def getNormal(face_):
	'''function that returns the normal vector of a face'''

	normal = cmds.polyInfo(face_, faceNormals = True)
	normal = normal[0].split(' ')
	last_element = len(normal)-1
	normal[last_element] = normal[last_element].replace("\n", "")

	normal = MVector( float(normal[last_element-2]),\
                      float(normal[last_element-1]),\
                      float(normal[last_element]) )
	
	return normal
#source from Constantinos Glynos ends here

def animateAgent(userMenu, *pArgs):
	'''animate the desired object along a chosen curve
	userMenu	:input from the UI	-agent_name	:name of the object that will be animated
						-curvePath_name	:name of the curve along which the object will be animated
						-animatedFrames	:the number of frames
						-particleDelay	:the delay between the end of the agent animation and the end of the particle animation
										the user input for trailLength (see 'createParticleTrail' for explanation)
	''' 
	#try/except statement used in case the user decides not to animate along a curve, but use an existing agent animation
	try:
		agent_name = cmds.textField(userMenu.agentName, query = True, text = True)
		curvePath_name = cmds.textField(userMenu.curveName, query = True, text = True)
		animatedFrames = cmds.intField(userMenu.numOfFrames, query = True, v = True)
		particleDelay = cmds.intSliderGrp(userMenu.trailLength, query = True, value = True)
			 
		#the agent will have a keyframe set for each curvePath span
		#therefore the number of animation frames for the agent is the number of total animation frames minus the particleDelay
		curvePath_spans = animatedFrames - particleDelay
		
		#source from Constantinos Glynos starts here
		cmds.rebuildCurve(curvePath_name,rpo=True,rt=0,end=True,kr=False,kt=False,s=curvePath_spans,d=1)
		
		extrudedPath = cmds.extrude(curvePath_name,n="extrudedPath",ch=True,rn=False,po=1,et=0,upn=0,d=(0.5,0,1),length=1,rotation=0,dl=3)
		cmds.delete(ch = True)
		
		for i in range(curvePath_spans):
				
			currentCV = MVector(*cmds.pointPosition(curvePath_name+".cv["+str(i)+"]"))
			nextCV = MVector(*cmds.pointPosition(curvePath_name+".cv["+str(i+1)+"]"))
				
			front = nextCV - currentCV
			front.normalize()
			
			face = str(extrudedPath[0]+".f["+str(i)+"]")
			cmds.select(face)
			normal = getNormal(face)
				
			side = front ^ normal 
				
			phi = cmds.angleBetween(euler=True, v1=(0.0,0.0,1.0), v2=(side.x,side.y,side.z))
			theta = cmds.angleBetween(euler=True, v1=(1.0,0.0,0.0), v2=(front.x,front.y,front.z))
			psi = cmds.angleBetween(euler=True, v1=(0.0,1.0,0.0), v2=(normal.x,normal.y,normal.z))
				
			position = (currentCV + nextCV)*0.5
			#source from Constantinos Glynos starts here
				
			cmds.setKeyframe(agent_name, time = i, attribute = 'translateX', value = position.x)
			cmds.setKeyframe(agent_name, time = i, attribute = 'translateY', value = position.y)
			cmds.setKeyframe(agent_name, time = i, attribute = 'translateZ', value = position.z)
			cmds.setKeyframe(agent_name, time = i, attribute = 'rotateX', value = phi[0])
			cmds.setKeyframe(agent_name, time = i, attribute = 'rotateY', value = theta[1])
			cmds.setKeyframe(agent_name, time = i, attribute = 'rotateZ', value = psi[2])
		
		cmds.delete(extrudedPath[0])
	except:
		print("No Curve Name input")

		
def createParticleTrail(userMenu, *pArgs):
	'''this function takes input from the user (UI) and creates the particle behind the object in accordance with 
	the existing animation of the model or the one created by this script (animating movement along a curve)

	userMenu	:input from the UI	-agent_name		:name of the object that will be animated
									-animatedFrames		:the number of frames
									-ratioOfObjectToParticle:the size of the particles 
									-trailLength		:the maximum number of frames behind the agent that the animation will be (particleDelay)
									-trailDensity		:how many particles will be generated
	''' 
	agent_name = cmds.textField(userMenu.agentName, query = True, text = True)
	animatedFrames = cmds.intField(userMenu.numOfFrames, query = True, v = True)
	ratioOfObjectToParticle = cmds.floatSliderGrp(userMenu.ratioOfObjectToParticle, query = True, v = True)
	trailLength = cmds.intSliderGrp(userMenu.trailLength, query = True, v = True)
	trailDensity = cmds.intSliderGrp(userMenu.trailDensity, query = True, v = True)

	#select the agent mesh
	cmds.select(agent_name, hierarchy=True)
	selectedObjects = cmds.ls(selection=True, type="mesh")
	
	numVertices = cmds.polyEvaluate(selectedObjects[0], vertex=True)
	
	transNodeName = cmds.listRelatives(selectedObjects[0], parent=True)

	coordArray = getCoordinatesOfAllVertices(transNodeName[0], numVertices)

	particleTrail = []
	numOfParticles = []
	particleTesting = []
		
	#the higher the trailDensity, the more particles are created
	for k in range(trailDensity):	
		particles = fillShapeWithParticles(transNodeName[0], coordArray, numVertices, ratioOfObjectToParticle)
		particleTrail.append(particles.particleGrp)
		numOfParticles.append(particles.numberOfParticles)
		particleTesting.append(particles.particleTest)
	
	for i in range(animatedFrames):
		#sets the frame to i, in order to get the coordinates of the object (coordArray) for every frame of the animation
		cmds.currentTime(i, e = 0)
		coordArray = getCoordinatesOfAllVertices(transNodeName[0], numVertices)
		
		for k in range(trailDensity):
			index = -1
			for j in range(numVertices):
				
				#tests if there is a particle for that vertex
				#if there isn't, it skips it
				if particleTesting[k][j] == 0:
					continue

				#this index goes through the number of particles, not the number of vertices 
				index += 1
						
				posX=coordArray[j][0]
				posY=coordArray[j][1]
				posZ=coordArray[j][2]

				#unless it's the first frame, randomise the frame at which the keyframe is set for every particle	
				if i==0:
					frame = i
				else:
					frame = i + rand.randint(0, trailLength)
				
				#if the particle exists for the vertex j and the index is within the number of particles, set keyframes
				if index<numOfParticles[k]:
					cmds.setKeyframe(particleTrail[k][index], time = frame, attribute = 'translateX', value = posX)
					cmds.setKeyframe(particleTrail[k][index], time = frame, attribute = 'translateY', value = posY)
					cmds.setKeyframe(particleTrail[k][index], time = frame, attribute = 'translateZ', value = posZ)

#main program starts here
if __name__ == "__main__":
	userMenu = Menu()
	userMenu.createUI()
