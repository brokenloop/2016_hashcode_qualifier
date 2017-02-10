from main import *


map = initialise("busy_day.txt")

print("Running first dataset...\n")
score1 = main("mother_of_all_warehouses.txt")

print("Running second dataset...\n")
score2 = main("busy_day.txt")

print("Running third dataset...\n")
score3 = main("redundancy.txt")

print("Final score:", score1 + score2 + score3)