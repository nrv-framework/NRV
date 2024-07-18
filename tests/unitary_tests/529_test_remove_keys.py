import nrv

key = "t_sim"
keys_set = {"record_I_mem", "record_I_ions"}
keys_list = ["record_V_mem", "record_particles", "record_g_mem"]




# Generating full results (testing contains method)
ax = nrv.myelinated()
res = ax()
print(key in res)
print(keys_set in res)
print(keys_list in res)
print(keys_list + ["not a key"] not in res)

# removing a set of keys
res.remove_key(key)
print(key not in res)
print(keys_set in res)
print(keys_list in res)

# removing not existing key
print("a warning should be written below:")
res.remove_key(key)

# removing a list of keys
res.remove_key(keys_set)
print(key not in res)
print(keys_set not in res)
print(keys_list in res)

# removing a list of keys
res.remove_key(keys_list)
print(key not in res)
print(keys_set not in res)
print(keys_list not in res)


# removing all keys exepts 
res.remove_key(keys_to_keep=["V_mem", "t", "Simulation_state"])
print(list(res.keys())==['Simulation_state', 't', 'V_mem'])