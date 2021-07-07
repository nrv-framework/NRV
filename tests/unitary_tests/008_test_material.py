import nrv

mat1 = nrv.load_material('material_1')
mat2 = nrv.load_material('material_2')

print(mat1.is_isotropic() == True)
print(mat1.sigma == 1.)
print(mat2.is_isotropic() == False)
print(mat2.sigma_xx == 1)
print(mat2.sigma_yy == 0.5)
print(mat2.sigma_zz == 0.5)
