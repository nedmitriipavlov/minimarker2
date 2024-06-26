from math import *


# Commands "imported" from laser's soft
def abs_visible_vector(x, y, num):
    return ' {0}, {1}, OwnMode{2})\n'.format(x, y, num)
             #return 'Line(0, 0, {0}, {1})\n'.format(x, y) ?


def visible_vector(dx, dy):
    return 'VAR {0}, {1}\n'.format(dx, dy)    # в процессе


def abs_vector(x, y):
   return 'Line({0}, {1},'.format(x, y)      # в процессе


def vector(dx, dy):
    return 'Line({0}, {1},'.format(dx, dy)   # в процессе


def circle(R: float):
    return 'Ellipse(0, 0, {0}, {0}, OwnMode0)\n'.format(R*2)          # return 'Ellipse(0, 0, {0}, {0})\n'.format(R)


def to_decart():
    return 'CoordinateSystemMode("LH")\nGalvoSize(110)\nCoordinateSystemProperties(0, 0, 5)\nMoveTo(0,0,0)\nGalvoStart("Гальвополе", "Режим по умолчанию")\nDynamics(Средняя, Средняя)\n'        # return 'CoordinateSystemMode("LH") \nMoveTo(0,0,0)\n'


def power(val, num):
    if num == 0:
        return 'LaserMode(Режим по умолчанию,40,800,70,-1)\nLaserMode(Оси,20,20,70,-1)\nLaserMode(OwnMode{0}, 0, 0, {1}, -1)\n'.format(num, val)
    return 'LaserMode(OwnMode{0}, 0, 0, {1}, -1)\n'.format(num, val)

def dynamic_mode():
    return 'DynamicMode(Средняя, 4000, 100, 200, 100, 0)\nDynamicMode(Быстрая, 4000, 100, 100, 200, 0)\nDynamicMode(Качественная, 4000, 100, 100, 200, 0)\n'


def rotate(R, angle):
    return 'CoordinateSystemMode("RF") \nMoveTo({0},{1},0) \nAbsoluteAngle(1)\n'.format(R, angle)  # return 'CoordinateSystemMode("RF") \nMoveTo({0},{1},0) \nAbsoluteAngle(1)\n'.format(R, angle)



def k_coef(angle, F):
    """Function that finds k coefficient in equation like y = kx + b for filling sector's line.
    This line forms an angle F with a bisector's line"""
    angle, F = (radians(angle), radians(F))
    k = (tan(F) + tan(pi - (pi / 2 - angle / 2))) / (1 - tan(pi - (pi / 2 - angle / 2)) * tan(F))
    return k


def b_coef(angle, num, F, delta):
    """Function that finds b coefficient in equation like y = kx + b for filling sector's line.
    This line forms an angle F with a bisector's line. Delta is distance between filling lines,
    k is step of filling process (of drawing a line)"""
    k = k_coef(angle, F)
    angle, F = (radians(angle), radians(F))
    b = -num * delta * (1 / cos(angle / 2) - (tan(angle / 2) * sin(angle / 2)) + k * sin(angle / 2))
    return b


def func(x, angle, num, F, delta):
    """Function that returns value in certain point of equation like y = kx + b for filling sector's line.
    This line forms an angle F with a bisector's line. Delta is distance between filling lines,
    k is step of filling process (of drawing a line)"""
    k = k_coef(angle, F)
    b = b_coef(angle, num, F, delta)
    return k * x + b


def crossed_point_r(angle, num, F, delta):
    """Function that returns coordinates of intersection of filling line and sector's line's point"""
    k = k_coef(angle, F)
    x = b_coef(angle, num, F, delta) / (tan(pi - (pi / 2 - radians(angle))) - k)
    y = func(x, angle, num, F, delta)
    return x, y


def where_line_crosses_circle(R, angle, num, F, delta):
    """Function that returns two points of intersection of filling line and circle"""
    b = b_coef(angle, num, F, delta)
    k = k_coef(angle, F)
    D = 4 * ((R ** 2) * (k ** 2 + 1) - b ** 2)
    if D > 0:
        x1 = (-2 * k * b + sqrt(D)) / (2 * (k ** 2 + 1))
        x2 = (-2 * k * b - sqrt(D)) / (2 * (k ** 2 + 1))
        return x1, x2
    return [-1]


def rotate_coord(x, y, share):
    share = radians(share)
    x_new = x * cos(share) + y * sin(share)
    y_new = -sin(share) * x + cos(share) * y
    return x_new, y_new


def sector(angle, R, F, delta, share, num):
    """Function that forms a filled sector!"""
    # x_edge and y_edge are points of intersection sector's line (not for x = 0!) and circle
    x_edge = R * sin(radians(angle))
    y_edge = - R * cos(radians(angle))
    # first actions are actions to create a circle a sector without filling
    first_actions = '{0}{1}{2}{3}\n'.format(abs_vector(*rotate_coord(0, -R, share)),
                                                  abs_visible_vector(0, 0, num),
                                                  abs_vector(*rotate_coord(x_edge, y_edge, share)),
                                                  abs_visible_vector(0, 0, num)
                                                  )
    # loop_actions consist of actions for filling a sector
    loop_actions = []

    # c is step of filling process
    c = 1
    k = k_coef(angle, F)
    if 0 <= k < 10 ** 5:
        x0 = 0
        x, y = crossed_point_r(angle, c, F, delta)
        b = b_coef(angle, c, F, delta)
        while 0 >= y >= y_edge:
            if b >= -R:
                loop_actions.append(abs_vector(*rotate_coord(0, b, share)))
                loop_actions.append(abs_visible_vector(*rotate_coord(x, y, share), num))
            elif where_line_crosses_circle(R, angle, c, F, delta):
                ans = where_line_crosses_circle(R, angle, c, F, delta)
                if ans == 1:
                    break
                x1, x2 = ans
                if x1 > 0 and x2 > 0:
                    x0 = min(x1, x2)
                else:
                    x0 = max(x1, x2)
                if x1 < 0 and x2 < 0:
                    break
                loop_actions.append(abs_vector(*rotate_coord(x0, -sqrt(R ** 2 - x0 ** 2), share)))
                loop_actions.append(abs_visible_vector(*rotate_coord(x, y, share), num))
            c += 1
            x, y = crossed_point_r(angle, c, F, delta)
            b = b_coef(angle, c, F, delta)

        while b > -R:
            ans = where_line_crosses_circle(R, angle, c, F, delta)
            if ans == 1:
                break
            x1, x2 = ans
            if x1 > 0 and x2 > 0:
                x0 = min(x1, x2)
            else:
                x0 = max(x1, x2)

            loop_actions.append(abs_vector(*rotate_coord(0, b, share)))
            loop_actions.append(abs_visible_vector(*rotate_coord(x0, -sqrt(R ** 2 - x0 ** 2), share), num))

            c += 1
            b = b_coef(angle, c, F, delta)

        points = where_line_crosses_circle(R, angle, c, F, delta)

        while len(points) > 1 and all([-sqrt(R ** 2 - points[0] ** 2) >= -R, -sqrt(R ** 2 - points[1] ** 2) >= -R,
                  points[0] <= x_edge, points[1] <= x_edge]):
            loop_actions.append(abs_vector(*rotate_coord(min(points), -sqrt(R ** 2 - min(points) ** 2), share)))
            loop_actions.append(
                abs_visible_vector(*rotate_coord(max(points), -sqrt(R ** 2 - max(points) ** 2), share), num))
            c += 1
            points = where_line_crosses_circle(R, angle, c, F, delta)


    elif k > 10 ** 3:
        x, y = (delta * c, c * delta * tan(pi - (pi / 2 - radians(angle))))
        while x <= x_edge:
            loop_actions.append(abs_vector(*rotate_coord(x, -sqrt(R ** 2 - x ** 2), share)))
            loop_actions.append(abs_visible_vector(*rotate_coord(x, y, share), num))
            c += 1
            x, y = (delta * c, c * delta * tan(pi - (pi / 2 - radians(angle))))

    else:
        c = -1
        elems = where_line_crosses_circle(R, angle, c, F, delta)
        x0 = max(elems)

        while x0 >= x_edge:
            c -= 1
            elems = where_line_crosses_circle(R, angle, c, F, delta)
            if elems != [-1]:
                x0 = max(elems)
            else:
                break

        while 0 <= x0 <= x_edge:
            b = b_coef(angle, c, F, delta)
            if 0 >= b >= -R:
                loop_actions.append(abs_vector(*rotate_coord(0, b, share)))
                loop_actions.append(abs_visible_vector(*rotate_coord(x0, -sqrt(R ** 2 - x0 ** 2), share), num))

            else:
                x, y = crossed_point_r(angle, c, F, delta)
                if 0 <= x <= x_edge:
                    loop_actions.append(abs_vector(*rotate_coord(x, y, share)))
                    loop_actions.append(abs_visible_vector(*rotate_coord(x0, -sqrt(R ** 2 - x0 ** 2), share), num))
            c -= 1
            elems = where_line_crosses_circle(R, angle, c, F, delta)
            if elems != [-1]:
                x1, x2 = where_line_crosses_circle(R, angle, c, F, delta)
                if x1 < 0 and x2 < 0:
                    break
                x0 = max(x1, x2)
            else:
                break

        c = -1
        elems = where_line_crosses_circle(R, angle, c, F, delta)
        b = b_coef(angle, c, F, delta)

        if elems != [-1]:
            x1, x2 = elems

        while elems != [-1] and ((x1 < 0 and x2 > x_edge) or (x1 > x_edge and x2 < 0)) and 0 >= b >= -R:
            x1, x2 = elems
            loop_actions.append(abs_vector(*rotate_coord(0, b, share)))
            x, y = crossed_point_r(angle, c, F, delta)
            if x <= x_edge:
                loop_actions.append(abs_visible_vector(*rotate_coord(x, y, share), num))
            else:
                loop_actions.pop(-1)
            elems = where_line_crosses_circle(R, angle, c, F, delta)

        c = 0
        x1, x2 = where_line_crosses_circle(R, angle, c, F, delta)
        x0 = max(x1, x2)

        while x0 >= x_edge:
            c += 1
            elems = where_line_crosses_circle(R, angle, c, F, delta)
            if elems != [-1]:
                x0 = max(elems)
            else:
                break

        while 0 <= x0 <= x_edge:
            b = b_coef(angle, c, F, delta)
            if 0 >= b >= -R:
                loop_actions.append(abs_vector(*rotate_coord(0, b, share)))
                loop_actions.append(abs_visible_vector(*rotate_coord(x0, -sqrt(R ** 2 - x0 ** 2), share), num))
            else:
                x, y = crossed_point_r(angle, c, F, delta)
                if 0 <= x <= x_edge:
                    loop_actions.append(abs_vector(*rotate_coord(x, y, share)))
                    loop_actions.append(abs_visible_vector(*rotate_coord(x0, -sqrt(R ** 2 - x0 ** 2), share), num))

            c += 1
            elems = where_line_crosses_circle(R, angle, c, F, delta)
            if elems != [-1]:
                x1, x2 = where_line_crosses_circle(R, angle, c, F, delta)
                if x1 < 0 and x2 < 0:
                    break
                x0 = max(x1, x2)
            else:
                break

        c = 0
        elems = where_line_crosses_circle(R, angle, c, F, delta)
        b = b_coef(angle, c, F, delta)

        if elems != [-1]:
            x1, x2 = elems

        while elems != [-1] and ((x1 < 0 and x2 > x_edge) or (x1 > x_edge and x2 < 0)) and 0 >= b >= -R:
            x1, x2 = elems
            loop_actions.append(abs_vector(*rotate_coord(0, b, share)))
            x, y = crossed_point_r(angle, c, F, delta)
            if x <= x_edge:
                loop_actions.append(abs_visible_vector(*rotate_coord(x, y, share), num))
            else:
                loop_actions.pop(-1)
            c += 1
            elems = where_line_crosses_circle(R, angle, c, F, delta)
            b = b_coef(angle, c, F, delta)

    return first_actions + ''.join(loop_actions)


def main(R, A, B, H, F, N, file_name='minimarker_script.txt'):
    with open(file_name, 'w') as file:

        share = 360 / N
        share_f = (B - A) / N
        share_p = (100 - 10) / N

        power_step = 10
        for i in range(N):
            file.write(power(power_step, i))
            if power_step + share_p < 100:
                power_step += share_p

        file.write(dynamic_mode())

        file.write(to_decart())
        file.write(circle(R))
        filling_step = A
        for i in range(N):
            if power_step + share_p < 100:
                power_step += share_p
            file.write(sector(share, R, F, filling_step, i * share, i))
            filling_step += share_f
        file.write('\nGalvoEnd')


# R = float(input('Радиус R: '))
# A = float(input('Нижняя граница шага заливки A: '))
# B = float(input('Верхняя граница шага заливки B: '))
# H = float(input('Шаг роста шага заливки H: '))
# F = float(input('Угол заливки относительно биссектрисы (в градусах) F: '))
# N = int(input('Число секторов N: '))
#
# main(R, A, B, H, F, N)
main(14, 0.01, 1, 0.01, 57, 12)
