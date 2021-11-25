import nrv 


#pass info
nrv.pass_info('ver=True', verbose=True)

nrv.pass_info('ver=False', verbose=False)
nrv.pass_info('ver=None')
nrv.pass_info(True)

nrv.pass_info(False, verbose=True)

my_dict = {'ID':12,'test':1}
nrv.remove_key(my_dict, 'test', verbose=False)
print(my_dict)
#Warning
nrv.rise_warning('ver=True', verbose=True)

nrv.rise_warning('ver=False', verbose=False)
nrv.rise_warning('ver=None')
nrv.rise_warning(True)

nrv.rise_warning(False, verbose=True)

#errors




nrv.rise_error(False, verbose=True)