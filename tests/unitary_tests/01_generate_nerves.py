import eit as eit

if __name__ == "__main__":
    nerves_folder = "./nerves/"
    parameters = {  
        "outer_d" : None ,   
        "nerve_d" : 105 , 
        "nerve_l" : 5010 ,
        "fasc1_d" : 70  ,
        "fasc1_y" : 0  ,  
        "fasc1_z" : 0  ,  
        "n_ax1" : 10 ,
        "t_sim" : 20 , 
        "dt" : 0.001,
        "percent_unmyel":1,
    }

    fname = "u1_nerve.json"
    eit.generate_1_fasc_nerve(
        nerves_folder+fname,
        **parameters
    )

    parameters.update({
        "percent_unmyel": 0,
        "nerve_l":20050,
        "t_sim" : 5 ,
    })
    fname = "m1_nerve.json"
    eit.generate_1_fasc_nerve(
        nerves_folder+fname,
        **parameters
    )