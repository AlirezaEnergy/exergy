import pyromat as pm
import numpy as np
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

#%% functions

def PUMP(p_inlet,p_outlet, working_fluid, eta_isentropic = 1, T0=25, p0=100):
    """
    inputs: inlet pressure:  p_inlet  (kPa)                    continuous number
            outlet pressure: p_outlet (kpa)                    continuous number
            working_fluid:   working fluid name (string)       based on pyromat
            eta_isentropic:  isentropic efficiency             [0,1]
            T0:              environment temperature (C)       continuous number
            p0:              environment pressure (kPa)        continuous number
            
        In rankine cycle, it is assumed that the inlet is saturated liquid as using subcold is not rational
        and multi-phase is not allowed. therefore, x_inlet = 0 (0% vapor is in the fluid) and rho_inlet is
        calculated based on saturated density (ds)
    """
    
    work_fluid = pm.get(working_fluid)
    
    h0 = work_fluid.h(T = T0, p = p0)
    s0 = work_fluid.s(T = T0, p = p0)
    
    p_inlet  = np.array([p_inlet])
    p_outlet = np.array([p_outlet]) 
    
    h_inlet  = work_fluid.hs(p = p_inlet)[0]                     # kJ/kg
    s_inlet  = work_fluid.ss(p = p_inlet)[0]                     # kJ/kg.C
    T_inlet  = work_fluid.Ts(p = p_inlet)                        # C
    ex_inlet = (h_inlet - h0) - (T0 + 273.15)*(s_inlet - s0)     # physical exergy of point 1 (kJ/kg)
    
    """isentropic assunption"""
    ss_outlet  = s_inlet                                         # kJ/kg.C
    Ts_outlet = work_fluid.T_s(p = p_outlet, s = ss_outlet)      # C
    hs_outlet = work_fluid.h(T = Ts_outlet, p = p_outlet)        # kJ/kg
    ws_pump   = hs_outlet - h_inlet                              # kJ/kg
    
    """actual work"""
    w_pump   = ws_pump / eta_isentropic                          # kJ/kg
    
    """actual outlets"""
    h_outlet = h_inlet + w_pump                                  # kJ/kg
    T_outlet = work_fluid.T_h(h = h_outlet, p = p_outlet)        # C
    s_outlet = work_fluid.s(T = T_outlet, p = p_outlet)          # kJ/kg.C
    ex_outlet = (h_outlet - h0) - (T0 + 273.15)*(s_outlet - s0)  # kJ/kg
    
    """exergy"""
    exf_pump = w_pump
    exp_pump = ex_outlet - ex_inlet
    exLD_pump = exf_pump - exp_pump
    eps_pump = exp_pump / exf_pump

    if exLD_pump < 0:
        exLD_pump = np.array([0])
        eps_pump = np.array([1])
    
    res = {'p_inlet':p_inlet[0], 'h_inlet':h_inlet[0], 's_inlet':s_inlet[0], 'T_inlet':T_inlet[0], 'ex_inlet':ex_inlet[0],
           'p_outlet':p_outlet[0], 'h_outlet':h_outlet[0], 's_outlet':s_outlet[0], 'T_outlet':T_outlet[0], 'ex_outlet':ex_outlet[0],
           'exf':exf_pump[0],'exp':exp_pump[0],'exLD':exLD_pump[0],'eps':eps_pump[0],'w':w_pump[0]}
    
    return res

#%% environment

T0 = 25           # environment tempreture (C)
p0 = 100          # environment pressure   (kPa)

#%% Pump (isentropic, without heat loss)

p1 = 10
p2 = 2000

pump = PUMP(p_inlet = p1,p_outlet = p2, working_fluid = 'mp.H2O', eta_isentropic = 0.9, T0=T0, p0=p0)

decimals = 3
pump = {key : round(pump[key], decimals) for key in pump}

pprint(pump)
