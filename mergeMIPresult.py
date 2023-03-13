import datetime
import glob
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

tag = "_simultaneousFit"

def set_axes_height(ax, h):
    fig = ax.figure
    aw, ah = np.diff(ax.transAxes.transform([(0, 0), (1, 1)]), axis=0)[0]
    fw, fh = fig.get_size_inches()
    dpi = fig.get_dpi()
    scale = h / (ah / dpi)
    fig.set_size_inches(fw*scale, fh*scale, forward=True)

df = pd.read_csv('run_match/pion_beams_sps_oct2022.csv',sep='\t')
print(df)

MergedResult = None
problematic_file = []

for _,row in df.iterrows():
    r    = row['run']
    E    = row['E']
    pad  = row['pad']
    gain = row['gain']

    r = f'/home/daq/sps_oct2022/pion_runs/pion_beam_150_{gain}fC/' + r
    try:
      df_result = pd.read_hdf(r+f'/pad{pad}' + tag + '.h5')
      if MergedResult is None:
        MergedResult = df_result
      else:
        MergedResult = pd.concat([MergedResult,df_result],axis=0)
    except:
      problematic_file.append((pad,gain))

Cell_type = {
  'mousebite':[1,8,96,111,190,198],
  'small_edge':[2,3,4,5,6,7,112,127,141,156,169,180,126,140,155,168,179,189],
  'large_edge':[9,19,29,40,52,66,81,18,28,39,51,65,80,95,191,192,193,194,195,196,197],
  'outer_cal':[13,61,69,142,153,162],
  'inner_cal':[14,62,70,143,154,163],
  'full':[]
}
pad_to_padType = dict()
for i in range(1,199):
  already_define = False
  for key in Cell_type:
    if i in Cell_type[key]:
      pad_to_padType[i] = key
      already_define = True
  if not already_define:
    pad_to_padType[i] = 'full'
MergedResult['Cell type'] = MergedResult['pad'].replace(pad_to_padType)

print(MergedResult)

info_list = []
info_list_onlyFullPad = []

for gain, gain_group in MergedResult.groupby('gain'):
  for chip, chip_group in gain_group.groupby('chip'):
    info_list.append((gain,chip,round(chip_group['mip'].mean(),2),round(chip_group['mip'].std(),2),round(chip_group['SoN'].mean(),2),round(chip_group['SoN'].std(),2),len(chip_group['SoN'])))
    for type_, type_group in chip_group.groupby('Cell type'):
      if not type_ == 'full':
        continue
      info_list_onlyFullPad.append((gain,chip,round(type_group['mip'].mean(),2),round(type_group['mip'].std(),2),round(type_group['SoN'].mean(),2),round(type_group['SoN'].std(),2),len(type_group['SoN'])))

for gain,gain_group in MergedResult.groupby('gain'):
  info_list.append((gain,'all',round(gain_group['mip'].mean(),2),round(gain_group['mip'].std(),2),round(gain_group['SoN'].mean(),2),round(gain_group['SoN'].std(),2),len(gain_group['SoN'])))   
  for type_, type_group in gain_group.groupby('Cell type'):
      if not type_ == 'full':
        continue
      info_list_onlyFullPad.append((gain,'all',round(type_group['mip'].mean(),2),round(type_group['mip'].std(),2),round(type_group['SoN'].mean(),2),round(type_group['SoN'].std(),2),len(type_group['SoN'])))


#    print(f'ADC range = {gain}fC, chip = {chip}')
#    print('  -- MIP peak  = %.2f +/- %.2f'%(chip_group['mip'].mean(),chip_group['mip'].std()))
#    print('  -- Sig/Noise = %.2f +/- %.2f'%(chip_group['SoN'].mean(),chip_group['SoN'].std()))

df1 = pd.DataFrame(np.array(info_list),columns=['gain','chip','mip_mean','mip_std','SoN_mean','SoN_std','NumPads'])
print(df1)
df1.to_csv('MIPstudy/mip_summary.csv',sep='\t')

df2 = pd.DataFrame(np.array(info_list_onlyFullPad),columns=['gain','chip','mip_mean','mip_std','SoN_mean','SoN_std','NumPads'])
print(df2)
df2.to_csv('MIPstudy/mip_summary_onlyFullPad.csv',sep='\t')

MergedResult.to_csv('MIPstudy/mip_detail.csv',sep='\t')

MergedResult = MergedResult.rename(columns={'mip':'MIP peak [ADC counts]','gain':'ADC range','SoN':'S/N'})
MergedResult['ADC range'] = MergedResult['ADC range'].map({80: '80fC', 160:'160fC', 320:'320fC'})

sns.set_theme()

plt.rcParams['font.size'] = '50'
sns.relplot(data=MergedResult, x="pad", y="MIP peak [ADC counts]", hue="ADC range",style="ADC range")
plt.ylim(bottom=0) #ymin is your value
plt.savefig('MIPstudy/Pad_vs_MIP' + tag + '.png')

sns.relplot(data=MergedResult, x="pad", y="noise", hue="ADC range",style="ADC range")
plt.ylim(bottom=0) #ymin is your value
plt.savefig('MIPstudy/Pad_vs_noise' + tag + '.png')

sns.relplot(data=MergedResult, x="pad", y="S/N", hue="ADC range", style="ADC range")
plt.ylim(bottom=0) #ymin is your value
plt.savefig('MIPstudy/Pad_vs_SoN' + tag + '.png')

sns.catplot(data=MergedResult, x="chip", y="MIP peak [ADC counts]", col="ADC range",kind="box")
plt.ylim(bottom=0) #ymin is your value
plt.savefig('MIPstudy/chip_vs_MIP' + tag + '.png')

sns.catplot(data=MergedResult, x="chip", y="S/N", col="ADC range", kind="box")
plt.ylim(bottom=0) #ymin is your value
plt.savefig('MIPstudy/chip_vs_SoN' + tag + '.png')

for type_, type_group in MergedResult.groupby('Cell type'):
  if type_ == 'full': 
  
    sns.catplot(data=type_group, x="chip", y="MIP peak [ADC counts]", col="ADC range",kind="box")
    plt.ylim(bottom=0) #ymin is your value
    plt.savefig('MIPstudy/chip_vs_MIP_fullPadOnly' + tag + '.png')

    sns.catplot(data=type_group, x="chip", y="S/N", col="ADC range", kind="box")
    plt.ylim(bottom=0) #ymin is your value
    plt.savefig('MIPstudy/chip_vs_SoN_fullPadOnly' + tag + '.png')


plt.rcParams['font.size'] = '24'
cat = sns.catplot(data=MergedResult, x="Cell type", y="MIP peak [ADC counts]", col="ADC range", kind="box")
xlabel = []
for xtick in plt.xticks()[1]:
  xlabel.append(xtick.get_text())
print(xlabel)
fig = cat.fig
for ax in fig.axes:
  ax.set_xticklabels(xlabel,rotation = 30)
  set_axes_height(ax, 4)
plt.ylim(bottom=0) #ymin is your value 
plt.savefig('MIPstudy/cellType_vs_MIP' + tag + '.png')

cat = sns.catplot(data=MergedResult, x="Cell type", y="S/N", col="ADC range", kind="box")
xlabel = []
for xtick in plt.xticks()[1]:
  xlabel.append(xtick.get_text())
print(xlabel)
fig = cat.fig
for ax in fig.axes:
  ax.set_xticklabels(xlabel,rotation = 30)
  set_axes_height(ax, 4)
plt.ylim(bottom=0) #ymin is your value
plt.savefig('MIPstudy/cellType_vs_SoN' + tag + '.png')
print("problematic (pad, ADC range):")
for i, prob_f in enumerate(problematic_file):
  print(i, prob_f)
    
