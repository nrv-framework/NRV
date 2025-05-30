import nrv 

if __name__ == '__main__':
    #pass info
    nrv.pass_info('This is a friendly message from NRV',' (ver=True)', verbose=True)

    nrv.pass_info('This is a friendly message from NRV',' (ver=False)', verbose=False)
    nrv.pass_info('This is a friendly message from NRV',' (ver=None)')
    nrv.pass_info(False)
    nrv.parameters.set_nrv_verbosity(2)
    nrv.pass_info('This should never be printed')



    #Warning
    nrv.rise_warning('This is a warning in yellow from NRV',' (ver=True)', verbose=True)

    nrv.rise_warning('This is a warning in yellow from NRV',' (ver=False)', verbose=False)
    nrv.rise_warning('This is a warning in yellow from NRV',' (ver=None)')
    nrv.rise_warning(False)
    nrv.parameters.set_nrv_verbosity(1)
    nrv.rise_warning('Oops this warning will never be seen')


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

    nrv.parameters.set_nrv_verbosity(0)
    try:
        nrv.rise_error('Ouch ! noone will see this error')
    except:
        print("error 4 (VERBOSITY_LEVEL=0)")


    # multiprocess
    

