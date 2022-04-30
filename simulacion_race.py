# -*- coding: utf-8 -*-
"""
Created on Tue Apr 26 19:22:15 2022

@author: FreHernd
"""

import os
import numpy as np
import pandas as pd
from itertools import cycle
from mpl_toolkits.mplot3d import Axes3D
import random
from scipy.interpolate import interp1d
colors = cycle('bgrcmykbgrcmykbgrcmykbgrcmyk')

dims = 1
step_t = 350   
partition_n=32
race=[2,17]
#race=[1,19]
df_interp = pd.DataFrame()
dog_lane= pd.DataFrame()
for id_race in race:
    print(id_race)
    #ganado
    win=(random.randrange(1, 99)) # perro ganador
    dog=[win]
    for k in range(1,10): #k=12
        #ot = (random.randrange(1, 999))
        ot=random.randint(1,999)
        if  ot==win:
            next()
        else:
            if ot not in dog: dog.append(ot)
    dog_lane_aux= pd.DataFrame(dog)
    dog_lane_aux.columns = ['id_dog']
    dog_lane_aux.reset_index(drop=False, inplace=True)
    dog_lane_aux.columns = ['lane','id_dog']
    dog_lane_aux['lane'] = dog_lane_aux['lane'] +1
    dog_lane_aux['id_race']=id_race
    dog_lane= dog_lane.append(dog_lane_aux)
    
    #step_set = [-100, 0, 100]
    df_dogs=pd.DataFrame()

    for k in dog: #k=989
        #print(k)
        if k==win:
            step_n=step_t 
            v_time=v_time=(random.uniform(5.3, 5.8))
        else:    
            step_n=(random.randrange(step_t -17, step_t - 2)) # puesto en pista
            v_time=(random.uniform(6, 9)) # segundos por cada 100 metros
        time_n=v_time*step_n/100 # total segundos carrera de step_n
    
        step_set = [-(step_n/time_n)/8, (step_n/time_n)/2, step_n/time_n] #  velocidad promedio 
        #step_set = [-1 ,0, 1]
        origin = np.zeros((1,dims))
        # Simulate steps 
        step_shape = (step_n,dims)
        # pasos por segundo o metros por segundo
        steps = np.random.choice(a=step_set, size=step_shape)
        path = np.concatenate([origin, steps]).cumsum(0)
    
        path= path[path <= step_t*(1.05)]
        if  path[-1:]>min(path[-2:]) and min(path[-2:])>  step_t:
            path= path[path <= min(path[-2:])]
        path[-1:]=step_t
    
        start = path[:1]
        stop = path[-1:]
       
        df=pd.DataFrame(path)
        df['id_dog']=k
        df['id_race']=id_race
        df.reset_index(drop=False, inplace=True)
        df.columns = ['time', 'distance', 'id_dog','id_race']
        a=np.stack(i*step_t/partition_n for i in range(1,partition_n+1))
        df_dogs=df_dogs.append(df)
        for col in a:
            y_interp = interp1d(df['distance'], df['time'])
            y=y_interp(col)
            df_aux =  pd.DataFrame.from_records({'time':y,'distance': col,'id_dog': k,'id_race':id_race} , index=[0]) 
            df_interp=pd.concat([df_aux,df_interp])
                
        df_interp.reset_index(drop=True, inplace=True)
        df_interp['speed']=df_interp.distance/df_interp.time
        df_interp['partition'] = df_interp.groupby(['id_race','id_dog'])['time'].rank(method='first',ascending=True)
        df_interp['ranking'] =  df_interp.groupby(['id_race','partition'])['time'].rank(method='first',ascending=True)

time_min=pd.DataFrame(df_interp.groupby(["id_race","partition"]).min("time")['time'])
time_min.reset_index(inplace=True)
time_min.columns = ['id_race','partition', 'time_min']
df_interp=df_interp.merge(time_min,left_on=['id_race','partition'] ,right_on=['id_race','partition'],how="inner")
df_interp['distance_min'] =  df_interp.speed*df_interp.time_min
df_interp=df_interp.merge(dog_lane,left_on=['id_race','id_dog'] ,right_on=['id_race','id_dog'],how="inner") 


valores=["partition","id_race","id_dog",'lane','distance_min','time_min','time','speed','ranking' ]
df_interp=df_interp[valores]
df_interp.columns = ['partition','id_race','id_dog','lane','distance','time_min','time','speed','ranking' ]

validar=df_interp[(df_interp['partition']==16)]
validar=validar[(validar['id_race']==2)]



'''os.chdir(r'C:/Users/FREHERND/Desktop/carreras/output/')
output_filename = 'simulation_partition_16.csv'
df_interp.to_csv(output_filename,header=True, index=False,sep=";",decimal=",")
output_filename = 'simulation_16.csv'
df_dogs.to_csv(output_filename,header=True, index=False,sep=";",decimal=",")'''

df_interp['partition']=df_interp['partition'].astype(int)
df_interp['ranking']=df_interp['ranking'].astype(int)

dict_data=df_interp.to_dict(orient='records')
json_data = json.dumps(dict_data,indent=3)


out_file = open("data_json_32_20220427.json", "w") 
json.dump(dict_data, out_file, indent = 3)  
out_file.close()
