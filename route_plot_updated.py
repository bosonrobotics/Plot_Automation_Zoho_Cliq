import numpy as np
import argparse
import matplotlib.pyplot as plt
import os
import bagpy
from bagpy import bagreader
import pandas as pd
import math
from pathlib import Path


def distance_in_km(lat1,lon1,lat2,lon2):
    lat1= lat1/10**7
    lat2 = lat2/10**7
    lon1= lon1/10**7
    lon2=lon2/10**7
    radius = 6371000  
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) * math.sin(dlon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = radius * c
    return d

# Set the path to the directory containing the images
username = os.getlogin()  # Get the current user's username
dir_path =f"/home/{username}/.bags"
# bag_directory = os.path.dirname(args.rosbag)

parser = argparse.ArgumentParser()

parser.add_argument('-b', '--rosbag', required=True,
    help="the rosbag file")

args = parser.parse_args()

b = bagreader(args.rosbag)
print(b.topic_table.to_string())
for index, row in b.topic_table.iterrows():
	print(row['Topics'])

canpose = b.message_by_topic('/received_messages')
pose = b.message_by_topic('/pure_pursuit_diagnose')
pose = b.message_by_topic('/pilot_status')
gpspose = b.message_by_topic('/mavros/gpsstatus/gps2/raw')
pose = b.message_by_topic('/vehicle/odom')
df_pose = pd.read_csv(pose)
tpose = b.message_by_topic('/target_pose')
df_tpose= pd.read_csv(tpose)
df_cpose= pd.read_csv(canpose)

gps_pose=pd.read_csv(gpspose)
lat1=0
lan1=0
distance=0
s_time=0
e_time=0
for index, row in gps_pose.iterrows():
	if (lat1==0):
		lat1=row['lat']
		lan1=row['lon']
		s_time=row['Time']
	else:
		distance= distance + distance_in_km(lat1,lan1, row['lat'], row['lon'])
		lat1=row['lat']
		lan1=row['lon']
		e_time=row['Time']

start_distance_travelled=0
end_distance_travelled=0
can_516= df_cpose.loc[df_cpose['id'] == 516]
msg=""
if (len(can_516)>=2):
	my_last_canbus = eval(can_516.iloc[-1]['data'])
	my_first_canbus= eval(can_516.iloc[0]['data'])
	last_distance_travelled = my_last_canbus[6]*2**24 + my_last_canbus[5]*2**16 +my_last_canbus[4]*2**8 + my_last_canbus[3]
	fist_distance_travelled = my_first_canbus[6]*2**24 + my_first_canbus[5]*2**16 +my_first_canbus[4]*2**8 + my_first_canbus[3]				
	print("As Canbus id Total distance Travelled: %d unit" %(last_distance_travelled-fist_distance_travelled))
	msg = "\nCanBus  Total distance Travelled: %d unit" %(last_distance_travelled-fist_distance_travelled)

print("Gps Distance %f Meter" %(distance))
msg = "%s GPS Distance %f Meter\n" %(msg,distance)
print("Total Time %f sec" %(e_time-s_time))
msg = "%s Total Time %f sec" %(msg,e_time-s_time)
print("Speed: %f meter/sec" %(distance/(e_time-s_time)))
msg = "%s Speed: %f meter/sec" %(msg, distance/(e_time-s_time))

fig = plt.figure()
ax = plt.axes()
plt.plot(df_pose['pose.pose.position.x'], df_pose['pose.pose.position.y'],linestyle='solid',color='r',label="Actual Pose") 
plt.plot(df_tpose['pose.position.x'], df_tpose['pose.position.y'],linestyle='dotted', color='b',label="Target Pose")
plt.annotate("MS",(df_pose['pose.pose.position.x'][0], df_pose['pose.pose.position.y'][0]))
plt.annotate("ME",(df_pose['pose.pose.position.x'][-1:], df_pose['pose.pose.position.y'][-1:]))
plt.annotate("TS",(df_tpose['pose.position.x'][0], df_tpose['pose.position.y'][0]))
plt.annotate("TE",(df_tpose['pose.position.x'][-1:], df_tpose['pose.position.y'][-1:]))
find_index=(args.rosbag).find('_')+1
plt.title("%s Target vs Actual" %((args.rosbag)[find_index:(len(args.rosbag)-4)]), color="#023020")
plt.legend()
fig.text(.5, .0001, msg, ha='center', fontsize="small",fontweight='extra bold')
png_file = os.path.join(dir_path , f"{Path(args.rosbag).stem}.png")
# png_file="%s.png" %(Path(args.rosbag).stem)
plt.savefig(png_file)
