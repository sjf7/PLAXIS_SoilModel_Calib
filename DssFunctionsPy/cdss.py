def cdss(g):
  
    if g.calculate(g.CDSS) is not None:
        tau_xy = g.CDSS.Results.Sigxy.value
        gamma_xy = g.CDSS.Results.Gamxy.value
        SigyyE = g.CDSS.Results.SigyyE.value

        return tau_xy, gamma_xy, SigyyE
    else:
        return None