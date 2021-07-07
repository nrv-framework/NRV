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
 
#define nrn_init _nrn_init__kaslow
#define _nrn_initial _nrn_initial__kaslow
#define nrn_cur _nrn_cur__kaslow
#define _nrn_current _nrn_current__kaslow
#define nrn_jacob _nrn_jacob__kaslow
#define nrn_state _nrn_state__kaslow
#define _net_receive _net_receive__kaslow 
#define rates rates__kaslow 
#define states states__kaslow 
 
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
#define gbar _p[0]
#define gka _p[1]
#define ik _p[2]
#define ninf _p[3]
#define ntau _p[4]
#define hinf _p[5]
#define h1tau _p[6]
#define h2tau _p[7]
#define n _p[8]
#define h1 _p[9]
#define h2 _p[10]
#define Dn _p[11]
#define Dh1 _p[12]
#define Dh2 _p[13]
#define ek _p[14]
#define v _p[15]
#define _g _p[16]
#define _ion_ek	*_ppvar[0]._pval
#define _ion_ik	*_ppvar[1]._pval
#define _ion_dikdv	*_ppvar[2]._pval
 
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
 /* declaration of user functions */
 static void _hoc_rates(void);
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
 "setdata_kaslow", _hoc_setdata,
 "rates_kaslow", _hoc_rates,
 0, 0
};
 /* declare global and static user variables */
#define AN AN_kaslow
 double AN = 1.1972;
#define A2 A2_kaslow
 double A2 = 200;
#define A1 A1_kaslow
 double A1 = 25.46;
#define BN BN_kaslow
 double BN = 2.56;
#define B2 B2_kaslow
 double B2 = 587.4;
#define B1 B1_kaslow
 double B1 = 67.41;
#define frac2 frac2_kaslow
 double frac2 = 0.7;
#define frac1 frac1_kaslow
 double frac1 = 0.3;
#define vh2 vh2_kaslow
 double vh2 = 74.2;
#define vh1 vh1_kaslow
 double vh1 = -40.8;
#define xcN xcN_kaslow
 double xcN = 60;
#define xc2 xc2_kaslow
 double xc2 = 0;
#define xc1 xc1_kaslow
 double xc1 = 50;
#define ycN ycN_kaslow
 double ycN = 45.7599;
#define yc2 yc2_kaslow
 double yc2 = 47.77;
#define yc1 yc1_kaslow
 double yc1 = 21.95;
 /* some parameters have upper and lower limits */
 static HocParmLimits _hoc_parm_limits[] = {
 0,0,0
};
 static HocParmUnits _hoc_parm_units[] = {
 "vh1_kaslow", "mV",
 "vh2_kaslow", "mV",
 "gbar_kaslow", "S/cm2",
 "gka_kaslow", "S/cm2",
 "ik_kaslow", "mA/cm2",
 "ntau_kaslow", "ms",
 "h1tau_kaslow", "ms",
 "h2tau_kaslow", "ms",
 0,0
};
 static double delta_t = 0.01;
 static double h20 = 0;
 static double h10 = 0;
 static double n0 = 0;
 /* connect global user variables to hoc */
 static DoubScal hoc_scdoub[] = {
 "A1_kaslow", &A1_kaslow,
 "B1_kaslow", &B1_kaslow,
 "xc1_kaslow", &xc1_kaslow,
 "yc1_kaslow", &yc1_kaslow,
 "A2_kaslow", &A2_kaslow,
 "B2_kaslow", &B2_kaslow,
 "xc2_kaslow", &xc2_kaslow,
 "yc2_kaslow", &yc2_kaslow,
 "AN_kaslow", &AN_kaslow,
 "BN_kaslow", &BN_kaslow,
 "xcN_kaslow", &xcN_kaslow,
 "ycN_kaslow", &ycN_kaslow,
 "vh1_kaslow", &vh1_kaslow,
 "vh2_kaslow", &vh2_kaslow,
 "frac1_kaslow", &frac1_kaslow,
 "frac2_kaslow", &frac2_kaslow,
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
 
#define _cvode_ieq _ppvar[3]._i
 static void _ode_matsol_instance1(_threadargsproto_);
 /* connect range variables in _p that hoc is supposed to know about */
 static const char *_mechanism[] = {
 "7.7.0",
"kaslow",
 "gbar_kaslow",
 0,
 "gka_kaslow",
 "ik_kaslow",
 "ninf_kaslow",
 "ntau_kaslow",
 "hinf_kaslow",
 "h1tau_kaslow",
 "h2tau_kaslow",
 0,
 "n_kaslow",
 "h1_kaslow",
 "h2_kaslow",
 0,
 0};
 static Symbol* _k_sym;
 
extern Prop* need_memb(Symbol*);

static void nrn_alloc(Prop* _prop) {
	Prop *prop_ion;
	double *_p; Datum *_ppvar;
 	_p = nrn_prop_data_alloc(_mechtype, 17, _prop);
 	/*initialize range parameters*/
 	gbar = 0.00136;
 	_prop->param = _p;
 	_prop->param_size = 17;
 	_ppvar = nrn_prop_datum_alloc(_mechtype, 4, _prop);
 	_prop->dparam = _ppvar;
 	/*connect ionic variables to this model*/
 prop_ion = need_memb(_k_sym);
 nrn_promote(prop_ion, 0, 1);
 	_ppvar[0]._pval = &prop_ion->param[0]; /* ek */
 	_ppvar[1]._pval = &prop_ion->param[3]; /* ik */
 	_ppvar[2]._pval = &prop_ion->param[4]; /* _ion_dikdv */
 
}
 static void _initlists();
  /* some states have an absolute tolerance */
 static Symbol** _atollist;
 static HocStateTolerance _hoc_state_tol[] = {
 0,0
};
 static void _update_ion_pointer(Datum*);
 extern Symbol* hoc_lookup(const char*);
extern void _nrn_thread_reg(int, int, void(*)(Datum*));
extern void _nrn_thread_table_reg(int, void(*)(double*, Datum*, Datum*, _NrnThread*, int));
extern void hoc_register_tolerance(int, HocStateTolerance*, Symbol***);
extern void _cvode_abstol( Symbol**, double*, int);

 void _kaslow_reg() {
	int _vectorized = 1;
  _initlists();
 	ion_reg("k", -10000.);
 	_k_sym = hoc_lookup("k_ion");
 	register_mech(_mechanism, nrn_alloc,nrn_cur, nrn_jacob, nrn_state, nrn_init, hoc_nrnpointerindex, 1);
 _mechtype = nrn_get_mechtype(_mechanism[1]);
     _nrn_setdata_reg(_mechtype, _setdata);
     _nrn_thread_reg(_mechtype, 2, _update_ion_pointer);
 #if NMODL_TEXT
  hoc_reg_nmodl_text(_mechtype, nmodl_file_text);
  hoc_reg_nmodl_filename(_mechtype, nmodl_filename);
#endif
  hoc_register_prop_size(_mechtype, 17, 4);
  hoc_register_dparam_semantics(_mechtype, 0, "k_ion");
  hoc_register_dparam_semantics(_mechtype, 1, "k_ion");
  hoc_register_dparam_semantics(_mechtype, 2, "k_ion");
  hoc_register_dparam_semantics(_mechtype, 3, "cvodeieq");
 	hoc_register_cvode(_mechtype, _ode_count, _ode_map, _ode_spec, _ode_matsol);
 	hoc_register_tolerance(_mechtype, _hoc_state_tol, &_atollist);
 	hoc_register_var(hoc_scdoub, hoc_vdoub, hoc_intfunc);
 	ivoc_help("help ?1 kaslow /Users/fkolbl/Desktop/NRV2/src/mods/kaslow.mod\n");
 hoc_register_limits(_mechtype, _hoc_parm_limits);
 hoc_register_units(_mechtype, _hoc_parm_units);
 }
static int _reset;
static char *modelname = "Slow KA Current for bladder small DRG neuron soma model";

static int error;
static int _ninits = 0;
static int _match_recurse=1;
static void _modl_cleanup(){ _match_recurse=1;}
static int rates(_threadargsprotocomma_ double);
 
static int _ode_spec1(_threadargsproto_);
/*static int _ode_matsol1(_threadargsproto_);*/
 static int _slist1[3], _dlist1[3];
 static int states(_threadargsproto_);
 
/*CVODE*/
 static int _ode_spec1 (double* _p, Datum* _ppvar, Datum* _thread, _NrnThread* _nt) {int _reset = 0; {
   rates ( _threadargscomma_ v ) ;
   Dn = ( ninf - n ) / ntau ;
   Dh1 = ( hinf - h1 ) / h1tau ;
   Dh2 = ( hinf - h2 ) / h2tau ;
   }
 return _reset;
}
 static int _ode_matsol1 (double* _p, Datum* _ppvar, Datum* _thread, _NrnThread* _nt) {
 rates ( _threadargscomma_ v ) ;
 Dn = Dn  / (1. - dt*( ( ( ( - 1.0 ) ) ) / ntau )) ;
 Dh1 = Dh1  / (1. - dt*( ( ( ( - 1.0 ) ) ) / h1tau )) ;
 Dh2 = Dh2  / (1. - dt*( ( ( ( - 1.0 ) ) ) / h2tau )) ;
  return 0;
}
 /*END CVODE*/
 static int states (double* _p, Datum* _ppvar, Datum* _thread, _NrnThread* _nt) { {
   rates ( _threadargscomma_ v ) ;
    n = n + (1. - exp(dt*(( ( ( - 1.0 ) ) ) / ntau)))*(- ( ( ( ninf ) ) / ntau ) / ( ( ( ( - 1.0 ) ) ) / ntau ) - n) ;
    h1 = h1 + (1. - exp(dt*(( ( ( - 1.0 ) ) ) / h1tau)))*(- ( ( ( hinf ) ) / h1tau ) / ( ( ( ( - 1.0 ) ) ) / h1tau ) - h1) ;
    h2 = h2 + (1. - exp(dt*(( ( ( - 1.0 ) ) ) / h2tau)))*(- ( ( ( hinf ) ) / h2tau ) / ( ( ( ( - 1.0 ) ) ) / h2tau ) - h2) ;
   }
  return 0;
}
 
static int  rates ( _threadargsprotocomma_ double _lv ) {
    ninf = ( 1.0 / ( 1.0 + exp ( ( vh1 - _lv ) / 9.5 ) ) ) ;
   ntau = AN + BN * exp ( - 2.0 * pow( ( ( _lv + xcN ) / ycN ) , 2.0 ) ) ;
   hinf = 1.0 / ( 1.0 + exp ( ( _lv + vh2 ) / 9.6 ) ) ;
   h1tau = A1 + B1 * exp ( - 2.0 * pow( ( ( _lv + xc1 ) / yc1 ) , 2.0 ) ) ;
   h2tau = A2 + B2 * exp ( - pow( ( ( _lv - xc2 ) / yc2 ) , 2.0 ) ) ;
    return 0; }
 
static void _hoc_rates(void) {
  double _r;
   double* _p; Datum* _ppvar; Datum* _thread; _NrnThread* _nt;
   if (_extcall_prop) {_p = _extcall_prop->param; _ppvar = _extcall_prop->dparam;}else{ _p = (double*)0; _ppvar = (Datum*)0; }
  _thread = _extcall_thread;
  _nt = nrn_threads;
 _r = 1.;
 rates ( _p, _ppvar, _thread, _nt, *getarg(1) );
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
  ek = _ion_ek;
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
  ek = _ion_ek;
 _ode_matsol_instance1(_threadargs_);
 }}
 extern void nrn_update_ion_pointer(Symbol*, Datum*, int, int);
 static void _update_ion_pointer(Datum* _ppvar) {
   nrn_update_ion_pointer(_k_sym, _ppvar, 0, 0);
   nrn_update_ion_pointer(_k_sym, _ppvar, 1, 3);
   nrn_update_ion_pointer(_k_sym, _ppvar, 2, 4);
 }

static void initmodel(double* _p, Datum* _ppvar, Datum* _thread, _NrnThread* _nt) {
  int _i; double _save;{
  h2 = h20;
  h1 = h10;
  n = n0;
 {
   rates ( _threadargscomma_ v ) ;
   n = ninf ;
   h1 = hinf ;
   h2 = hinf ;
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
  ek = _ion_ek;
 initmodel(_p, _ppvar, _thread, _nt);
 }
}

static double _nrn_current(double* _p, Datum* _ppvar, Datum* _thread, _NrnThread* _nt, double _v){double _current=0.;v=_v;{ {
   gka = gbar * n * ( h1 * frac1 + h2 * frac2 ) ;
   ik = gka * ( v - ek ) ;
   }
 _current += ik;

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
  ek = _ion_ek;
 _g = _nrn_current(_p, _ppvar, _thread, _nt, _v + .001);
 	{ double _dik;
  _dik = ik;
 _rhs = _nrn_current(_p, _ppvar, _thread, _nt, _v);
  _ion_dikdv += (_dik - ik)/.001 ;
 	}
 _g = (_g - _rhs)/.001;
  _ion_ik += ik ;
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
  ek = _ion_ek;
 {   states(_p, _ppvar, _thread, _nt);
  } }}

}

static void terminal(){}

static void _initlists(){
 double _x; double* _p = &_x;
 int _i; static int _first = 1;
  if (!_first) return;
 _slist1[0] = &(n) - _p;  _dlist1[0] = &(Dn) - _p;
 _slist1[1] = &(h1) - _p;  _dlist1[1] = &(Dh1) - _p;
 _slist1[2] = &(h2) - _p;  _dlist1[2] = &(Dh2) - _p;
_first = 0;
}

#if defined(__cplusplus)
} /* extern "C" */
#endif

#if NMODL_TEXT
static const char* nmodl_filename = "/Users/fkolbl/Desktop/NRV2/src/mods/kaslow.mod";
static const char* nmodl_file_text = 
  "TITLE Slow KA Current for bladder small DRG neuron soma model\n"
  ": Author: Darshan Mandge (darshanmandge@iitb.ac.in)\n"
  ": Computational Neurophysiology Lab\n"
  ": Indian Institute of Technology Bombay, India \n"
  "\n"
  ": For details refer: \n"
  ": A biophysically detailed computational model of bladder small DRG neuron soma \n"
  ": Darshan Mandge and Rohit Manchanda, PLOS Computational Biology (2018)\n"
  "\n"
  "\n"
  "UNITS {\n"
  "    (mA) = (milliamp)\n"
  "    (mV) = (millivolt)\n"
  "	(S) = (siemens)\n"
  "}\n"
  "\n"
  "NEURON {\n"
  "	SUFFIX kaslow\n"
  "	USEION k READ ek WRITE ik\n"
  "	RANGE gbar, gka, ik\n"
  "	RANGE ninf, ntau, hinf, h1tau, h2tau\n"
  "	THREADSAFE\n"
  "}\n"
  " \n"
  "PARAMETER {\n"
  "        gbar = 0.00136 (S/cm2)\n"
  "		\n"
  "		A1 = 25.46\n"
  "		B1 = 67.41\n"
  "		xc1 = 50\n"
  "		yc1 = 21.95\n"
  "		\n"
  "		A2 = 200\n"
  "		B2 = 587.4\n"
  "		xc2 = 0\n"
  "		yc2 = 47.77\n"
  "		\n"
  "		AN =  1.1972\n"
  "		BN = 2.56\n"
  "		xcN = 60\n"
  "		ycN = 45.75992\n"
  "		\n"
  "		vh1 = -40.8 (mV)\n"
  "		vh2 = 74.2 (mV)\n"
  "		\n"
  "		frac1 = 0.3\n"
  "		frac2 = 0.7\n"
  "}\n"
  " \n"
  "STATE {\n"
  "        n 	: activation\n"
  "		h1  : fast inactivation\n"
  "		h2	: slow inactivation\n"
  "}\n"
  " \n"
  "ASSIGNED {\n"
  "	v (mV)\n"
  "	ek (mV)\n"
  "	gka (S/cm2)\n"
  "    ik (mA/cm2)\n"
  "	    \n"
  "    ninf\n"
  "	ntau (ms)\n"
  "	hinf\n"
  "	h1tau (ms)\n"
  "	h2tau (ms)\n"
  "}\n"
  " \n"
  "BREAKPOINT {\n"
  "	SOLVE states METHOD cnexp\n"
  "	gka = gbar*n*(h1*frac1+h2*frac2)\n"
  "	ik = gka*(v - ek)\n"
  "}\n"
  " \n"
  "INITIAL {\n"
  "	rates(v)\n"
  "	\n"
  "	n = ninf\n"
  "	h1 = hinf\n"
  "	h2 = hinf\n"
  "}\n"
  "\n"
  "DERIVATIVE states {  \n"
  "	rates(v)\n"
  "	\n"
  "	n'  = (ninf-n)/ntau\n"
  "	h1' = (hinf-h1)/h1tau\n"
  "	h2' = (hinf-h2)/h2tau\n"
  "}\n"
  " \n"
  "PROCEDURE rates(v(mV)) { \n"
  "        UNITSOFF   \n"
  "		ninf = (1/(1+exp((vh1-v)/9.5)))  		: Data fit: Yoshimura et al., 1996\n"
  "		ntau = AN + BN*exp(-2*((v+xcN)/ycN)^2)	: Data fit: Yoshimura et al., 2006\n"
  "		\n"
  "		hinf  = 1/(1 + exp((v+vh2)/9.6))  		: Data fit: Yoshimura et al., 1996\n"
  "		h1tau = A1 + B1*exp(-2*((v+xc1)/yc1)^2) : Both h1tau and h2tau Data fit: Yoshimura et al., 2006\n"
  "		h2tau = A2 + B2*exp(-((v-xc2)/yc2)^2)	\n"
  "}\n"
  " \n"
  "UNITSON\n"
  ;
#endif
