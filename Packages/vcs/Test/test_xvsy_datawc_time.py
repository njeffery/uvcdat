# Adapted for numpy/ma/cdms2 by convertcdms.py
import sys,cdms2 as cdms,vcs,cdtime,support,os
bg=support.bg

t0=cdtime.comptime(2000,7,15)
t1=cdtime.comptime(2000,11)
f=cdms.open(os.path.join(cdms.__path__[0],'..','..','..','..','sample_data','ta_ncep_87-6-88-4.nc'))

s=f('ta',latitude=slice(5,6),level=slice(0,1),longitude=slice(6,7),squeeze=1)
s2=f('ta',latitude=slice(5,6),level=slice(0,1),longitude=slice(18,19),squeeze=1)
s3=s()+30
s4=s2()+30
## s.info()
print s.shape
t2=s3.getTime()
t2.units='months since 1949-2'
x=vcs.init()
y=vcs.init()


b=x.createxvsy('new2')
b.datawc_y1=t0
b.datawc_y2=t1
b.datawc_x1=t0
b.datawc_x2=t1

x.plot(s,s2,b,bg=bg)
support.check_plot(x)
y.plot(s3,s4,b,bg=bg)
support.check_plot(y)
x.clear()
y.clear()

b.script('test.scr','w')

a = x.listelements('xvsy')
x.removeobject(b)
a2 = x.listelements('xvsy')
if a2==a:
    raise Exception,"Error obj not removed"
x.scriptrun('test.scr')
a3 = x.listelements('xvsy')
if a3!=a:
    raise Exception,"Error obj not loaded"
b=x.getxvsy('new2')
