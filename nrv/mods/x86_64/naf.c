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
 
#define nrn_init _nrn_init__naf
#define _nrn_initial _nrn_initial__naf
#define nrn_cur _nrn_cur__naf
#define _nrn_current _nrn_current__naf
#define nrn_jacob _nrn_jacob__naf
#define nrn_state _nrn_state__naf
#define _net_receive _net_receive__naf 
#define states states__naf 
 
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
#define shiftnaf _p[1]
#define ina _p[2]
#define m _p[3]
#define h _p[4]
#define l _p[5]
#define ena _p[6]
#define g _p[7]
#define tau_h _p[8]
#define tau_m _p[9]
#define tau_j _p[10]
#define minf _p[11]
#define hinf _p[12]
#define jinf _p[13]
#define Dm _p[14]
#define Dh _p[15]
#define Dl _p[16]
#define v _p[17]
#define _g _p[18]
#define _ion_ena	*_ppvar[0]._pval
#define _ion_ina	*_ppvar[1]._pval
#define _ion_dinadv	*_ppvar[2]._pval
 
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
 "setdata_naf", _hoc_setdata,
 "rates_naf", _hoc_rates,
 0, 0
};
#define rates rates_naf
 extern double rates( _threadargsprotocomma_ double );
 /* declare global and static user variables */
#define A_tauj A_tauj_naf
 double A_tauj = 25;
#define A_tauh A_tauh_naf
 double A_tauh = 6.5;
#define A_taum A_taum_naf
 double A_taum = 0.75;
#define B_tauj B_tauj_naf
 double B_tauj = 4.5;
#define B_tauh B_tauh_naf
 double B_tauh = 0.0295;
#define B_taum B_taum_naf
 double B_taum = 0.0635;
#define C_tauj C_tauj_naf
 double C_tauj = 0.01;
#define C_tauh C_tauh_naf
 double C_tauh = 0.55;
#define C_taum C_taum_naf
 double C_taum = 0.12;
#define Q10TempB Q10TempB_naf
 double Q10TempB = 10;
#define Q10TempA Q10TempA_naf
 double Q10TempA = 22.85;
#define Q10nafh Q10nafh_naf
 double Q10nafh = 1.5;
#define Q10nafm Q10nafm_naf
 double Q10nafm = 2.3;
#define S0p5j S0p5j_naf
 double S0p5j = -1.5;
#define S0p5h S0p5h_naf
 double S0p5h = -4.5;
#define S0p5m S0p5m_naf
 double S0p5m = 4.75;
#define Vpj Vpj_naf
 double Vpj = -20;
#define V0p5j V0p5j_naf
 double V0p5j = -40;
#define Vph Vph_naf
 double Vph = -75;
#define V0p5h V0p5h_naf
 double V0p5h = -62;
#define Vpm Vpm_naf
 double Vpm = -40.35;
#define V0p5m V0p5m_naf
 double V0p5m = -41.35;
 /* some parameters have upper and lower limits */
 static HocParmLimits _hoc_parm_limits[] = {
 0,0,0
};
 static HocParmUnits _hoc_parm_units[] = {
 "Q10TempA_naf", "degC",
 "Q10TempB_naf", "degC",
 "V0p5m_naf", "mV",
 "S0p5m_naf", "mV",
 "A_taum_naf", "ms",
 "B_taum_naf", "/mV",
 "C_taum_naf", "ms",
 "Vpm_naf", "mV",
 "V0p5h_naf", "mV",
 "S0p5h_naf", "mV",
 "A_tauh_naf", "ms",
 "B_tauh_naf", "/mV",
 "C_tauh_naf", "ms",
 "Vph_naf", "mV",
 "V0p5j_naf", "mV",
 "S0p5j_naf", "mV",
 "A_tauj_naf", "ms",
 "B_tauj_naf", "mV",
 "C_tauj_naf", "ms",
 "Vpj_naf", "mV",
 "gbar_naf", "S/cm2",
 "shiftnaf_naf", "mV",
 "ina_naf", "mA/cm2",
 0,0
};
 static double delta_t = 0.01;
 static double h0 = 0;
 static double l0 = 0;
 static double m0 = 0;
 /* connect global user variables to hoc */
 static DoubScal hoc_scdoub[] = {
 "Q10nafm_naf", &Q10nafm_naf,
 "Q10nafh_naf", &Q10nafh_naf,
 "Q10TempA_naf", &Q10TempA_naf,
 "Q10TempB_naf", &Q10TempB_naf,
 "V0p5m_naf", &V0p5m_naf,
 "S0p5m_naf", &S0p5m_naf,
 "A_taum_naf", &A_taum_naf,
 "B_taum_naf", &B_taum_naf,
 "C_taum_naf", &C_taum_naf,
 "Vpm_naf", &Vpm_naf,
 "V0p5h_naf", &V0p5h_naf,
 "S0p5h_naf", &S0p5h_naf,
 "A_tauh_naf", &A_tauh_naf,
 "B_tauh_naf", &B_tauh_naf,
 "C_tauh_naf", &C_tauh_naf,
 "Vph_naf", &Vph_naf,
 "V0p5j_naf", &V0p5j_naf,
 "S0p5j_naf", &S0p5j_naf,
 "A_tauj_naf", &A_tauj_naf,
 "B_tauj_naf", &B_tauj_naf,
 "C_tauj_naf", &C_tauj_naf,
 "Vpj_naf", &Vpj_naf,
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
"naf",
 "gbar_naf",
 "shiftnaf_naf",
 0,
 "ina_naf",
 0,
 "m_naf",
 "h_naf",
 "l_naf",
 0,
 0};
 static Symbol* _na_sym;
 
extern Prop* need_memb(Symbol*);

static void nrn_alloc(Prop* _prop) {
	Prop *prop_ion;
	double *_p; Datum *_ppvar;
 	_p = nrn_prop_data_alloc(_mechtype, 19, _prop);
 	/*initialize range parameters*/
 	gbar = 0.0689671;
 	shiftnaf = -17.5;
 	_prop->param = _p;
 	_prop->param_size = 19;
 	_ppvar = nrn_prop_datum_alloc(_mechtype, 4, _prop);
 	_prop->dparam = _ppvar;
 	/*connect ionic variables to this model*/
 prop_ion = need_memb(_na_sym);
 nrn_promote(prop_ion, 0, 1);
 	_ppvar[0]._pval = &prop_ion->param[0]; /* ena */
 	_ppvar[1]._pval = &prop_ion->param[3]; /* ina */
 	_ppvar[2]._pval = &prop_ion->param[4]; /* _ion_dinadv */
 
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

 void _naf_reg() {
	int _vectorized = 1;
  _initlists();
 	ion_reg("na", -10000.);
 	_na_sym = hoc_lookup("na_ion");
 	register_mech(_mechanism, nrn_alloc,nrn_cur, nrn_jacob, nrn_state, nrn_init, hoc_nrnpointerindex, 1);
 _mechtype = nrn_get_mechtype(_mechanism[1]);
     _nrn_setdata_reg(_mechtype, _setdata);
     _nrn_thread_reg(_mechtype, 2, _update_ion_pointer);
 #if NMODL_TEXT
  hoc_reg_nmodl_text(_mechtype, nmodl_file_text);
  hoc_reg_nmodl_filename(_mechtype, nmodl_filename);
#endif
  hoc_register_prop_size(_mechtype, 19, 4);
  hoc_register_dparam_semantics(_mechtype, 0, "na_ion");
  hoc_register_dparam_semantics(_mechtype, 1, "na_ion");
  hoc_register_dparam_semantics(_mechtype, 2, "na_ion");
  hoc_register_dparam_semantics(_mechtype, 3, "cvodeieq");
 	hoc_register_cvode(_mechtype, _ode_count, _ode_map, _ode_spec, _ode_matsol);
 	hoc_register_tolerance(_mechtype, _hoc_state_tol, &_atollist);
 	hoc_register_var(hoc_scdoub, hoc_vdoub, hoc_intfunc);
 	ivoc_help("help ?1 naf /Users/fkolbl/Desktop/NRV2/src/mods/naf.mod\n");
 hoc_register_limits(_mechtype, _hoc_parm_limits);
 hoc_register_units(_mechtype, _hoc_parm_units);
 }
static int _reset;
static char *modelname = "";

static int error;
static int _ninits = 0;
static int _match_recurse=1;
static void _modl_cleanup(){ _match_recurse=1;}
 
static int _ode_spec1(_threadargsproto_);
/*static int _ode_matsol1(_threadargsproto_);*/
 static int _slist1[3], _dlist1[3];
 static int states(_threadargsproto_);
 
/*CVODE*/
 static int _ode_spec1 (double* _p, Datum* _ppvar, Datum* _thread, _NrnThread* _nt) {int _reset = 0; {
   rates ( _threadargscomma_ v ) ;
   Dm = ( minf - m ) / tau_m ;
   Dh = ( hinf - h ) / tau_h ;
   Dl = ( jinf - l ) / tau_j ;
   }
 return _reset;
}
 static int _ode_matsol1 (double* _p, Datum* _ppvar, Datum* _thread, _NrnThread* _nt) {
 rates ( _threadargscomma_ v ) ;
 Dm = Dm  / (1. - dt*( ( ( ( - 1.0 ) ) ) / tau_m )) ;
 Dh = Dh  / (1. - dt*( ( ( ( - 1.0 ) ) ) / tau_h )) ;
 Dl = Dl  / (1. - dt*( ( ( ( - 1.0 ) ) ) / tau_j )) ;
  return 0;
}
 /*END CVODE*/
 static int states (double* _p, Datum* _ppvar, Datum* _thread, _NrnThread* _nt) { {
   rates ( _threadargscomma_ v ) ;
    m = m + (1. - exp(dt*(( ( ( - 1.0 ) ) ) / tau_m)))*(- ( ( ( minf ) ) / tau_m ) / ( ( ( ( - 1.0 ) ) ) / tau_m ) - m) ;
    h = h + (1. - exp(dt*(( ( ( - 1.0 ) ) ) / tau_h)))*(- ( ( ( hinf ) ) / tau_h ) / ( ( ( ( - 1.0 ) ) ) / tau_h ) - h) ;
    l = l + (1. - exp(dt*(( ( ( - 1.0 ) ) ) / tau_j)))*(- ( ( ( jinf ) ) / tau_j ) / ( ( ( ( - 1.0 ) ) ) / tau_j ) - l) ;
   }
  return 0;
}
 
double rates ( _threadargsprotocomma_ double _lVm ) {
   double _lrates;
 tau_m = A_taum * exp ( - pow( ( B_taum ) , 2.0 ) * pow( ( _lVm - Vpm ) , 2.0 ) ) + C_taum ;
   minf = 1.0 / ( 1.0 + exp ( ( _lVm - V0p5m + shiftnaf ) / ( - S0p5m ) ) ) ;
   tau_h = A_tauh * exp ( - pow( ( B_tauh ) , 2.0 ) * pow( ( _lVm - Vph ) , 2.0 ) ) + C_tauh ;
   hinf = 1.0 / ( 1.0 + exp ( ( _lVm - V0p5h + shiftnaf ) / ( - S0p5h ) ) ) ;
   tau_j = ( A_tauj / ( 1.0 + exp ( ( _lVm + Vpj ) / B_tauj ) ) ) + C_tauj ;
   jinf = 1.0 / ( 1.0 + exp ( ( _lVm - V0p5j ) / ( - S0p5j ) ) ) ;
   tau_m = tau_m * pow( Q10nafm , ( ( Q10TempA - celsius ) / Q10TempB ) ) ;
   tau_h = tau_h * pow( Q10nafh , ( ( Q10TempA - celsius ) / Q10TempB ) ) ;
   
return _lrates;
 }
 
static void _hoc_rates(void) {
  double _r;
   double* _p; Datum* _ppvar; Datum* _thread; _NrnThread* _nt;
   if (_extcall_prop) {_p = _extcall_prop->param; _ppvar = _extcall_prop->dparam;}else{ _p = (double*)0; _ppvar = (Datum*)0; }
  _thread = _extcall_thread;
  _nt = nrn_threads;
 _r =  rates ( _p, _ppvar, _thread, _nt, *getarg(1) );
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
  ena = _ion_ena;
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
  ena = _ion_ena;
 _ode_matsol_instance1(_threadargs_);
 }}
 extern void nrn_update_ion_pointer(Symbol*, Datum*, int, int);
 static void _update_ion_pointer(Datum* _ppvar) {
   nrn_update_ion_pointer(_na_sym, _ppvar, 0, 0);
   nrn_update_ion_pointer(_na_sym, _ppvar, 1, 3);
   nrn_update_ion_pointer(_na_sym, _ppvar, 2, 4);
 }

static void initmodel(double* _p, Datum* _ppvar, Datum* _thread, _NrnThread* _nt) {
  int _i; double _save;{
  h = h0;
  l = l0;
  m = m0;
 {
   rates ( _threadargscomma_ v ) ;
   m = minf ;
   h = hinf ;
   l = jinf ;
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
  ena = _ion_ena;
 initmodel(_p, _ppvar, _thread, _nt);
 }
}

static double _nrn_current(double* _p, Datum* _ppvar, Datum* _thread, _NrnThread* _nt, double _v){double _current=0.;v=_v;{ {
   g = gbar * pow( m , 3.0 ) * h * l ;
   ina = g * ( v - ena ) ;
   }
 _current += ina;

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
  ena = _ion_ena;
 _g = _nrn_current(_p, _ppvar, _thread, _nt, _v + .001);
 	{ double _dina;
  _dina = ina;
 _rhs = _nrn_current(_p, _ppvar, _thread, _nt, _v);
  _ion_dinadv += (_dina - ina)/.001 ;
 	}
 _g = (_g - _rhs)/.001;
  _ion_ina += ina ;
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
  ena = _ion_ena;
 {   states(_p, _ppvar, _thread, _nt);
  } }}

}

static void terminal(){}

static void _initlists(){
 double _x; double* _p = &_x;
 int _i; static int _first = 1;
  if (!_first) return;
 _slist1[0] = &(m) - _p;  _dlist1[0] = &(Dm) - _p;
 _slist1[1] = &(h) - _p;  _dlist1[1] = &(Dh) - _p;
 _slist1[2] = &(l) - _p;  _dlist1[2] = &(Dl) - _p;
_first = 0;
}

#if defined(__cplusplus)
} /* extern "C" */
#endif

#if NMODL_TEXT
static const char* nmodl_filename = "/Users/fkolbl/Desktop/NRV2/src/mods/naf.mod";
static const char* nmodl_file_text = 
  ": Author: David Catherall; Grill Lab; Duke University\n"
  ": Created: November 2016\n"
  ": Naf is the fast, TTX-sensitive current in Schild 1994 \n"
  "\n"
  ": Neuron Block creates mechanism\n"
  "	NEURON {\n"
  "		   SUFFIX naf						:Sets suffix of mechanism for insertion into models\n"
  "		   USEION na READ ena WRITE ina		:Lays out which NEURON variables will be used/modified by file\n"
  "		   RANGE gbar, ena, ina, shiftnaf	:Allows variables to be modified in hoc and collected in vectors\n"
  "\n"
  "	}\n"
  "\n"
  ": Defines Units different from NEURON base units\n"
  "	UNITS {\n"
  "		  (S) = (siemens)\n"
  "		  (mV) = (millivolts)\n"
  "		  (mA) = (milliamp)\n"
  "	}\n"
  "\n"
  ": Defines variables which will have a constant value throughout any given simulation run\n"
  "	PARAMETER {\n"
  "		gbar =0.068967142	(S/cm2)	: (S/cm2) Channel Conductance\n"
  "		Q10nafm=2.30				: m Q10 Scale Factor\n"
  "		Q10nafh=1.50				: h Q10 Scale Factor\n"
  "		Q10TempA = 22.85	(degC)		: Used to shift tau values based on temperature with equation : tau(T1)=tau(Q10TempA)*Q10^((Q10TempA-T1)/Q10TempB)\n"
  "		Q10TempB = 10	(degC)		: Note that a Q10 value for j is not defined in Schild 1994. \n"
  "\n"
  "	 \n"
  "		shiftnaf=-17.5 (mV) 		: Shift factor present in C-fiber (Note that this shift is not applied to the j gating variable, as per Schild 1994)\n"
  "		\n"
  "		\n"
  "		: naf_m Variables\n"
  "		\n"
  "			: Steady State Variables\n"
  "			V0p5m=-41.35 (mV)	:As defined by Schild 1994, zinf=1.0/(1.0+exp((V-V0p5z)/(-S0p5z))\n"
  "			S0p5m=4.75 (mV)\n"
  "			\n"
  "			: Tau Variables\n"
  "			A_taum=0.75	(ms)	:As defined by Schild 1994, tauz=A_tauz*exp(-B^2(V-Vpz)^2)+C\n"
  "			B_taum=0.0635	(/mV)\n"
  "			C_taum=0.12	(ms)\n"
  "			Vpm=-40.35		(mV)\n"
  "		\n"
  "		\n"
  "		: naf_h Variables\n"
  "		\n"
  "			: Steady State Variables\n"
  "				V0p5h=-62.00 (mV)\n"
  "				S0p5h=-4.50 (mV)\n"
  "			\n"
  "			: Tau Variables\n"
  "				A_tauh=6.5	(ms)\n"
  "				B_tauh=0.0295	(/mV)\n"
  "				C_tauh=0.55	(ms)\n"
  "				Vph=-75.00	(mV)\n"
  "			\n"
  "		: naf_j Variables\n"
  "		\n"
  "			: Steady State Variables\n"
  "				V0p5j=-40.00 (mV)\n"
  "				S0p5j=-1.50 (mV)\n"
  "			\n"
  "			: Tau Variables\n"
  "				A_tauj=25	(ms)\n"
  "				B_tauj=4.50	(mV)\n"
  "				C_tauj=0.01	(ms)\n"
  "				Vpj=-20.00		(mV)\n"
  "	}\n"
  "\n"
  ": Defines variables which will be used or calculated throughout the simulation which may not be constant. Also included NEURON provided variables, like v, celsius, and ina\n"
  "	ASSIGNED {\n"
  "		\n"
  "		:NEURON provided Variables\n"
  "		 v	(mV) \n"
  "		 celsius (degC)\n"
  "		 ina	(mA/cm2)\n"
  "		 ena	(mV)\n"
  "		 \n"
  "		 :Model Specific Variables\n"
  "		 g	(S/cm2)\n"
  "		 tau_h	(ms)\n"
  "		 tau_m	(ms)\n"
  "		 tau_j	(ms)\n"
  "		 minf\n"
  "		 hinf\n"
  "		 jinf\n"
  "		 \n"
  "			 \n"
  "	}\n"
  "\n"
  ": Defines state variables which will be calculated by numerical integration\n"
  "	STATE { m h l } \n"
  "\n"
  "COMMENT\n"
  "	:#####NOTE##### The variable j is a reserved name in NMODL, so the\n"
  "	gating variable j in the naf mechanism was renamed to l. This prevents\n"
  "	any compiling errors. tauj and jinf retain their j naming convention\n"
  "ENDCOMMENT\n"
  "\n"
  ": This block iterates the state variable calculations and uses those calculations to calculate currents\n"
  "	BREAKPOINT {\n"
  "		   SOLVE states METHOD cnexp\n"
  "		   g = gbar * m^3 * h *l\n"
  "		   ina = g * (v-ena)\n"
  "	}\n"
  "\n"
  ": Intializes State Variables\n"
  "	INITIAL {\n"
  "		rates(v) : set tau_m, tau_h, hinf, minf\n"
  "		: assume that equilibrium has been reached\n"
  "		\n"
  "\n"
  "		m = minf\n"
  "		h = hinf\n"
  "		l = jinf\n"
  "	}\n"
  "\n"
  ":Defines Governing Equations for State Variables\n"
  "	DERIVATIVE states {\n"
  "		   rates(v)\n"
  "		   m' = (minf - m)/tau_m\n"
  "		   h' = (hinf - h)/tau_h\n"
  "		   l' = (jinf - l)/tau_j\n"
  "	}\n"
  "\n"
  "\n"
  ": Any other functions go here\n"
  "	\n"
  "	:rates is a function which calculates the current values for tau and steady state equations based on voltage.\n"
  "		FUNCTION rates(Vm (mV)) (/ms) {\n"
  "			 tau_m = A_taum*exp(-(B_taum)^2*(Vm-Vpm)^2)+C_taum\n"
  "				 minf = 1.0/(1.0+exp((Vm-V0p5m+shiftnaf)/(-S0p5m)))\n"
  "\n"
  "			 tau_h = A_tauh*exp(-(B_tauh)^2*(Vm-Vph)^2)+C_tauh\n"
  "				 hinf = 1.0/(1.0+exp((Vm-V0p5h+shiftnaf)/(-S0p5h)))\n"
  "\n"
  "			 tau_j = (A_tauj/(1.0+exp((Vm+Vpj)/B_tauj)))+C_tauj\n"
  "				 jinf = 1.0/(1.0+exp((Vm-V0p5j)/(-S0p5j)))\n"
  "			\n"
  "				tau_m=tau_m*Q10nafm^((Q10TempA-celsius)/Q10TempB)\n"
  "				tau_h=tau_h*Q10nafh^((Q10TempA-celsius)/Q10TempB)\n"
  "		}\n"
  "\n"
  "		\n"
  ;
#endif
