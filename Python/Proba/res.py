import ROOT
from ROOT import gROOT, TCanvas, TF1, TPad, TH1I, TLegend
from ROOT import TH2F
import numpy as np
#from matplotlib import pyplot as plt
import time 
import progressbar
from time import sleep 

channels = -1.
fine1 = -1
fine2 = -1
coarse = -1.
rising = -1.
diff = int()

fineAll = [-1]

f = ROOT.TFile.Open("dabc_[18201172953].root")
myTree = f.Get("FTAB_Timeslots")
Nentries = myTree.GetEntries()
#Nentries = 100000
bar = progressbar.ProgressBar(maxval=Nentries, widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
barIter=0
bar.start()

#for ch_indx in range (0,40):
respad = TH1I( 'pad2', 'Res', 510, -255, 255 )
barIter=0
#print "ChIndx:", ch_indx
for entry in myTree:
    if barIter == 1000:#Nentries:#10000:
        break
    barIter = barIter + 1
    bar.update(barIter)
    # Now you have acess to the leaves/branches of each entry in the tree, e.g.
    
    for idx, val in enumerate(myTree.FTAB_Fine):  
        #print "idx ", idx, "val", val      
        #print "coarse",  myTree.FTAB_Coarse[idx]        
        #print "fine",  myTree.FTAB_Fine[idx]
        #print "channel",  myTree.FTAB_Channel[idx]
        #print "rising",  myTree.FTAB_Rising[idx]
        if myTree.FTAB_Channel[idx] == 92 and myTree.FTAB_Rising[idx] == 0:
            fine1 = myTree.FTAB_Fine[idx]+myTree.FTAB_Coarse[idx]*128            
        if myTree.FTAB_Channel[idx] == 100 and myTree.FTAB_Rising[idx] == 0:
            fine2 = myTree.FTAB_Fine[idx]+myTree.FTAB_Coarse[idx]*128             
        #print "fine1aa", fine1
        #print "fine2aa", fine2
        #time.sleep(0.1)
                    
    if fine1 != -1 and fine2 != -1:
        #diff = fine1 - fine2
        #print "fine1", fine1
        #print "fine2", fine2
        #print "res", diff
        respad.Fill(diff)
        
    
#fine1 = -1
#fine2 = -1
    
c1 = TCanvas( 'c1', 'Histogram Drawing Options', 200, 10, 700, 900 )
respad.Draw()

a=respad.Fit("gaus")
time.sleep(200)
respad.Delete()
#leg = TLegend( 0.15, 0.70, 0.38, 0.85 )
#leg.SetFillColor(kWhite)
#leg.SetLineColor(kWhite)
#leg.AddEntry(Hist_x, " Gaussian (#mu = -0.5)", "L")
#leg.AddEntry(fit_x, " Fit with Gaussian to x", "L")
#leg.AddEntry(Hist_y, " Gaussian (#mu = +0.5)", "L")
#leg.Draw()
    #print fine
    #for fine_del in fine:
    #    np.delete(fine,(0))
