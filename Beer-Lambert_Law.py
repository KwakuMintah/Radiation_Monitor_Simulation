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
    "Tungsten": {"denisty": 19.254, "mu": 0.5} #I'm not sure where Vasan
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
        self.n = self.params.get("num_particles")
    #Replicating Josh's code for defining the volume of the shield. The object will always be a block in this case
    def volume(self):
        self.l = self.params.get("length")
        self.w = self.params.get("width")
        self.h = self.params.get("depth")
        if self.l is None or self.w is None or self.h is None:
            raise ValueError("Block requires 'length', 'width', and 'depth'")
        return self.l * self.w * self.h 

    def particle_sim(self):
        self.particles = np.zeros((self.n, 3))
        self.particles[:,0] = np.random.uniform(0, self.w, size=self.n)
        self.particles[:,1] = np.full(self.n,0)

        particle_states = np.zeros(self.n,dtype=int) #0->active,1->absorbed,2->transmitted
        speed = 100
        self.particles[:, 2] = np.full(self.n,speed)

        angles = np.random.uniform(np.pi/3,2*np.pi/3,size=self.n)
        self.particles[:,0] += np.cos(angles) * self.particles[:,2]
        self.particles[:,1] += np.sin(angles) * self.particles[:,2]

        detection_layer_y = (self.h // 2) + self.l
        transmission_probabilities = np.exp(-self.mu * self.l)
        #results[material] = np.sum(particle_states == 2)
        
        def update(self):
            nonlocal particle_states

            active_particles = particle_states == 0
            self.particles[active_particles, 0] += np.cos(angles[active_particles]) * 1
            self.particles[active_particles, 1] += np.sin(angles[active_particles]) * 1

            for i in range(self.n):
                if particle_states[i] == 0:
                    if self.h // 2 <= self.particles[i,1] <= (self.h // 2 + self.l):
                        if np.random.rand() < transmission_probabilities:
                            particle_states[i] = 2 #Transmitted
                        else:
                            particle_states[i] = 1 #Absorbed
            if np.all(particle_states != 0):
                print("Simulation Ended")
        results[material] = np.sum(particle_states == 2)


shield_test = ShieldingObject("Lead",length=10,width=15,depth=50,num_particles=1000)
vol_test = shield_test.volume()

for material in materials.keys():
    shield_test.particle_sim()

materials_list = list(materials.keys())
transmitted_counts = [results[material] for material in materials_list]
print(transmitted_counts)