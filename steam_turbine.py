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

#%% turbine

def TURBINE(p_outlet,p_inlet,T_inlet,working_fluid,eta_isentropic=1,eff_mech=1,eff_gen=1,T0=25,p0=100):
    """
    inputs: p_outlet:         outlet pressure             (kPa)      continuous variable
            T_inlet:          inlet temperature           (C)        continuous variable
            p_inlet:          inlet pressure              (kPa)      continuous variable
            working_fluid:    working fluid name          (string)   base on pyromat
            eta_isentropic:   isentropic efficiency       (-)        [0,1]
            eff_mech:         shaft mechnical efficiency  (-)        [0,1]
            eff_gen:          generator efficiency        (-)        [0,1]
            T0:               environment temperature     (C)        continuous number
            p0:               environment pressure        (kPa)      continuous number
    """
    
    work_fluid = pm.get(working_fluid)
    
    h0 = work_fluid.h(T = T0, p = p0)                            # kJ/kg
    s0 = work_fluid.s(T = T0, p = p0)                            # kJ/kg.C
    
    h_inlet  = work_fluid.h(p = p_inlet, T = T_inlet)            # kJ/kg
    s_inlet  = work_fluid.s(p = p_inlet, T = T_inlet)            # kJ/kg.C
    ex_inlet = (h_inlet - h0) - (T0 + 273.15)*(s_inlet - s0)     # kJ/kg
    
    """isentropic work"""
    ss_outlet = s_inlet                                          # kJ/kg.C
    Ts_outlet, xs_outlet = work_fluid.T_s(s = ss_outlet, p = p_outlet, quality = True) # calculate temperature using entropy, C
    hs_outlet = work_fluid.h(p = p_outlet, x = xs_outlet)        # kJ/kg
    ws_turbine = h_inlet - hs_outlet                             # isentropic work kJ/kg
    
    """non_isentropic work"""
    w_turbine = eta_isentropic * ws_turbine                                         # kJ/kg
    h_outlet = h_inlet - w_turbine                                                  # kJ/kg
    T_outlet, x_outlet = work_fluid.T_h(p = p_outlet, h = h_outlet, quality = True) # C
    s_outlet = work_fluid.s(x = x_outlet, T = T_outlet) # it wont give the correct answer if one uses p_outlet and h_outlet
    ex_outlet = (h_outlet - h0) - (T0 + 273.15)*(s_outlet - s0)                     # kJ/kg
    
    """actual work"""
    wa_turbine = eff_mech*eff_gen*w_turbine # actual work, kJ/kg
    
    exp_turbine = wa_turbine
    exf_turbine = ex_inlet - ex_outlet
    exL_turbine = w_turbine - wa_turbine
    exDL_turbine = exf_turbine - exp_turbine
    exD_turbine = exDL_turbine - exL_turbine
    
    eps_turbine = exp_turbine / exf_turbine
    eta_turbine = wa_turbine / (h_inlet - h_outlet)
    
    res = {'p_inlet':p_inlet, 'h_inlet':h_inlet[0], 's_inlet':s_inlet[0], 'T_inlet':T_inlet, 'ex_inlet':ex_inlet[0],
           'p_outlet':p_outlet, 'h_outlet':h_outlet[0], 's_outlet':s_outlet[0], 'T_outlet':T_outlet[0],
           'ex_outlet':ex_outlet[0],'x_outlet':x_outlet[0],'exf':exf_turbine[0],'exp':exp_turbine[0],
           'exLD':exDL_turbine[0], 'exL':exL_turbine[0], 'exD':exD_turbine[0],'eps':eps_turbine[0],'w':wa_turbine[0],
           'eta':eta_turbine[0]}
    
    return res
#%%
working_fluid = 'mp.H2O'
p_outlet = 1000
p_inlet = 10000
T_inlet = 300

turbine = TURBINE(p_outlet,p_inlet,T_inlet,working_fluid,eta_isentropic=0.9,eff_mech=0.95,
                  eff_gen=0.95,T0=25,p0=100)

decimals = 3
turbine = {key : round(turbine[key], decimals) for key in turbine}
pprint(turbine)
