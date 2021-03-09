#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 28 19:33:18 2020

@author: si_sutantawibul1
"""

import uproot
import pandas as pd
from analib import PhysObj, Event
import sys
import os
import pickle
import numpy as np
from dataManager import getSubJetData, getnSVCounts
from htoaaRootFilesLoc import TTJetsPaths, WJetsPaths, bEnrPaths, BGenPaths
from htoaaRootFilesLoc import ZJetsPaths, ParkedDataPaths, JetHTPaths, ggHPaths, MuonEGPaths
#import htoaaRootFilesLoc

#JetHT = False

#exec(open("./htoaaRootFilesLoc.py").read())


BGenWeight = [1, 0.259, 0.0515, 0.01666, 0.00905, 0.003594, 0.001401]
bEnrWeight =[ 1.0, 0.33, 0.034, 0.034, 0.024, 0.0024, 0.00044]
ZJetsWeight = [ 145400. / 16704355, 34000. / 14642701, 18670. / 10561192]
WJetsWeight = [315600. / 10071273, 68570./ 15298056, 34900. / 14627242]
TJetsWeight = [831760.0 / 10244307]
ParkedDataWeight = [7.1055]

BGenDict = dict(zip(BGenPaths, BGenWeight))
bEnrDict = dict(zip(bEnrPaths, bEnrWeight))
ZJetsDict = dict(zip(ZJetsPaths, ZJetsWeight))
WJetsDict = dict(zip(WJetsPaths, WJetsWeight))
TTJetsDict = dict(zip(TTJetsPaths, TJetsWeight))
ParkedDataDict = dict(zip(ParkedDataPaths, ParkedDataWeight))



jetVars = ['FatJet_pt',
           'FatJet_eta',
           'FatJet_mass',
           'FatJet_msoftdrop',
           'FatJet_btagCSVV2',
           'FatJet_btagDeepB',
           'FatJet_msoftdrop',
           'FatJet_btagDDBvL',
           'FatJet_deepTagMD_H4qvsQCD',
           'FatJet_n2b1',
           'SubJet_mass(1)',
           'SubJet_mass(2)',
           'SubJet_tau1(1)',
           'FatJet_n3b1',
           'FatJet_tau2',
           'FatJet_tau2',
           'SubJet_n2b1(1)',
           'SubJet_pt(1)|FatJet_pt',
           'SubJet_pt(2)|FatJet_pt',
           'SubJet_btagDeepB(2)',
           'SubJet_tau1(2)',
           'FatJet_nSV']

muonVars = ['Muon_pt',
            'Muon_eta',
            'Muon_ip3d',
            'Muon_softId']

PVVars = ['PV_npvs', 'PV_npvsGood']

allVars = list(jetVars + muonVars + PVVars + ['LHE_HT'])
allVars.sort()


muonR = pickle.load(open('muontensor/MuonRtensor.p', 'rb'))
muonL = pickle.load(open('muontensor/MuonLtensor.p', 'rb'))




#ptkeys = list(muonL.keys()) + [999999]
ptkeys = list(muonL.keys())
ptkeys.append(999999)
ptkeys.remove('meta')

#ipkeys = list(muonL[ptkeys[0]].keys()) + [999999]
ipkeys = list(muonL[ptkeys[0]].keys())
ipkeys.append(999999)

npvsGkeys = muonR[6][2]['H']

tagslist = ['bEnr', 'BGen', 'data', 'JetHT', 'WJets', 'TTJets', 'ZJets', 'ggH', 'MuonEG']
dataSetList = ['Base', 'Parked', 'JetHT', 'MuonEG']

def getMaxPt(physobj, col):
    colidx = physobj[col].idxmax(axis=1).to_numpy()
    rowidx = list(range(len(colidx)))
    maxPtData = pd.DataFrame()

    for var in physobj.keys():
        npArr = physobj[var].to_numpy()
        maxPtData[var] = npArr[rowidx, colidx]
    return maxPtData

## I don't have the getSubjetData here becuase i imported the dataManager one because yeah




## filePath: (str) path to root file to process
## tag: (str) what dataset the root file is (BGen, GGH..) check list of valid tags
## dataset: (str) what kind of cuts you want to be making. check list of valid datasets
## MC: (bool) is this file MC or not
## trigger: (bool) on for have trigger info in the resulting dataframe
def processData (filePath, tag, dataSet, MC, trigger): #JetHT=False):
    ## open file, get events
    fileName, fileExtension = os.path.splitext(filePath)

    print(filePath)

    if fileExtension != '.root':
        print('this program only supports .root  files')
        sys.exit()

    if tag not in tagslist:
        print('check yo tags')
        sys.exit()

    if dataSet not in dataSetList:
        print('check dataset')
        sys.exit()

    if type(MC) != bool:
        print('MC needs to be set true/false')
        sys.exit()

    if type(trigger) != bool:
        print('trigger needs to be set true/false')
        sys.exit()

    f = uproot.open(fileName + '.root')
    events = f.get('Events')

    jets = PhysObj('jets' + fileName)
    muons = PhysObj('muons' + fileName)
    other = PhysObj('other' + fileName)
    trig = PhysObj('trig' + fileName)
    electrons = PhysObj('electrons'+fileName)

    ## data doens't have LHE_HT
    if tag == 'data' and 'LHE_HT' in allVars:
        allVars.remove('LHE_HT')

    ## fill the PhysObjs with data from the root file
    ## fatjets vars
    jets['FatJet_pt'] = pd.DataFrame(events.array('FatJet_pt'))
    jets['FatJet_eta'] = pd.DataFrame(np.abs(events.array('FatJet_eta')))
    jets['FatJet_mass'] = pd.DataFrame(events.array('FatJet_mass'))
    jets['FatJet_btagCSVV2'] = pd.DataFrame(events.array('FatJet_btagCSVV2'))
    jets['FatJet_btagDeepB'] = pd.DataFrame(events.array('FatJet_btagDeepB'))
    jets['FatJet_msoftdrop'] = pd.DataFrame(events.array('FatJet_msoftdrop'))
    jets['FatJet_btagDDBvL'] = pd.DataFrame(events.array('FatJet_btagDDBvL'))
    jets['FatJet_deepTagMD_H4qvsQCD'] = pd.DataFrame(events.array('FatJet_deepTagMD_H4qvsQCD'))
    jets['FatJet_n2b1'] = pd.DataFrame(events.array('FatJet_n2b1'))
    # jets['SubJet_mass(1)'] = getSubJetData(1,'SubJet_mass', events)
    # jets['SubJet_mass(2)'] = getSubJetData(2, 'SubJet_mass', events)
    # jets['SubJet_tau1(1)'] = getSubJetData(1, 'SubJet_tau1', events)
    # jets['FatJet_n3b1'] = pd.DataFrame(events.array('FatJet_n3b1'))
    # jets['FatJet_tau2'] = pd.DataFrame(events.array('FatJet_tau2'))
    # jets['SubJet_n2b1(1)'] = getSubJetData(1, 'SubJet_n2b1', events)
    # jets['SubJet_pt(1)|FatJet_pt'] = getSubJetData(1, 'SubJet_pt', events)/jets.FatJet_pt
    # jets['SubJet_pt(2)|FatJet_pt'] = getSubJetData(2, 'SubJet_pt', events)/jets.FatJet_pt
    # jets['SubJet_btagDeepB(2)'] = getSubJetData(2, 'SubJet_btagDeepB', events)
    # jets['SubJet_tau1(2)'] = getSubJetData(2, 'SubJet_tau1', events)

    ## JetHT triggers
    ## add them all up, so passing at least one is just see if event has trig > 0
    '''if JetHT:
        trig1 = events.array('HLT_AK8PFJet500')
        trig2 = events.array('HLT_AK8PFJet330_TrimMass30_PFAK8BoostedDoubleB_np4')
        trig3 = events.array('HLT_DoublePFJets116MaxDeta1p6_DoubleCaloBTagDeepCSV_p71')
        trig4 = events.array('HLT_PFHT330PT30_QuadPFJet_75_60_45_40_TriplePFBTagDeepCSV_4p5')
        other['HLT_trigger'] = pd.DataFrame(trig1+trig2+trig3+trig4)'''

    ## muons
    if 'Parked'==dataSet:
        muons['Muon_pt'] = pd.DataFrame(events.array('Muon_pt'))
        muons['Muon_eta'] = pd.DataFrame(np.abs(events.array('Muon_eta')))
        muons['Muon_ip3d'] = pd.DataFrame(events.array('Muon_ip3d'))
        muons['Muon_softId'] = pd.DataFrame(events.array('Muon_softId')).fillna(0).astype(int)
        muons['Muon_IP'] = pd.DataFrame(events.array('Muon_dxy')/events.array('Muon_dxyErr')).abs()

    #-------------- Jet HT Trigger efficiency vals ---------------------------

    #L1_SingleJet180 and HLT_AK8PFJet500
    if trigger:
        trig['L1_SingleJet180'] = pd.DataFrame(events.array('L1_SingleJet180')).fillna(0)
        trig['HLT_AK8PFJet500'] = pd.DataFrame(events.array('HLT_AK8PFJet500')).fillna(0)
    #-------------------------------------------------------------------------

    #--------------- Calculate MuonEG pass triggers --------------------------
    ## each event must pass one of the trigger combinations,
    ## first two combinations is such that it passes one of two L1 trigger
    ## and must pass the HLT, so it is calculated as L1+L1*HLT
    ## then triggers are added together and what is > 0 is true
    ## this is safe to do becuase the array is 1 col, and no nan/None
    if 'MuonEG'==dataSet:
        trig1 = (events.array('L1_Mu7_EG23er2p5')
                 +events.array('L1_Mu7_LooseIsoEG20er2p5')
                 *events.array('HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ'))
        trig2 = (events.array('L1_Mu20_EG10er2p5')
                 +events.array('L1_SingleMu22')
                 *events.array('HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL'))
        trig3 = (events.array('L1_SingleMu25')
                 *events.array('HLT_Mu27_Ele37_CaloIdL_MW'))
        trig4 = (events.array('L1_SingleMu25')
                 *events.array('HLT_Mu37_Ele27_CaloIdL_MW'))
        trig['MuonEGTriggers'] = pd.DataFrame(trig1+trig2+trig3+trig4)

        muons['Muon_pt'] = pd.DataFrame(events.array('Muon_pt'))
        muons['Muon_eta'] = pd.DataFrame(events.array('Muon_eta')).abs()
        muons['Muon_mediumPromptId'] = pd.DataFrame(events.array('Muon_mediumPromptId')).fillna(0).astype(int)
        muons['Muon_miniIsoId'] = pd.DataFrame(events.array('Muon_miniIsoId'))

        electrons['Electron_pt'] = pd.DataFrame(events.array('Electron_pt'))
        electrons['Electron_eta'] = pd.DataFrame(events.array('Electron_eta')).abs()
        electrons['Electron_mvaFall17V2Iso_WP90'] = pd.DataFrame(events.array('Electron_mvaFall17V2Iso_WP90')).fillna(0).astype(int)

    #-----------------------------------------------------------------------

    ## other vars
    if MC:
        other['LHE_HT'] = pd.DataFrame(events.array('LHE_HT')).astype(np.float64)
    other['PV_npvs'] = pd.DataFrame(events.array('PV_npvs'))
    other['PV_npvsGood'] = pd.DataFrame(events.array('PV_npvsGood'))

    ## make Event object
    ev = Event(jets, muons, other, trig, electrons)


    ## cutting events
    ## jet cuts
    jets.cut(jets['FatJet_pt'] > 170)
    jets.cut(jets['FatJet_eta'] < 2.4)
    jets.cut(jets['FatJet_btagDDBvL'] > 0.8)
    jets.cut(jets['FatJet_btagDeepB'] > 0.4184)
    jets.cut(jets['FatJet_msoftdrop'] > 90)
    jets.cut(jets['FatJet_msoftdrop'] < 200)#<= 200)
    jets.cut(jets['FatJet_mass'] > 90)
    #jets.cut(jets['FatJet_mass'] <= 200)
    other.cut(other['PV_npvsGood'] >= 1)


    ## muon cuts
    if 'Parked'==dataSet:
        muons.cut((muons['Muon_softId'] > 0))
        muons.cut(muons['Muon_eta'] < 2.4)
        muons.cut(muons['Muon_pt'] > 7)
        muons.cut(muons['Muon_IP'] > 2)
        muons.cut(muons['Muon_ip3d'] < 0.5)
    if 'JetHT'==dataSet:
        other.cut(other['HLT_trigger'] > 0)

    ## include or exclude triggers for trigger efficiency study for JetHT
    '''if trigger:
        print('in trig')
        trig.cut(trig['L1_SingleJet180'] == True)
        trig.cut(trig['HLT_AK8PFJet500'] == True)'''

    if 'MuonEG'==dataSet:
        trig.cut(trig['MuonEGTriggers'] == True)
        electrons.cut(electrons['Electron_pt'] > 25)
        electrons.cut(electrons['Electron_eta'] < 2.5)
        electrons.cut(electrons['Electron_mvaFall17V2Iso_WP90'] == 1)
        muons.cut(muons['Muon_pt'] > 10)
        muons.cut(muons['Muon_eta'] < 2.4)
        muons.cut(muons['Muon_mediumPromptId'] == 1)
        muons.cut(muons['Muon_miniIsoId'] >= 2)

    ## sync so all events cut to same events after apply individual cuts
    ev.sync()
    pickle.dump(ev.frame, open('JetHTTrigEff/frames/frame.pkl', 'wb'))


    ## rename the columns of LHE_HT, PV_npvs, PV_npvsGood to match the ones that get
    ## passed into getMaxPt
    if MC:
        other.LHE_HT = other.LHE_HT.rename({0:'LHE_HT'}, axis='columns')
    other.PV_npvs = other.PV_npvs.rename({0:'PV_npvs'}, axis='columns')
    other.PV_npvsGood =other.PV_npvsGood.rename({0:'PV_npvsGood'}, axis='columns')

    #other.Generator_weight = other.Generator_weight.rename({0:'Generator_weight'}, axis='columns')

    ## if nothing's left after cut, return empty dataframe
    if (jets.FatJet_pt.empty):
       return pd.DataFrame()

    else:
        maxPtJets = getMaxPt(jets, 'FatJet_pt')#.reindex(jets.FatJet_pt.index)
        if ('JetHT'==dataSet) or ('Base'==dataSet):
            maxPtData = maxPtJets
        if 'Parked'==dataSet:
            maxPtMuons = getMaxPt(muons, 'Muon_pt')#.reindex(muons.Muon_pt.index)
            maxPtData = pd.concat([maxPtJets, maxPtMuons], axis=1)
        if 'MuonEG'==dataSet:
            maxPtMuons = getMaxPt(muons, 'Muon_pt')
            maxPtElectrons = getMaxPt(electrons, 'Electron_pt')
            maxPtData = pd.concat([maxPtJets, maxPtMuons, maxPtElectrons],
                                  axis=1)

        maxPtData = maxPtData.assign(PV_npvs=other.PV_npvs.to_numpy())
        maxPtData = maxPtData.assign(PV_npvsGood=other.PV_npvsGood.to_numpy())
        if trigger:
            maxPtData = maxPtData.assign(L1_SingleJet180=trig['L1_SingleJet180'].to_numpy().flatten())
            maxPtData = maxPtData.assign(HLT_AK8PFJet500=trig['HLT_AK8PFJet500'].to_numpy().flatten())


        #----- MuonEG only pass events w/ electron pt or muon pt > 25 -----
        if 'MuonEG'==dataSet:
            maxPtData = maxPtData[(maxPtData['Electron_pt'] > 25) |
                                  (maxPtData['Muon_pt'] > 25)]

        #------------------------------------------------------------------


        if MC:
            maxPtData = maxPtData.assign(LHE_HT=other.LHE_HT.to_numpy())

        ## LHE_weights
        if 'ggH'==tag:
             maxPtData['LHE_weights'] = 0.0046788#1
             wgt = 3.9 - 0.4*np.log2(maxPtData.FatJet_pt)
             wgt[wgt<0.1] = 0.1
             maxPtData['ggH_weights'] = wgt

             maxPtData['final_weights'] = (maxPtData['LHE_weights'] *
                                           maxPtData['ggH_weights'])

        elif 'BGen'==tag:
            maxPtData['LHE_weights'] = BGenDict[filePath]

            wgt = 4.346 - 0.356*np.log2(maxPtData.LHE_HT)
            wgt[wgt<0.1] = 0.1
            maxPtData['QCD_correction'] = wgt
            Xsec_wgt = 21.56

            maxPtData = maxPtData.assign(final_weights =
                                         maxPtData['LHE_weights']*
                                         maxPtData['QCD_correction']*
                                         Xsec_wgt)


        elif 'bEnr'==tag:
            maxPtData['LHE_weights'] = bEnrDict[filePath]

            wgt = 4.346 - 0.356*np.log2(maxPtData.LHE_HT)
            wgt[wgt<0.1] = 0.1
            maxPtData['QCD_correction'] = wgt
            Xsec_wgt = 8.2

            maxPtData = maxPtData.assign(final_weights=
                                         maxPtData['LHE_weights']*
                                         maxPtData['QCD_correction']*
                                         Xsec_wgt)


        elif 'WJets'==tag:
            maxPtData['LHE_weights'] = WJetsDict[filePath]
            maxPtData = maxPtData.assign(final_weights = maxPtData['LHE_weights'])


        elif 'ZJets'==tag:
            maxPtData['LHE_weights'] = ZJetsDict[filePath]
            maxPtData = maxPtData.assign(final_weights = maxPtData['LHE_weights'])


        elif 'TTJets'==tag:
            maxPtData['LHE_weights'] = TTJetsDict[filePath]
            maxPtData = maxPtData.assign(final_weights=maxPtData['LHE_weights'])



        if 'Parked'==dataSet and 'data'!=tag and 'ggH'!=tag: #not JetHT and tag != 'ggH' and tag!='data':
            ## npvs Ratio (PU) weights
            for i in range(len(ptkeys)-1):
                for j in range(len(ipkeys)-1):
                    for k in range(len(npvsGkeys)):
                        ## for places where npvs good is in range
                        maxPtData.loc[(maxPtData.Muon_pt >= ptkeys[i]) &
                                      (maxPtData.Muon_pt < ptkeys[i+1]) &
                                      (maxPtData.Muon_IP >= ipkeys[j]) &
                                      (maxPtData.Muon_IP < ipkeys[j+1]) &
                                      (maxPtData.Muon_eta < 1.5) &
                                      (maxPtData.PV_npvsGood == k+1),
                                      'PU_weights'] = muonR[ptkeys[i]][ipkeys[j]]['L'][k]
                        maxPtData.loc[(maxPtData.Muon_pt >= ptkeys[i]) &
                                      (maxPtData.Muon_pt < ptkeys[i+1]) &
                                      (maxPtData.Muon_IP >= ipkeys[j]) &
                                      (maxPtData.Muon_IP < ipkeys[j +1]) &
                                      (maxPtData.Muon_eta >= 1.5) &
                                      (maxPtData.PV_npvsGood == k+1),
                                      'PU_weights'] = muonR[ptkeys[i]][ipkeys[j]]['H'][k]
                        ## for places npvs good is out of range
                        maxPtData.loc[(maxPtData.Muon_pt >= ptkeys[i]) &
                                      (maxPtData.Muon_pt < ptkeys[i+1]) &
                                      (maxPtData.Muon_IP >= ipkeys[j]) &
                                      (maxPtData.Muon_IP < ipkeys[j+1]) &
                                      (maxPtData.Muon_eta < 1.5) &
                                      (maxPtData.PV_npvsGood > len(npvsGkeys)),
                                      'PU_weights'] = muonR[ptkeys[i]][ipkeys[j]]['L'][k]
                        maxPtData.loc[(maxPtData.Muon_pt >= ptkeys[i]) &
                                      (maxPtData.Muon_pt < ptkeys[i+1]) &
                                      (maxPtData.Muon_IP >= ipkeys[j]) &
                                      (maxPtData.Muon_IP < ipkeys[j +1]) &
                                      (maxPtData.Muon_eta >= 1.5) &
                                      (maxPtData.PV_npvsGood > len(npvsGkeys)),
                                      'PU_weights'] = muonR[ptkeys[i]][ipkeys[j]]['H'][k]

            # lumi weights
            for i in range(len(ptkeys)-1):
                for j in range(len(ipkeys)-1):
                    maxPtData.loc[(maxPtData.Muon_pt >= ptkeys[i]) &
                                  (maxPtData.Muon_pt < ptkeys[i+1]) &
                                  (maxPtData.Muon_IP >= ipkeys[j]) &
                                  (maxPtData.Muon_IP < ipkeys[j+1]) &
                                  (maxPtData.Muon_eta < 1.5),
                                  'lumi_weights'] = muonL[ptkeys[i]][ipkeys[j]]['L']
                    maxPtData.loc[(maxPtData.Muon_pt >= ptkeys[i]) &
                                  (maxPtData.Muon_pt < ptkeys[i+1]) &
                                  (maxPtData.Muon_IP >= ipkeys[j]) &
                                  (maxPtData.Muon_IP  < ipkeys[j +1]) &
                                  (maxPtData.Muon_eta >= 1.5),
                                  'lumi_weights'] = muonL[ptkeys[i]][ipkeys[j]]['H']


            ### !!! add this to the datamanager fixed too
            ## no do not add this.
            #maxPtData.PU_weights.fillna(1, inplace=True)
            #maxPtData.lumi_weights.fillna(1, inplace=True)



            maxPtData = maxPtData.assign(final_weights =
                                         maxPtData['lumi_weights']*
                                         maxPtData['PU_weights']*
                                         maxPtData['final_weights'])


        if tag == 'data':
            maxPtData['final_weights'] = ParkedDataDict[filePath]

    maxPtData['FatJet_nSV'] = getnSVCounts(jets, events)

    maxPtData = maxPtData.dropna(how='all')
    #maxPtData = maxPtData.fillna(0)

    return maxPtData



