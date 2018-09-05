import os
import requests
import webbrowser
import datetime
import pytz
import time
import math
import psycopg2 as p

#Since we just have to demonstrate the working of A*
#we will use our campus as the starting point and
#Alwal as the ending point. Since most nodes as obtained from
#the OSM files were unnamed, we didn't use them in the graph.

#To implement A*, we need adjacency list/matrix, to form
#adjacancy list/matrix we must find out those nodes (as extracted
#OSM API) which are directly connected. G value is from
#Google Developers Map Matrix

def distance(sourcex,sourcey,destx,desty):
    
    gmap_api_key = 'AIzaSyDo5g18GxPPdReGsvZeNph97yYi1Ud1DiM'
    dist_matrix_url='https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins={0},{1}&destinations={2},{3}&key='.format(sourcex,sourcey,destx,desty)
    api_response = requests.get(dist_matrix_url+gmap_api_key)
    api_response_dict = api_response.json()
    return(api_response_dict['rows'][0]['elements'][0]['distance']['value'])/1000
    


#Factor for 'x' gap.
km_perlat=110.57

#Function returns 'y' gap.
def km_perlong(long):
    return abs(long*math.cos(math.radians(long))*111.321)

#Returns SLD needed for heuristics. H value. 
def sld(x,y):
    return math.sqrt(x*x+y*y)
dbname = input("Type in the database where OSM data (test.sql) was dumped ")
user = input("Type in your username please ")
host = input("Host ID (Example : localhost) ")
password = input("Please enter your password ")
print("Fetching nodes from Database...")
con = p.connect("dbname={0} user={1} host={2} password={3}".format(dbname,user,host,password))
cur = con.cursor()

cur.execute("select gid,name,ST_y(geom),ST_x(geom) from points where name!='null'")
rows = cur.fetchall()
rows1=[]

for i in range(123):
    rows1.append((i,rows[i][1],rows[i][2],rows[i][3]))
rows1.append((123,'BITS Pilani Hyderabad', 17.544088, 78.571545))

############################################################

source = rows1[123] #BITS Pilani Hyderabad Campus
dest = rows1[56] #Alwal
heuristics =[]  #Hvalue
fvalue=[] #Fvalue
#For any r in rows1, r[0] is id, r[1] is name, r[2] is lat and r[3] is long
for i in range(124):
    heuristics.append(sld(abs(rows1[i][2]-dest[2])*km_perlat,km_perlong(rows1[i][3]-dest[3])))



adjacency = [[0 for j in range(124)] for i in range(124)] #To check adjacency. Initialized all to zero. 
cost = [[2000 for j in range(124)] for i in range(124)] #Infinite for now. Once the DB is fetched, we'll get the actual costs


gvalues=[] #GValue

for i in range(124):
    gvalues.append(2000.00) #Giving infinite value
    fvalue.append(2000.00 + heuristics[i]) #Initializing FValues
    
#Since checking each pair of points is almost impossible (n^3 complexity), we use an approximation/buffer area
#of radius 2.5 km around a node where we consider the other nodes as adjacent
#
##
totcount=0
for i in range(124):
    for j in range(124):
        if(j>i and sld(abs(rows1[i][2]-rows1[j][2])*km_perlat,km_perlong(rows1[i][3]-rows1[j][3]))<2.5):
            adjacency[i][j]=1
            adjacency[j][i]=1
            totcount=totcount+1
tot=0
dbname = input("Type in the database where gvalue data (gvalues.sql) was dumped")
#user = input("Type in your username please")
#host = input("Host ID (Example : localhost) ")
#password = input("Please enter your password")
print("Fetching nodes from Database...")
con1 = p.connect("dbname={0} user={1} host={2} password={3}".format(dbname,user,host,password))
#con1 = p.connect("dbname='gvalue' user='postgres' host='localhost' password='ansuman'")
cur = con1.cursor()
'''
for i in range(124):
    for j in range(124):
        if(j>i and sld(abs(rows1[i][2]-rows1[j][2])*km_perlat,km_perlong(rows1[i][3]-rows1[j][3]))>2 and sld(abs(rows1[i][2]-rows1[j][2])*km_perlat,km_perlong(rows1[i][3]-rows1[j][3]))<2.5):
            cur.execute("insert into distances values({0},{1},{2})".format(i,j,distance(rows1[i][2],rows1[i][3],rows1[j][2],rows1[j][3])))
            tot=tot+1
            print(tot)

            
con1.commit()
'''            
## Since BITS's node wasn't obtained from OSM, we added adjacency ourselves ##          
adjacency[121][123]=1
adjacency[123][121]=1
###############################################################################
##

con2 = p.connect("dbname='gvalue' user='postgres' host='localhost' password='ansuman'")
cur = con2.cursor()
cur.execute("Select * from distances")
costs = cur.fetchall()
for c in costs:
    cost[c[0]][c[1]]=c[2]
    cost[c[1]][c[0]]=c[2]

cost[121][123]=11.145
cost[123][121]=11.145

##################### The most important part of the program - A* implementation #####################################
def notempty(a,b):
    summ=0
    sumc=0
    for i in range(124):
        summ=summ+a[i]
    
        sumc=sumc+b[i]
    return summ

closed=[0 for i in range(124)]
opened=[0 for i in range(124)]
parent=[-1 for i in range(124)]

opened[source[0]]=1
parent[source[0]]=source[0]
gvalues[source[0]]=0.0
fvalue[source[0]]=gvalues[source[0]]+heuristics[source[0]]

while (notempty(opened,closed)):
    #print("Entered the loop")
    mink=0
    minn=5000.00
    for k in range(124):
        if(fvalue[k]<minn and opened[k]==1 and closed[k]==0):
            mink=k;
            minn=fvalue[k]

    smallest= mink
    opened[smallest]=0
    closed[smallest]=1
    #print("This is the smallest " + str(smallest))
    if(smallest==dest[0] ):
         break


    for j in range(124):
        if(adjacency[smallest][j]==1):
           
            if(opened[j]==0 and closed[j]==0):
                gvalues[j]=float(gvalues[smallest])+float(cost[smallest][j])
                parent[j]=smallest
                fvalue[j]=float(gvalues[j])+heuristics[j]
                opened[j]=1
            elif (opened[j]!=0 and closed[j]==0):
                if(float(gvalues[smallest])+float(cost[smallest][j])<gvalues[j]):
                    gvalues[j]=float(gvalues[smallest])+float(cost[smallest][j])
                    fvalue[j]=heuristics[j]+float(gvalues[j])
                    parent[j]=smallest
            elif(closed[j]==1):
                if(float(gvalues[smallest])+float(cost[smallest][j])<gvalues[j]):
                    closed[j]==0
                    opened[j]==1
                    gvalues[j]=float(gvalues[smallest])+float(cost[smallest][j])
        

i = dest[0]
route=[]
while (i!=source[0]):
    #print(i,rows1[i][1],parent[i],rows1[parent[i]][1])
    route.append((rows1[i][1],rows1[i][2], rows1[i][3]))
    i = parent[i]
route.append((rows1[i][1],rows1[i][2], rows1[i][3]))
for r in reversed(route): 
    print(r)

    
