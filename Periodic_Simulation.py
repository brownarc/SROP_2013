from scipy.stats import erlang

class Simulation (object):
    def __init__ (self, File_Name, Demand, Period, Kappa):
        self.SKU = []
        self.SKU_Consumed = []
        self.Cost_Per_Stockout = 0
        self.Board = []
        self.Data = []
        self.Demand = Demand
        self.File_Name = File_Name
        self.Fixed_Cost = 0
        self.Inventory = []
        self.Kappa = Kappa
        self.Lead_Finish = 0
        self.Lead_Time = [False, 4]
        self.Period = Period
        self.Track_Board = []
        self.Track_Virtual = []
        self.Virtual_Board = []
        self.Time = 0

        self.Extraction ()


    def Add_To_Board (self, SKU, Spot):
        self.Board.append ([self.SKUs[SKU][0]])
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


    def Consumed_SKU (self):
        print erlang (200, scale = 0.002778).rvs(200)
        

    def Cost_Per_Stockout_t (self):
        pass


    def Empty_SKU (self, Emptied_SKU):
        if self.Primary_Full(Emptied_SKU):
            self.SKUs[Emptied_SKU][1] = "S"
            self.SKUs[Emptied_SKU][2] = "E"
            if self.Lead_Time[0] == False:
                self.Add_To_Board (Emptied_SKU, 1)
            elif self.Lead_Time[0] == True:
                self.Add_To_Virtual (Emptied_SKU, 1)
            else:
                print "*****Unexpected Input For Lead_Time*****"

        elif self.Primary_Is_Secondary (Emptied_SKU):
            self.SKUs[Emptied_SKU][1] = "E"
            if self.Lead_Time[0] == True:
                self.Add_To_Board (Emptied_SKU, 2)                                      # Need Lead Time check
            elif self.Lead_Time[0] == False:
                self.Add_To_Virtual (Emptied_SKU, 2)
            else:
                print "*****Unexpected Input For Lead_Time*****"
                self.Stock_Out ()
                
        elif self.Secondary_Full(Emptied_SKU):
            print "*****Error: Primary Emptied and Secondary Is Full*****"

        elif self.Primary_Empty(Emptied_SKU) and self.Secondary_Empty(Emptied_SKU):
            print "*****Error: Both Primary and Secondary SKU are already empty.*****"

            
    def Extraction (self):        
        File = open (self.File_Name)
        File.readline()
        Raw_Data = File.readlines()
        File.close()

        for element in Raw_Data:
            element = element.split()
            self.Data.append ((element[0], element[1]))

        self.Initialize_SKU()

    def Initialize_SKU (self):
        for element in self.Data:
            self.SKU.append ([element[0], "P", "S"])
        for element in self.SKU:
            self.Inventory.append (element[0])

        self.Consumed_SKU()
    

    def Replenishment (self):                                                           # Need to run more tests in this area
        self.Check_Board()
        self.Fixed_Cost += self.Kappa

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

        print "-Successful Replenishemnt- \n"


    def Stock_Out (self):
        pass


    def Total_Cost (self):
        pass
