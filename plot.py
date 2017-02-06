from main import *

def getData(file):

    map = initialise(file)
    map.generate_requests()
    map.find_useful_wh()

    drone_x = []
    drone_y = []

    order_x = []
    order_y = []

    # for order in map.open_orders:
    #     print(order.location)

    while (map.turn < map.deadline) and (len(map.open_orders) > 0):

        current_x = []
        current_y = []

        current_order_x = []
        current_order_y = []

        for order in map.visual_orders:
            current_order_x.append(int(order[0]))
            current_order_y.append(int(order[1]))

        for drone in map.drones:

            current_x.append(int(drone.location[0]))
            current_y.append(int(drone.location[1]))


            if drone.available and (len(map.open_orders) > 0):
                closest_wh, distance1 = map.find_closest(drone, map.useful_warehouses)
                closest_order, distance2 = map.find_closest(closest_wh, map.open_orders)
                tot_distance = math.ceil(distance1 + distance2) + 2  # +2 because it takes one turn each to load the drone and deliver the items
                drone.take_order(closest_order, closest_wh, distance1, distance2, map)


        drone_x.append(current_x)
        drone_y.append(current_y)

        order_x.append(current_order_x)
        order_y.append(current_order_y)

        map.move_drones()
        map.turn += 1



    wh_x = []
    wh_y = []

    for warehouse in map.useful_warehouses:
        wh_x.append(int(warehouse.location[0]))
        wh_y.append(int(warehouse.location[1]))



    return (drone_x, drone_y, wh_x, wh_y, order_x, order_y, map.deadline, map.rows, map.columns)


drone_x, drone_y, wh_x, wh_y, order_x, order_y, deadline, rows, columns = getData("redundancy.txt")

print(order_x, order_y)

# print(getData("busy_day.txt"))
import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots()

plt.plot(wh_x, wh_y, marker="s", linestyle="None")
#plt.plot(order_x[:-1], order_y[:-1], marker="o", linestyle="None")
#print(order_x)
for t in range(deadline):
    if t == 0:
        drone_points, = ax.plot(drone_x[0], drone_y[0], marker='o', linestyle='None')
        points, = ax.plot(order_x[0], order_y[0], marker='o', linestyle='None')
        ax.set_xlim(0, rows)
        ax.set_ylim(0, columns)
    else:
        new_x = drone_x[t]
        new_y = drone_y[t]
        new_order_x = order_x[t]
        new_order_y = order_y[t]
        drone_points.set_data(new_x, new_y)
        points.set_data(new_order_x, new_order_y)
    plt.pause(0.0000000000000000001)