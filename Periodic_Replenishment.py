from copy import deepcopy
from random import randint
from scipy.stats import gamma
from time import time


## Allows User to input parameters needing only how long the simulation
## is to run and how many whole days (as hours) as warmup time.
## Can change any of the other parameters. An example follows:
## Simulation (168, 48, Fixed_Cost = 200) where Simulation Length would be
## a week (168 hours), with a two day Warm-Up Time, and Fixed Cost of 200.

class Simulation (object):                                                                                      
    def __init__ (self, Simulation_Length, Warmup_Time=0, Cycle_Length = 24, Demand = 0.002778, \
                  Fixed_Cost= 100, Lead_Time = 4, Num_SKU = 200, Stockout_Cost = 55, Rho_Hat = 0.004):          # This portion initializes parameters and variables used throughout         
                                                                                                                # the program.
        self.Sim_Begin = time()

        self.Board = []
        self.Data = []
        self.Erlang_Nums = []
        self.Inventory = []
        self.Lead_Time_Intervals = []
        self.Replenishment_Times = []
        self.SKU = []
        self.SKU_Consumed = []
        self.Times_Stored = []
        self.Track_Board = []
        self.Track_Virtual = []
        self.Virtual_Board = []
        
        self.Cost_Fixed = 0
        self.Cost_Stockout = 0
        self.Cost_Stockout_t = 0
        self.Order_Amount = 0
        self.Secondary_Amount = 0
        self.Time = 0
        
        self.Cycle_Length = Cycle_Length
        self.Demand = Demand
        self.Fixed_Cost = Fixed_Cost
        self.Lead_Time = [Lead_Time, 4]
        self.Num_SKU = Num_SKU
        self.Sim_Length = Simulation_Length
        self.Stockout_Cost = Stockout_Cost
        self.Rho_Hat = Rho_Hat
        self.Warmup_Time = Warmup_Time


        for ele in range (1, self.Sim_Length/self.Cycle_Length):
            self.Lead_Time_Intervals.append ((ele*self.Cycle_Length, ele*self.Cycle_Length+4))
            
        self.Initialize_SKU()


    def Add_To_Board (self, SKU, Spot):                                                                         # This function places consumed items on the Board.
        
        self.Board.append ([self.SKU[SKU][0]])
        if Spot == 1:
            self.Board [-1].append ("P")
        elif Spot == 2:
            self.Board [-1].append ("S")
        else:
            print "*****Error: Adding to Board Received Unexpected Input*****\n"


    def Add_To_Virtual (self, SKU, Spot):                                                                       # If item is consumed during Lead Time, item goes to this Board.
        
        self.Virtual_Board.append ([self.SKU[SKU][0]])
        if Spot == 1:
            self.Virtual_Board [-1].append ("P")
        elif Spot == 2:
            self.Virtual_Board [-1].append ("S")
        else:
            print "*****Error: Adding To Virtual Board Received Unexpected Input*****\n"

    def Clear (self):                                                                                           # Used to erase relevant variables after warmup.
        
##        for element in self.Board:                                                                            # If secondaries on board before warmup count at the start of the steady state
##            if element[1] == "S":
##                self.Secondary_Amount += 1
        self.Secondary_Amount = 0
        self.Sim_Begin = time ()
        self.Cost_Stockout_t = 0
        self.Track_Board = []
        self.Track_Virtual = []

        print "----- Tracking Takes Place Now -----\n"

    def Check_Lead_Time (self):                                                                                 #  Toggles whether system is under Lead Time.
        
        if len (self.Lead_Time_Intervals) > 0:
            if self.Lead_Time_Intervals[0][0] <= self.Time <= self.Lead_Time_Intervals[0][1]:                   # If time is between expected lead time periods, toggle on
                self.Lead_Time[0] = True
            else:
                self.Lead_Time[0] = False
                if self.Time > self.Lead_Time_Intervals[0][1]:
                    self.Lead_Time_Intervals.pop (0)
        else:
            self.Lead_Time[0] = False

                    

    def Compute_Stockout (self):                                                                                # Computes cost of Stock-outs.
        
        self.Cost_Stockout = self.Secondary_Amount * self.Stockout_Cost


    def Compute_Stockout_t (self):                                                                              # Computes a time-weighted Stock-out cost.
        
        for element in self.Times_Stored:
            self.Cost_Stockout_t += (self.Time - element)*(self.Rho_Hat)
        self.Times_Stored = []
        return self.Cost_Stockout_t

    

    def Consumed_SKU (self):                                                                                    # Function that determines which SKU's are consumed.
        
        check = True
        while self.Time < self.Sim_Length:
            while self.Time < self.Cycle_Length * (self.Order_Amount + 1):
                arrival = gamma (self.Num_SKU, scale = self.Demand).rvs()
                self.Erlang_Nums.append (arrival)
                Location = randint (0, self.Num_SKU-1)

                if self.Time + arrival <= self.Cycle_Length * (self.Order_Amount + 1):                          # Analyzes whether order is needed based on time.
                    self.Time += arrival
                    self.Check_Lead_Time ()

                else:
                    break

                if self.Check_SKU (Location):
                    check = self.Empty_SKU (Location)
                else:
                    print "***** Unable to consume SKU *****\n"
                
                while check == False:                                                                           # If unable to consume an SKU, will try another and output error.
                    Location = randint (0, self.Num_SKU-1)
                    check = self.Empty_SKU (Location)
                
            self.Replenishment()
            self.Time += arrival
            if int (self.Time) == self.Warmup_Time:                                                             # When Warm-Up period is over, clear relevant information.
                self.Clear()
                
        self.Total_Cost()


    def Empty_SKU (self, Emptied_SKU):                                                                          # Consumption of SKU's occurs here. If error occurs, a statement is printed
                                                                                                                # another SKU is consumed
        if self.Primary_Full(Emptied_SKU):                                                                      # Consumes Primary SKU and switches the Secondary into Primary location.
            self.SKU[Emptied_SKU][1] = "S"
            self.SKU[Emptied_SKU][2] = "E"
            if self.Lead_Time[0] == False:                                                                      # Posts to either Board or Virtual Board.
                self.Add_To_Board (Emptied_SKU, 1)
                return True
            elif self.Lead_Time[0] == True:
                self.Add_To_Virtual (Emptied_SKU, 1)
                return True
            else:
                print "*****Unexpected Input For Lead_Time*****\n"
                return False

        elif self.Primary_Is_Secondary (Emptied_SKU):                                                           # Consumes a Secondary SKU if the Primary was consumed.
            self.Times_Stored.append (self.Time)                                                                # Records the time the Secondary went to a board.
            self.SKU[Emptied_SKU][1] = "E"
            self.Secondary_Amount += 1                                                                          # Records one to the amount of Secondaries that were consumed.
            if self.Lead_Time[0] == False:                                                                      # Checks Lead Time to post to correct Board.
                self.Add_To_Board (Emptied_SKU, 2)  
                return True
            elif self.Lead_Time[0] == True:
                self.Add_To_Virtual (Emptied_SKU, 2)
                return True
            else:
                print "*****Unexpected Input For Lead_Time*****\n"
                return False
                
        elif self.Secondary_Full(Emptied_SKU):                                                                  # Error case for improper location of Secondary, a case of (Empty, Secondary). 
            print "*****Error: Primary Emptied and Secondary Is Full*****\n"
            return False

        elif self.Primary_Empty(Emptied_SKU) and self.Secondary_Empty(Emptied_SKU):                             # Occurs when both SKU's of a particular item have been consumed, consumes another SKU.
            print "***** Both Primary and Secondary SKU are already empty *****"
            print "\nWill Consume Different Bin\n"
            return False
        
        else:
            print "!!!*****Unknown Error*****!!!\n"                                                             # If a case occurs that the code is not prepared for, an error statement is shown and
            return False                                                                                        # a different SKU is consumed.


##    def Extraction (self):                                                                                    # Demonstrates the potential of extracting data for use
##        File = open (self.File_Name)
##        File.readline()
##        Raw_Data = File.readlines()
##        File.close()
##
##        for element in Raw_Data:
##            element = element.split()
##            self.Data.append ((element[0], element[1]))
##
##        self.Initialize_SKU()


    def Initialize_SKU (self):
##        for element in self.Data:                                                                             # For if Extraction is used
##            self.SKU.append ([element[0], "P", "S"])
        
        for element in range (1, self.Num_SKU + 1):
            self.SKU.append (["Item" + str(element), "P", "S"])

        for element in self.SKU:
            self.Inventory.append (element[0])

        self.Consumed_SKU()
    

    def Replenishment (self):                                                                                   # Need to run more tests in this area
        self.Cost_Fixed += self.Fixed_Cost
        self.Replenishment_Times.append (self.Time)

        for element in self.Board:
            location = self.Inventory.index (element[0])
            if element[1] == "P":                                                                               # If Tag on Board is a Primary SKU
                if self.Primary_Is_Secondary(location):                                                         # Check if Item is using Secondary SKU
                    self.SKU[location][2] = "S"                                                                 # If yes, Replenished SKU should become Secondary and Primary should be named properly
                    self.SKU[location][1] = "P"
                elif self.Primary_Empty(location):
                    self.SKU[location][1] = "P"
                elif self.Primary_Full(location):
                    print "*****Error: Should not have two Primaries*****\n"
                else:
                    print "*****Error: Expected Primary SKU", str(self.SKU[location][0]), "To Be Empty or Full (By Secondary)*****\n"
                    print self.SKU[location]
            elif element[1] == "S":
                if self.Primary_Full (location) and self.Secondary_Empty(location):                             # Primary SKU should be Replenished first
                    self.SKU[location][2] = "S"
                    
                elif self.Primary_Is_Secondary (location):
                    print "***** Error: Should not have two Secondaries*****\n"
                    print self.SKU[location]
                    
                elif self.Primary_Empty(location) and self.Secondary_Empty(location):
                    print "***** Secondary replenished before Primary *****\n"
                    self.SKU[location][1] = "S"
                    
                else:
                    print self.SKU [location]
                    print ">>>>>>>>>>>>>>> HERE <<<<<<<<<<<<<<<\n"
                        
            else:
                print "*****Error: Received Invalid Input ('P', 'S', 'E')*****\n"

        self.Track_Board.append (len(self.Board))
        self.Track_Virtual.append (len(self.Virtual_Board))
        self.Board = deepcopy (self.Virtual_Board)
        self.Virtual_Board = []
        self.Lead_Time[0] = True

        self.Order_Amount += 1

        self.Compute_Stockout_t()

        print "-Successful Replenishemnt- \n"
    

    def Total_Cost (self):
        self.Cost_Fixed = self.Fixed_Cost * ((self.Sim_Length - self.Warmup_Time)/self.Cycle_Length)
        self.Compute_Stockout()
        self.end_time = time ()
        A = self.Cost_Stockout
        B = self.Cost_Stockout_t
        C = self.Cost_Fixed

        print (A+B+C) / ((self.Sim_Length - self.Warmup_Time) * 1.0)    

## Various Error Checking Functions      

    def Check_SKU (self, Location):                                                                             # Will check error conditions on SKU
        if self.SKU[Location][0] == "S" and self.SKU[Location][1] == "P":
            print "***** Error: SKU is of the form (S, P) *****\n"
            return False
        elif self.SKU[Location][0] == "P" and self.SKU[Location][1] == "P":
            print "***** Error: Have two Primary SKU's *****\n"
            return False
        elif self.SKU[Location][0] == "S" and self.SKU[Location][1] == "S":
            print "***** Error: Two Secondary SKU's *****\n"
            return False
        elif self.SKU[Location][0] == "E" and self.SKU[Location][1] == "S":
            print "***** Error: Improper SKU (E, S) *****\n"
            return False
        else:
            return True
        

    def Primary_Empty (self, SKU_Location):                                                                     # Checks for Nothing to be in Primary Bin (it is Empty)
        return self.SKU[SKU_Location][1] == "E"


    def Primary_Full (self, SKU_Location):                                                                      # Checks if Primary Bin is filled by Primary Bin
        return self.SKU[SKU_Location][1] == "P"

    
    def Primary_Is_Secondary (self, SKU_Location):                                                              # Checks if Primary Bin is filled by a Secondary Bin
        return self.SKU[SKU_Location][1] == "S"


    def Secondary_Full (self, SKU_Location):                                                                    # Checks if Secondary Bin is filled by a Secondary Bin
        return self.SKU[SKU_Location][2] == "S"


    def Secondary_Empty (self, SKU_Location):                                                                   # Checks if Seconday Bin is Empty
        return self.SKU[SKU_Location][2] == "E"

## Functions That Will Gather Relevant Information

    def Avg_Time_Board (self):
        pass


    def Avg_Time_Virtual (self):
        pass


    def Avg_Num_Board (self):
        print (sum (self.Track_Board) * 1.0) / (len (self.Track_Board))


    def Avg_Num_Virtual (self):
        print (sum (self.Track_Virtual) * 1.0) / (len (self.Track_Virtual))

    


