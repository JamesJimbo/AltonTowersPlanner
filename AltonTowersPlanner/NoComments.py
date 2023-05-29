import requests
import heapq
from datetime import datetime

ExcludedRides = {'Enterprise', 'Funk’n’Fly', 'Spinjam', 'Twistatron', 'Nemesis'}

def fetchQueueTimes():
    url = (f"https://queue-times.com/parks/1/queue_times.json")
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print("Error fetching queue times:", e)
        return None


def processQueueTimes(queueTimesData):
    lands = queueTimesData["lands"]

    rollerCoasters = set()
    coasterWaitingTimes = {}
    graph = {}

    for land in lands:
        if land["name"] == ("Thrills"):
            rides = land["rides"]
            for ride in rides:
                rideName = ride["name"]
                if rideName not in ExcludedRides:
                    rollerCoasters.add(rideName)
                    coasterWaitingTimes[rideName] = ride["wait_time"]
                    graph[rideName] = [(adjRide["name"], adjRide["wait_time"]) for adjRide in rides
                                       if adjRide["name"] != rideName and adjRide["name"] in rollerCoasters]

    startCoaster = next(iter(rollerCoasters))
    route = [startCoaster]
    remainingCoasters = set(rollerCoasters)
    remainingCoasters.remove(startCoaster)

    while remainingCoasters:
        nextCoaster = min(remainingCoasters, key=lambda coaster: dijkstra(graph, route[-1], coaster))
        route.append(nextCoaster)
        remainingCoasters.remove(nextCoaster)

    totalWaitTime = sum(coasterWaitingTimes[coaster] for coaster in route)
    routeWithTimes = sorted(route, key=lambda coaster: coasterWaitingTimes[coaster])

    return route, routeWithTimes, coasterWaitingTimes, totalWaitTime


def dijkstra(graph, start, end):
    distances = {node: float('inf') for node in graph}
    distances[start] = 0

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


def printProgramHeader():
    print("+------------------------------------------+")
    print("| Alton Towers Roller Coaster Ride Planner |")
    print("+------------------------------------------+\n")

def printRoute(route, coasterWaitingTimes, header):
    print(header)
    for i, coaster in enumerate(route):
        waitTime = coasterWaitingTimes[coaster]
        print(f"{i + 1}. {coaster.ljust(16)} - Queue Time: {str(waitTime).ljust(2)} minutes")

while True:
    printProgramHeader()

    currentTime = datetime.now().strftime("%A %d %B %Y %I:%M%p")
    print(f"Current Time: {currentTime}\n")

    queueTimesData = fetchQueueTimes()

    print("Please note that Nemesis is temporarily closed and will reopen in 2024")
    print("____________________________________________\n")

    route, routeWithTimes, coasterWaitingTimes, totalWaitTime = processQueueTimes(queueTimesData)

    printRoute(route, coasterWaitingTimes, "Optimal Route Based on Dijkstra's Algorithm:\n")
    print("____________________________________________\n")
    
    printRoute(routeWithTimes, coasterWaitingTimes, "Route In Ascending Order of Waiting Times:\n")
    print("____________________________________________\n")
    
    print(f"\nTotal Waiting Time: {totalWaitTime} minutes")
    print("\nPowered by Queue-Times.com (https://queue-times.com)")

    userInput = input("\nPress any key to refresh or 'q' to quit: ")
    if userInput.lower() == 'q':
        break
