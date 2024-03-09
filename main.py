from math import *


# Commands "imported" from laser's soft
def abs_visible_vector(x, y):
    return 'VAA {0}, {1}\n'.format(x, y)


def visible_vector(dx, dy):
    return 'VAR {0}, {1}\n'.format(dx, dy)


def abs_vector(x, y):
    return 'VPA {0}, {1}\n'.format(x, y)


def vector(dx, dy):
    return 'VPR {0}, {1}\n'.format(dx, dy)


def circle(R: float):
    return 'CIRCLE {0}\n'.format(R)


def to_decart():
    return 'AXMODE "LH"\nMOVER 0, 0\n'


def power(val):
    return 'POWER {}\n'.format(val)


def rotate(R, angle):
    return 'AXMODE RF\nMOVER {0}, {1}\nRFROTATE 1\n'.format(R, angle)


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
    x1 = (-2 * k * b + sqrt(D)) / (2 * (k ** 2 + 1))
    x2 = (-2 * k * b - sqrt(D)) / (2 * (k ** 2 + 1))
    return x1, x2


def sector(angle, R, F, delta):
    """Function that forms a filled sector!"""
    # x_edge and y_edge are points of intersection sector's line (not for x = 0!) and circle
    x_edge = R * sin(radians(angle))
    y_edge = - R * cos(radians(angle))
    # first actions are actions to create a circle a sector without filling
    first_actions = '{0}\n{1}\n{2}\n{3}\n'.format(abs_vector(0, -R),
                                                  abs_visible_vector(0, 0),
                                                  abs_visible_vector(x_edge, y_edge),
                                                  abs_vector(0, 0)
                                                  )
    # loop_actions consist of actions for filling a sector
    loop_actions = []

    # k is step of filling process
    k = 1

    # There are two variants depending on angle between lines' F value: for acute and obtuse angles
    if F >= 90:
        # This is an algorithm to fill a space between circle's center and right edge of sector
        while crossed_point_r(angle, k, F, delta)[0] <= x_edge:
            # First, find a point of intersection of filling line and circle
            x1, x2 = where_line_crosses_circle(R, angle, k, F, delta)
            if x1 > x2:
                x2_ = x2
                x2 = x1
                x1 = x2_
            if func(0, angle, k, F, delta) < -R:
                x = x1
                # Note a point on circle
                loop_actions.append(abs_vector(x, -sqrt(R ** 2 - x ** 2)))
                # Note a point on sector's line
                loop_actions.append(abs_visible_vector(*crossed_point_r(angle, k, F, delta)))
                k += 1
                continue
            # If there is not a line that connects circle and sector's line, It will a line
            # that connects a line x = 0 and sector's line:
            loop_actions.append(abs_vector(0, func(0, angle, k, F, delta)))
            loop_actions.append(abs_visible_vector(*crossed_point_r(angle, k, F, delta)))
            k += 1

        # There is an algorithm to connect two points on the circle, if they exist considering actual conditions
        while k * delta <= R:
            print('f')
            x1, x2 = where_line_crosses_circle(R, angle, k, F, delta)
            if x1 > x2 or k > 0:
                x2_ = x2
                x2 = x1
                x1 = x2_
            if 0 < x1 < x2 < x_edge:
                loop_actions.append(abs_vector(x1, -sqrt(R ** 2 - x1 ** 2)))
                loop_actions.append(abs_visible_vector(x2, -sqrt(R ** 2 - x2 ** 2)))
                k += 1
    else:
        # It's an algorithm for acute angle.
        while b_coef(angle, k, F, delta) >= -R:
            x, y = crossed_point_r(angle, k, F, delta)
            if x <= x_edge:
                loop_actions.append(abs_vector(0, b_coef(angle, k, F, delta)))
                loop_actions.append(abs_visible_vector(x, y))
            x1, x2 = where_line_crosses_circle(R, angle, k, F, delta)
            if x1 > 0:
                x = x1
            elif x2 > 0:
                x = x2
            if x1 > 0 and x2 > 0:
                x = min((x1, x2))
                print(x)
            if x <= x_edge:
                loop_actions.append(abs_vector(x, -sqrt(R ** 2 - x ** 2)))
                loop_actions.append(abs_visible_vector(0, b_coef(angle, k, F, delta)))
            k += 1
    return first_actions + ''.join(loop_actions)

def main(angle, R, F, delta, file_name='minimarker_script.lsc'):
    with open(file_name, 'w') as file:
        file.write(to_decart())
        file.write(circle(R))
        file.write(sector(angle, R, F, delta))

main(10, 25, 130, 5)



