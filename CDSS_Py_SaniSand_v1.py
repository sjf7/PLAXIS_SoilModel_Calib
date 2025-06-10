from plxscripting.easy import new_server
import numpy as np
import itertools
from scipy.interpolate import CubicSpline
import datetime
import os
import sys
import traceback


# --------------------------------------------- My functions
from DssFunctionsPy.cdss import *
from DssFunctionsPy.undrained_runs_CDSS  import *
from CommandSheet.Read_controlSheet import *
from makeList.makeList_v1 import *
#----------------------------------------------------------

#----------------------------------------------------------
#       Control panel
#----------------------------------------------------------



ControlPanel_name = 'ControlSheet_PM4Sand.yml'




ControlPanel_location = 'C:\\Users\\URL\\'
PASSWORD = '*******'


       



variables = Read_controlSheet(ControlPanel_name, ControlPanel_location)
#----------------------------------------------------------
#       input params ranges
#----------------------------------------------------------


G_0s  = makeList_v1(variables[0]['G_0s'])       
h_p0s = makeList_v1(variables[0]['h_p0s'])   
n_bs  = makeList_v1(variables[0]['n_bs'])    
n_ds  = makeList_v1(variables[0]['n_ds'])    
Qs    = makeList_v1(variables[0]['Qs'])      


D_R0            = variables[0]['D_R0']       

R               = variables[0]['R']           
PostShake       = variables[0]['PostShake']   
p_A             = variables[0]['p_A']         
poisson_ratio   = variables[0]['poisson_ratio'] 
Gs              = variables[0]['Gs']            
water_density   = variables[0]['water_density']
min_dry_density = variables[0]['min_dry_density']
max_dry_density = variables[0]['max_dry_density']


#----------------------------------------------------------
#       Assigning Experimental_DSS params
#----------------------------------------------------------


eff_sigma_v     = variables[0]['eff_sigma_v']     
phi_cv          = variables[0]['phi_cv']          

h_consolidation = variables[0]['h_consolidation'] 
 
weight_specimen = variables[0]['weight_specimen']  
gamma_sat       = variables[0]['gamma_sat']        

CSR             = variables[0]['CSR']
num_cycles      = variables[0]['num_cycles']

Steps_per_Quarter_Cycle = variables[0]['Steps_per_Quarter_Cycle']






#----------------------------------------------------------
#       API - 1
#----------------------------------------------------------



PORT = 10000



s, g = new_server('localhost', PORT, password=PASSWORD)
now = datetime.datetime.now()




print("---------------------------------------------------------- ")
print("\n")
print(f"******* -------- API connected on Date and Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} -------- *******")
#----------------------------------------------------------
#       Experimental data location
#----------------------------------------------------------
filename = variables[0]['filename_lab']    


filelocation = variables[0]['filelocation_lab_data_PC']   
output_location = variables[0]['output_location_PC']  



DSS_exp_results = np.loadtxt(os.path.join(filelocation, filename), delimiter=',')


print("\n")
print("******* Exp data was read..... ")
#----------------------------------------------------------
#       Outcomes location
#----------------------------------------------------------

   


output_string = f"PM4Sand_output{now.strftime('__Date_%Y-%m-%d__Time_%H-%M')}.csv"


f = open(os.path.join(output_location, output_string), 'w')




# To get just the file name
if getattr(sys, 'frozen', False):
    # The application is frozen
    file_path = os.path.abspath(sys.executable)
else:
    # The application is not frozen
    file_path = os.path.abspath(__file__)

code_version_info = os.path.basename(file_path)
Exp_file_location_info = f"EXP DSS file: {filelocation}"

ControlPanel_details = 'Command sheet: '+ControlPanel_location+ControlPanel_name 

f.write(
        f"#DR0, G0, hp0, pA, emax, emin, nb, nd, phi_cv, "
        f"poisson_ratio, Q, R, PostShake, K0_cal, Tau_cal, Error (RMSE_Tau), Error (RMSE_PWP), "
        f"{ControlPanel_details}, {code_version_info}, {Exp_file_location_info}\n"
        )





gamma_unsat_specimen = weight_specimen / (np.pi/4*6.3**2*h_consolidation/10)*9.8066358553  # kN/m3 
friction_angle_rad = phi_cv * np.pi / 180
k0_calculated = (1 - np.sin(friction_angle_rad)) * (1 + (2/3) * np.sin(friction_angle_rad)) / (1 + np.sin(friction_angle_rad))

e_max = (Gs*water_density/min_dry_density)-1
e_min = (Gs*water_density/max_dry_density)-1








if gamma_sat < gamma_unsat_specimen:
        raise ValueError("gammaSat must be greater than gammaUnsat")




print("******* -------- Output file was created..... ")
#----------------------------------------------------------


g.CDSS.AbsSigyyinit                 = eff_sigma_v    # initial stress

g.CDSS.Behaviour                    = "Undrained"
g.CDSS.Consolidation                = "K0"
g.CDSS.TestControlType              = "Stress"
g.CDSS.K0                           = k0_calculated
g.CDSS.ShearStressAmplitude         = CSR*eff_sigma_v
g.CDSS.NumberOfCycles               = num_cycles
g.CDSS.NumberOfStepsPerQuarterCycle = Steps_per_Quarter_Cycle

g.CDSS.Duration           = 0
g.CDSS.InitialStaticShear = 0


g.Material.User1        = D_R0            

g.Material.User4        = p_A
g.Material.User5        = e_max           
g.Material.User6        = e_min
#g.Material.User7        = n_b
#g.Material.User8        = n_d
g.Material.User9        = phi_cv
g.Material.User10       = poisson_ratio
#g.Material.User11       = Q
g.Material.User12       = R
g.Material.User13       = PostShake


print("******* initial params were assigned..... ")



#----------------------------------------------------------
#       opt process - 4
#----------------------------------------------------------
print("---------------------------------------------------------- ")


# print(f"Gref\tnG\tGamma\tlambda_e\tMtc\tN\t\tXtc\tH0\tH_psi\tR\tPsi_0\t\t\t\t\t\tError - RMSE")


print(f"{'Error - RMSE_Tau':^8}\t{'Error - RMSE_PWP':^8}")




params = list(itertools.product(G_0s, h_p0s, n_bs, n_ds, Qs))
                         

for i, p in enumerate(params): 
     
    G_0, h_p0, n_b, n_d, Q = p

    g.Material.User2  = G_0
    g.Material.User3  = h_p0    
    
    g.Material.User7  = n_b
    g.Material.User8  = n_d

    g.Material.User11 = Q



    results_simulation = undrained_runs_CDSS(DSS_exp_results, g, np, cdss)




    print(f"{str(np.round(results_simulation[1], 3)):^8}\t\t{str(np.round(results_simulation[2], 3)):^8}")



#               DR0,   G0,  hp0,    pA,   emax,   emin,   nb,   nd,  phi_cv,  poisson_ratio,  Q,  R,  PostShake, K0_cal, Tau_cal, Error                                                                  
    f.write(f"{D_R0},{G_0},{h_p0},{p_A},{e_max},{e_min},{n_b},{n_d},{phi_cv},{poisson_ratio},{Q},{R},{PostShake},"
            f"{k0_calculated},{str(results_simulation[0])},{str(np.round(results_simulation[1], 3))},{str(np.round(results_simulation[2], 3))}\n")


     

  





f.close()






print("---------------------------------------------------------- ")





