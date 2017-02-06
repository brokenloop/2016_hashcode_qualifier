import math


class Drone:
    def __init__(self, location, max_load):
        self.location = location
        self.destination = None
        self.max_load = int(max_load)
        self.load = 0
        self.inventory = []
        self.current_warehouse = None
        self.warehouse_distance = None
        self.current_order = None
        self.order_distance = None
        self.destination_distance = None
        self.remaining_distance = None
        self.available = True
        self.has_final = False

    def take_order(self, order, warehouse, distance1, distance2, map):
        """
        Takes the order that the drone has been given.
        """

        self.current_order = order
        self.warehouse_distance = distance1
        self.order_distance = distance2
        self.available = False
        self.current_warehouse = warehouse
        self.destination = warehouse.location
        self.destination_distance = self.warehouse_distance
        self.remaining_distance = distance1 + distance2

        # calculates which items it can take, adds them to the inventory, then marks them as "in transit"
        for item in self.current_order.items:
            weight = int(map.product_weights[int(item)])
            if self.load + weight < self.max_load:
                self.inventory.append(item)
                self.load += weight

                self.current_order.items_in_transit.append(item)
                self.current_order.items.remove(item)

        # removes these items from the "requested_items"
        for item in self.inventory:
            map.requested_items[int(item)] -= 1

        # checks whether order has been fulfilled by this drone, removes order from open orders if it has.
        if self.current_order.items == []:
            self.current_order.fulfilled = True
            map.open_orders.remove(self.current_order)
            map.closed_orders.append(self.current_order)
            self.has_final = True

    def deliver(self, map):
        """
        Delivers the order.
        """

        for item in self.inventory:
            self.current_order.items_delivered.append(item)
            self.current_order.items_in_transit.remove(item)

        if self.has_final == True:
            map.delivery_times.append(map.turn)
            map.visual_orders.remove(self.current_order.location)

        self.inventory = []
        self.load = 0
        self.current_order = None
        self.available = True
        self.has_final = False


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
        self.turn = 0
        self.num_products = int(num_products)
        self.product_weights = product_weights
        self.drones = drones
        self.warehouses = warehouses
        self.open_orders = orders
        self.closed_orders = []
        self.requested_items = []  # use this to store the items that are being requested. This is used to calculate which warehouses are useful/can fulfil open_orders
        self.useful_warehouses = []  # use this to store which warehouses can fulfil open_orders
        self.delivery_times = []
        self.visual_orders = []
        self.generate_visual_orders()

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

    def generate_visual_orders(self):
        for order in self.open_orders:
            self.visual_orders.append(order.location)

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

            distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

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

                    if drone.destination_distance <= 0:

                        drone.destination = drone.current_order.location
                        drone.destination_distance = drone.order_distance
                        drone.remaining_distance = drone.order_distance

                    x1 = float(drone.location[0])
                    y1 = float(drone.location[1])
                    x2 = float(drone.destination[0])
                    y2 = float(drone.destination[1])
                    n = drone.destination_distance

                    new_x = (((n - 1) / n) * x1) + (1 / n) * x2
                    new_y = (((n - 1) / n) * y1) + (1 / n) * y2

                    drone.location = (new_x, new_y)
                    drone.remaining_distance -= 1
                    drone.destination_distance -= 1


                else:
                    drone.deliver(self)

    def calculate_score(self):
        """
        Calculates score based on the list of delivery times entered.
        """
        scores = []
        for time in self.delivery_times:
            score = math.ceil(((self.deadline - time) / self.deadline) * 100)
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
        placemarker = int(
            num_warehouses) * 2 + 4  # storing this index to make it easier to tell where warehouse list ends

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

        # create objects
        drones = []
        warehouses = []
        orders = []

        for i in range(int(num_drones)):
            drones.append(Drone(wh_coords[0], max_load))

        for i in range(int(num_warehouses)):
            warehouses.append(Warehouse(wh_coords[i], wh_products[i]))

        for i in range(int(num_orders)):
            orders.append(Order(delivery_coords[i], num_contents[i], order_contents[i]))

        map = Map(rows, columns, deadline, num_products, product_weights, drones, warehouses, orders)
        return map


def main(file):
    """
    Main method for the program.
    """

    map = initialise(file)
    map.generate_requests()
    map.find_useful_wh()


    while (map.turn < map.deadline) and (len(map.open_orders) > 0):
        print("Turn", map.turn)
        print("Orders left:", len(map.open_orders))
        print()

        print(map.visual_orders)

        for drone in map.drones:
            if drone.available and (len(map.open_orders) > 0):
                closest_wh, distance1 = map.find_closest(drone, map.useful_warehouses)
                closest_order, distance2 = map.find_closest(closest_wh, map.open_orders)
                tot_distance = math.ceil(
                    distance1 + distance2) + 2  # +2 because it takes one turn each to load the drone and deliver the items
                drone.take_order(closest_order, closest_wh, distance1, distance2, map)
                print("Drone", map.drones.index(drone), "delivering items", drone.inventory, "to",
                      drone.current_order.location)
                print("Distance to delivery:", drone.remaining_distance)

        map.move_drones()
        map.turn += 1
        print()

    print("Finished!")
    print("Score for this dataset:", map.calculate_score())
    print()
    return (map.calculate_score())


if __name__ == "__main__":
    main("busy_day.txt")




