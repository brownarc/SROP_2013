from scipy.stats import gamma
from random import randint
from time import time

class Simulation (object):
    def __init__ (self, SKU, Lead_Time, Demand, Cycle_Length, Fixed_Cost, Stockout_Cost, Rho_Hat):                  # Change Stockout_Cost to Stockout_Amount

        self.Sim_Begin = time()

        self.Board = []
        self.Data = []
        self.Inventory = []
        self.Replenishment_Times = []
        self.SKU = []
        self.SKU_Consumed = []
        self.Times_Stored = []
        self.Track_Board = []
        self.Track_Virtual = []
        self.Virtual_Board = []
        
        self.Rho_Hat_t = 0
        self.Cost_Fixed = 0
        self.Cost_Stockout = 0
        self.Cost_Stockout_t = 0
        self.Lead_Finish = 0
        self.Order_Amount = 0
        self.Secondary_Amount = 0
        self.Time = 0
        
        self.Cycle_Length = Cycle_Length
        self.Demand = Demand
        self.Fixed_Cost = Fixed_Cost
        self.Lead_Time = [False, Lead_Time]
        self.Num_SKU = SKU
        self.Stockout_Cost = Stockout_Cost
        self.Rho_Hat = Rho_Hat

        self.Initialize_SKU()


    def Add_To_Board (self, SKU, Spot):
        self.Board.append ([self.SKU[SKU][0]])
        if Spot == 1:
            self.Board [-1].append ("P")
        elif Spot == 2:
            self.Board [-1].append ("S")
        else:
            print "*****Error: Adding to Board Received Unexpected Input*****"


    def Add_To_Virtual (self, SKU, Spot):
        self.Virtual_Board.append ([self.SKU[SKU][0]])
        if Spot == 1:
            self.Virtual_Board [-1].append ("P")
        elif Spot == 2:
            self.Virtual_Board [-1].append ("S")
        else:
            print "*****Error: Adding To Virtual Board Received Unexpected Input*****"


    def Compute_Stockout (self):
        self.Cost_Stockout = self.Secondary_Amount * self.Stockout_Cost


    def Compute_Stockout_t (self):
        for element in self.Times_Stored:
            self.Rho_Hat_t += (self.Time - element)*(self.Rho_Hat)
        self.Cost_Stockout_t = self.Rho_Hat_t
        return self.Rho_Hat_t

    

    def Consumed_SKU (self):
        check = True
        while self.Time < self.Cycle_Length:
            arrival = gamma (self.Num_SKU, scale = self.Demand).rvs()
            Location = randint (0, 199)

            check = self.Empty_SKU (Location)
            
            while check == False:
                Location = randint (0, 199)
                check = self.Empty_SKU (Location)

            if self.Time + arrival <= self.Cycle_Length:
                self.Time += arrival

            else:
                break
            
        self.Replenishment()
            


    def Empty_SKU (self, Emptied_SKU):
        if self.Primary_Full(Emptied_SKU):
            self.SKU[Emptied_SKU][1] = "S"
            self.SKU[Emptied_SKU][2] = "E"
            if self.Lead_Time[0] == False:
                self.Add_To_Board (Emptied_SKU, 1)
            elif self.Lead_Time[0] == True:
                self.Add_To_Virtual (Emptied_SKU, 1)
            else:
                print "*****Unexpected Input For Lead_Time*****"
                return False

        elif self.Primary_Is_Secondary (Emptied_SKU):
            self.SKU[Emptied_SKU][1] = "E"
            self.Secondary_Amount += 1
            self.Times_Stored.append (self.Time)
            if self.Lead_Time[0] == True:
                self.Add_To_Board (Emptied_SKU, 2)                                      # Need Lead Time check
            elif self.Lead_Time[0] == False:
                self.Add_To_Virtual (Emptied_SKU, 2)
            else:
                print "*****Unexpected Input For Lead_Time*****"
                self.Stock_Out ()
                return False
                
        elif self.Secondary_Full(Emptied_SKU):
            print "*****Error: Primary Emptied and Secondary Is Full*****"
            return False

        elif self.Primary_Empty(Emptied_SKU) and self.Secondary_Empty(Emptied_SKU):
            print "*****Error: Both Primary and Secondary SKU are already empty.*****"
            print "\nWill Consume Different Bin\n\n"
            return False
        
        else:
            return True


##    def Extraction (self):                                                            # Demonstrates the potential of extracting data for use
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
##        for element in self.Data:                                                     # For if Extraction is used
##            self.SKU.append ([element[0], "P", "S"])
        
        for element in range (1, self.Num_SKU + 1):
            self.SKU.append (["Item" + str(element), "P", "S"])

        for element in self.SKU:
            self.Inventory.append (element[0])

        self.Consumed_SKU()
    

    def Replenishment (self):                                                           # Need to run more tests in this area
        self.Cost_Fixed += self.Fixed_Cost
        self.Replenishment_Times.append (self.Time)

        for element in self.Board:
            location = self.Inventory.index (element[0])
            if element[1] == "P":                                                       # If Tag on Board is a Primary SKU
                if self.Primary_Is_Secondary(location):                                 # Check if Item is using Secondary SKU
                    self.SKU[location][2] = "S"                                         # If yes, Replenished SKU should become Secondary and Primary should be named properly
                    self.SKU[location][1] = "P"
                elif self.Primary_Empty(location):
                    self.SKU[location][1] = "P"
                else:
                    print "*****Error: Expected Primary SKU", str(self.SKU[location][0]), "To Be Empty or Full (By Secondary)*****"
            elif element[1] == "S":
                if self.Primary_Full (location) and self.Secondary_Empty(location):     # Primary SKU should be Replenished first
                    self.SKU[location][2] = "S"

                else:
                    print "*****Error: Secondary SKU Replenishment Problem*****"        # Need to revist logic
                    self.SKU[location][2] = "S"
            else:
                print "*****Error: Received Invalid Input ('P', 'S', 'E')*****"

        self.Track_Board.append (len(self.Board))
        self.Board = []

        self.Order_Amount += 1

        print "-Successful Replenishemnt- \n"

        self.Total_Cost ()
    

    def Total_Cost (self):
        self.Compute_Stockout()
        self.Compute_Stockout_t()
        self.end_time = time ()
        print (self.Cost_Stockout + self.Cost_Stockout_t + self.Cost_Fixed)/ ((self.end_time-self.Sim_Begin)*self.Cycle_Length*1.0)
    

## Various Error Checking Functions      

    def Check_Board (self):                                                             # Will check both error conditions
        pass
        

    def Primary_Empty (self, SKU_Location):                                             # Checks for Nothing to be in Primary Bin (it is Empty)
        return self.SKU[SKU_Location][1] == "E"


    def Primary_Full (self, SKU_Location):                                              # Checks if Primary Bin is filled by Primary Bin
        return self.SKU[SKU_Location][1] == "P"

    
    def Primary_Is_Secondary (self, SKU_Location):                                      # Checks if Primary Bin is filled by a Secondary Bin
        return self.SKU[SKU_Location][1] == "S"


    def Secondary_Full (self, SKU_Location):                                            # Checks if Secondary Bin is filled by a Secondary Bin
        return self.SKU[SKU_Location][2] == "S"


    def Secondary_Empty (self, SKU_Location):                                           # Checks if Seconday Bin is Empty
        return self.SKU[SKU_Location][2] == "E"

## Functions That Gather Relevant Information

    def Avg_Time_Board (self):
        pass


    def Avg_Time_Virtual (self):
        pass


    def Avg_Num_Board (self):
        print (sum (self.Track_Board) * 1.0) / (len (self.Track_Board))


    def Avg_Num_Virtual (self):
        print (sum (self.Track_Virtual) * 1.0) / (len (self.Track_Virtual))

    


