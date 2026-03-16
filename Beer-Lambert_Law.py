import numpy as np
import decimal
import matplotlib.pyplot as plt
import scipy as sci
from decimal import Decimal as dec
#Adapted from the tutorial on Medium by Vipran Vasan

materials = {
    "Lead": {"density": 11.35, "mu": 0.5},
    "Aluminium" : {"density": 2.7, "mu": 0.136},
    "Steel": {"density": 7.85, "mu": 0.15},
    "Concrete": {"density": 2.4, "mu": 0.03},
    "Tungsten": {"density": 19.254, "mu": 0.5} #I'm not sure where Vasan
    #got their values for mu from so I have given tungsten the same value as 
    #lead until I find it
}

results = {material: 0 for material in materials.keys()}

class ShieldingObject:
    def __init__(self,mat,**kwargs):
        self.mat = materials[mat]
        self.dens = self.mat["density"]
        self.mu = self.mat["mu"]
        if mat is None:
            mat = materials["Lead"]
        self.params = kwargs
    #Replicating Josh's code for defining the volume of the shield. The object will always be a block in this case
    def volume(self):
        self.l = self.params.get("length")
        self.w = self.params.get("width")
        self.h = self.params.get("depth")
        if self.l is None or self.w is None or self.h is None:
            raise ValueError("Block requires 'length', 'width', and 'depth'")
        return self.l * self.w * self.h 


def particle_sim(shield,num_particles):
    particles = np.zeros((num_particles,3))
    particles[:,0] = np.random.uniform(0, shield.w, size=num_particles)
    particles[:,1] = np.full(num_particles,0)

    particle_states = np.zeros(num_particles,dtype=int) #0->active,1->absorbed,2->transmitted
    speed = 100
    particles[:, 2] = np.full(num_particles,speed)

    angles = np.random.uniform(np.pi/3,2*np.pi/3,size=num_particles)
    particles[:,0] += np.cos(angles) * particles[:,2]
    particles[:,1] += np.sin(angles) * particles[:,2]

    detection_layer_y = (shield.h // 2) + shield.l
    transmission_probabilities = np.exp(-shield.mu * shield.l)
    #results[material] = np.sum(particle_states == 2)
        
    def update():
        nonlocal particle_states, particles

        active_particles = particle_states == 0
        particles[active_particles, 0] += np.cos(angles[active_particles]) * 1
        particles[active_particles, 1] += np.sin(angles[active_particles]) * 1

        for i in range(num_particles):
            if particle_states[i] == 0:
                if shield.h // 2 <= particles[i,1] <= (shield.h // 2 + shield.l):
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
    shield_test = ShieldingObject(material,length=10,width=15,depth=10)
    vol_test = shield_test.volume()
    particle_sim(shield_test,num_particles=300)

materials_list = list(materials.keys())
transmitted_counts = [results[material] for material in materials_list]
print(transmitted_counts)