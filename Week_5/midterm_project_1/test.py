import pandas as pd
import numpy as np
import copy

flights_ = pd.read_csv('../../../large_files/flights_w_weather_full.csv')

flights = copy.deepcopy(flights_)#.sample(10**6)
cols = ['fl_date','op_unique_carrier','origin_airport_id','dest_airport_id','dep_time','dep_delay','taxi_out','carrier_delay','weather_delay','nas_delay','security_delay','late_aircraft_delay']
flights = flights[cols]

import random

eps = 2**-16
indys = flights.loc[~flights.carrier_delay.isna()].index
total = len(indys)
count = 0
for i in indys:
    print(i/total*100)
    c = flights.loc[i,'late_aircraft_delay']
    w = flights.loc[i,'weather_delay']
    n = flights.loc[i,'nas_delay']
    s = flights.loc[i,'security_delay']
    l = flights.loc[i,'late_aircraft_delay']
    max_delay = max([c,w,n,s,l,1])
    k = [k for k,j in enumerate([c,w,n,s,l]) if j == max_delay]

    if not k:
        k = random.randint(0,4)
    else:
        rand_gen = random.choice(k)

    flights.loc[i,'carrier_delay'] = int(c+int(rand_gen == 0)*eps > max_delay)
    flights.loc[i,'weather_delay'] = int(w+int(rand_gen == 1)*eps > max_delay)
    flights.loc[i,'nas_delay'] = int(n+int(rand_gen == 2)*eps > max_delay)
    flights.loc[i,'security_delay'] = int(s+int(rand_gen == 3)*eps > max_delay)
    flights.loc[i,'late_aircraft_delay'] = int(l+int(rand_gen == 4)*eps > max_delay)

    flights.to_csv('../../../large_files/flights_transformed.csv',index=False)