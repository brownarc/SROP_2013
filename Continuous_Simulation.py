class Simulation (object):
    def __init__ (self, File_Name, Demand):        
        self.Bins = []                                                                  # Gives all available bins along with P/S/E info
        self.Bins_Consumed = []                                                         # Let's user know which bins have been consumed and need to be Emptied
        self.Board = []                                                                 # Replenishment Board
        self.Cost = 0
        self.Data = []                                                                  # Extracted Data from user inputted file
        self.Demand = Demand                                                            # Allows user to input Demand
        self.File_Name = File_Name                                                      # File to attract data from
        self.Inventory = []                                                             # Inventory of all tracked data
        self.Kappa = 100
        self.Lead_Finish = 0
        self.Lead_Time = [False, 4]                                                     # Needs to toggle True/False and give Lead Time ************
        self.Need_Replenishment = False                                                 # Toggles True/False for needing replenishment
        self.Rho = 55
        self.Rho_Hat = 0.04
        self.Track_Board = []                                                           # Used for stat tracking of Board
        self.Track_Virtual = []                                                         # Used for stat tracking of Virtual Board
        self.Virtual_Board = []                                                         # Replenishment Virtual Board
        self.Time = 0                                                                   # Time for simulation

        self.Extraction()


    def Add_To_Board (self, Bin, Spot):                                                 # Spot says whether it is P or S
        self.Board.append ([self.Bins[Bin][0]])
        if Spot == 1:
            self.Board [-1].append ("P")
        elif Spot == 2:
            self.Board [-1].append ("S")
        else:
            print "*****Error: Adding to Board Received Unexpected Input*****"


    def Add_To_Virtual (self, Bin, Spot):
        self.Virtual_Board.append ([self.Bins[Bin][0]])
        if Spot == 1:
            self.Virtual_Board [-1].append ("P")
        elif Spot == 2:
            self.Virtual_Board [-1].append ("S")
        else:
            print "*****Error: Adding To Virtual Board Received Unexpected Input*****"


    def Consumed_Bin (self):                                                            # With, Item spot = I_N and Time put on board = T_N with N integer
        from scipy.stats import erlang
        
        self.Time = 1
        while self.Time <= 24:                                                          # Data will be of the form [[I_1,T_1], [I_2, T_2], ...]
            if self.Lead_Time[0] == True and self.Lead_Finish == self.Time:             # Function should have a while loop
                self.Lead_Time [0] = False
                for item in self.Virtual_Board:
                    self.Board.append (item)
                self.Track_Virtual.append (len (self.Virtual_Board))
                self.Virtual_Board = []
                
            Random_Variables = erlang.rvs (self.Demand, size = len (self.Bins))

            count = 0
            
            for element in Random_Variables:                                            # For loop will continue to give the same few numbers starting numbers, or pattern of numbers
                if element > self.Demand:
                    self.Bins_Consumed.append ([count, self.Time])                      # Function empties the next one (want to empty 43, will empty 44) <--- Fine item2 will come up as index 1
                    
                count += 1

            
            for element in self.Bins_Consumed:
                self.Empty_Bin (element[0])
                self.Bins_Consumed = []

            if self.Need_Replenishment:
                self.Replenishment()                                                    # Out of supplies triggers replenishment
                self.Lead_Time[0] = True                                                # ***********Still need to deactivate lead_time***********
                self.Lead_Finish = self.Time + self.Lead_Time[1]
            self.Time += 1


    def Cost (self, m, t):
        from scipy import stats

        self.Cost = self.Rho*((self.Demand*t)*stats.poisson.pmf(m-1,self.Demand*t) \
                              + (self.Demand*t-m+1)*     #upper tail (the P) 
    
    def Empty_Bin (self, Emptied_Bin):                                                  # Configured by location of emptied bin in list
        if self.Primary_Full(Emptied_Bin):
            self.Bins[Emptied_Bin][1] = "S"
            self.Bins[Emptied_Bin][2] = "E"
            if self.Lead_Time[0] == False:
                self.Add_To_Board (Emptied_Bin, 1)
            elif self.Lead_Time[0] == True:
                self.Add_To_Virtual (Emptied_Bin, 1)
            else:
                print "*****Unexpected Input For Lead_Time*****"

        elif self.Primary_Is_Secondary (Emptied_Bin):
            self.Bins[Emptied_Bin][1] = "E"
            if self.Lead_Time[0] == True:
                self.Add_To_Board (Emptied_Bin, 2)                                      # Need Lead Time check
            elif self.Lead_Time[0] == False:
                self.Add_To_Virtual (Emptied_Bin, 2)
            else:
                print "*****Unexpected Input For Lead_Time*****"
                
            self.Stock_Out()
            self.Need_Replenishment = True

        elif self.Secondary_Full(Emptied_Bin):
            print "*****Error: Primary Emptied and Secondary Is Full*****"

        elif self.Primary_Empty(Emptied_Bin) and self.Secondary_Empty(Emptied_Bin):
            print "*****Error: Both Primary and Secondary Bin are already empty.*****"
            

    def Extraction (self):        
        File = open (self.File_Name)
        File.readline()
        Raw_Data = File.readlines()
        File.close()

        for element in Raw_Data:
            element = element.split()
            self.Data.append ((element[0], element[1]))

        self.Initialize_Bins()

    def Initialize_Bins (self):
        for element in self.Data:
            self.Bins.append ([element[0], "P", "S"])
        for element in self.Bins:
            self.Inventory.append (element[0])

        self.Consumed_Bin()
    

    def Replenishment (self):                                                           # Need to run more tests in this area
        self.Check_Board()

        for element in self.Board:
            location = self.Inventory.index (element[0])
            if element[1] == "P":                                                       # If Tag on Board is a Primary Bin
                if self.Primary_Is_Secondary(location):                                 # Check if Item is using Secondary Bin
                    self.Bins[location][2] = "S"                                        # If yes, Replenished Bin should become Secondary and Primary should be named properly
                    self.Bins[location][1] = "P"
                elif self.Primary_Empty(location):
                    self.Bins[location][1] = "P"
                else:
                    print "*****Error: Expected Primary Bin", str(self.Bins[location][0]), "To Be Empty or Full (By Secondary)*****"
            elif element[1] == "S":
                if self.Primary_Full (location) and self.Secondary_Empty(location):     # Primary Bin should be Replenished first
                    self.Bins[location][2] = "S"

                else:
                    print "*****Error: Secondary Bin Replenishment Problem*****"        # Need to revist logic
                    self.Bins[location][2] = "S"
            else:
                print "*****Error: Received Invalid Input ('P', 'S', 'E')*****"

        self.Track_Board.append (len(self.Board))
        self.Board = []
        self.Need_Replenishment = False

        print "-Successful Replenishemnt- \n"
        

    def Stock_Out (self):
        pass

## Various Error Checking Functions      

    def Check_Board (self):                                                             # Will check both error conditions
        pass


    def Primary_Empty (self, Bin_Location):                                             # Checks for Nothing to be in Primary Bin (it is Empty)
        return self.Bins[Bin_Location][1] == "E"


    def Primary_Full (self, Bin_Location):                                              # Checks if Primary Bin is filled by Primary Bin
        return self.Bins[Bin_Location][1] == "P"

    
    def Primary_Is_Secondary (self, Bin_Location):                                      # Checks if Primary Bin is filled by a Secondary Bin
        return self.Bins[Bin_Location][1] == "S"


    def Secondary_Full (self, Bin_Location):                                            # Checks if Secondary Bin is filled by a Secondary Bin
        return self.Bins[Bin_Location][2] == "S"


    def Secondary_Empty (self, Bin_Location):                                           # Checks if Seconday Bin is Empty
        return self.Bins[Bin_Location][2] == "E"

## Functions That Gather Relevant Information

    def Avg_Time_Board (self):
        pass


    def Avg_Time_Virtual (self):
        pass


    def Avg_Num_Board (self):
        print (sum (self.Track_Board) * 1.0) / (len (self.Track_Board))


    def Avg_Num_Virtual (self):
        print (sum (self.Track_Virtual) * 1.0) / (len (self.Track_Virtual))

    
