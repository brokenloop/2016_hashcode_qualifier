import math


class Drone:

    def __init__(self, location, max_load):
        self.location = location
        self.max_load = int(max_load)
        self.load = 0
        self.inventory = []
        self.current_order = None
        self.available = True

    def take_order(self, order, map):
        """
        Takes the order that the drone has been given.
        """

        self.current_order = order
        self.available = False

        #calculates which items it can take, adds them to the inventory, then marks them as "in transit"
        for item in self.current_order.items:
            weight = int(map.product_weights[int(item)])
            if self.load + weight < self.max_load:
                self.inventory.append(item)
                self.load += weight

                self.current_order.items_in_transit.append(item)
                self.current_order.items.remove(item)

        #removes these items from the "requested_items"
        for item in self.inventory:
            map.requested_items[int(item)] -= 1

        #checks whether order has been fulfilled by this drone, removes order from open orders if it has.
        if self.current_order.items == []:
            self.current_order.fulfilled = True
            map.open_orders.remove(self.current_order)
            map.closed_orders.append(self.current_order)


    def deliver(self):
        """
        Delivers the order. --Needs testing!! Added before turn counter, so has not been tested.
        """

        for item in self.inventory:
            self.current_order.items_delivered.append(item)
            self.current_order.items_in_transit.remove(item)

        self.location = self.current_order.location

        self.inventory = []
        self.load = 0
        self.current_order = None
        self.available = True



class Warehouse:

    def __init__(self, location, inventory):
        self.location = location
        self.inventory = inventory


class Order:
    
    def __init__(self, location, num_items, items):
        self.location = location
        self.num_items = num_items
        self.items = items
        self.items_in_transit = []
        self.items_delivered = []
        self.fulfilled = False


class Map:

    def __init__(self, rows, columns, deadline, num_products, product_weights, drones, warehouses, orders):
        self.rows = int(rows)
        self.columns = int(columns)
        self.deadline = int(deadline)
        self.num_products = int(num_products)
        self.product_weights = product_weights
        self.drones = drones
        self.warehouses = warehouses
        self.open_orders = orders
        self.closed_orders = []
        self.requested_items = [] #use this to store the items that are being requested. This is used to calculate which warehouses are useful/can fulfil open_orders
        self.useful_warehouses = [] #use this to store which warehouses can fulfil open_orders


    def generate_requests(self):
        """
        generates the list of requested items
        """
        for i in range(int(self.num_products)):
            self.requested_items.append(0)

        for i in range(len(self.open_orders)):
            for j in range(len(self.open_orders[i].items)):
                index = int(self.open_orders[i].items[j])
                self.requested_items[index] += 1


    def find_useful_wh(self):
        """
        Finds the warehouses that can fulfil open_orders.
        One Q: How should we update this list when open_orders are filled?
        """

        for i in range(len(self.warehouses)):
            for j in range(len(self.warehouses[i].inventory)):
                if (int(self.warehouses[i].inventory[j]) > 0) and (self.requested_items[j] > 0):
                    self.useful_warehouses.append(self.warehouses[i])
                    break



    def find_closest(self, object, candidates):
        """
        finds the closest neighbour to "object" from a list of candidate objects (candidates).
        """
        x1 = int(object.location[0])
        y1 = int(object.location[1])
        x2 = int(candidates[0].location[0])
        y2 = int(candidates[0].location[1])

        shortest_distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        closest = candidates[0]

        for i in range(1, len(candidates)):
            x2 = int(candidates[i].location[0])
            y2 = int(candidates[i].location[1])

            distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

            if distance < shortest_distance:
                shortest_distance = distance
                closest = candidates[i]

        return closest



def initialise(file):
    """
    Reads data from "file", generates objects based on that data
    """
    with open(file) as file:
        input_data = file.readlines()

        for i in range(len(input_data)):
            input_data[i] = input_data[i].replace("\n", "")  # getting rid of newlines

        parameters = input_data[0].split(" ")  # first line of the input_data

        rows = parameters[0]
        columns = parameters[1]
        num_drones = parameters[2]
        deadline = parameters[3]
        max_load = parameters[4]

        num_products = input_data[1]
        product_weights = input_data[2].split(" ")

        # get warehouse info
        num_warehouses = input_data[3]
        wh_coords = []
        wh_products = []

        for i in range(int(num_warehouses) * 2):
            if i % 2 == 0:
                wh_coords.append(input_data[i + 4].split(" "))

            elif i % 2 == 1:
                wh_products.append(input_data[i + 4].split(" "))

        # get order info
        placemarker = int(num_warehouses) * 2 + 4  # storing this index to make it easier to tell where warehouse list ends

        num_orders = input_data[placemarker]  # don't even ask...
        delivery_coords = []
        num_contents = []
        order_contents = []

        placemarker += 1

        for i in range(int(num_orders) * 3):
            if i % 3 == 0:
                delivery_coords.append(input_data[i + placemarker].split(" "))

            elif i % 3 == 1:
                num_contents.append(input_data[i + placemarker].split(" "))

            elif i % 3 == 2:
                order_contents.append(input_data[i + placemarker].split(" "))


        #create objects
        drones = []
        warehouses = []
        orders = []

        for i in range(int(num_drones)):
            drones.append(Drone(wh_coords[0], max_load))

        for i in range(int(num_warehouses)):
            warehouses.append(Warehouse(wh_coords[i], wh_products[i]))

        for i in range(int(num_orders)):
            orders.append(Order(delivery_coords[i], num_contents, order_contents[i]))

        map = Map(rows, columns, deadline, num_products, product_weights, drones, warehouses, orders)

        return map

    #return(rows, columns, num_drones, deadline, max_load, num_products, product_weights, num_warehouses, wh_coords,
    #       wh_products, num_orders, delivery_coords, num_contents, order_contents)



def main(file):
    """
    Main method for the program.
    """

    map = initialise(file)

    map.generate_requests()
    map.find_useful_wh()

    turn = 0
    while (turn < map.deadline) and (len(map.open_orders) > 0):
        print("Orders left:", len(map.open_orders))
        print()

        for drone in map.drones:
            if drone.available and (len(map.open_orders) > 0):
                closest_wh = map.find_closest(drone, map.useful_warehouses)
                closest_order = map.find_closest(closest_wh, map.open_orders)
                drone.take_order(closest_order, map)
                print("Drone", map.drones.index(drone), "delivering items", drone.inventory, "to", drone.current_order.location)
                print()
                drone.deliver()

        turn += 1

    print("Finished!")

main("input.txt")






