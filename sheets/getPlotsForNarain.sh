#!/bin/bash

mkdir plots
cp sheets/sheet5.csv plots/
cd plots/
 
root -l -b -q ../scripts/analyse.C
#scp *.{C,png,html} ecoleman@lxplus.cern.ch:~/www/LPCSurveyPlots/
#scp *.{C,png,html} ecoleman@lxplus.cern.ch:~/www/LPCSurveyPlots/RunI
scp *.{C,png,html} ecoleman@lxplus.cern.ch:~/www/LPCSurveyPlots/RunII
