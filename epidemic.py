import networkx as nx
import random
import matplotlib
import random
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FFMpegWriter
from matplotlib.pyplot import figure
import os
import subprocess
from numpy import trapz
class Person:
    

    def __init__(self, node, G):
        #self.location = node

        #Timers are multiplied by 3 because there are now 3 timesteps per day 
        self.exposedTimer = 5 * 3 #This will be how long someone is exposed
        self.infectedTimer = 10 * 3 
        self.state = 0 # 0 is S, 1 is E, 2 is I, 3 is R
        self.fixed = False
        self.home = node
        #self.location = node
        self.steps = 1 #Give everyone a max of 1 moves per timestep
        self.neighborhood = []
        self.bedRidden = False

        for nodes in G: #Assigning a neighborhood of nodes in which this individual can travel to. 
            if self.tooFarAway(G,nodes) == False: 
                self.neighborhood.append(nodes)
            #print(self.neighborhood)

        if self.home in self.neighborhood: #removing the home node from the neighborhood, because I wanted more interesting behavior
            self.neighborhood.remove(self.home)
 

    def updateLocation(self, node):
        self.location = node

    def infected(self):
        self.state = 1

    def updateStatus(self): #need to call this every time step 
        #print(self.state)
        if self.state == 1:
            self.exposedTimer = self.exposedTimer - 1
            if self.exposedTimer == 0:
                #print("timer swapped")
                self.state = 2

        elif self.state == 2:
            self.infectedTimer = self.infectedTimer - 1
            if self.infectedTimer == 0:
                #("othertimer swapped")
                self.state = 3

    def setHome(self, node):
        self.home = node

    def howFarFromHome(self, node, G):
        return nx.shortest_path_length(G, self.location, node)

    def tooFarAway(self, G, node):
        if nx.shortest_path_length(G, node, self.home) > 6:
            return True

        return False

    def stayHome(self, G, node):
        if self.bedRidden == False and self.state == 2: #If they have not previously been bedRiddne, and they are infected, update
            self.bedRidden = True
            G.node[node]['stuckAtHome'] += 1

        elif self.bedRidden == True and self.state != 2: #If they are bedridden but sick, update 
            self.bedRidden = False
            G.node[node]['stuckAtHome'] -= 1







    
            

    


class World:
    
    def __init__(self):
        self.size = 100
        self.G = nx.watts_strogatz_graph(100, 4, 0.65)
        i = 0
        for node in self.G:
            self.G.add_node(i)
            self.G.node[i]['population'] = 0
            self.G.node[i]['S'] = []
            self.G.node[i]['I'] = []
            self.G.node[i]['E'] = []
            self.G.node[i]['R'] = []
            self.G.node[i]['stuckAtHome'] = 0 #Used to keep track of how many people are staying at home.
            i += 1

    def swapExposed(self, node, person):
        #person = self.G.node[node]['S'].pop()
        person.state = 1
        self.G.node[node]['S'].remove(person)
        self.G.node[node]['E'].append(person)

    def populateNode(self, node, population): #population is an integer
        for i in range(0,population):
            #TODO populate a set node with the specified population
            #Add population many Persons to lits of node
            p1 = Person(node, self.G)
            p1.setHome = node
            self.G.node[node]['S'].append(p1)
            #print("appended")

        self.G.node[node]['population'] = population

    def populateGraph(self):
        for node in self.G:
            self.populateNode(node, 100)



            

    def insertInfected(self, node, size):
        #place size number of infected individuals into a node
        print("I have run")
        for i in range(0,size):
            p1 = Person(node, self.G)
            p1.infected()
            p1.setHome(node)
            self.G.node[node]['E'].append(p1)
            self.G.node[node]['population'] += 1
            
        
    '''def checkInfected(self):
        #TODO check every node for the ratio of infected to Whole population.
        #Then, spread infection to people accordingly.
        for node in self.G:
            if self.G.node[node]['population'] != 0:
                becomeInfected = 0
                ratio = len(self.G.node[node]['I'])/self.G.node[node]['population']
                if ratio == 0:
                    becomeInfected = 0
                elif ratio < 0.3 and ratio > 0:
                    becomeInfected = len(self.G.node[node]['S']) * 0.05

                elif ratio >= 0.3 and ratio < 0.50:
                    becomeInfected = len(self.G.node[node]['S']) * 0.2

                elif ratio >= 0.50 and ratio < 0.90:
                    becomeInfected = len(self.G.node[node]['S'])*0.35

                else: 
                    becomeInfected = len(self.G.node[node]['S'])*0.50

                #print(becomeInfected)

                for i in range(int(becomeInfected)):
                    self.swapExposed(node)
                   #print("We've swapped")

            else:
                continue'''

    def checkInfectedRandom(self): #The random infection method 
        for node in self.G:
            if self.G.node[node]['population'] != 0:
                ratio = (len(self.G.node[node]['I']) - self.G.node[node]['stuckAtHome'])/self.G.node[node]['population']
                iChance = 0
                if ratio == 0:
                    iChance = 0
                elif ratio < 0.3 and ratio > 0:
                    iChance = 5 #chance to be infected is iChance/100

                elif ratio >= 0.3 and ratio < 0.50:
                    iChance = 20

                elif ratio >= 0.50 and ratio < 0.90:
                    iChance = 35

                else: 
                    iChance = 50

                for person in self.G.node[node]['S']:
                    if random.randint(0,99) <= iChance:
                        self.swapExposed(node, person)




                                
    def updatePopulation(self): #Checking if we have to move people from list to list based on their state 
        for node in self.G:
            for person in self.G.node[node]['E']:
                person.updateStatus()
                if person.state == 2:
                    #print("moved from E to I")
                    dude = person
                    self.G.node[node]['E'].remove(person)
                    self.G.node[node]['I'].append(person)

            for person in self.G.node[node]['I']:
                person.updateStatus()
                if person.state == 3:
                    self.G.node[node]['I'].remove(person)
                    self.G.node[node]['R'].append(person)



    def movePopulation(self):
        #TODO move a certain amount of each list to another node that is adjacent to the node they are at.
       
        for node in self.G:
            '''neighbors = []
            dummy = Person(node)
            dummy.setHome(node)
            for nodes in self.G.neighbors(node): 

                if dummy.tooFarAway(self.G, nodes) == False: #making sure the list of destinations isn't too far away from home
                    neighbors.append(nodes)



            #print(neighbors)
            if dummy.home in neighbors:
                neighbors.remove(dummy.home)'''

            for person in self.G.node[node]['S']:

                if random.randint(0, 10) > 5 and len(self.G.node[node]['S']) > 0 and person.fixed == False:

                    '''neighbors = []
                    for nodes in G.neighbors(node):
                        if nodes in person.neighborhood:
                            neighbors.append(node)
                    person.fixed = True'''

                    self.G.node[node]['S'].remove(person)
                    self.G.node[node]['population'] -= 1
                    choice = random.randint(0, len(person.neighborhood) - 1)


                    destinationNode = person.neighborhood[choice]

                    self.G.node[destinationNode]['S'].append(person)
                    self.G.node[destinationNode]['population'] += 1
                    #person.updateLocation(destinationNode)
                    #print("S moved")

            for person in self.G.node[node]['E']:

                if random.randint(0, 10) > 5 and len(self.G.node[node]['E']) > 0 and person.fixed == False:

                    person.fixed = True

                    self.G.node[node]['E'].remove(person)
                    self.G.node[node]['population'] -= 1
                    choice = random.randint(0, len(person.neighborhood) - 1)
                    destinationNode = person.neighborhood[choice]
                    self.G.node[destinationNode]['E'].append(person)
                    self.G.node[destinationNode]['population'] += 1
                    #person.updateLocation(destinationNode)
                    #print("E moved")

            for person in self.G.node[node]['I']:

                if random.randint(0, 10) > 5 and len(self.G.node[node]['I']) > 0 and person.fixed == False and person.bedRidden == False: #checking if their stuck at home

                    person.fixed = True

                    self.G.node[node]['I'].remove(person)
                    self.G.node[node]['population'] -= 1
                    choice = random.randint(0, len(person.neighborhood) - 1)
                    destinationNode = person.neighborhood[choice]
                    self.G.node[destinationNode]['I'].append(person)
                    self.G.node[destinationNode]['population'] += 1
                    #person.updateLocation(destinationNode)
                    #print("I moved")

            for person in self.G.node[node]['R']:

                if random.randint(0, 10) > 5 and len(self.G.node[node]['R']) > 0 and person.fixed == False:

                    person.fixed = True

                    self.G.node[node]['R'].remove(person)
                    self.G.node[node]['population'] -= 1
                    choice = random.randint(0, len(person.neighborhood) - 1)
                    destinationNode = person.neighborhood[choice]
                    self.G.node[destinationNode]['R'].append(person)
                    self.G.node[destinationNode]['population'] += 1
                    #person.updateLocation(destinationNode)


    def recover(self):
        for node in self.G:
            for person in self.G.node[node]['S']:
                person.fixed = False

            for person in self.G.node[node]['E']:
                person.fixed = False

            for person in self.G.node[node]['I']:
                person.fixed = False

            for person in self.G.node[node]['R']:
                person.fixed = False

    def returnHome(self): #Checking if everyone in each node is close enough to home as they should be per code design, and then 
                          #moving them back home. It is also checking if they will decide to stay home the next day if they are sick
        for node in self.G:
            for person in self.G.node[node]['S']: 
                if person.tooFarAway(self.G, node) == False:
                    self.G.node[node]['S'].remove(person)
                    self.G.node[node]['population'] -= 1
                    self.G.node[person.home]['S'].append(person)
                    self.G.node[node]['population'] += 1
                    person.stayHome(self.G, node)

                else:
                    print("Something went wrong")
                    

            for person in self.G.node[node]['E']:
                if person.tooFarAway(self.G, node) == False:
                    self.G.node[node]['E'].remove(person)
                    self.G.node[node]['population'] -= 1
                    self.G.node[person.home]['E'].append(person)
                    self.G.node[node]['population'] += 1
                    person.stayHome(self.G, node)

                else:
                    print("Something went wrong")

            for person in self.G.node[node]['I']:
                if person.tooFarAway(self.G, node) == False:
                    self.G.node[node]['I'].remove(person)
                    self.G.node[node]['population'] -= 1
                    self.G.node[person.home]['I'].append(person)
                    self.G.node[node]['population'] += 1
                    person.stayHome(self.G, node) #checking if they should choose to stay at home

                else:
                    print("Something went wrong")
                    

            for person in self.G.node[node]['R']:
                if person.tooFarAway(self.G, node) == False:
                    self.G.node[node]['R'].remove(person)
                    self.G.node[node]['population'] -= 1
                    self.G.node[person.home]['R'].append(person)
                    self.G.node[node]['population'] += 1
                    person.stayHome(self.G, node)

                else:
                    print("Something went wrong")
                    

def main():
    newWorld = World()
    newWorld.populateGraph()
    newWorld.insertInfected(0, 1)
    files = []
    dayCycle = 3 #represents morning, afternoon, and night for movement, allowing everyone to move each part of the daycycle
    
    fig = plt.figure(num = None, figsize = (10,10))
    position = nx.spring_layout(newWorld.G, dim = 2)
    infectionTime = []
    regularTime = []
    #with writer.saving(fig, "epi_movie.mp4", 365):
    for i in range(40):
        
        #print(colors)

        plt.cla()
        for timestep in range(dayCycle): #representing 3 steps per day

            colors = []
            for node in newWorld.G:
                colors.append(len(newWorld.G.node[node]['I']))
            '''nx.draw_networkx(newWorld.G, with_labels = True, node_size = 10, width = 0.7, node_color = colors, cmap = plt.cm.OrRd, pos = position)
                #writer.grab_frame()

            fname = '_tmp%d' % i + '-%d' % timestep

            plt.savefig(fname)

            print('Saving frame', fname)'''
            
            newWorld.checkInfectedRandom()
            newWorld.updatePopulation()
            newWorld.movePopulation()
            newWorld.recover()

            totalInfected = 0

        for node in newWorld.G:
            totalInfected = totalInfected + len(newWorld.G.node[node]['I'])

            
        infectionTime.append(totalInfected)
        regularTime.append(i)
            

        newWorld.returnHome() #Now, at the end of the day, everyone is going home

            


            


    plt.plot(regularTime, infectionTime)

    plt.savefig("INFECTEDPLOT.png");

    print(max(infectionTime))
    print(trapz(infectionTime, dx = 1))


main()








