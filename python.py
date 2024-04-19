import numpy as np
import matplotlib.pyplot as plt
import serial
import time

# Initializing connection with Arduino-------------
ser = serial.Serial('/dev/ttyACM0',115200,timeout=2)
if not ser:
    print("Serial error")
    exit()
#--------------------------------------------------

def getData():
    ser.flushOutput()
    text = ser.readline().decode('utf-8').split('\n')[0]
    data = np.array(list(map(float,text.split())))
    return data

def printTable(a,p,w,u):
    a = np.round(a,7)
    p = np.round(p,7)
    w = np.round(w,7)
    u = np.round(u,7)
    print(f"{prev*6}")
    print(f"{cyan}{'':<21} {'X':>15} {'Y':>15} {'Z':>15}")
    print(f"{cyan}{'Accleration(m/s^2)':<21}{white} {a[0]:>15} {a[1]:>15} {a[2]:>15}")
    print(f"{cyan}{'Position(m)':<21}{white} {p[0]:>15} {p[1]:>15} {p[2]:>15}")
    print(f"{cyan}{'RadialVelocity(deg/s)':<21}{white} {w[0]:>15} {w[1]:>15} {w[2]:>15}")
    print(f"{cyan}{'RadialPos(deg)':<21}{white} {u[0]:>15} {u[1]:>15} {u[2]:>15}")


def Rmatrix(x_angle,y_angle,z_angle):
    a = x_angle
    b = y_angle
    c = z_angle
    cx = np.cos(x_angle)
    sx = np.sin(x_angle)
    cy = np.cos(y_angle)
    sy = np.cos(y_angle)
    cz = np.cos(z_angle)
    sz = np.cos(z_angle)
    return (
        np.array([
            [np.cos(a), -np.sin(a), 0],
            [np.sin(a), np.cos(a), 0],
            [0,0,1]
            ]) @
        np.array([
            [np.cos(b), 0, np.sin(b)],
            [0,1,0],
            [-np.sin(b),0,np.cos(b)]
            ]) @
        np.array([
            [1,0,0],
            [0,np.cos(c),-np.sin(c)],
            [0,np.sin(c),np.cos(c)]
            ])
        )

# Constants----------------------------------------
# delay in seconds between two samples, where acceleration is assumed constant
dt = 0.019
# default size of 3D plot cube in meters
size = 0.2
# calibration sample count
N = 100
# colors
white = "\x1b[38;2;255;255;255m"
red = "\x1b[38;2;200;10;10m"
green = "\x1b[38;2;10;200;10m"
cyan = "\x1b[38;2;10;200;200m"
# extras
prev = "\033[F"
space = "\033[K\r"
#------------------------------------------------

# Configuring matplotlib------------------------
plt.ion()
fig = plt.figure()
ax = fig.add_subplot(projection='3d')
ax.set_xlim(-size,size)
ax.set_xlabel('X')
ax.set_ylim(-size,size)
ax.set_ylabel('Y')
ax.set_zlim(-size,size/4)
ax.set_zlabel('Z')
ax.grid(True)
line, = ax.plot([],[],[],'c-')
#-----------------------------------------------

# Variables-------------------------------------
x,y,z = [],[],[]
a = np.array([0.,0.,0.])    # acceleration vector
p = np.array([0.,0.,0.])    # position vector
w = np.array([0.,0.,0.])    # angular velocity vector
u = np.array([0.,0.,0.])    # angular position vector
acc_calib = np.array([0.,0.,0.])
gyr_calib = np.array([0.,0.,0.])
#----------------------------------------------

# Calibration---------------------------------
print(f"{green}Calibrating...")
for i in range(N):
    try:
        data = getData()
        assert len(data)==6
    except Exception as E:
        print(f"{red}Error: ",E)
        continue
    acc_calib += data[:3]/N
    gyr_calib += data[3:]/N
    print(f"{white}{i}{cyan} {list(np.round(data,5))}",end=f"\n{prev}")
    time.sleep(dt-dt/100)
print(f"{green}Calibration done: ",np.round(acc_calib,5),np.round(gyr_calib,5))
#---------------------------------------------


print('\n'*10)
while True:
    try:
        data = getData()
        assert len(data)==6
    except Exception as E:
        print(f"{red}Error: ",E)
        continue
    w = data[3:] - gyr_calib
    u += (w*dt)*np.pi/180
# rotation matrix multiplication for orientation
    a = (Rmatrix(u[0],u[1],u[2])@data[:3] - np.array([0.,0.,9.8]))
    p += a*(dt**2)/2
    #print(f"{white}>{cyan}",a,w)
    #print(f"{white}>>{cyan}",p,u,end=f"\r\033[F{50*' '}\n{50*' '}\n\033[F\033[F")
    printTable(a,p,w,u*180/np.pi)
    x.append(p[0])
    y.append(p[1])
    z.append(p[2])
    line.set_xdata(x)
    line.set_ydata(y)
    line.set_3d_properties(z)
    plt.draw()
    plt.pause(dt-dt/100)
