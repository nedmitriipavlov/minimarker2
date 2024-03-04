freq = int(input())
lamp = int(input())
speed = int(input())
R = int(input())
F = float(input())
N = int(input()) #количество секторов
corner = 360 / (3.14 * R**2 / N)
# AXMODE LH
# CIRCLE R
for i in range(N):
    #VAA R, 0
    #RESET
    #VAA R*cos(corner), R*sin(corner)
    #RESET
    #VPA R*cos(corner / 2), R*sin(corner / 2)
    #RFROTATE corner
