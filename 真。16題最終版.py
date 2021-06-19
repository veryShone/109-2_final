import requests
import json
import numpy as np

#爬蟲-----------------------------------------------------------------------

#網址
url = 'https://opendata.cwb.gov.tw/api/v1/rest/datastore/O-A0001-001?Authorization=CWB-CA26F272-B818-4E31-838B-FEE190DA0D77&elementName=ELEV,PRES,TEMP'
#得到網頁內容 type=str
text = requests.get(url).text
#將得到網頁內容轉成 dict
data = json.loads(text)
#資料所在位置
location = data['records']["location"]
#儲存測站名稱
測站s = [ location[i]["locationName"] for i in range(len(location)) ]
#儲存測站海拔
海拔s = [float(location[i]["weatherElement"][0]["elementValue"]) \
        for i in range(len(location))]
#儲存測站溫度
溫度s = [float(location[i]["weatherElement"][1]["elementValue"]) \
        for i in range(len(location))]
#儲存測站氣壓
氣壓s = [float(location[i]["weatherElement"][2]["elementValue"]) \
        for i in range(len(location))]


#開關-----------------------------------------------------------------------

  #請在執行前調整
  # 0關 1開
print_data = 0
清除outliers = 1
擬合漸近線 = 1
漸近線投影 = 1
圖例 = 0

#判別outliers----------------------------------------------------------------
'''邏輯錯誤，嚴重BUG，會跳號
counter=0
for k in range(len(測站s)):
    if k<len(測站s):
      if 溫度s[k]==-99.0  or 氣壓s[k]==-99.0:
          counter+=1
          if 清除outliers ==1:
            del 測站s[k]
            del 溫度s[k]
            del 氣壓s[k]
            del 海拔s[k]
'''
  #new solution

#準備好放outliers的索引值得空串列
outs =[]
#判斷每筆溫度和海拔，是否為outlier
for out_index in range(len(測站s)):
    if 溫度s[out_index]==-99.0  or 氣壓s[out_index]==-99.0:
          #將outliers的索引值放入 outs 串列
          outs.append(out_index)
          
#outliers 數量
counter =  len(outs)
#將 outs 串列轉成 array
outs = np.array(outs)

if 清除outliers ==1:
    #從數據中清除outliers
    for out in outs:
        del 測站s[out]
        del 溫度s[out]
        del 氣壓s[out]
        del 海拔s[out]
        #避免跳號
        outs-=1
    print('共清除',counter,'筆outlier')

#Data-----------------------------------------------------------------------
print('共',len(測站s),'筆數據')
if 清除outliers ==0:
    #print outliers的數據
    print('包含',counter,'筆outlier')
    if print_data ==0:
        for j in range(len(測站s)):
          if 溫度s[j] ==-99.0  or 氣壓s[j] ==-99.0:
            print(j+1,'. ',測站s[j] +'：')
            print('    海拔：'+str(海拔s[j]))
            print('    溫度：'+str(溫度s[j]))
            print('    氣壓：'+str(氣壓s[j]))
        print('共',counter,'筆outlier')
if print_data ==1:
  #print 全資料
    for n in range(len(測站s)):
            print(n+1,'. ',測站s[n] +'：')
            print('    海拔：'+str(海拔s[n]))
            print('    溫度：'+str(溫度s[n]))
            print('    氣壓：'+str(氣壓s[n]))
    print('共',len(測站s),'筆數據')

    print('')

    if 清除outliers ==1:
        #不print outliers，並告知清除數量
        print('共清除',counter,'筆outlier')
    else:
      #print outliers的數據
      print('包含',counter,'筆outlier')
      for j in range(len(測站s)):
          if 溫度s[j] ==-99.0  or 氣壓s[j] ==-99.0:
            print(j+1,'. ',測站s[j] +'：')
            print('    海拔：'+str(海拔s[j]))
            print('    溫度：'+str(溫度s[j]))
            print('    氣壓：'+str(氣壓s[j]))
      print('共',counter,'筆outlier')



#作圖-----------------------------------------------------------------------

#方法一，利用關鍵字
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy import stats #計算R^2

#定義座標軸
fig = plt.figure()
ax1 = plt.axes(projection='3d')
#座標軸名稱
ax1.set_xlabel('Temperature (°C)',color="g",size=16)
ax1.set_ylabel('pressure (hPa)',color="r",size=16)
ax1.set_zlabel('Elevation (m)',color="b",size=16)


z = 海拔s
x = 溫度s
y = 氣壓s
ax1.scatter3D(x,y,z, cmap='Blacks')  #繪製散點圖
#ax1.plot3D(x,y,z,'gray')    #繪製空間曲線


linear_model_xy=np.polyfit(x,y,1) #xy擬合
linear_model_fn_xy=np.poly1d(linear_model_xy)


linear_model_yz=np.polyfit(y,z,1) #yz擬合
linear_model_fn_yz=np.poly1d(linear_model_yz)


linear_model_xz=np.polyfit(x,z,1) #xz擬合
linear_model_fn_xz=np.poly1d(linear_model_xz)

x_s=np.arange(min(x),max(x))
yy=linear_model_fn_xy[1]*x_s+linear_model_fn_xy[0] #xy擬合的y值
zz=linear_model_fn_yz[1]*yy+linear_model_fn_yz[0]  #yz擬合的z值
zx=linear_model_fn_xz[1]*x_s+linear_model_fn_xz[0] #xz擬合的z值

if 漸近線投影 == 1:
    ax1.plot3D(x_s,yy,min(zz),'blue',label='P = '+\
               str(linear_model_fn_xy).lstrip(' \n').replace('x','T'))
    
    #plt.plot(x_s,linear_model_fn_xy(x_s),color="green") #無法調z
    
    xp=yy*0+max(x_s) # x projection   x_s最大值
    ax1.plot3D(xp,yy,zz,'red',label='E = '+\
               str(linear_model_fn_yz).lstrip(' \n').replace('x','P'))  #yz投影

    yp=yy*0+max(yy) # y projection   yy最大值
    ax1.plot3D(x_s,yp,zz,'green',label='P = '+\
               str(linear_model_fn_xy).lstrip(' \n').replace('x','T'))  #xz投影

    #計算R^2值
    resR = stats.linregress(y, z)
    resG = stats.linregress(x, z)
    resB = stats.linregress(x, y)
    #列出方程與R^2
    print('')
    print('投影方程：\n  氣溫 T，氣壓 P，海拔 E')
    
    print('  PE平面(紅)：E =',str(linear_model_fn_yz).lstrip(' \n').replace('x','P'))
    print('              R^2 =',resR.rvalue**2)
    print('\n  TE平面(綠)：E =',str(linear_model_fn_xz).lstrip(' \n').replace('x','T'))
    print('              R^2 =',resG.rvalue**2)
    print('\n  TP平面(藍)：P =',str(linear_model_fn_xy).lstrip(' \n').replace('x','T'))
    print('              R^2 =',resB.rvalue**2)



if 擬合漸近線 == 1:
    print('')
    print('漸近線比例式(黑)：\n  氣溫 T，氣壓 P，海拔 E')
    if x_s[0] >= 0:
        eq = '(T - '+str(x_s[0])+')=(P - '+str(yy[0])+')/('+str(yy[1]-yy[0])\
              +')=(E - '+str(zz[0])+')/('+str(zz[1]-zz[0])+')'
        print('  '+eq)
    else:
        eq = '(T +'+str(-1*x_s[0])+')=(P - '+str(yy[0])+')/('+str(yy[1]-yy[0])\
              +')=(E - '+str(zz[0])+')/('+str(zz[1]-zz[0])+')'
        print('  '+eq)
    ax1.plot3D(x_s,yy,zz,'black',label=eq)  #xy擬合線加入z
    
    
if 圖例 == 1:
    plt.legend()


plt.show()



