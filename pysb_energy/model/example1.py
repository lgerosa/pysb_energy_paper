import sympy as sp
import numpy as np

from pysb import (
    Model, Monomer, Parameter, Rule, EnergyPattern, Initial, Expression, Observable
)

#convers reaction kinetics (kon, koff) into the corresponding free energy (Gf)
#Formula: Gf/RT= -ln(koff/kon) 
def getGfRT(kon, koff):
    GfRT = sp.ln(koff)-sp.ln(kon);
    return GfRT

#converts reaction kinetics (kon, koff and phi) into the corresponding baseline activation energy (Ea0) 
#Formula: Ea0/RT= - RT * (phi ln(koff) + (1-phi) ln(kon))
#Alternative formula: Ea0/RT= - RT * ln(kon) - phi * Gf
def getEa0RT(kon, koff, phi):
    Ea0RT = - (phi * sp.ln(koff) + (1-phi) * sp.ln(kon));
    return Ea0RT

#converts thermodynamic factors into corresponding free energy modifier
#Formula: Gf/RT= ln(tf)
def getTGfRT(tf):
    tGfRT = sp.ln(tf);
    return tGfRT

Model()

#fundamental constants
#RT = 2.577 #temperature and gas constant product, kJ/mol
#NA=  6.022140857e23 #Avogadro's number , /mol
#V=  1**-12 #volume of cytoplasm, L
#T= 310 #temperature, K 

#R= 8.3144598 #gas constant, J/mol/K 
#RT = R * T  #temperature * gas constant, kJ/mol
#C= #Arrhenius constant or pre-exponential factor, number of collision for a reaction to happen (same ) 
#RTlogC= R*T*np.ln(C) #factor enmbedded in energies

#Monomer definition
Monomer('A', ['r']) #Ras-GTP
Monomer('R', ['a', 'r', 'i']) #RAF
Monomer('I', ['r']) #RAF inhibitor

#Kinetic parameters, koff /s/M, kon /s
Parameter('koff_RA', 10**-2) 
Parameter('kon_RA',10**-1) 
Parameter('koff_RR', 10**-1) 
Parameter('kon_RR', 10**-2) 
Parameter('koff_RI', 10**-1) 
Parameter('kon_RI', 10)
#Thermodynamic factors, no units
Parameter('h', 0.0001)
Parameter('f', 1)
Parameter('g', 1)
#Rate distribution parameter, no units
Parameter('phi', 0.5) 

#Standard free energy of formation, kJ/mol. 
Expression('Gf_RA', getGfRT(kon_RA,koff_RA))
Expression('Gf_RR', getGfRT(kon_RR,koff_RR)) 
Expression('Gf_RI', getGfRT(kon_RI,koff_RI)) 
Expression('h_Gf', getTGfRT(h)) 
Expression('f_Gf', getTGfRT(f))
Expression('g_Gf', getTGfRT(g))
#Baseline activation energy, kJ/mol. 
Expression('Ea0_RA', getEa0RT(kon_RA, koff_RA, phi)) 
Expression('Ea0_RR', getEa0RT(kon_RR, koff_RR, phi))
Expression('Ea0_RI', getEa0RT(kon_RI, koff_RI, phi))

#Ras-GTP and RAF binding
EnergyPattern('ep_RA', R(a=1) % A(r=1), Gf_RA)
EnergyPattern('ep_ARRA', A(r=1) % R(a=1, r=2) % R(r=2,a=3) % A(r=3), h_Gf)
#EnergyPattern('ep_ARR', A(r=1) % R(a=1, r=2) % R(r=2), h_Gf)
Rule('RA_binding', R(a=None) + A(r=None) | A(r=1) % R(a=1), phi, Ea0_RA, energy=True)
#RAF dimerization
EnergyPattern('ep_RR', R(r=1) % R(r=1), Gf_RR)
Rule('RR_binding', R(r=None) + R(r=None) | R(r=1) % R(r=1), phi, Ea0_RR, energy=True)
#RAF and RAFi binding
EnergyPattern('ep_RI', R(i=1) % I(r=1), Gf_RI)
EnergyPattern('ep_RRI',R(r=1, i=None) % R(r=1, i=2) % I(r=2), f_Gf)
EnergyPattern('ep_IRRI',I(r=3) % R(r=1, i=3) % R(r=1, i=2) % I(r=2), Expression('fg_G', f_Gf + g_Gf))
Rule('RAF_binds_RAFi', R(i=None) + I(r=None) | R(i=1) % I(r=1), phi, Ea0_RI, energy=True)

#Initial concentrations, mol/L
Parameter('A_0', 0.1) 
Parameter('R_0', 0.01) 
Parameter('I_0', 0) 

#Set initial concentrations
Initial(A(r=None), A_0) 
Initial(R(a=None, r=None, i=None), R_0) 
Initial(I(r=None), I_0)

#Observables (all possible R and I combination independent of A)
Observable('R_obs', R(r=None, i=None))    
Observable('I_obs', I(r=None))   
Observable('RR_obs', R(r=1, i=None) % R(r=1, i=None))   
Observable('RI_obs', R(r=None, i=1) % I(r=1))   
Observable('RRI_obs', R(r=1, i=None) % R(r=1,i=2) % I(r=2))   
Observable('IRRI_obs', I(r=2) % R(r=1, i=2) % R(r=1,i=3) % I(r=3))   
Observable('RA_obs', R(r=None, a=1) % A(r=1))   
Observable('RRA_obs', R(r=1, a=None) % R(r=1,a=2) % A(r=2))    
Observable('ARRA_obs', A(r=2) % R(r=1, a=2) % R(r=1,a=3) % A(r=3)) 
Observable('AIR_obs', A(r=2) % R(r=None, a=2, i=1) % I(r=1)) 

#not inhibited RAF promoter in dimer
Observable('RAF_active_dimer_obs', A(r=2) % R(r=1, i=None, a=2) % R(r=1))   
#not inhibited RAF monomers and promoter in dimer
Observable('RAF_active_monomer_and_dimer_obs', R(r=None, i=None) + A(r=2) % R(r=1, i=None, a=2) % R(r=1))  

