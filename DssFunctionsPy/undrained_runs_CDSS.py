def undrained_runs_CDSS(DSS_exp_results, g, np, cdss):


    results_simulation = []
    
    

    tau_xy_simulated, gamma_xy_simulated, SigyyE_simulated = cdss(g)
    PWP_simulated = np.max(SigyyE_simulated) - SigyyE_simulated

    PWP_CDSS = np.max(DSS_exp_results[:,2]) - DSS_exp_results[:,2]



    if gamma_xy_simulated is not None:
    # print(gamma_xy_simulated)
        tau_xy_max = np.max(tau_xy_simulated)
        tau_CDSS_after_inter = np.interp(gamma_xy_simulated, DSS_exp_results[:,0], DSS_exp_results[:,1])
        PWP_CDSS_after_inter = np.interp(gamma_xy_simulated, DSS_exp_results[:,0], PWP_CDSS)   

        rmse_tau = np.sqrt(np.mean(np.square(np.array(tau_CDSS_after_inter) - np.array(tau_xy_simulated))))
        rmse_PWP = np.sqrt(np.mean(np.square(np.array(PWP_CDSS_after_inter) - np.array(PWP_simulated))))
    else:
        print(f"gamma_xy_simulated is None - value: {gamma_xy_simulated}")
        tau_xy_max = None
        rmse = None
        # rmspe = None


    results_simulation.append(tau_xy_max)
    results_simulation.append(rmse_tau)
    results_simulation.append(rmse_PWP)

    

    return results_simulation