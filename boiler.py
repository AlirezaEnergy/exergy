import pyromat as pm
from pprint import pprint

"""
print(pm.config) shows currently using units

for help on enthalpy for nitrogen -> help(N2.h)

list of all units:
    
          force : lb lbf kN N oz kgf 
         energy : BTU kJ J cal eV kcal BTU_ISO 
    temperature : K R eV C F 
       pressure : mmHg psi inHg MPa inH2O kPa Pa bar atm GPa torr mmH2O ksi 
          molar : Ncum NL Nm3 kmol scf n mol sci Ncc lbmol 
         volume : cumm cc mL L mm3 in3 gal UKgal cuin ft3 cuft USgal m3 cum 
         length : ft nm cm mm m km um mile in 
           mass : mg kg g oz lb lbm slug 
           time : s ms min hr ns year day us 
"""

pm.config['unit_pressure'] = 'kPa'
pm.config['unit_temperature'] = 'C'

#%% environmet (dead state for exergy analysis)
T0 = 25           # environment tempreture (C)
p0 = 100          # environment pressure   (kPa)

#%% Boiler

def BOILER(p_outlet,T_inlet,p_inlet,working_fluid,T_outlet,eff=1,T0=25,p0=100,saturated_outlet = True):
    """
    inputs: T_outlet:         outlet temperature       (C)        continuous variable
            p_outlet:         outlet pressure          (kPa)      continuous variable
            T_inlet:          inlet temperature        (C)        continuous variable
            p_inlet:          inlet pressure           (kPa)      continuous variable
            working_fluid:    working fluid name       (string)   base on pyromat
            eff:              thermal efficiency       (-)        [0,1]
            T0:               environment temperature  (C)        continuous number
            p0:               environment pressure     (kPa)      continuous number
            saturated_outlet: True:saturated False:o.w (bool)
    
    T_outlet is ignored if saturated_outlet = True.
    if the outlet is saturated then the cycle is ideal.
    assumes that the inlet is subcold water.
    """
    
    work_fluid = pm.get(working_fluid)
    
    h0 = work_fluid.h(T = T0, p = p0)                         # kJ/kg
    s0 = work_fluid.s(T = T0, p = p0)                         # kJ/kg.C
    
    h_inlet  = work_fluid.h(p = p_inlet, T = T_inlet)         # kJ/kg
    s_inlet  = work_fluid.s(p = p_inlet, T = T_inlet)         # kJ/kg.C
    ex_inlet = (h_inlet - h0) - (T0 + 273.15)*(s_inlet - s0)  # kJ/kg
    
    if saturated_outlet:
            
        h_outlet = work_fluid.hs(p = p_outlet)[1] #the result is a list in which [0] is saturated liquid and [1] is saturated vapor
        s_outlet = work_fluid.ss(p = p_outlet)[1]
        T_outlet = work_fluid.T_s(s = s_outlet, p = p_outlet)[0]
        ex_outlet = (h_outlet - h0) - (T0 + 273.15)*(s_outlet - s0)
        
        qh_ideal  = h_outlet - h_inlet
        qh_actual = qh_ideal / eff
        heat_loss = qh_actual - qh_ideal
        
    else:
        h_outlet = work_fluid.h(p = p_outlet, T = T_outlet)
        s_outlet = work_fluid.s(p = p_outlet, T = T_outlet)
        ex_outlet = (h_outlet - h0) - (T0 + 273.15)*(s_outlet - s0)
        
        qh_ideal  = h_outlet - h_inlet
        qh_actual = qh_ideal / eff
        heat_loss = qh_actual - qh_ideal
        
    exp_boiler = ex_outlet - ex_inlet                        # product exergy
    exf_boiler = qh_actual*(1-(T0+273.15)/(T_outlet+273.15)) # feed exergy
    exDL_boiler = exf_boiler - exp_boiler                    # exergy destruction and loss
    exL = heat_loss*(1-(T0+273.15)/(T_outlet+273.15))        # exergy loss
    exD = exDL_boiler - exL                                  # exergy destruction
    s_gen = exD / (T0+273.15)                                # entropy generation
    
    eps_boiler = exp_boiler / exf_boiler                     # boiler exergy efficiency
    
    res = {'p_inlet':p_inlet, 'h_inlet':h_inlet[0], 's_inlet':s_inlet[0], 'T_inlet':T_inlet, 'ex_inlet':ex_inlet[0],
           'p_outlet':p_outlet, 'h_outlet':h_outlet[0], 's_outlet':s_outlet[0], 'T_outlet':T_outlet, 'ex_outlet':ex_outlet[0],
           'exf':exf_boiler[0],'exp':exp_boiler[0],'exLD':exDL_boiler[0], 'exL':exL[0], 'exD':exD[0],'eps':eps_boiler[0],
           'sgen':s_gen[0],'qh_actual':qh_actual[0], 'qh_ideal': qh_ideal[0]}
    
    return res

#%% testing the function
working_fluid = 'mp.H2O'
p_outlet = 2000  # kPa
p_inlet = 2000   # kPa (note that p_inlet == p_outlet so there is no pressure loss in the boiler)
T_inlet = 45     # C

boiler = BOILER(p_outlet,T_inlet,p_inlet,working_fluid,T_outlet=300,eff=0.9,T0=25,p0=100,saturated_outlet = False)

decimals = 2
boiler = {key : round(boiler[key], decimals) for key in boiler}

pprint(boiler)





