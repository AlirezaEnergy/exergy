import pyromat as pm
from pprint import pprint
"""
print(pm.config) # currently using units

for help on enthalpy -> help(N2.h)

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

#%% Condenser

def CONDENSER(p_inlet,x_inlet,p_outlet,T_outlet,working_fluid,saturated_outlet=True,T0=25,p0=100):
    """
    T_outlet:   T_outlet:         outlet temperature       (C)        continuous variable
                p_outlet:         outlet pressure          (kPa)      continuous variable
                T_inlet:          inlet temperature        (C)        continuous variable
                p_inlet:          inlet pressure           (kPa)      continuous variable
                working_fluid:    working fluid name       (string)   base on pyromat
                T0:               environment temperature  (C)        continuous number
                p0:               environment pressure     (kPa)      continuous number
                saturated_outlet: True:saturated False:subcold (bool)
    
    If saturated_outlet=True then T_outlet is ignored.
    
    If saturated_outlet = False, then T_outlet MUST be strictly less than T_inlet. Otherwise the output will be wrong.
    
    It is assumed that absorbed heat is transfered to the environment so no product is produced and
    the exp = 0. Therefore, eps = 0
    
    """
    work_fluid = pm.get(working_fluid)
    
    h0 = work_fluid.h(T = T0, p = p0)
    s0 = work_fluid.s(T = T0, p = p0)
    
    h_inlet  = work_fluid.h(p = p_inlet, x = x_inlet)
    s_inlet  = work_fluid.s(p = p_inlet, x = x_inlet)
    T_inlet  = work_fluid.T(p = p_inlet, x = x_inlet)
    ex_inlet = (h_inlet - h0) - (T0 + 273.15)*(s_inlet - s0)
    
    if saturated_outlet:
        h_outlet = work_fluid.hs(p = p_outlet)[0]
        s_outlet = work_fluid.ss(p = p_outlet)[0]
        T_outlet = work_fluid.Ts(p = p_outlet)[0]
        ex_outlet = (h_outlet - h0) - (T0 + 273.15)*(s_outlet - s0)
    else:
        h_outlet = work_fluid.h(p = p_outlet, T = T_outlet)
        s_outlet = work_fluid.s(p = p_outlet, T = T_outlet)
        ex_outlet = (h_outlet - h0) - (T0 + 273.15)*(s_outlet - s0)
    
    qc = h_inlet - h_outlet
    
    if qc < 0:
        print('The condenser results are wrong:')
        print('If saturated_outlet = False, then T_outlet MUST be strictly less than T_inlet.')
        print(' ')
    
    # the aim is to lower the temperature of hot stream so 
    # the exergy difference of the hot stream is the product
    exLD_condenser = ex_inlet - ex_outlet
    exL_condenser = qc * (1-(T0+273.15)/(T_inlet+273.15))
    exD_condenser = exLD_condenser - exL_condenser
    
    eps_condenser = 0
    
    res = {'p_inlet':p_inlet, 'h_inlet':h_inlet[0], 's_inlet':s_inlet[0], 'T_inlet':T_inlet[0], 'ex_inlet':ex_inlet[0],
           'p_outlet':p_outlet, 'h_outlet':h_outlet[0], 's_outlet':s_outlet[0], 'T_outlet':T_outlet, 'ex_outlet':ex_outlet[0],
           'exD':exD_condenser[0],'exL':exL_condenser[0],'exLD':exLD_condenser[0],'eps':eps_condenser,'qc':qc[0]}
    
    return res
#%% environment
T0 = 25           # environment tempreture (K)
P0 = 100          # environment pressure   (kPa)

#%% test the function

working_fluid = 'mp.H2O'
p_inlet = p_outlet = 10 # assumes no pressure loss
T_outlet = 45.81       
x_inlet = 0.75          # steam turbine outlet is two phase (ideal rankin cycle) so p and T are not independent. 
                        # therefore x_inlet is required.
condenser = CONDENSER(p_inlet,x_inlet,p_outlet,T_outlet,working_fluid,saturated_outlet=True,T0=T0,p0=P0)

decimals = 2
condenser = {key : round(condenser[key], decimals) for key in condenser}
pprint(condenser)
