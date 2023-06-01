#Made by James McKenna using Queue-Times API. jmmckenna.co.uk
import requests
import heapq
from datetime import datetime

#This program finds the shortest ride plan for every major roller coaster in
#Alton Towers. It uses Dijkstra's algorithm to visit every location once and
#return the shortest path based on the current wait times of the rides.

ExcludedRides = {'Enterprise', 'Funk’n’Fly', 'Spinjam', 'Twistatron'}
#List of excluded rides as some are either no roller coasters or closed.

def fetchQueueTimes():
    url = (f"https://queue-times.com/parks/1/queue_times.json")
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print("Error fetching queue times:", e)
        return None

    #Fetches the queue times from the API.


def processQueueTimes(queueTimesData):
    lands = queueTimesData["lands"]

    rollerCoasters = set()
    coasterWaitingTimes = {}
    coasterStatus = {}
    graph = {}

    for land in lands:
        if land["name"] == ("Thrills"):
            rides = land["rides"]
            for ride in rides:
                rideName = ride["name"]
                if rideName not in ExcludedRides:
                    rollerCoasters.add(rideName)
                    coasterWaitingTimes[rideName] = ride["wait_time"]
                    coasterStatus[rideName] = ride["is_open"]
                    graph[rideName] = [(adjRide["name"], adjRide["wait_time"]) for adjRide in rides
                                       if adjRide["name"] != rideName and adjRide["name"] in rollerCoasters]

    #Iterates through the lands and their rides, only filters to retrieve "thrills". For each roller coaster
    #ride, it adds it to rollerCoasters and stores its waiting time in coasterWaitingTimes. It then creates
    #a list of rides with their names and waiting times in the graph dictionary.
                    
    startCoaster = next(iter(rollerCoasters))
    route = [startCoaster]
    remainingCoasters = set(rollerCoasters)
    remainingCoasters.remove(startCoaster)

    #Finds the initial state for finding the shortest route. It selects the first roller coaster as the
    #starting coaster and initalises the route list and removes the starting coaster from the
    #remainingCoasters.

    while remainingCoasters:
        nextCoaster = min(remainingCoasters, key=lambda coaster: dijkstra(graph, route[-1], coaster))
        route.append(nextCoaster)
        remainingCoasters.remove(nextCoaster)

    #The loop iteratively finds the next roller coaster with the minimum distance from the current
    #coaster and adds it to the "route" list. It updates the 'remainingCoasters' set by removing the
    #chosen coaster. It repeats this until there are no remaining coasters.

    totalWaitTime = sum(coasterWaitingTimes[coaster] for coaster in route)
    routeWithTimes = sorted(route, key=lambda coaster: coasterWaitingTimes[coaster])

    return route, routeWithTimes, coasterWaitingTimes, coasterStatus, totalWaitTime, rollerCoasters

def dijkstra(graph, start, end):
    distances = {node: float('inf') for node in graph}
    distances[start] = 0

    #The function takes arguments 'graph' (all roller coasters and their connections),
    #'start' (starting coaster), and 'end' (end destination). The function initalises
    #a dictionary called 'distances' where each coaster node is initially assigned a
    #distance of infinity except for the starting coaster, which is assigned 0.

    priorityQueue = [(0, start)]
    while priorityQueue:
        currentDist, currentNode = heapq.heappop(priorityQueue)
        if currentDist == distances[currentNode]:
            for neighbour, weight in graph[currentNode]:
                newDist = currentDist + weight
                if newDist < distances[neighbour]:
                    distances[neighbour] = newDist
                    heapq.heappush(priorityQueue, (newDist, neighbour))

    return distances[end]

    #The algorithm retrives the node with the smallest distance from the priority queue
    #using 'heapq.heappop()' where the current distance and node are assigned to 'currentDist'
    #and 'currentNode' respectively.

    #The algorithm then checks if the current distance is equal to the distance stored in
    #'distances' dictionary for the current node. This ensures that only the shortest paths
    #are considered.


def chooseStartingCoaster(rollerCoasters):
    print("Choose a Starting Coaster:\n")
    coasterList = sorted(list(rollerCoasters))
    for i, coaster in enumerate(coasterList):
        print(f"{i + 1}. {coaster}")

    while True:
        choice = input("\nEnter The Number of The Coaster: ")
        if choice.isdigit():
            index = int(choice) - 1
            if 0 <= index < len(coasterList):
                return coasterList[index]
        print("Invalid choice. Please enter a valid number.")


def printRoute(route, coasterWaitingTimes, coasterStatus, header):
    print(header)
    for i, coaster in enumerate(route):
        waitTime = coasterWaitingTimes[coaster]
        status = coasterStatus[coaster]
        statusText = "Open" if status else "Closed"
        print(f"{i + 1}. {coaster.ljust(16)} - Queue Time: {str(waitTime).ljust(2)} minutes ({statusText})")

    #The loop iterates over the 'route' list, which contains the optimal order of roller coasters.
    #The enumerate function gets both the index and the name in each iteration. It then displays
    #the index and coaster name in a formatted string.


def printTotalWaitTime(totalWaitTime):
    totalWaitHours = totalWaitTime // 60
    totalWaitMinutes = totalWaitTime % 60
    totalWaitFormatted = (f"{totalWaitTime} minutes ({totalWaitHours} hour(s) {totalWaitMinutes} minutes)")
    print(f"\nTotal waiting Time: {totalWaitFormatted}")

    #It formats the total wait time in hours and minutes. The hours are calculated using integer division (//)
    #and the minutes are calculated using modular division (%) by 60, so it returns the respective time in a
    #more readable format. Then the function prints the waiting time.


print("+------------------------------------------+")
print("| Alton Towers Roller Coaster Ride Planner |")
print("+------------------------------------------+\n")

print("Powered by Queue-Times.com (https://queue-times.com)\n")
print("Queue times are updated every 5 minutes and are subject to change\n")
print("Please note that Nemesis is temporarily closed and will reopen in 2024")
print("______________________________________________________________________\n")


while True:
    currentTime = datetime.now().strftime("%A %d %B %Y %I:%M%p")
    print(f"Current Time: {currentTime}\n")

    queueTimesData = fetchQueueTimes()

    route, routeWithTimes, coasterWaitingTimes, coasterStatus, totalWaitTime, rollerCoasters = processQueueTimes(queueTimesData)

    startingCoaster = chooseStartingCoaster(rollerCoasters)
    print(f"\nStarting Coaster: {startingCoaster}")

    route.remove(startingCoaster)
    route.insert(0, startingCoaster)

    print("_____________________________________________________")
    printRoute(route, coasterWaitingTimes, coasterStatus, "\nOptimal Route Based on Dijkstra's Algorithm:\n")
    print("_____________________________________________________\n")
    
    printRoute(routeWithTimes, coasterWaitingTimes, coasterStatus, "Route In Ascending Order of Waiting Times:\n")
    print("_____________________________________________________\n")
    
    printTotalWaitTime(totalWaitTime)

    userInput = input("\nPress any key to refresh or 'q' to quit: \n")
    if userInput.lower() == 'q':
        break
