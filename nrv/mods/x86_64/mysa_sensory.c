/* Created by Language version: 7.7.0 */
/* VECTORIZED */
#define NRN_VECTORIZED 1
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "scoplib_ansi.h"
#undef PI
#define nil 0
#include "md1redef.h"
#include "section.h"
#include "nrniv_mf.h"
#include "md2redef.h"
 
#if METHOD3
extern int _method3;
#endif

#if !NRNGPU
#undef exp
#define exp hoc_Exp
extern double hoc_Exp(double);
#endif
 
#define nrn_init _nrn_init__mysa_sensory
#define _nrn_initial _nrn_initial__mysa_sensory
#define nrn_cur _nrn_cur__mysa_sensory
#define _nrn_current _nrn_current__mysa_sensory
#define nrn_jacob _nrn_jacob__mysa_sensory
#define nrn_state _nrn_state__mysa_sensory
#define _net_receive _net_receive__mysa_sensory 
#define evaluate_fct evaluate_fct__mysa_sensory 
#define states states__mysa_sensory 
 
#define _threadargscomma_ _p, _ppvar, _thread, _nt,
#define _threadargsprotocomma_ double* _p, Datum* _ppvar, Datum* _thread, _NrnThread* _nt,
#define _threadargs_ _p, _ppvar, _thread, _nt
#define _threadargsproto_ double* _p, Datum* _ppvar, Datum* _thread, _NrnThread* _nt
 	/*SUPPRESS 761*/
	/*SUPPRESS 762*/
	/*SUPPRESS 763*/
	/*SUPPRESS 765*/
	 extern double *getarg();
 /* Thread safe. No static _p or _ppvar. */
 
#define t _nt->_t
#define dt _nt->_dt
#define gkbar _p[0]
#define gl _p[1]
#define gq _p[2]
#define gkf _p[3]
#define ek _p[4]
#define el _p[5]
#define eq _p[6]
#define ekf _p[7]
#define ik _p[8]
#define il _p[9]
#define iq _p[10]
#define ikf _p[11]
#define s_inf _p[12]
#define q_inf _p[13]
#define n_inf _p[14]
#define tau_s _p[15]
#define tau_q _p[16]
#define tau_n _p[17]
#define s _p[18]
#define q _p[19]
#define n _p[20]
#define Ds _p[21]
#define Dq _p[22]
#define Dn _p[23]
#define q10_1 _p[24]
#define q10_2 _p[25]
#define q10_3 _p[26]
#define v _p[27]
#define _g _p[28]
 
#if MAC
#if !defined(v)
#define v _mlhv
#endif
#if !defined(h)
#define h _mlhh
#endif
#endif
 
#if defined(__cplusplus)
extern "C" {
#endif
 static int hoc_nrnpointerindex =  -1;
 static Datum* _extcall_thread;
 static Prop* _extcall_prop;
 /* external NEURON variables */
 extern double celsius;
 /* declaration of user functions */
 static void _hoc_Exp(void);
 static void _hoc_evaluate_fct(void);
 static void _hoc_vtrapNB(void);
 static void _hoc_vtrapNA(void);
 static int _mechtype;
extern void _nrn_cacheloop_reg(int, int);
extern void hoc_register_prop_size(int, int, int);
extern void hoc_register_limits(int, HocParmLimits*);
extern void hoc_register_units(int, HocParmUnits*);
extern void nrn_promote(Prop*, int, int);
extern Memb_func* memb_func;
 
#define NMODL_TEXT 1
#if NMODL_TEXT
static const char* nmodl_file_text;
static const char* nmodl_filename;
extern void hoc_reg_nmodl_text(int, const char*);
extern void hoc_reg_nmodl_filename(int, const char*);
#endif

 extern void _nrn_setdata_reg(int, void(*)(Prop*));
 static void _setdata(Prop* _prop) {
 _extcall_prop = _prop;
 }
 static void _hoc_setdata() {
 Prop *_prop, *hoc_getdata_range(int);
 _prop = hoc_getdata_range(_mechtype);
   _setdata(_prop);
 hoc_retpushx(1.);
}
 /* connect user functions to hoc names */
 static VoidFunc hoc_intfunc[] = {
 "setdata_mysa_sensory", _hoc_setdata,
 "Exp_mysa_sensory", _hoc_Exp,
 "evaluate_fct_mysa_sensory", _hoc_evaluate_fct,
 "vtrapNB_mysa_sensory", _hoc_vtrapNB,
 "vtrapNA_mysa_sensory", _hoc_vtrapNA,
 0, 0
};
#define Exp Exp_mysa_sensory
#define vtrapNB vtrapNB_mysa_sensory
#define vtrapNA vtrapNA_mysa_sensory
 extern double Exp( _threadargsprotocomma_ double );
 extern double vtrapNB( _threadargsprotocomma_ double );
 extern double vtrapNA( _threadargsprotocomma_ double );
 /* declare global and static user variables */
#define anC anC_mysa_sensory
 double anC = 1.1;
#define anB anB_mysa_sensory
 double anB = -83.2;
#define anA anA_mysa_sensory
 double anA = 0.0462;
#define aqC aqC_mysa_sensory
 double aqC = -12.2;
#define aqB aqB_mysa_sensory
 double aqB = -94.2;
#define aqA aqA_mysa_sensory
 double aqA = 0.00522;
#define asC asC_mysa_sensory
 double asC = -5;
#define asB asB_mysa_sensory
 double asB = -27;
#define asA asA_mysa_sensory
 double asA = 0.3;
#define bnC bnC_mysa_sensory
 double bnC = 10.5;
#define bnB bnB_mysa_sensory
 double bnB = -66;
#define bnA bnA_mysa_sensory
 double bnA = 0.0824;
#define bqC bqC_mysa_sensory
 double bqC = -12.2;
#define bqB bqB_mysa_sensory
 double bqB = -94.2;
#define bqA bqA_mysa_sensory
 double bqA = 0.00522;
#define bsC bsC_mysa_sensory
 double bsC = -1;
#define bsB bsB_mysa_sensory
 double bsB = 10;
#define bsA bsA_mysa_sensory
 double bsA = 0.03;
#define vtraub vtraub_mysa_sensory
 double vtraub = -80;
 /* some parameters have upper and lower limits */
 static HocParmLimits _hoc_parm_limits[] = {
 0,0,0
};
 static HocParmUnits _hoc_parm_units[] = {
 "gkbar_mysa_sensory", "mho/cm2",
 "gl_mysa_sensory", "mho/cm2",
 "gq_mysa_sensory", "mho/cm2",
 "gkf_mysa_sensory", "mho/cm2",
 "ek_mysa_sensory", "mV",
 "el_mysa_sensory", "mV",
 "eq_mysa_sensory", "mV",
 "ekf_mysa_sensory", "mV",
 "ik_mysa_sensory", "mA/cm2",
 "il_mysa_sensory", "mA/cm2",
 "iq_mysa_sensory", "mA/cm2",
 "ikf_mysa_sensory", "mA/cm2",
 0,0
};
 static double delta_t = 1;
 static double n0 = 0;
 static double q0 = 0;
 static double s0 = 0;
 /* connect global user variables to hoc */
 static DoubScal hoc_scdoub[] = {
 "vtraub_mysa_sensory", &vtraub_mysa_sensory,
 "asA_mysa_sensory", &asA_mysa_sensory,
 "asB_mysa_sensory", &asB_mysa_sensory,
 "asC_mysa_sensory", &asC_mysa_sensory,
 "bsA_mysa_sensory", &bsA_mysa_sensory,
 "bsB_mysa_sensory", &bsB_mysa_sensory,
 "bsC_mysa_sensory", &bsC_mysa_sensory,
 "aqA_mysa_sensory", &aqA_mysa_sensory,
 "aqB_mysa_sensory", &aqB_mysa_sensory,
 "aqC_mysa_sensory", &aqC_mysa_sensory,
 "bqA_mysa_sensory", &bqA_mysa_sensory,
 "bqB_mysa_sensory", &bqB_mysa_sensory,
 "bqC_mysa_sensory", &bqC_mysa_sensory,
 "anA_mysa_sensory", &anA_mysa_sensory,
 "anB_mysa_sensory", &anB_mysa_sensory,
 "anC_mysa_sensory", &anC_mysa_sensory,
 "bnA_mysa_sensory", &bnA_mysa_sensory,
 "bnB_mysa_sensory", &bnB_mysa_sensory,
 "bnC_mysa_sensory", &bnC_mysa_sensory,
 0,0
};
 static DoubVec hoc_vdoub[] = {
 0,0,0
};
 static double _sav_indep;
 static void nrn_alloc(Prop*);
static void  nrn_init(_NrnThread*, _Memb_list*, int);
static void nrn_state(_NrnThread*, _Memb_list*, int);
 static void nrn_cur(_NrnThread*, _Memb_list*, int);
static void  nrn_jacob(_NrnThread*, _Memb_list*, int);
 
static int _ode_count(int);
static void _ode_map(int, double**, double**, double*, Datum*, double*, int);
static void _ode_spec(_NrnThread*, _Memb_list*, int);
static void _ode_matsol(_NrnThread*, _Memb_list*, int);
 
#define _cvode_ieq _ppvar[0]._i
 static void _ode_matsol_instance1(_threadargsproto_);
 /* connect range variables in _p that hoc is supposed to know about */
 static const char *_mechanism[] = {
 "7.7.0",
"mysa_sensory",
 "gkbar_mysa_sensory",
 "gl_mysa_sensory",
 "gq_mysa_sensory",
 "gkf_mysa_sensory",
 "ek_mysa_sensory",
 "el_mysa_sensory",
 "eq_mysa_sensory",
 "ekf_mysa_sensory",
 0,
 "ik_mysa_sensory",
 "il_mysa_sensory",
 "iq_mysa_sensory",
 "ikf_mysa_sensory",
 "s_inf_mysa_sensory",
 "q_inf_mysa_sensory",
 "n_inf_mysa_sensory",
 "tau_s_mysa_sensory",
 "tau_q_mysa_sensory",
 "tau_n_mysa_sensory",
 0,
 "s_mysa_sensory",
 "q_mysa_sensory",
 "n_mysa_sensory",
 0,
 0};
 
extern Prop* need_memb(Symbol*);

static void nrn_alloc(Prop* _prop) {
	Prop *prop_ion;
	double *_p; Datum *_ppvar;
 	_p = nrn_prop_data_alloc(_mechtype, 29, _prop);
 	/*initialize range parameters*/
 	gkbar = 0.001324;
 	gl = 0.001716;
 	gq = 0.003102;
 	gkf = 0.1642;
 	ek = -90;
 	el = -90;
 	eq = -54.9;
 	ekf = -90;
 	_prop->param = _p;
 	_prop->param_size = 29;
 	_ppvar = nrn_prop_datum_alloc(_mechtype, 1, _prop);
 	_prop->dparam = _ppvar;
 	/*connect ionic variables to this model*/
 
}
 static void _initlists();
  /* some states have an absolute tolerance */
 static Symbol** _atollist;
 static HocStateTolerance _hoc_state_tol[] = {
 0,0
};
 extern Symbol* hoc_lookup(const char*);
extern void _nrn_thread_reg(int, int, void(*)(Datum*));
extern void _nrn_thread_table_reg(int, void(*)(double*, Datum*, Datum*, _NrnThread*, int));
extern void hoc_register_tolerance(int, HocStateTolerance*, Symbol***);
extern void _cvode_abstol( Symbol**, double*, int);

 void _mysa_sensory_reg() {
	int _vectorized = 1;
  _initlists();
 	register_mech(_mechanism, nrn_alloc,nrn_cur, nrn_jacob, nrn_state, nrn_init, hoc_nrnpointerindex, 1);
 _mechtype = nrn_get_mechtype(_mechanism[1]);
     _nrn_setdata_reg(_mechtype, _setdata);
 #if NMODL_TEXT
  hoc_reg_nmodl_text(_mechtype, nmodl_file_text);
  hoc_reg_nmodl_filename(_mechtype, nmodl_filename);
#endif
  hoc_register_prop_size(_mechtype, 29, 1);
  hoc_register_dparam_semantics(_mechtype, 0, "cvodeieq");
 	hoc_register_cvode(_mechtype, _ode_count, _ode_map, _ode_spec, _ode_matsol);
 	hoc_register_tolerance(_mechtype, _hoc_state_tol, &_atollist);
 	hoc_register_var(hoc_scdoub, hoc_vdoub, hoc_intfunc);
 	ivoc_help("help ?1 mysa_sensory /Users/louisregnacq/Dropbox/Work/Model/NRV/NRV/nrv/mods/mysa_sensory.mod\n");
 hoc_register_limits(_mechtype, _hoc_parm_limits);
 hoc_register_units(_mechtype, _hoc_parm_units);
 }
static int _reset;
static char *modelname = "Motor Axon MYSA channels";

static int error;
static int _ninits = 0;
static int _match_recurse=1;
static void _modl_cleanup(){ _match_recurse=1;}
static int evaluate_fct(_threadargsprotocomma_ double);
 
static int _ode_spec1(_threadargsproto_);
/*static int _ode_matsol1(_threadargsproto_);*/
 static int _slist1[3], _dlist1[3];
 static int states(_threadargsproto_);
 
/*CVODE*/
 static int _ode_spec1 (double* _p, Datum* _ppvar, Datum* _thread, _NrnThread* _nt) {int _reset = 0; {
   evaluate_fct ( _threadargscomma_ v ) ;
   Ds = ( s_inf - s ) / tau_s ;
   Dq = ( q_inf - q ) / tau_q ;
   Dn = ( n_inf - n ) / tau_n ;
   }
 return _reset;
}
 static int _ode_matsol1 (double* _p, Datum* _ppvar, Datum* _thread, _NrnThread* _nt) {
 evaluate_fct ( _threadargscomma_ v ) ;
 Ds = Ds  / (1. - dt*( ( ( ( - 1.0 ) ) ) / tau_s )) ;
 Dq = Dq  / (1. - dt*( ( ( ( - 1.0 ) ) ) / tau_q )) ;
 Dn = Dn  / (1. - dt*( ( ( ( - 1.0 ) ) ) / tau_n )) ;
  return 0;
}
 /*END CVODE*/
 static int states (double* _p, Datum* _ppvar, Datum* _thread, _NrnThread* _nt) { {
   evaluate_fct ( _threadargscomma_ v ) ;
    s = s + (1. - exp(dt*(( ( ( - 1.0 ) ) ) / tau_s)))*(- ( ( ( s_inf ) ) / tau_s ) / ( ( ( ( - 1.0 ) ) ) / tau_s ) - s) ;
    q = q + (1. - exp(dt*(( ( ( - 1.0 ) ) ) / tau_q)))*(- ( ( ( q_inf ) ) / tau_q ) / ( ( ( ( - 1.0 ) ) ) / tau_q ) - q) ;
    n = n + (1. - exp(dt*(( ( ( - 1.0 ) ) ) / tau_n)))*(- ( ( ( n_inf ) ) / tau_n ) / ( ( ( ( - 1.0 ) ) ) / tau_n ) - n) ;
   }
  return 0;
}
 
static int  evaluate_fct ( _threadargsprotocomma_ double _lv ) {
   double _la , _lb , _lv2 ;
 _lv2 = _lv - vtraub ;
   _la = q10_3 * asA / ( Exp ( _threadargscomma_ ( _lv2 + asB ) / asC ) + 1.0 ) ;
   _lb = q10_3 * bsA / ( Exp ( _threadargscomma_ ( _lv2 + bsB ) / bsC ) + 1.0 ) ;
   tau_s = 1.0 / ( _la + _lb ) ;
   s_inf = _la / ( _la + _lb ) ;
   _la = q10_3 * aqA * ( Exp ( _threadargscomma_ ( _lv - aqB ) / aqC ) ) ;
   _lb = q10_3 * bqA / ( Exp ( _threadargscomma_ ( _lv - bqB ) / bqC ) ) ;
   tau_q = 1.0 / ( _la + _lb ) ;
   q_inf = _la / ( _la + _lb ) ;
   _la = q10_3 * vtrapNA ( _threadargscomma_ _lv ) ;
   _lb = q10_3 * vtrapNB ( _threadargscomma_ _lv ) ;
   tau_n = 1.0 / ( _la + _lb ) ;
   n_inf = _la / ( _la + _lb ) ;
    return 0; }
 
static void _hoc_evaluate_fct(void) {
  double _r;
   double* _p; Datum* _ppvar; Datum* _thread; _NrnThread* _nt;
   if (_extcall_prop) {_p = _extcall_prop->param; _ppvar = _extcall_prop->dparam;}else{ _p = (double*)0; _ppvar = (Datum*)0; }
  _thread = _extcall_thread;
  _nt = nrn_threads;
 _r = 1.;
 evaluate_fct ( _p, _ppvar, _thread, _nt, *getarg(1) );
 hoc_retpushx(_r);
}
 
double vtrapNA ( _threadargsprotocomma_ double _lx ) {
   double _lvtrapNA;
 if ( fabs ( ( anB - _lx ) / anC ) < 1e-6 ) {
     _lvtrapNA = anA * anC ;
     }
   else {
     _lvtrapNA = anA * ( v - anB ) / ( 1.0 - Exp ( _threadargscomma_ ( anB - v ) / anC ) ) ;
     }
   
return _lvtrapNA;
 }
 
static void _hoc_vtrapNA(void) {
  double _r;
   double* _p; Datum* _ppvar; Datum* _thread; _NrnThread* _nt;
   if (_extcall_prop) {_p = _extcall_prop->param; _ppvar = _extcall_prop->dparam;}else{ _p = (double*)0; _ppvar = (Datum*)0; }
  _thread = _extcall_thread;
  _nt = nrn_threads;
 _r =  vtrapNA ( _p, _ppvar, _thread, _nt, *getarg(1) );
 hoc_retpushx(_r);
}
 
double vtrapNB ( _threadargsprotocomma_ double _lx ) {
   double _lvtrapNB;
 if ( fabs ( ( _lx - bnB ) / bnC ) < 1e-6 ) {
     _lvtrapNB = bnA * bnC ;
     }
   else {
     _lvtrapNB = bnA * ( bnB - v ) / ( 1.0 - Exp ( _threadargscomma_ ( v - bnB ) / bnC ) ) ;
     }
   
return _lvtrapNB;
 }
 
static void _hoc_vtrapNB(void) {
  double _r;
   double* _p; Datum* _ppvar; Datum* _thread; _NrnThread* _nt;
   if (_extcall_prop) {_p = _extcall_prop->param; _ppvar = _extcall_prop->dparam;}else{ _p = (double*)0; _ppvar = (Datum*)0; }
  _thread = _extcall_thread;
  _nt = nrn_threads;
 _r =  vtrapNB ( _p, _ppvar, _thread, _nt, *getarg(1) );
 hoc_retpushx(_r);
}
 
double Exp ( _threadargsprotocomma_ double _lx ) {
   double _lExp;
 if ( _lx < - 100.0 ) {
     _lExp = 0.0 ;
     }
   else {
     _lExp = exp ( _lx ) ;
     }
   
return _lExp;
 }
 
static void _hoc_Exp(void) {
  double _r;
   double* _p; Datum* _ppvar; Datum* _thread; _NrnThread* _nt;
   if (_extcall_prop) {_p = _extcall_prop->param; _ppvar = _extcall_prop->dparam;}else{ _p = (double*)0; _ppvar = (Datum*)0; }
  _thread = _extcall_thread;
  _nt = nrn_threads;
 _r =  Exp ( _p, _ppvar, _thread, _nt, *getarg(1) );
 hoc_retpushx(_r);
}
 
static int _ode_count(int _type){ return 3;}
 
static void _ode_spec(_NrnThread* _nt, _Memb_list* _ml, int _type) {
   double* _p; Datum* _ppvar; Datum* _thread;
   Node* _nd; double _v; int _iml, _cntml;
  _cntml = _ml->_nodecount;
  _thread = _ml->_thread;
  for (_iml = 0; _iml < _cntml; ++_iml) {
    _p = _ml->_data[_iml]; _ppvar = _ml->_pdata[_iml];
    _nd = _ml->_nodelist[_iml];
    v = NODEV(_nd);
     _ode_spec1 (_p, _ppvar, _thread, _nt);
 }}
 
static void _ode_map(int _ieq, double** _pv, double** _pvdot, double* _pp, Datum* _ppd, double* _atol, int _type) { 
	double* _p; Datum* _ppvar;
 	int _i; _p = _pp; _ppvar = _ppd;
	_cvode_ieq = _ieq;
	for (_i=0; _i < 3; ++_i) {
		_pv[_i] = _pp + _slist1[_i];  _pvdot[_i] = _pp + _dlist1[_i];
		_cvode_abstol(_atollist, _atol, _i);
	}
 }
 
static void _ode_matsol_instance1(_threadargsproto_) {
 _ode_matsol1 (_p, _ppvar, _thread, _nt);
 }
 
static void _ode_matsol(_NrnThread* _nt, _Memb_list* _ml, int _type) {
   double* _p; Datum* _ppvar; Datum* _thread;
   Node* _nd; double _v; int _iml, _cntml;
  _cntml = _ml->_nodecount;
  _thread = _ml->_thread;
  for (_iml = 0; _iml < _cntml; ++_iml) {
    _p = _ml->_data[_iml]; _ppvar = _ml->_pdata[_iml];
    _nd = _ml->_nodelist[_iml];
    v = NODEV(_nd);
 _ode_matsol_instance1(_threadargs_);
 }}

static void initmodel(double* _p, Datum* _ppvar, Datum* _thread, _NrnThread* _nt) {
  int _i; double _save;{
  n = n0;
  q = q0;
  s = s0;
 {
   q10_1 = pow( 2.2 , ( ( celsius - 20.0 ) / 10.0 ) ) ;
   q10_2 = pow( 2.9 , ( ( celsius - 20.0 ) / 10.0 ) ) ;
   q10_3 = pow( 3.0 , ( ( celsius - 36.0 ) / 10.0 ) ) ;
   evaluate_fct ( _threadargscomma_ v ) ;
   s = s_inf ;
   q = q_inf ;
   n = n_inf ;
   }
 
}
}

static void nrn_init(_NrnThread* _nt, _Memb_list* _ml, int _type){
double* _p; Datum* _ppvar; Datum* _thread;
Node *_nd; double _v; int* _ni; int _iml, _cntml;
#if CACHEVEC
    _ni = _ml->_nodeindices;
#endif
_cntml = _ml->_nodecount;
_thread = _ml->_thread;
for (_iml = 0; _iml < _cntml; ++_iml) {
 _p = _ml->_data[_iml]; _ppvar = _ml->_pdata[_iml];
#if CACHEVEC
  if (use_cachevec) {
    _v = VEC_V(_ni[_iml]);
  }else
#endif
  {
    _nd = _ml->_nodelist[_iml];
    _v = NODEV(_nd);
  }
 v = _v;
 initmodel(_p, _ppvar, _thread, _nt);
}
}

static double _nrn_current(double* _p, Datum* _ppvar, Datum* _thread, _NrnThread* _nt, double _v){double _current=0.;v=_v;{ {
   ik = gkbar * s * ( v - ek ) ;
   il = gl * ( v - el ) ;
   iq = gq * q * ( v - eq ) ;
   ikf = gkf * n * n * n * n * ( v - ekf ) ;
   }
 _current += ik;
 _current += il;
 _current += iq;
 _current += ikf;

} return _current;
}

static void nrn_cur(_NrnThread* _nt, _Memb_list* _ml, int _type) {
double* _p; Datum* _ppvar; Datum* _thread;
Node *_nd; int* _ni; double _rhs, _v; int _iml, _cntml;
#if CACHEVEC
    _ni = _ml->_nodeindices;
#endif
_cntml = _ml->_nodecount;
_thread = _ml->_thread;
for (_iml = 0; _iml < _cntml; ++_iml) {
 _p = _ml->_data[_iml]; _ppvar = _ml->_pdata[_iml];
#if CACHEVEC
  if (use_cachevec) {
    _v = VEC_V(_ni[_iml]);
  }else
#endif
  {
    _nd = _ml->_nodelist[_iml];
    _v = NODEV(_nd);
  }
 _g = _nrn_current(_p, _ppvar, _thread, _nt, _v + .001);
 	{ _rhs = _nrn_current(_p, _ppvar, _thread, _nt, _v);
 	}
 _g = (_g - _rhs)/.001;
#if CACHEVEC
  if (use_cachevec) {
	VEC_RHS(_ni[_iml]) -= _rhs;
  }else
#endif
  {
	NODERHS(_nd) -= _rhs;
  }
 
}
 
}

static void nrn_jacob(_NrnThread* _nt, _Memb_list* _ml, int _type) {
double* _p; Datum* _ppvar; Datum* _thread;
Node *_nd; int* _ni; int _iml, _cntml;
#if CACHEVEC
    _ni = _ml->_nodeindices;
#endif
_cntml = _ml->_nodecount;
_thread = _ml->_thread;
for (_iml = 0; _iml < _cntml; ++_iml) {
 _p = _ml->_data[_iml];
#if CACHEVEC
  if (use_cachevec) {
	VEC_D(_ni[_iml]) += _g;
  }else
#endif
  {
     _nd = _ml->_nodelist[_iml];
	NODED(_nd) += _g;
  }
 
}
 
}

static void nrn_state(_NrnThread* _nt, _Memb_list* _ml, int _type) {
double* _p; Datum* _ppvar; Datum* _thread;
Node *_nd; double _v = 0.0; int* _ni; int _iml, _cntml;
#if CACHEVEC
    _ni = _ml->_nodeindices;
#endif
_cntml = _ml->_nodecount;
_thread = _ml->_thread;
for (_iml = 0; _iml < _cntml; ++_iml) {
 _p = _ml->_data[_iml]; _ppvar = _ml->_pdata[_iml];
 _nd = _ml->_nodelist[_iml];
#if CACHEVEC
  if (use_cachevec) {
    _v = VEC_V(_ni[_iml]);
  }else
#endif
  {
    _nd = _ml->_nodelist[_iml];
    _v = NODEV(_nd);
  }
 v=_v;
{
 {   states(_p, _ppvar, _thread, _nt);
  }}}

}

static void terminal(){}

static void _initlists(){
 double _x; double* _p = &_x;
 int _i; static int _first = 1;
  if (!_first) return;
 _slist1[0] = &(s) - _p;  _dlist1[0] = &(Ds) - _p;
 _slist1[1] = &(q) - _p;  _dlist1[1] = &(Dq) - _p;
 _slist1[2] = &(n) - _p;  _dlist1[2] = &(Dn) - _p;
_first = 0;
}

#if defined(__cplusplus)
} /* extern "C" */
#endif

#if NMODL_TEXT
static const char* nmodl_filename = "/Users/louisregnacq/Dropbox/Work/Model/NRV/NRV/nrv/mods/mysa_sensory.mod";
static const char* nmodl_file_text = 
  "TITLE Motor Axon MYSA channels\n"
  "\n"
  ": 06/16\n"
  ": Jessica Gaines\n"
  ":\n"
  ": Modification of channel properties\n"
  ":\n"
  ": 04/15\n"
  ": Lane Heyboer\n"
  ":\n"
  ": Fast K+ current\n"
  ": Ih current\n"
  ":\n"
  ": 02/02\n"
  ": Cameron C. McIntyre\n"
  ":\n"
  ": Fast Na+, Persistant Na+, Slow K+, and Leakage currents \n"
  ": responsible for nodal action potential\n"
  ": Iterative equations H-H notation rest = -80 mV\n"
  ":\n"
  ": This model is described in detail in:\n"
  ": \n"
  ": Gaines JS, Finn KE, Slopsema JP, Heyboer LA, Polasek KH. A Model of \n"
  ": Motor and Sensory Axon Activation in the Median Nerve Using Surface \n"
  ": Electrical Stimulation. Journal of Computational Neuroscience, 2018.\n"
  ":\n"
  ": McIntyre CC, Richardson AG, and Grill WM. Modeling the excitability of\n"
  ": mammalian nerve fibers: influence of afterpotentials on the recovery\n"
  ": cycle. Journal of Neurophysiology 87:995-1006, 2002.\n"
  "\n"
  "INDEPENDENT {t FROM 0 TO 1 WITH 1 (ms)}\n"
  "\n"
  "NEURON {\n"
  "	SUFFIX mysa_sensory\n"
  "	NONSPECIFIC_CURRENT ik\n"
  "	NONSPECIFIC_CURRENT il\n"
  "	NONSPECIFIC_CURRENT iq\n"
  "	NONSPECIFIC_CURRENT ikf\n"
  "	RANGE gkbar, gl, gq, gkf, ek, el, eq, ekf\n"
  "	RANGE s_inf, q_inf, n_inf\n"
  "	RANGE tau_s, tau_q, tau_n\n"
  "}\n"
  "\n"
  "\n"
  "UNITS {\n"
  "	(mA) = (milliamp)\n"
  "	(mV) = (millivolt)\n"
  "}\n"
  "\n"
  "PARAMETER {\n"
  "\n"
  "    : channel conductances\n"
  "	gkbar   = 0.001324 (mho/cm2)\n"
  "	gl	= 0.001716 (mho/cm2)\n"
  "	gq	= 0.003102 (mho/cm2)\n"
  "	gkf	= 0.1642 (mho/cm2)\n"
  "\n"
  "    : reversal potentials\n"
  "	ek      = -90.0 (mV)\n"
  "	el	= -90.0 (mV)\n"
  "	eq	= -54.9 (mV)\n"
  "	ekf	= -90.0 (mV)\n"
  "\n"
  "    : read in from .hoc file\n"
  "	celsius		(degC)\n"
  "	dt              (ms)\n"
  "	v               (mV)\n"
  "	vtraub=-80\n"
  "\n"
  "    : parameters determining rate constants\n"
  "\n"
  "    : slow K+\n"
  "	asA = 0.3\n"
  "	asB = -27\n"
  "	asC = -5\n"
  "	bsA = 0.03\n"
  "	bsB = 10\n"
  "	bsC = -1\n"
  "\n"
  "    : HCN\n"
  "	aqA = .00522\n"
  "	aqB = -94.2\n"
  "	aqC = -12.2\n"
  "	bqA = .00522\n"
  "	bqB = -94.2\n"
  "	bqC = -12.2\n"
  "   \n"
  "    : fast K+\n"
  "	anA = 0.0462\n"
  "	anB = -83.2\n"
  "	anC = 1.1\n"
  "	bnA = 0.0824\n"
  "	bnB = -66\n"
  "	bnC = 10.5\n"
  "}\n"
  "\n"
  "STATE {\n"
  "	s q n\n"
  "}\n"
  "\n"
  "ASSIGNED {\n"
  "	ik      (mA/cm2)\n"
  "	il      (mA/cm2)\n"
  "	iq	(mA/cm2)\n"
  "	ikf	(mA/cm2)\n"
  "	s_inf\n"
  "	q_inf\n"
  "	n_inf\n"
  "	tau_s\n"
  "	tau_q\n"
  "	tau_n\n"
  "	q10_1\n"
  "	q10_2\n"
  "	q10_3\n"
  "}\n"
  "\n"
  "BREAKPOINT {\n"
  "	SOLVE states METHOD cnexp\n"
  "	ik   = gkbar * s * (v - ek)\n"
  "	il   = gl * (v - el)\n"
  "	iq = gq * q * (v-eq)\n"
  "	ikf = gkf * n*n*n*n* (v-ekf)\n"
  "}\n"
  "\n"
  "DERIVATIVE states {   : exact Hodgkin-Huxley equations\n"
  "       evaluate_fct(v)\n"
  "	s' = (s_inf - s) / tau_s\n"
  "	q' = (q_inf - q) / tau_q\n"
  "	n' = (n_inf - n) / tau_n\n"
  "}\n"
  "\n"
  "UNITSOFF\n"
  "\n"
  "INITIAL {\n"
  ":\n"
  ":	Q10 adjustment\n"
  ":   Temperature dependence\n"
  ":\n"
  "\n"
  "	q10_1 = 2.2 ^ ((celsius-20)/ 10 )\n"
  "	q10_2 = 2.9 ^ ((celsius-20)/ 10 )\n"
  "	q10_3 = 3.0 ^ ((celsius-36)/ 10 )\n"
  "\n"
  "	evaluate_fct(v)\n"
  "	s = s_inf\n"
  "	q = q_inf\n"
  "	n = n_inf\n"
  "}\n"
  "\n"
  "PROCEDURE evaluate_fct(v(mV)) { LOCAL a,b,v2\n"
  "\n"
  "	v2 = v - vtraub : convert to traub convention\n"
  "\n"
  "    : slow K+\n"
  "	a = q10_3*asA / (Exp((v2+asB)/asC) + 1) \n"
  "	b = q10_3*bsA / (Exp((v2+bsB)/bsC) + 1)\n"
  "	tau_s = 1 / (a + b)\n"
  "	s_inf = a / (a + b)\n"
  "\n"
  "    : HCN\n"
  "	a = q10_3*aqA * (Exp((v-aqB)/aqC)) \n"
  "	b = q10_3*bqA / (Exp((v-bqB)/bqC))\n"
  "	tau_q = 1 / (a + b)\n"
  "	q_inf = a / (a + b)\n"
  "\n"
  "    : fast K+\n"
  "	a = q10_3*vtrapNA(v)\n"
  "	b = q10_3*vtrapNB(v)\n"
  "	tau_n = 1 / (a + b)\n"
  "	n_inf = a / (a + b)\n"
  "}\n"
  "\n"
  ": vtrap functions to prevent discontinuity\n"
  "FUNCTION vtrapNA(x){\n"
  "    if(fabs((anB - x)/anC) < 1e-6){\n"
  "        vtrapNA = anA*anC\n"
  "    }else{\n"
  "        vtrapNA = anA*(v-anB)/(1-Exp((anB-v)/anC))\n"
  "    }\n"
  "}\n"
  "\n"
  "FUNCTION vtrapNB(x){\n"
  "    if(fabs((x - bnB)/bnC) < 1e-6){\n"
  "        vtrapNB = bnA*bnC  \n"
  "    }else{\n"
  "        vtrapNB = bnA*(bnB-v)/(1-Exp((v-bnB)/bnC))\n"
  "    }\n"
  "}\n"
  "\n"
  "FUNCTION Exp(x) {\n"
  "	if (x < -100) {\n"
  "		Exp = 0\n"
  "	}else{\n"
  "		Exp = exp(x)\n"
  "	}\n"
  "}\n"
  "\n"
  "UNITSON\n"
  ;
#endif
