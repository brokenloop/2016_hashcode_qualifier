import math

class Drone:

    def __init__(self, location, max_load):
        self.location = location
        self.max_load = int(max_load)
        self.load = 0
        self.inventory = []
        self.current_order = None
        self.remaining_distance = 0
        self.available = True
        self.has_final = False

    def take_order(self, warehouse, order, distance, world):
        """
        Takes the order that the drone has been given.
        """

        self.current_order = order
        self.remaining_distance = distance
        self.available = False

        #calculates which items it can take, adds them to the inventory, then marks them as "in transit"
        for item in self.current_order.items:
            weight = int(world.product_weights[int(item)])
            if (self.load + weight < self.max_load) and (warehouse.inventory[int(item)] > 0):
                self.inventory.append(item)
                self.load += weight
                self.current_order.items_in_transit.append(item)
                self.current_order.items.remove(item)
                world.requested_items[int(item)] -= 1

        #removes items in the order from the warehouse's inventory
        warehouse.update_inv(self.inventory)


        #checks whether order has been fulfilled by this drone, removes order from open orders if it has.
        if self.current_order.items == []:
            self.current_order.fulfilled = True
            world.open_orders.remove(self.current_order)
            self.has_final = True


    def deliver(self, world):
        """
        Delivers the order. Resets the drone's variables, and marks the drone as available.
        """

        #marks items as delivered, removes them from items_in_transit
        for item in self.inventory:
            self.current_order.items_delivered.append(item)
            self.current_order.items_in_transit.remove(item)

        #if drone was carrying the final delivery for the order, mark the order as closed. Also record the time that this order took.
        if self.has_final == True:
            world.closed_orders.append(self.current_order)
            world.delivery_times.append(world.turn)

        #reset object variables, move the drone to the location of the order, and mark it as available.
        self.location = self.current_order.location
        self.inventory = []
        self.load = 0
        self.current_order = None
        self.available = True
        self.has_final = False


class Warehouse:

    def __init__(self, location, inventory):
        self.location = location
        self.inventory = inventory
        self.int_inv()


    def int_inv(self):
        """
        Changes inventory from str to int - hacky solution to an annoying bug.
        """
        for i in range(len(self.inventory)):
            self.inventory[i] = int(self.inventory[i])

    def update_inv(self, items):
        """
        Removes items from inventory. To be used when a drone accepts an order.
        """
        for item in items:
            self.inventory[int(item)] -= 1

class Order:
    def __init__(self, location, num_items, items):
        self.location = location
        self.num_items = num_items
        self.items = items
        self.items_in_transit = []
        self.items_delivered = []
        self.fulfilled = False


class World:

    def __init__(self, rows, columns, deadline, num_products, product_weights, drones, warehouses, orders):
        self.rows = int(rows)
        self.columns = int(columns)
        self.deadline = int(deadline)
        self.turn = 0
        self.num_products = int(num_products)
        self.product_weights = product_weights
        self.drones = drones
        self.warehouses = warehouses
        self.open_orders = orders
        self.closed_orders = []
        self.requested_items = [] #use this to store the items that are being requested. This is used to calculate which warehouses are useful/can fulfil open_orders
        self.useful_warehouses = [] #use this to store which warehouses can fulfil open_orders
        self.delivery_times = []
        self.generate_requests()
        self.find_useful_wh()


    def generate_requests(self):
        """
        generates a list of items requested by orders.
        """

        #initialise a list with a "0" for every entry.
        for i in range(int(self.num_products)):
            self.requested_items.append(0)

        #Update this list to reflect how many of each item is needed by all of the orders.
        for i in range(len(self.open_orders)):
            for j in range(len(self.open_orders[i].items)):
                index = int(self.open_orders[i].items[j])
                self.requested_items[index] += 1


    def find_useful_wh(self):
        """
        Finds the warehouses that can fulfil open_orders.
        """

        self.useful_warehouses = []

        #searches self.requested_items for items that the warehouse has.
        for warehouse in self.warehouses:
            for i in range(len(self.requested_items)):
                if (warehouse.inventory[i] > 0) and (self.requested_items[i] > 0):
                    self.useful_warehouses.append(warehouse)
                    break


    def find_orders_from_wh(self, warehouse):
        """
        Finds list of orders that can be satisfied by a specific warehouse
        """
        wh_orders = []

        for order in self.open_orders:
            for item in order.items:
                if warehouse.inventory[int(item)] > 0:
                    wh_orders.append(order)
        return wh_orders


    def find_closest(self, object, candidates):
        """
        finds the closest neighbour to "object" from a list of candidate objects "candidates".
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

        return closest, shortest_distance


    def move_drones(self):
        """
        Moves the drones. To be called every turn from the main method.
        """
        for drone in self.drones:
            if not drone.available:
                if drone.remaining_distance > 0:
                    drone.remaining_distance -= 1
                else:
                    drone.deliver(self)


    def calculate_score(self):
        """
        Calculates score based on the list of delivery times entered.
        """
        scores = []
        for time in self.delivery_times:
            score = math.ceil(((self.deadline - time)/self.deadline) * 100)
            scores.append(score)

        return sum(scores)


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

        world = World(rows, columns, deadline, num_products, product_weights, drones, warehouses, orders)
        return world


def main(file):
    """
    Main method for the program.
    """

    world = initialise(file)

    while (world.turn < world.deadline) and (len(world.open_orders) > 0):

        print("Turn", world.turn)
        print("Orders left:", len(world.open_orders))
        print("Warehouses left:", len(world.useful_warehouses))
        print()

        # this section checks whether a drone is available, and that there are still orders to be filled
        # then it recalculates the list of useful warehouses
        # after that, it finds the closest warehouse to the drone's current location
        # it then calculates which orders can be fulfilled by that warehouse, and which order is closest
        # then it assigns that order to the drone, and the drone marks itself as unavailable until the order has been completed
        for drone in world.drones:
            if drone.available and (len(world.open_orders) > 0):
                world.find_useful_wh()
                closest_wh, distance1 = world.find_closest(drone, world.useful_warehouses)
                wh_orders = world.find_orders_from_wh(closest_wh)
                closest_order, distance2 = world.find_closest(closest_wh, wh_orders)
                tot_distance = math.ceil(distance1 + distance2) + 2 # +2 because it takes one turn each to load the drone and deliver the items
                drone.take_order(closest_wh, closest_order, tot_distance, world)
                print("Drone", world.drones.index(drone), "delivering items", drone.inventory, "to", drone.current_order.location)
                print("Distance to delivery:", drone.remaining_distance)

        world.move_drones()
        world.turn += 1
        print()

    print("Finished!")
    print("Score for this dataset:", world.calculate_score())
    print()
    return(world.calculate_score())


if __name__=="__main__":

    main("busy_day.txt")



