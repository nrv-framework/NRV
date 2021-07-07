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
 
#define nrn_init _nrn_init__nav1p8
#define _nrn_initial _nrn_initial__nav1p8
#define nrn_cur _nrn_cur__nav1p8
#define _nrn_current _nrn_current__nav1p8
#define nrn_jacob _nrn_jacob__nav1p8
#define nrn_state _nrn_state__nav1p8
#define _net_receive _net_receive__nav1p8 
#define states states__nav1p8 
 
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
#define celsiusT _p[1]
#define ina _p[2]
#define m _p[3]
#define h _p[4]
#define s _p[5]
#define u _p[6]
#define g _p[7]
#define tau_h _p[8]
#define tau_m _p[9]
#define tau_s _p[10]
#define tau_u _p[11]
#define minf _p[12]
#define hinf _p[13]
#define sinf _p[14]
#define uinf _p[15]
#define ena _p[16]
#define am _p[17]
#define bm _p[18]
#define Dm _p[19]
#define Dh _p[20]
#define Ds _p[21]
#define Du _p[22]
#define v _p[23]
#define _g _p[24]
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
 /* declaration of user functions */
 static void _hoc_alphau(void);
 static void _hoc_alphas(void);
 static void _hoc_betau(void);
 static void _hoc_betas(void);
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
 "setdata_nav1p8", _hoc_setdata,
 "alphau_nav1p8", _hoc_alphau,
 "alphas_nav1p8", _hoc_alphas,
 "betau_nav1p8", _hoc_betau,
 "betas_nav1p8", _hoc_betas,
 "rates_nav1p8", _hoc_rates,
 0, 0
};
#define alphau alphau_nav1p8
#define alphas alphas_nav1p8
#define betau betau_nav1p8
#define betas betas_nav1p8
#define rates rates_nav1p8
 extern double alphau( _threadargsprotocomma_ double );
 extern double alphas( _threadargsprotocomma_ double );
 extern double betau( _threadargsprotocomma_ double );
 extern double betas( _threadargsprotocomma_ double );
 extern double rates( _threadargsprotocomma_ double );
 /* declare global and static user variables */
 static int _thread1data_inuse = 0;
static double _thread1data[1];
#define _gth 0
#define kvot_qt_nav1p8 _thread1data[0]
#define kvot_qt _thread[_gth]._pval[0]
#define shift_inact shift_inact_nav1p8
 double shift_inact = 0;
#define shift_act shift_act_nav1p8
 double shift_act = 0;
 /* some parameters have upper and lower limits */
 static HocParmLimits _hoc_parm_limits[] = {
 0,0,0
};
 static HocParmUnits _hoc_parm_units[] = {
 "shift_act_nav1p8", "mV",
 "shift_inact_nav1p8", "mV",
 "gbar_nav1p8", "S/cm2",
 "ina_nav1p8", "mA/cm2",
 0,0
};
 static double delta_t = 0.01;
 static double h0 = 0;
 static double m0 = 0;
 static double s0 = 0;
 static double u0 = 0;
 /* connect global user variables to hoc */
 static DoubScal hoc_scdoub[] = {
 "kvot_qt_nav1p8", &kvot_qt_nav1p8,
 "shift_act_nav1p8", &shift_act_nav1p8,
 "shift_inact_nav1p8", &shift_inact_nav1p8,
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
"nav1p8",
 "gbar_nav1p8",
 "celsiusT_nav1p8",
 0,
 "ina_nav1p8",
 0,
 "m_nav1p8",
 "h_nav1p8",
 "s_nav1p8",
 "u_nav1p8",
 0,
 0};
 static Symbol* _na_sym;
 
extern Prop* need_memb(Symbol*);

static void nrn_alloc(Prop* _prop) {
	Prop *prop_ion;
	double *_p; Datum *_ppvar;
 	_p = nrn_prop_data_alloc(_mechtype, 25, _prop);
 	/*initialize range parameters*/
 	gbar = 0;
 	celsiusT = 0;
 	_prop->param = _p;
 	_prop->param_size = 25;
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
 static void _thread_mem_init(Datum*);
 static void _thread_cleanup(Datum*);
 static void _update_ion_pointer(Datum*);
 extern Symbol* hoc_lookup(const char*);
extern void _nrn_thread_reg(int, int, void(*)(Datum*));
extern void _nrn_thread_table_reg(int, void(*)(double*, Datum*, Datum*, _NrnThread*, int));
extern void hoc_register_tolerance(int, HocStateTolerance*, Symbol***);
extern void _cvode_abstol( Symbol**, double*, int);

 void _DNav18_reg() {
	int _vectorized = 1;
  _initlists();
 	ion_reg("na", -10000.);
 	_na_sym = hoc_lookup("na_ion");
 	register_mech(_mechanism, nrn_alloc,nrn_cur, nrn_jacob, nrn_state, nrn_init, hoc_nrnpointerindex, 2);
  _extcall_thread = (Datum*)ecalloc(1, sizeof(Datum));
  _thread_mem_init(_extcall_thread);
  _thread1data_inuse = 0;
 _mechtype = nrn_get_mechtype(_mechanism[1]);
     _nrn_setdata_reg(_mechtype, _setdata);
     _nrn_thread_reg(_mechtype, 1, _thread_mem_init);
     _nrn_thread_reg(_mechtype, 0, _thread_cleanup);
     _nrn_thread_reg(_mechtype, 2, _update_ion_pointer);
 #if NMODL_TEXT
  hoc_reg_nmodl_text(_mechtype, nmodl_file_text);
  hoc_reg_nmodl_filename(_mechtype, nmodl_filename);
#endif
  hoc_register_prop_size(_mechtype, 25, 4);
  hoc_register_dparam_semantics(_mechtype, 0, "na_ion");
  hoc_register_dparam_semantics(_mechtype, 1, "na_ion");
  hoc_register_dparam_semantics(_mechtype, 2, "na_ion");
  hoc_register_dparam_semantics(_mechtype, 3, "cvodeieq");
 	hoc_register_cvode(_mechtype, _ode_count, _ode_map, _ode_spec, _ode_matsol);
 	hoc_register_tolerance(_mechtype, _hoc_state_tol, &_atollist);
 	hoc_register_var(hoc_scdoub, hoc_vdoub, hoc_intfunc);
 	ivoc_help("help ?1 nav1p8 /Users/fkolbl/Desktop/NRV2/src/mods/DNav18.mod\n");
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
 static int _slist1[4], _dlist1[4];
 static int states(_threadargsproto_);
 
/*CVODE*/
 static int _ode_spec1 (double* _p, Datum* _ppvar, Datum* _thread, _NrnThread* _nt) {int _reset = 0; {
   rates ( _threadargscomma_ v ) ;
   Dm = ( minf - m ) / tau_m ;
   Dh = ( hinf - h ) / tau_h ;
   Ds = ( sinf - s ) / tau_s ;
   Du = ( uinf - u ) / tau_u ;
   }
 return _reset;
}
 static int _ode_matsol1 (double* _p, Datum* _ppvar, Datum* _thread, _NrnThread* _nt) {
 rates ( _threadargscomma_ v ) ;
 Dm = Dm  / (1. - dt*( ( ( ( - 1.0 ) ) ) / tau_m )) ;
 Dh = Dh  / (1. - dt*( ( ( ( - 1.0 ) ) ) / tau_h )) ;
 Ds = Ds  / (1. - dt*( ( ( ( - 1.0 ) ) ) / tau_s )) ;
 Du = Du  / (1. - dt*( ( ( ( - 1.0 ) ) ) / tau_u )) ;
  return 0;
}
 /*END CVODE*/
 static int states (double* _p, Datum* _ppvar, Datum* _thread, _NrnThread* _nt) { {
   rates ( _threadargscomma_ v ) ;
    m = m + (1. - exp(dt*(( ( ( - 1.0 ) ) ) / tau_m)))*(- ( ( ( minf ) ) / tau_m ) / ( ( ( ( - 1.0 ) ) ) / tau_m ) - m) ;
    h = h + (1. - exp(dt*(( ( ( - 1.0 ) ) ) / tau_h)))*(- ( ( ( hinf ) ) / tau_h ) / ( ( ( ( - 1.0 ) ) ) / tau_h ) - h) ;
    s = s + (1. - exp(dt*(( ( ( - 1.0 ) ) ) / tau_s)))*(- ( ( ( sinf ) ) / tau_s ) / ( ( ( ( - 1.0 ) ) ) / tau_s ) - s) ;
    u = u + (1. - exp(dt*(( ( ( - 1.0 ) ) ) / tau_u)))*(- ( ( ( uinf ) ) / tau_u ) / ( ( ( ( - 1.0 ) ) ) / tau_u ) - u) ;
   }
  return 0;
}
 
double rates ( _threadargsprotocomma_ double _lVm ) {
   double _lrates;
 am = 2.85 - ( 2.839 ) / ( 1.0 + exp ( ( _lVm - 1.159 ) / 13.95 ) ) ;
   bm = ( 7.6205 ) / ( 1.0 + exp ( ( _lVm + 46.463 ) / 8.8289 ) ) ;
   tau_m = 1.0 / ( am + bm ) ;
   minf = am / ( am + bm ) ;
   hinf = 1.0 / ( 1.0 + exp ( ( _lVm + 32.2 ) / 4.0 ) ) ;
   tau_h = ( 1.218 + 42.043 * exp ( - ( pow( ( _lVm + 38.1 ) , 2.0 ) ) / ( 2.0 * pow( 15.19 , 2.0 ) ) ) ) ;
   tau_s = 1.0 / ( alphas ( _threadargscomma_ _lVm ) + betas ( _threadargscomma_ _lVm ) ) ;
   sinf = 1.0 / ( 1.0 + exp ( ( _lVm + 45.0 ) / 8.0 ) ) ;
   tau_u = 1.0 / ( alphau ( _threadargscomma_ _lVm ) + betau ( _threadargscomma_ _lVm ) ) ;
   uinf = 1.0 / ( 1.0 + exp ( ( _lVm + 51.0 ) / 8.0 ) ) ;
   kvot_qt = 1.0 / ( ( pow( 2.5 , ( ( celsiusT - 22.0 ) / 10.0 ) ) ) ) ;
   tau_m = tau_m * kvot_qt ;
   tau_h = tau_h * kvot_qt ;
   tau_s = tau_s * kvot_qt ;
   tau_u = tau_u * kvot_qt ;
   
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
 
double alphas ( _threadargsprotocomma_ double _lVm ) {
   double _lalphas;
 _lalphas = 0.001 * 5.4203 / ( 1.0 + exp ( ( _lVm + 79.816 ) / 16.269 ) ) ;
   
return _lalphas;
 }
 
static void _hoc_alphas(void) {
  double _r;
   double* _p; Datum* _ppvar; Datum* _thread; _NrnThread* _nt;
   if (_extcall_prop) {_p = _extcall_prop->param; _ppvar = _extcall_prop->dparam;}else{ _p = (double*)0; _ppvar = (Datum*)0; }
  _thread = _extcall_thread;
  _nt = nrn_threads;
 _r =  alphas ( _p, _ppvar, _thread, _nt, *getarg(1) );
 hoc_retpushx(_r);
}
 
double alphau ( _threadargsprotocomma_ double _lVm ) {
   double _lalphau;
 _lalphau = 0.0002 * 2.0434 / ( 1.0 + exp ( ( _lVm + 67.499 ) / 19.51 ) ) ;
   
return _lalphau;
 }
 
static void _hoc_alphau(void) {
  double _r;
   double* _p; Datum* _ppvar; Datum* _thread; _NrnThread* _nt;
   if (_extcall_prop) {_p = _extcall_prop->param; _ppvar = _extcall_prop->dparam;}else{ _p = (double*)0; _ppvar = (Datum*)0; }
  _thread = _extcall_thread;
  _nt = nrn_threads;
 _r =  alphau ( _p, _ppvar, _thread, _nt, *getarg(1) );
 hoc_retpushx(_r);
}
 
double betas ( _threadargsprotocomma_ double _lVm ) {
   double _lbetas;
 _lbetas = 0.001 * 5.0757 / ( 1.0 + exp ( - ( _lVm + 15.968 ) / 11.542 ) ) ;
   
return _lbetas;
 }
 
static void _hoc_betas(void) {
  double _r;
   double* _p; Datum* _ppvar; Datum* _thread; _NrnThread* _nt;
   if (_extcall_prop) {_p = _extcall_prop->param; _ppvar = _extcall_prop->dparam;}else{ _p = (double*)0; _ppvar = (Datum*)0; }
  _thread = _extcall_thread;
  _nt = nrn_threads;
 _r =  betas ( _p, _ppvar, _thread, _nt, *getarg(1) );
 hoc_retpushx(_r);
}
 
double betau ( _threadargsprotocomma_ double _lVm ) {
   double _lbetau;
 _lbetau = 0.0002 * 1.9952 / ( 1.0 + exp ( - ( _lVm + 30.963 ) / 14.792 ) ) ;
   
return _lbetau;
 }
 
static void _hoc_betau(void) {
  double _r;
   double* _p; Datum* _ppvar; Datum* _thread; _NrnThread* _nt;
   if (_extcall_prop) {_p = _extcall_prop->param; _ppvar = _extcall_prop->dparam;}else{ _p = (double*)0; _ppvar = (Datum*)0; }
  _thread = _extcall_thread;
  _nt = nrn_threads;
 _r =  betau ( _p, _ppvar, _thread, _nt, *getarg(1) );
 hoc_retpushx(_r);
}
 
static int _ode_count(int _type){ return 4;}
 
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
	for (_i=0; _i < 4; ++_i) {
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
 
static void _thread_mem_init(Datum* _thread) {
  if (_thread1data_inuse) {_thread[_gth]._pval = (double*)ecalloc(1, sizeof(double));
 }else{
 _thread[_gth]._pval = _thread1data; _thread1data_inuse = 1;
 }
 }
 
static void _thread_cleanup(Datum* _thread) {
  if (_thread[_gth]._pval == _thread1data) {
   _thread1data_inuse = 0;
  }else{
   free((void*)_thread[_gth]._pval);
  }
 }
 extern void nrn_update_ion_pointer(Symbol*, Datum*, int, int);
 static void _update_ion_pointer(Datum* _ppvar) {
   nrn_update_ion_pointer(_na_sym, _ppvar, 0, 0);
   nrn_update_ion_pointer(_na_sym, _ppvar, 1, 3);
   nrn_update_ion_pointer(_na_sym, _ppvar, 2, 4);
 }

static void initmodel(double* _p, Datum* _ppvar, Datum* _thread, _NrnThread* _nt) {
  int _i; double _save;{
  h = h0;
  m = m0;
  s = s0;
  u = u0;
 {
   rates ( _threadargscomma_ v ) ;
   m = minf ;
   h = hinf ;
   s = sinf ;
   u = uinf ;
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
   g = gbar * pow( m , 3.0 ) * h * s * u ;
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
 _slist1[2] = &(s) - _p;  _dlist1[2] = &(Ds) - _p;
 _slist1[3] = &(u) - _p;  _dlist1[3] = &(Du) - _p;
_first = 0;
}

#if defined(__cplusplus)
} /* extern "C" */
#endif

#if NMODL_TEXT
static const char* nmodl_filename = "/Users/fkolbl/Desktop/NRV2/src/mods/DNav18.mod";
static const char* nmodl_file_text = 
  ": The m and h are form sheets  2007\n"
  ":s and u are form Delmas\n"
  ": run NaV18_delmas.m to plot the model\n"
  ": F. Kolbl modification on 19/01/2021, celsiusT added in RANGE - NRV2 specific\n"
  "\n"
  "NEURON {\n"
  "	SUFFIX nav1p8\n"
  "	USEION na READ ena WRITE ina\n"
  " 	RANGE gbar, ena, ina, celsiusT\n"
  "}\n"
  "\n"
  "UNITS {\n"
  "	(S) = (siemens)\n"
  "	(mV) = (millivolts)\n"
  "	(mA) = (milliamp)\n"
  "}\n"
  "\n"
  "PARAMETER {\n"
  "	gbar = 0 (S/cm2) : =220e-9/(100e-12*1e8) (S/cm2) : 220(nS)/100(um)^2       \n"
  "	kvot_qt\n"
  "    celsiusT\n"
  "	shift_act = 0 (mV)\n"
  "	shift_inact = 0 (mV)\n"
  "}\n"
  "\n"
  "ASSIGNED {\n"
  "	v	(mV) : NEURON provides this\n"
  "	ina	(mA/cm2)\n"
  "	g	(S/cm2)\n"
  "	tau_h	(ms)\n"
  "   	tau_m	(ms)\n"
  "	tau_s	(ms)\n"
  "	tau_u	(ms)\n"
  "	minf\n"
  "	hinf\n"
  "	sinf\n"
  "	uinf\n"
  "        ena    	(mV)\n"
  "        am\n"
  "        bm\n"
  "}\n"
  "\n"
  "STATE { m h s u }\n"
  "\n"
  "BREAKPOINT {\n"
  "	SOLVE states METHOD cnexp	\n"
  "	g = gbar * m^3* h * s * u\n"
  "	ina = g * (v-ena)\n"
  "}\n"
  "\n"
  "INITIAL {\n"
  "	: assume that equilibrium has been reached\n"
  "        rates(v)\n"
  "        m=minf\n"
  "        h=hinf\n"
  "        s=sinf\n"
  "        u=uinf\n"
  "    	\n"
  "\n"
  "}\n"
  "\n"
  "DERIVATIVE states {\n"
  "	rates(v)\n"
  "	m' = (minf - m)/tau_m\n"
  "	h' = (hinf - h)/tau_h\n"
  "	s' = (sinf - s)/tau_s\n"
  "	u' = (uinf - u)/tau_u\n"
  "}\n"
  "\n"
  "FUNCTION rates(Vm (mV)) {\n"
  "        \n"
  "        am= 2.85-(2.839)/(1+exp((Vm-1.159)/13.95))\n"
  "        bm= (7.6205)/(1+exp((Vm+46.463)/8.8289))\n"
  "	tau_m = 1/(am+bm)\n"
  "	minf = am/(am+bm)\n"
  "        \n"
  "        hinf= 1/(1+exp((Vm+32.2)/4))  \n"
  "        tau_h=(1.218+42.043*exp(-((Vm+38.1)^2)/(2*15.19^2)))\n"
  "	\n"
  "	tau_s = 1/(alphas(Vm) + betas(Vm))			\n"
  "        sinf = 1/(1 + exp((Vm + 45)/8(mV)))	 	\n"
  " 	tau_u = 1/(alphau(Vm) + betau(Vm))	\n"
  "	uinf = 1/(1 + exp((Vm + 51)/8(mV)))\n"
  "\n"
  "\n"
  "	kvot_qt=1/((2.5^((celsiusT-22)/10)))\n"
  "        tau_m=tau_m*kvot_qt\n"
  "        tau_h=tau_h*kvot_qt\n"
  "        tau_s=tau_s*kvot_qt\n"
  "        tau_u=tau_u*kvot_qt\n"
  "}\n"
  "\n"
  "\n"
  "FUNCTION alphas(Vm (mV)) (/ms) {\n"
  "	alphas=	0.001(/ms)*5.4203/(1 + exp((Vm + 79.816)/16.269(mV)))	\n"
  "}\n"
  "\n"
  "FUNCTION alphau(Vm (mV)) (/ms) {\n"
  "	alphau=	0.0002(/ms)*2.0434/(1 + exp((Vm + 67.499)/19.51(mV)))\n"
  "}\n"
  "\n"
  "FUNCTION betas(Vm (mV)) (/ms) {\n"
  "	betas= 0.001(/ms)*5.0757/(1 + exp(-(Vm + 15.968)/11.542(mV)))\n"
  "}\n"
  "\n"
  "FUNCTION betau(Vm (mV)) (/ms) {\n"
  "	betau= 0.0002(/ms)*1.9952/(1 + exp(-(Vm + 30.963)/14.792(mV)))\n"
  "}\n"
  "\n"
  "\n"
  "\n"
  ;
#endif
