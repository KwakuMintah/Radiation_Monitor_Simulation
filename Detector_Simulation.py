#Putting the source and shield code into one Python file
import numpy as np
import decimal
import matplotlib.pyplot as plt
import scipy as sci
from decimal import Decimal as dec
#All units are SI
#Shielding function adapted from the tutorial on Medium by Vipran Vasan

#This is a dictionary of the densities and mu values for different shielding materials
materials = {
    "Lead": {"density": 11.35, "mu": 0.5},
    "Aluminium" : {"density": 2.7, "mu": 0.136},
    "Steel": {"density": 7.85, "mu": 0.15},
    "Concrete": {"density": 2.4, "mu": 0.03},
    "Tungsten": {"density": 19.254, "mu": 0.5} #I'm not sure where Vasan
    #got their values for mu from so I have given tungsten the same value as 
    #lead until I find it
}

#This is a dictionary of the energies for different sources measured in MeV
sources = {
    "Tc-99m": {"energy": 0.140},
    "Cs-137": {"energy": 0.662}
}

results = {material: 0 for material in materials.keys()}

#This is the class for Radioactive Source, written primarily by Joshua Hanrahan
class RadioactiveObject:

    _shape_aliases = {
        "puck": "puck",
        "pill": "puck",
        "cylinder": "puck",

        "block": "block",
        "cuboid": "block",
        "box": "block",
        "brick": "block"
    }

    def __init__(self, shape, source, **kwargs):
        shape = shape.strip().lower()

        if shape not in self._shape_aliases:
            raise ValueError(f"Unknown shape '{shape}'")

        self.shape = self._shape_aliases[shape]#allows different inputs, for example josh says "puck", kwaku says "pill"
        self.params = kwargs
        #kwargs makes it so that arguments are sorted by keyword rather than index i.e examplePuck = RadiativeObject("pill", depth=5, radius=1) or examplePuck = RadiativeObject("pill", radius=1, depth=5) both work
        self.no = self.params.get("num_particles")
        self.source = sources[source]
        self.energy = self.source["energy"]
        self.loc = self.params.get("location")
        self.x = self.loc[0]
        self.y = self.loc[1]

    def volume(self):
        if self.shape == "puck":
            self.r = self.params.get("radius")
            self.h = self.params.get("height")
            if self.r is None or self.h is None:
                raise ValueError("Puck requires 'radius' and 'depth'")
            return np.pi * self.r**2 * self.h

        elif self.shape == "block":
            self.l = self.params.get("length")
            self.w = self.params.get("width")
            self.h = self.params.get("height")
            if self.l is None or self.w is None or self.h is None:
                raise ValueError("Block requires 'length', 'width', and 'depth'")
            return self.l * self.w * self.h

        else:
            raise ValueError(f"Unknown shape '{self.shape}'")

#This is a class for defining the shield, adapted by Kwaku from the source class
class ShieldingObject:
    def __init__(self,mat,**kwargs):
        self.mat = materials[mat]
        self.dens = self.mat["density"]
        self.mu = self.mat["mu"]
        if mat is None:
            mat = materials["Lead"]
        self.params = kwargs
        self.no = self.params.get("num_particles")
        self.loc = self.params.get("location")
        self.x = self.loc[0]
        self.y = self.loc[1]
    #Replicating Josh's code for defining the volume of the shield. The object will always be a block in this case
    def volume(self):
        self.l = self.params.get("length")
        self.w = self.params.get("width")
        self.h = self.params.get("height")
        #This is to define the space the particle must be within to interact
        self.x_one = self.x - (self.w/2)
        self.x_two = self.x + (self.w/2)
        self.y_one = self.y - (self.l/2)
        self.y_two = self.y + (self.l/2)
        if self.l is None or self.w is None or self.h is None:
            raise ValueError("Block requires 'length', 'width', and 'depth'")
        return self.l * self.w * self.h
    
def particle_gen(shield,source):
    #This code assumes the source and shield are in a straight line across the y axis
    dist = abs(source.y - shield.y)
    #This initialises the matrix representing the particles. Each is assigned a random value
    particles = np.zeros((source.no,3))
    try:
        particles[:,0] = np.random.uniform(0, source.w, size=source.no) #This is the x position
    except AttributeError:
        particles[:,0] = np.random.uniform(0, source.r, size=source.no) #This uses the radius if it can't find a width
    particles[:,1] = np.full(source.no,0) #This is the y position

    particle_states = np.zeros(source.no,dtype=int) #0->active,1->absorbed,2->transmitted
    #The speed is then applied to all particles uniformly
    #I calculated the speed as a function of the shield's thickness
    #speed = (shield.l/(2*np.cos(np.pi/3))) - 1
    speed = source.energy
    #print(speed)
    speed_inverse = speed / np.pow(dist,2)
    #print(speed_inverse)
    particles[:, 2] = np.full(source.no,speed_inverse)
    
    angles = np.random.uniform(np.pi/3,2*np.pi/3,size=source.no)
    #This takes a random angle from 60 to 120 degrees, multiplies by the speed then applies it to each particle to determine the location
    particles[:,0] += np.cos(angles) * particles[:,2]
    particles[:,1] += np.sin(angles) * particles[:,2]
    return particles, particle_states, angles


def particle_sim(shield,source,particles,particle_states,angles):
    
    detection_layer_y = (shield.h // 2) + shield.l
    #This is the Beer Lambert Law
    transmission_probabilities = np.exp(-shield.mu * shield.l)
        
    def update():
        nonlocal particle_states, particles

        #Any particles assigned zero are designated active
        active_particles = particle_states == 0
        #Then the active particles are assigned a random angle
        particles[active_particles, 0] += np.cos(angles[active_particles]) * 1
        particles[active_particles, 1] += np.sin(angles[active_particles]) * 1

        for i in range(source.no):
            if particle_states[i] == 0:
                #print((shield.h // 2),particles[i,1],detection_layer_y)
                #if shield.h // 2 <= particles[i,1] <= detection_layer_y:
                #print(shield.x_one,particles[i,0],shield.x_two)
                #print(shield.y_one,particles[i,1],shield.y_two)
                if shield.x_one <= particles[i,0] <= shield.x_two:
                    #print('x')
                    if shield.y_one <= particles[i,1]:# <= shield.y_two:
                        #print('y')
                        if np.random.rand() < transmission_probabilities:
                            #print("Transmitted")
                            particle_states[i] = 2 #Transmitted
                        else:
                            #print("Absorbed")
                            particle_states[i] = 1 #Absorbed
        if np.all(particle_states != 0):
            print("Simulation Ended")
    
    update()
    results[material] = np.sum(particle_states == 2)
        
for material in materials.keys():
    #puck_test = RadioactiveObject("block",length=0.01,width=0.01,height=0.01,location=[0,0],num_particles=1000000)
    puck_test = RadioactiveObject("pill","Cs-137",radius=0.01,height=0.01,location=[0,0],num_particles=1000000)
    puck_vol = puck_test.volume()
    shield_test = ShieldingObject(material,length=0.1,width=0.05,height=0.01,location=[0,1])
    vol_test = shield_test.volume()
    parts, part_states, part_angles = particle_gen(shield=shield_test,source=puck_test)
    particle_sim(shield=shield_test,source=puck_test,particles=parts,particle_states=part_states,angles=part_angles)

materials_list = list(materials.keys())
transmitted_counts = [results[material] for material in materials_list]
print(transmitted_counts)