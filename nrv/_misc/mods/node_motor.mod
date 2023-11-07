TITLE Motor Axon Node channels

: 06/16
: Jessica Gaines
:
: Modification of channel properties
:
: 04/15
: Lane Heyboer
:
: Fast K+ current
:
: 02/02
: Cameron C. McIntyre
:
: Fast Na+, Persistant Na+, Slow K+, and Leakage currents 
: responsible for nodal action potential
: Iterative equations H-H notation rest = -80 mV
:
: This model is described in detail in:
: 
: Gaines JS, Finn KE, Slopsema JP, Heyboer LA, Polasek KH. A Model of 
: Motor and Sensory Axon Activation in the Median Nerve Using Surface 
: Electrical Stimulation. Journal of Computational Neuroscience, 2018.
:
: McIntyre CC, Richardson AG, and Grill WM. Modeling the excitability of
: mammalian nerve fibers: influence of afterpotentials on the recovery
: cycle. Journal of Neurophysiology 87:995-1006, 2002.

INDEPENDENT {t FROM 0 TO 1 WITH 1 (ms)}

NEURON {
    SUFFIX node_motor
    NONSPECIFIC_CURRENT ina
    NONSPECIFIC_CURRENT inap
    NONSPECIFIC_CURRENT ik
    NONSPECIFIC_CURRENT il
    NONSPECIFIC_CURRENT ikf
    RANGE gnapbar, gnabar, gkbar, gl, gkfbar, ena, ek, el, ekf
    RANGE gnap, gna, gk, gkf
    RANGE mp_inf, m_inf, h_inf, s_inf, n_inf
    RANGE tau_mp, tau_m, tau_h, tau_s, tau_n
}


UNITS {
    (mA) = (milliamp)
    (mV) = (millivolt)
}

PARAMETER {

    : channel conductances
    gnapbar = 0.01	(mho/cm2)
    gnabar	= 3.0	(mho/cm2)
    gkbar   = 0.08	(mho/cm2)
    gl	= 0.007 (mho/cm2)
    gkfbar	= 0.02568	(mho/cm2)

    : reversal potentials
    ena     = 50.0  (mV)
    ek      = -90.0 (mV)
    el	= -90.0 (mV)
    ekf	= -90.0 (mV)

    : variables read in from .hoc file
    celsius		(degC)
    dt              (ms)
    v               (mV)
    vtraub=-80

    : parameters determining rate constants

    : persistent Na+
    ampA = 0.01
    ampB = 27
    ampC = 10.2
    bmpA = 0.00025
    bmpB = 34
    bmpC = 10

    : fast Na+
    amA = 1.86
    amB = 20.4
    amC = 10.3
    bmA = 0.086
    bmB = 25.7
    bmC = 9.16
    ahA = 0.062
    ahB = 114.0
    ahC = 11.0
    bhA = 2.3
    bhB = 31.8
    bhC = 13.4

    : slow K+
    asA = 0.3
    asB = -27
    asC = -5
    bsA = 0.03
    bsB = 10
    bsC = -1

    : fast K+
    anA = 0.0462
    anB = -83.2
    anC = 1.1
    bnA = 0.0824
    bnB = -66
    bnC = 10.5
}

STATE {
    mp m h s n
}

ASSIGNED {
    gnap    (mho/cm2)
    gna     (mho/cm2)
    gk      (mho/cm2)
    gkf     (mho/cm2)
    inap    (mA/cm2)
    ina	(mA/cm2)
    ik      (mA/cm2)
    il      (mA/cm2)
    ikf	(mA/cm2)
    mp_inf
    m_inf
    h_inf
    s_inf
    n_inf
    tau_mp	(ms)
    tau_m	(ms)
    tau_h	(ms)
    tau_s	(ms)
    tau_n	(ms)
    q10_1
    q10_2
    q10_3
}

BREAKPOINT {
    SOLVE states METHOD cnexp
    gnap = gnapbar * mp*mp*mp
    inap = gnap * (v - ena)
    gna = gnabar * m*m*m*h
    ina = gna * (v - ena)
    gk = gkbar * s
    ik = gk * (v - ek)
    il = gl * (v - el)
    gkf = gkfbar * n*n*n*n
    ikf = gkf * (v-ekf)
}

DERIVATIVE states {   : exact Hodgkin-Huxley equations
    evaluate_fct(v)
    mp'= (mp_inf - mp) / tau_mp
    m' = (m_inf - m) / tau_m
    h' = (h_inf - h) / tau_h
    s' = (s_inf - s) / tau_s
    n' = (n_inf - n) / tau_n
}

UNITSOFF

INITIAL {
:
:	Q10 adjustment
:   Temperature dependence
:

    q10_1 = 2.2 ^ ((celsius-20)/ 10 )
    q10_2 = 2.9 ^ ((celsius-20)/ 10 )
    q10_3 = 3.0 ^ ((celsius-36)/ 10 )

    evaluate_fct(v)
    mp = mp_inf
    m = m_inf
    h = h_inf
    s = s_inf
    n = n_inf
}

PROCEDURE evaluate_fct(v(mV)) { LOCAL a,b,v2

    : persistent Na+
    a = q10_1*vtrap1(v)
    b = q10_1*vtrap2(v)
    tau_mp = 1 / (a + b)
    mp_inf = a / (a + b)

    : fast Na+
    a = q10_1*vtrap6(v)
    b = q10_1*vtrap7(v)
    tau_m = 1 / (a + b)
    m_inf = a / (a + b)

    a = q10_2*vtrap8(v)
    b = q10_2*bhA / (1 + Exp(-(v+bhB)/bhC))
    tau_h = 1 / (a + b)
    h_inf = a / (a + b)

    v2 = v - vtraub : convert to traub convention

    : slow K+
    a = q10_3*asA / (Exp((v2+asB)/asC) + 1) 
    b = q10_3*bsA / (Exp((v2+bsB)/bsC) + 1)
    tau_s = 1 / (a + b)
    s_inf = a / (a + b)

    : fast K+
    a = q10_3*vtrapNA(v) 
    b = q10_3*vtrapNB(v)
    tau_n = 1 / (a + b)
    n_inf = a / (a + b)
}

: vtrap functions to prevent discontinuity
FUNCTION vtrap(x) {
    if (x < -50) {
        vtrap = 0
    }else{
        vtrap = bsA / (Exp((x+bsB)/bsC) + 1)
    }
}

FUNCTION vtrap1(x) {
    if (fabs((x+ampB)/ampC) < 1e-6) {
        vtrap1 = ampA*ampC
    }else{
        vtrap1 = (ampA*(x+ampB)) / (1 - Exp(-(x+ampB)/ampC))
    }
}

FUNCTION vtrap2(x) {
    if (fabs((x+bmpB)/bmpC) < 1e-6) {
        vtrap2 = bmpA*bmpC : Ted Carnevale minus sign bug fix
    }else{
        vtrap2 = (bmpA*(-(x+bmpB))) / (1 - Exp((x+bmpB)/bmpC))
    }
}

FUNCTION vtrap6(x) {
    if (fabs((x+amB)/amC) < 1e-6) {
        vtrap6 = amA*amC
    }else{
        vtrap6 = (amA*(x+amB)) / (1 - Exp(-(x+amB)/amC))
    }
}

FUNCTION vtrap7(x) {
    if (fabs((x+bmB)/bmC) < 1e-6) {
        vtrap7 = bmA*bmC : Ted Carnevale minus sign bug fix
    }else{
        vtrap7 = (bmA*(-(x+bmB))) / (1 - Exp((x+bmB)/bmC))
    }
}

FUNCTION vtrap8(x) {
    if (fabs((x+ahB)/ahC) < 1e-6) {
        vtrap8 = ahA*ahC : Ted Carnevale minus sign bug fix
    }else{
        vtrap8 = (ahA*(-(x+ahB))) / (1 - Exp((x+ahB)/ahC)) 
    }
}

FUNCTION vtrapNA(x){
    if(fabs((anB - x)/anC) < 1e-6){
        vtrapNA = anA*anC
    }else{
        vtrapNA = anA*(v-anB)/(1-Exp((anB-v)/anC))
    }
}

FUNCTION vtrapNB(x){
    if(fabs((x - bnB)/bnC) < 1e-6){
        vtrapNB = bnA*bnC  
    }else{
        vtrapNB = bnA*(bnB-v)/(1-Exp((v-bnB)/bnC))
    }
}

FUNCTION Exp(x) {
    if (x < -100) {
        Exp = 0
    }else{
        Exp = exp(x)
    }
}

UNITSON