import nrv 


#pass info
nrv.pass_info('This is a friendly message from NRV',' (ver=True)', verbose=True)

nrv.pass_info('This is a friendly message from NRV',' (ver=False)', verbose=False)
nrv.pass_info('This is a friendly message from NRV',' (ver=None)')
nrv.pass_info(False)


#Warning
nrv.rise_warning('This is a warning in yellow from NRV',' (ver=True)', verbose=True)

nrv.rise_warning('This is a warning in yellow from NRV',' (ver=False)', verbose=False)
nrv.rise_warning('This is a warning in yellow from NRV',' (ver=None)')
nrv.rise_warning(False)


#errors

try:
    nrv.rise_error('This is an error in red from NRV', verbose=True)
except:
    print("error 1 (ver=True)")
try:
    nrv.rise_error('This is an error in red from NRV', verbose=False)
except:
    print("error 2 (ver=False)")
try:
    nrv.rise_error('This is an error in red from NRV')
except:
    print("error 3(ver=None)")
