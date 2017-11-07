#!/usr/bin/python

from subprocess import call
import matplotlib.pyplot as plt
import numpy as np
import math

#-------------------- COLOR -------------------------------------------------------
class C:
    ORG     = '\033[33m'
    PURPLE  = '\033[35m'
    CYAN    = '\033[36m'
    BLUE    = '\033[34m'
    RED     = '\033[31m'
    GREEN   = '\033[92m'
    WARNING = '\033[93m'
    FAIL    = '\033[91m'
    ENDC    = '\033[0m'
    BOLD    = '\033[1m'
    UND     = '\033[4m'
#-------------------- SETTING -----------------------------------------------------
COF_A        = 0.0039/2
YEAR_SEC     = 365*86400                                            # Unit = sec
YR_LB        = 1                                                    # Unit = 0.1 year, Upper Bound for swing
YR_UB        = 500                                                  # Unit = 0.1 year, Lower Bound for swing
NL_VTH       = 0.28                                                 # Unit = V, Std(Nominal)Vth = 0.28v (Assumption)
HI_VTH       = 0.38                                                 # Unit = V, Hight_Vth Vth
FIN_YEAR     = 500                                                  # Unit = 1.0 year, Final year
FIN_NBTI_VTH = 0.0039/2*( pow( 0.5*FIN_YEAR*YEAR_SEC, 0.2))         # Unit = V
DEL_HI_VTH   = HI_VTH - NL_VTH                                      # Unit = V
#-------------------- Func -------------------------------------------------------
def CalSv( del_Vth ):
    if del_Vth == 0:
        return 0
    else:
        Right   = FIN_NBTI_VTH - del_Vth
        Time    = 0.5*( FIN_YEAR )*( YEAR_SEC )
        C       = COF_A*(( Time )**(0.2))
        Sv      = -( Right/float(C) - 1 )/del_Vth
        return Sv

#-------------------- Func -------------------------------------------------------
def CalVthNBTI( Delta_Vth, Sv, Yr ):
    """Estemate nbti-induced delta vth under Yr year aging"""
    Time     = 0.5*( float(Yr) )*( YEAR_SEC )
    Vth_nbti = ( 1 - Sv*Delta_Vth )*( COF_A )*( ( Time )**(0.2) )
    return Vth_nbti

#-------------------- Main -------------------------------------------------------
def main():
    Sv_nominal    = 0
    Sv_high_vth   = CalSv( DEL_HI_VTH )
    dic_nm_yr_ag  = {} # Year-to-agingrate dictionary of nominal buffer
    dic_hi_yr_ag  = {} # Year-to-agingrate dictionary of high-Vth buffer
    ##--------------- Vth = nominal ----------------------------------------------
    for time in range( YR_LB, YR_UB):
        Vth_nbti  = CalVthNBTI( 0, 0, float(time)/10 )
        agingrate = ( Vth_nbti )*2
        dic_nm_yr_ag[ time ] = ( agingrate )*100 #Unit %
    ##--------------- Vth = High-Vth ----------------------------------------------
    for time in range( YR_LB, YR_UB):
        Vth_nbti = CalVthNBTI( DEL_HI_VTH, Sv_high_vth, float(time)/10 )
        agingrate= ( Vth_nbti )*2
        dic_hi_yr_ag[ time ] = ( agingrate )*100 #Unit %

    ##--------------- Write -------------------------------------------------------
    f1 = open( "agingrate_nominal.txt" , "w+" )
    f2 = open( "agingrate_high_vth.txt", "w+" )
    f3 = open( "years.txt", "w+" )
    list_yr        = []
    list_nl_ag     = [] #nl = Nominal
    list_hi_ag     = [] #hi = Hi-Vth
    list_hi_ag_ttl = []
    ##--------------- Nominal ------------------------------
    for key in dic_nm_yr_ag:
        f1.write( "{} \n".format( str(dic_nm_yr_ag[key]) ) )
        list_nl_ag.append( dic_nm_yr_ag[key] )
    ##--------------- High-Vth ------------------------------
    for key in dic_hi_yr_ag:
        f2.write( "{} \n".format( str(dic_hi_yr_ag[key]) ) )
        list_hi_ag.append( dic_hi_yr_ag[key] )
        list_hi_ag_ttl.append( dic_hi_yr_ag[key] + ( DEL_HI_VTH )*2*100 )
    ##--------------- Year -----------------------------------
    for key in dic_nm_yr_ag:
        f3.write( "{} \n".format( float(key)/10 ) )
        list_yr.append( float(key)/10 )
    ##--------------- Close File ---------------------------------------------------
    f1.close()
    f2.close()
    f3.close()
    ##--------------- PRINT ---------------------------------------------------------
    call(["clear"])
    print C.CYAN+"----------------- [Setting] ----------------------------------------------"+C.ENDC
    print "Standard Vth ="+C.RED, NL_VTH, C.ENDC+"(V)"
    print "High-Vth Vth ="+C.ORG, HI_VTH, C.ENDC+"(V)"
    print C.CYAN+"----------------- [Assumption] -------------------------------------------"+C.ENDC
    print "ASSUME: After"+C.GREEN, FIN_YEAR, C.ENDC+"years, Vth of both 2 types of clock buffers "
    print "        will reach the same value of Vth = "+C.GREEN, NL_VTH + FIN_NBTI_VTH, C.ENDC+"(V)"
    print "Note: 0.0039/2x((0.5*"+C.GREEN, FIN_YEAR, C.ENDC+"yx365dx86400s)^(0.2))=Vth_nbti="+C.PURPLE, FIN_NBTI_VTH, C.ENDC+"(V)"
    print "Note: Standard Vth+ Vth_nbti ="+C.RED, NL_VTH, C.ENDC+"+"+C.PURPLE, FIN_NBTI_VTH, C.ENDC+"="+C.GREEN, NL_VTH + FIN_NBTI_VTH, C.ENDC+"(V)"
    print "Note: High-Vth Buffer's Vth_nbti ="+C.GREEN, NL_VTH + FIN_NBTI_VTH, C.ENDC+"-"+C.ORG, HI_VTH, C.ENDC+"="+C.ORG, FIN_NBTI_VTH-DEL_HI_VTH, C.ENDC+"(V)"
    print C.CYAN+"----------------- [Aging rate] -------------------------------------------"+C.ENDC
    print " 0-year Standard Buffer delay gain"+C.RED, 0                     , C.ENDC+"%"
    print "10-year Standard Buffer aging rate"+C.RED, round(list_nl_ag[98],3)      , C.ENDC+"%"
    print " 0-year High-Vth Buffer delay gain"+C.ORG, round((DEL_HI_VTH)*2*100,3)  , C.ENDC+"%"
    print "10-year High-Vth Buffer aging rate"+C.ORG, round(list_hi_ag[98],3)      , C.ENDC+"%"
    print "10-year High-Vth Buffer delay gain"+C.ORG, round(list_hi_ag_ttl[98],3)  , C.ENDC+"%"

     ##--------------- PLOT ---------------------------------------------------------
    plt.plot( list_yr, list_hi_ag, "b" )
    plt.plot( list_yr, list_hi_ag_ttl, "b" )
    plt.plot( list_yr, list_nl_ag, "g" )
    plt.ylabel('Delay gain (%)')
    plt.xlabel('Years')
    plt.grid(True)
    plt.show()
#-------------------- Enter -------------------------------------------------------
if __name__ == '__main__':
    main()


