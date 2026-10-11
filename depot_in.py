"""Fit-out of the depot buildings: office, inspection shed, roundhouse stalls, assembly hall (benches, machines, lights)."""
from common import *
import lib
import props
import rooms as R
from rooms import A, lamp_point
from props import G, face_plane
import depot


def office_in():
    g = G("office_in", "Depot")
    x, y = -47.0, -35.5
    x0, x1, y0, y1 = x, x + 9.0, y, y + 5.5
    t = 0.22
    zf = 0.12
    # floor + ceiling
    A(g, "floor", 0.004).box(x0 + t, x1 - t, y0 + t, y1 - t, 0.04, zf)
    R.ceiling(g, x0 + t, x1 - t, y0 + t, y1 - t, 2.78, 'y', step=1.1)
    A(g, "plaster_in").box(x0 + t, x1 - t, y0 + t, y0 + t + 0.01, zf, 2.78) if False else None
    # glazing in the long walls (windows at x+1.2+2.2*i .. +1.2, z 1.0..2.2)
    for i in range(4):
        xa, xb = x + 1.2 + 2.2 * i, x + 2.4 + 2.2 * i
        for (yy, out) in ((y0 + t / 2, -1), (y1 - t / 2, 1)):
            A(g, "glass").box(xa + 0.04, xb - 0.04, yy - 0.004, yy + 0.004, 1.04, 2.16)
            fr = A(g, "wood_dark", 0.004)
            fr.box(xa, xb, yy - 0.04, yy + 0.04, 0.97, 1.04)
            fr.box(xa, xb, yy - 0.04, yy + 0.04, 2.16, 2.23)
            fr.box(xa, xa + 0.05, yy - 0.04, yy + 0.04, 1.0, 2.2)
            fr.box(xb - 0.05, xb, yy - 0.04, yy + 0.04, 1.0, 2.2)
            fr.box((xa + xb) / 2 - 0.02, (xa + xb) / 2 + 0.02, yy - 0.03, yy + 0.03, 1.04, 2.16)
            fr.box(xa, xb, yy - 0.03, yy + 0.03, 1.6, 1.64)
            fr.box(xa - 0.04, xb + 0.04, yy - 0.12 if out < 0 else yy - 0.02, yy + 0.02 if out < 0 else yy + 0.12, 0.93, 0.98)
    # door leaf (east end door opening y+2.2..3.3), half open
    A(g, "wood_dark", 0.005).box(x1 - t, x1 - t + 0.05, y0 + 2.75, y0 + 3.3, 0.04, 2.0)
    # desks: south row (chair south of desk) and north row
    for k, xx in enumerate((-45.2, -42.6, -40.0)):
        R.desk(g, xx, y0 + 1.5, zf, w=1.3, d=0.7, face='S')
    for k, xx in enumerate((-45.2, -42.0)):
        R.desk(g, xx, y1 - 1.5, zf, w=1.3, d=0.7, face='N')
    # lockers (west wall) + filing cabinets (east of the stove)
    for k in range(5):
        A(g, "cabinet_g", 0.01).box(x0 + t, x0 + t + 0.5, y0 + 2.5 + k * 0.5 - 0.01, y0 + 2.5 + k * 0.5 + 0.47, zf, zf + 1.75)
        A(g, "iron_black").box(x0 + t + 0.5, x0 + t + 0.52, y0 + 2.5 + k * 0.5 + 0.2, y0 + 2.5 + k * 0.5 + 0.25, zf + 1.0, zf + 1.1)
    for k in range(3):
        A(g, "cabinet_g", 0.01).box(x1 - t - 0.5, x1 - t, y0 + 0.4 + k * 0.5, y0 + 0.4 + k * 0.5 + 0.47, zf, zf + 1.3)
    R.shelf(g, x0 + 5.0, x0 + 7.4, y1 - t, zf, h=1.9, rows=4, face='S', goods="books", seed=31, key="wood_dark")
    # stove + kettle + tea table (the chimney stands at x+7.2.., y+4.0..)
    R.pot_stove(g, x0 + 7.4, y0 + 4.4, zf, pipe_to=4.6)
    A(g, "tin").cyl((x0 + 7.4, y0 + 4.4, zf + 0.8), (x0 + 7.4, y0 + 4.4, zf + 0.96), 0.1, 0.07, seg=10)
    R.low_table(g, x0 + 5.6, y0 + 2.7, zf, 0.9, 0.6)
    # wall clock, roster board, notices
    face_plane("office_clock", "clock.png", 'S', x0 + 2.2, y1 - t - 0.01, 2.0, 0.45, h=0.45)
    face_plane("office_roster", "timetable_old.png", 'E', x0 + t + 0.01, y0 + 1.2, 1.2, 0.55) if False else None
    face_plane("office_notice", "notice.png", 'S', x0 + 4.4, y1 - t - 0.01, 1.2, 0.9)
    face_plane("office_poster", "poster_safety.png", 'N', x0 + 3.0, y0 + t + 0.01, 1.2, 0.5)
    face_plane("office_map", "poster_map.png", 'N', x0 + 5.4, y0 + t + 0.01, 1.2, 0.9)
    # blackboard (operations board) on the west wall
    A(g, "wood_dark", 0.01).box(x0 + t, x0 + t + 0.04, y0 + 0.4, y0 + 2.0, 1.1, 2.0)
    A(g, "soot").box(x0 + t + 0.04, x0 + t + 0.05, y0 + 0.45, y0 + 1.95, 1.15, 1.95)
    face_plane("office_sign", "depot_sign.png", 'S', x0 + 4.5, y0 - 0.02, 2.3, 3.2)
    face_plane("office_fire", "fire_sign.png", 'S', x0 + 8.0, y0 - 0.02, 1.3, 0.5)
    lamp_point(x0 + 2.5, (y0 + y1) / 2, 2.55, 30)
    lamp_point(x0 + 6.0, (y0 + y1) / 2, 2.55, 25)
    g.build()


def inspection_shed_in():
    g = G("shed_in", "Depot")
    x0, x1, y0, y1 = -64.0, -34.0, -60.0, -46.5
    t = 0.22
    # glazing for the clerestory windows on the long walls
    for i in range(6):
        xa = -62 + 3.0 + 5.0 * i
        xb = xa + 1.4
        for yy in (y0 + t / 2, y1 - t / 2):
            A(g, "glass").box(xa + 0.04, xb - 0.04, yy - 0.004, yy + 0.004, 2.24, 3.36)
            fr = A(g, "wood_dark", 0.004)
            fr.box(xa, xb, yy - 0.04, yy + 0.04, 2.17, 2.24)
            fr.box(xa, xb, yy - 0.04, yy + 0.04, 3.36, 3.43)
            fr.box(xa, xa + 0.05, yy - 0.04, yy + 0.04, 2.2, 3.4)
            fr.box(xb - 0.05, xb, yy - 0.04, yy + 0.04, 2.2, 3.4)
            fr.box((xa + xb) / 2 - 0.02, (xa + xb) / 2 + 0.02, yy - 0.03, yy + 0.03, 2.24, 3.36)
    # pits between the rails of both roads (shallow trench rims + dark floor)
    for yc in (-51.0, -55.5):
        A(g, "concrete", 0.01).box(x0 + 3.0, x1 - 3.0, yc - 0.52, yc - 0.34, 0.05, 0.14) if False else None
        A(g, "concrete", 0.01).box(-62.0, -36.0, yc - 0.40, yc - 0.34, 0.0, 0.16)
        A(g, "concrete", 0.01).box(-62.0, -36.0, yc + 0.34, yc + 0.40, 0.0, 0.16)
    # work benches + vises along the north wall, tool cabinets, drums
    for k in range(5):
        xb = -62.0 + 4.5 + k * 5.5
        R.counter(g, xb, xb + 2.4, y1 - 0.9, 0.05, d=0.7, h=0.95, key="desk")
        A(g, "iron_black", 0.01).box(xb + 0.3, xb + 0.5, y1 - 1.0, y1 - 0.8, 1.0, 1.15)         # vise
        A(g, "cabinet_g", 0.01).box(xb + 1.5, xb + 2.2, y1 - 1.2, y1 - 0.6, 1.0, 1.2)           # parts bin
        R.shelf(g, xb, xb + 2.4, y1 - 0.25, 0.05, h=2.0, rows=4, face='S', goods="cans", seed=40 + k, key="wood_dark")
    for k in range(6):
        props.drums(g, -63.0 + 0.7 * (k % 3), y0 + 0.6 + (k // 3) * 0.7, n=1)
    # a lathe + a drill press (west end)
    A(g, "cabinet_g", 0.01).box(-62.4, -59.4, y0 + 0.8, y0 + 1.5, 0.05, 1.0)
    A(g, "iron_black", 0.01).box(-62.4, -61.2, y0 + 0.75, y0 + 1.55, 1.0, 1.35)
    A(g, "iron_black").cyl((-60.0, y0 + 1.15, 1.0), (-59.8, y0 + 1.15, 1.2), 0.18, seg=12)
    A(g, "cabinet_g", 0.01).box(-58.4, -57.8, y0 + 0.8, y0 + 1.4, 0.05, 0.4)
    A(g, "iron_black").cyl((-58.1, y0 + 1.1, 0.4), (-58.1, y0 + 1.1, 1.7), 0.05, seg=8)
    A(g, "cabinet_g", 0.01).box(-58.4, -57.8, y0 + 0.85, y0 + 1.35, 1.7, 2.0)
    # monorail hoist along each road
    for yc in (-51.0, -55.5):
        A(g, "iron", 0.01).box(-62.5, -36.0, yc - 0.1, yc + 0.1, 4.3, 4.45) if False else A(g, "iron_black", 0.01).box(-62.5, -36.0, yc - 0.1, yc + 0.1, 4.3, 4.45)
        A(g, "iron_black", 0.01).box(-48.0, -47.0, yc - 0.25, yc + 0.25, 3.8, 4.3)
        A(g, "iron_black").cyl((-47.5, yc, 3.8), (-47.5, yc, 2.6), 0.02, seg=5)
        A(g, "iron_black").box(-47.65, -47.35, yc - 0.15, yc + 0.15, 2.3, 2.6)
    for xx in np.arange(-60.0, -36.0, 6.0):
        for yc in (-48.4, -53.2, -57.9):
            lamp_point(xx, yc, 4.3, 22)
            A(g, "tin").cyl((xx, yc, 4.55), (xx, yc, 4.1), 0.05, 0.3, seg=12)
            A(g, "lamp_glow").sphere((xx, yc, 4.1), (0.12, 0.12, 0.06), seg=8, rings=4)
    g.build()


def roundhouse_in():
    g = G("roundhouse_in", "Depot")
    for ang in depot.STALLS:
        px, py = depot.pol(depot.ROUT - 5.0, ang)
        lamp_point(px, py, 3.5, 35)
        A(g, "lamp_glow").sphere((px, py, 3.4), (0.12, 0.12, 0.07), seg=8, rings=4)
        # inspection pit rims, tool trolleys, drums at the back wall
        qx, qy = depot.pol(depot.ROUT - 1.6, ang + 4.2)
        A(g, "cabinet_g", 0.01).box(qx - 0.4, qx + 0.4, qy - 0.3, qy + 0.3, 0.05, 0.9)
        qx, qy = depot.pol(depot.ROUT - 1.6, ang - 4.2)
        A(g, "tr_red").cyl((qx, qy, 0.05), (qx, qy, 0.9), 0.29, seg=12)
    g.build()


def hall_in():
    g = G("hall_in", "Depot")
    x0, x1, y0, y1 = 21.0, 35.0, -99.0, -74.5
    t = 0.28
    # window panes in the long walls (openings at y=-96+5.2i .. +1.6, z 3.3..4.7)
    for i in range(4):
        ya, yb = -96.0 + 5.2 * i, -96.0 + 5.2 * i + 1.6
        for xx in (x0 + t / 2, x1 - t / 2):
            A(g, "glass").box(xx - 0.004, xx + 0.004, ya + 0.04, yb - 0.04, 3.34, 4.66)
            fr = A(g, "wood_dark", 0.004)
            fr.box(xx - 0.04, xx + 0.04, ya, yb, 3.27, 3.34)
            fr.box(xx - 0.04, xx + 0.04, ya, yb, 4.66, 4.73)
            fr.box(xx - 0.04, xx + 0.04, ya, ya + 0.05, 3.3, 4.7)
            fr.box(xx - 0.04, xx + 0.04, yb - 0.05, yb, 3.3, 4.7)
            fr.box(xx - 0.03, xx + 0.03, (ya + yb) / 2 - 0.02, (ya + yb) / 2 + 0.02, 3.34, 4.66)
    # benches, gas cylinders, cable reels, tool chests along the south wall and east/west walls
    for k in range(4):
        xb = x0 + 1.3 + k * 3.2
        R.counter(g, xb, xb + 2.4, y0 + 1.0, 0.05, d=0.8, h=0.95, key="desk")
        A(g, "iron_black", 0.01).box(xb + 0.4, xb + 0.6, y0 + 0.9, y0 + 1.1, 1.0, 1.15)
        A(g, "cabinet_g", 0.01).box(xb + 1.5, xb + 2.3, y0 + 0.7, y0 + 1.3, 1.0, 1.35)
    for k in range(4):
        A(g, "tr_red").cyl((x1 - 0.8 - k * 0.3, y0 + 2.0, 0.05), (x1 - 0.8 - k * 0.3, y0 + 2.0, 1.4), 0.1, seg=10)
        A(g, "tr_grey").cyl((x1 - 0.8 - k * 0.3, y0 + 2.0, 1.4), (x1 - 0.8 - k * 0.3, y0 + 2.0, 1.5), 0.05, seg=8)
    for k in range(3):
        A(g, "wood", 0.02).cyl((x0 + 0.7, y0 + 3.0 + k * 0.9, 0.05), (x0 + 0.7, y0 + 3.0 + k * 0.9, 0.2), 0.45, seg=14)
        A(g, "wood", 0.02).cyl((x0 + 0.7, y0 + 3.0 + k * 0.9, 0.2), (x0 + 0.7, y0 + 3.0 + k * 0.9, 0.9), 0.1, seg=10)
    R.shelf(g, x0 + 0.4, x0 + 3.0, y0 + 0.35, 0.05, h=2.2, rows=5, face='N', goods="boxes", seed=51, key="wood_dark")
    A(g, "cabinet_g", 0.02).box(x1 - 2.5, x1 - 0.5, y1 - 1.8, y1 - 0.6, 0.05, 2.2)                  # electrical switch cabinet
    A(g, "iron_black").box(x1 - 2.4, x1 - 0.6, y1 - 1.82, y1 - 1.8, 1.2, 1.6)
    for xx in (x0 + 3.5, x0 + 7.0, x0 + 10.5):
        for yy in (-79.0, -87.0, -95.0):
            lamp_point(xx, yy, 6.4, 45)
            A(g, "tin").cyl((xx, yy, 6.7), (xx, yy, 6.15), 0.06, 0.45, seg=14)
            A(g, "lamp_glow").sphere((xx, yy, 6.15), (0.18, 0.18, 0.08), seg=8, rings=4)
    face_plane("hall_board", "timetable_old.png", 'N', 28.0, y0 + t + 0.01, 3.2, 0.9) if False else None
    face_plane("hall_notice", "ad_safety.png", 'N', 24.5, y0 + t + 0.01, 3.4, 1.4)
    g.build()


def build_depot_interiors():
    office_in()
    inspection_shed_in()
    roundhouse_in()
    hall_in()
