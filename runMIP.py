import datetime
import glob
import os
import pandas as pd

df = pd.read_csv('run_match/pion_beams_sps_oct2022.csv',sep='\t')
print(df)

trigtime_range0=67
trigtime_range1=95
trigtime_range2=67
trigtime_range3=95
limit_range0 = datetime.datetime.strptime('run_20221008_084814'.split('run_')[1],"%Y%m%d_%H%M%S").timestamp()
limit_range1 = datetime.datetime.strptime('run_20221008_124604'.split('run_')[1],"%Y%m%d_%H%M%S").timestamp()
limit_range2 = datetime.datetime.strptime('run_20221011_093547'.split('run_')[1],"%Y%m%d_%H%M%S").timestamp()

for _,row in df.iterrows():
    r    = row['run']
    E    = row['E']
    pad  = row['pad']
    gain = row['gain']

    _,stime = r.split('run_')
    timestamp = datetime.datetime.strptime(stime,"%Y%m%d_%H%M%S").timestamp()
    if timestamp<limit_range0:
        trigtime = trigtime_range0
    elif timestamp<limit_range1:
        trigtime = trigtime_range1
    elif timestamp<limit_range2:
        trigtime = trigtime_range2
    else:
        trigtime = trigtime_range3
    
    if gain == 80:
      min_adc = 10
      max_adc = 100
    elif gain == 160:
      min_adc = 6
      max_adc = 50
    else:
      min_adc = 4 
      max_adc = 50   
    r = f'/home/daq/sps_oct2022/pion_runs/pion_beam_150_{gain}fC/' + r
    print(r,trigtime,pad,gain)
    cmd=f'cd /home/daq/hexactrl-sw/hexactrl-script; source etc/env.sh; python3 analysis/level0/fitMIP.py -i {r}/data.root -p {pad} -t {trigtime} -M {max_adc} -m {min_adc} -g {gain}'
    os.system(cmd)
    if pad in [142, 61, 153]:
        cmd=f'cd /home/daq/hexactrl-sw/hexactrl-script; source etc/env.sh; python3 analysis/level0/fitMIP.py -i {r}/data.root -p {pad+1} -t {trigtime} -M {max_adc} -m {min_adc} -g {gain}'
        os.system(cmd)
    else:
        pass
    
