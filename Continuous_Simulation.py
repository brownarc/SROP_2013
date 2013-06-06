class Simulation (object):
    def __init__ (self, File_name):
        self.Bins = []
        self.Bins_Consumed = []
        self.Board = []
        self.Data = []
        self.File_name = File_name
        self.Inventory = []
        self.Track_Board = []
        self.Track_Virtual = []
        self.Virtual_Board = []
        self.Time = 0

        self.Extraction()


    def Add_To_Board (self, Bin, Spot):
        self.Board.append ([self.Bins[Bin][0]])
        if Spot == 1:
            self.Board [-1].append ("P")
        elif Spot == 2:
            self.Board [-1].append ("S")
        else:
            print "*****Error: Adding to Board Received Unexpected Results*****"


    def Add_To_Virtual (self, Bin):
        pass


    def Consumed_Bin (self):
        self.Time += 1
        
        for element in self.Bins_Consumed:
            self.Empty_Bin (element)
    
    def Empty_Bin (self, Emptied_Bin):                                                  # Configured by location of emptied bin in list
        if self.Primary_Full(Emptied_Bin):
            self.Bins[Emptied_Bin][1] = "S"
            self.Bins[Emptied_Bin][2] = "E"
            self.Add_To_Board (Emptied_Bin, 1)                                          # Need Lead Time Check

        elif self.Primary_Is_Secondary (Emptied_Bin):
            self.Bins[Emptied_Bin][1] = "E"
            self.Add_To_Board (Emptied_Bin, 2)                                          # Need Lead Time Check
            self.Stock_Out()
            self.Replenishment()                                                        # Out of supplies triggers replenishment

        elif self.Secondary_Full(Emptied_Bin):
            print "*****Error: Primary Emptied and Secondary Is Full*****"

        elif self.Primary_Empty(Emptied_Bin) and self.Secondary_Empty(Emptied_Bin):
            print "*****Error: Both Primary and Secondary Bin are Emptied.*****"


    def Extraction (self):
        import os
        
        File = open (self.File_name)
        File.readline()
        Raw_Data = File.readlines()
        File.close()

        for element in Raw_Data:
            element = element.split()
            self.Data.append ((element[0], element[1], element[2]))

        self.Initialize_Bins()

    def Initialize_Bins (self):
        for element in self.Data:
            self.Bins.append ([element[0], "P", "S"])
        for element in self.Bins:
            self.Inventory.append (element[0])


    def Lead_Time (self):
        pass
    

    def Replenishment (self):                                                           # Need to run more tests in this area
        self.Check_Board()

        for element in self.Board:
            location = self.Inventory.index (element[0])
            if element[1] == "P":                                                       # If Tag on Board is a Primary Bin
                if self.Primary_Is_Secondary(location):                                         # Check if Item is using Secondary Bin
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
                    print "*****Error: Secondary Bin Replenishment Problem*****"       # Need to revist logic
            else:
                print "*****Error: Received Invalid Input ('P', 'S', 'E')*****"

        self.Track_Board.append (len(self.Board))
        self.Board = []

        print "-Successful Replenishemnt- \n"
        

    def Stock_Out (self):
        pass

## Various Error Checking Functions      

    def Check_Board (self):                                                             #Will check both error conditions
        pass

        
    def Primary_Empty (self, Bin_Location):                                             #Checks for Nothing to be in Primary Bin (it is Empty)
        return self.Bins[Bin_Location][1] == "E"


    def Primary_Full (self, Bin_Location):                                              #Checks if Primary Bin is filled by Primary Bin
        return self.Bins[Bin_Location][1] == "P"

    
    def Primary_Is_Secondary (self, Bin_Location):                                      #Checks if Primary Bin is filled by a Secondary Bin
        return self.Bins[Bin_Location][1] == "S"


    def Secondary_Full (self, Bin_Location):                                            #Checks if Secondary Bin is filled by a Secondary Bin
        return self.Bins[Bin_Location][2] == "S"


    def Secondary_Empty (self, Bin_Location):                                           #Checks if Seconday Bin is Empty
        return self.Bins[Bin_Location][2] == "E"

## Functions That Gather Relevant Information

    def Avg_On_Board (self):
        pass


    def Avg_On_Virtual (self):
        pass


    def Avg_Num_Board (self):
        print (sum (self.Track_Board) * 1.0) / (len (self.Track_Board))


    def Avg_Num_Virtual (self):
        print (sum (self.Track_Virtual) * 1.0) / (len (self.Track_Virtual))

    
