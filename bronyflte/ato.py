import numpy as np
import colorcet as cc
import matplotlib.pyplot as plt
from datetime import timedelta
import dcs
import pathlib
import pprint


def sort_flight(element):
    """
    this function takes an schedule array element and return the first non-zero waypoint time, if the waypoint array
    is empty it's that the flight runs the duration of the mission.

    :param element:

    :return: first waypoint time or 0
    """

    waypoints = element['waypoints']

    if waypoints:
        return waypoints[0]
    else:
        return 0


def get_schedule(flights):
    """
    this function will parse a flight array from a mission file and generate

    :param flights:
    :return:
    """

    schedule = []

    for flight in flights:
        name = flight['name'].split('|')
        waypoints = [x['ETA'] for i, x in flight['route']['points'].items() if x['ETA'] > 0]

        data = {
            'name': f'{name[0]} ',
            'task': flight['task'],
            'type': flight['units'][1]['type'],
            'waypoints': waypoints
        }

        schedule.append(data)

    return schedule


def get_groups(mission, side='blue', category='plane'):

    countries = mission.dict()['coalition'][side]['country']

    items = []
    for i, country in countries.items():

        cat = country.get(category)

        if cat:
            items += [x for j, x in cat['group'].items()]

    return items


def generate_ato(mission, side='blue'):
    """
    take a dcs mission and generate an ato

    :param side: str blue or red
    :param mission:
    :return:
    """

    flights = get_groups(mission, side, 'plane')
    flights += get_groups(mission, side, 'helicopter')

    schedule = get_schedule(flights)
    schedule.sort(key=sort_flight, reverse=True)

    fig, ax = plt.subplots(figsize=(10, 4))

    names = [x['name'].upper() for x in schedule]
    tasks = {x['task'] for x in schedule}

    task_codes = {x: y for x, y in zip(tasks, cc.glasbey_cool[:len(tasks)])}

    for i, flight in enumerate(schedule):

        task = flight['task']

        if flight.get('waypoints'):
            ax.barh(y=i, left=flight['waypoints'][0], width=flight['waypoints'][-1], color=task_codes[task], label=task)

        else:
            ax.barh(y=i, width=10800, color=task_codes[task], label=task)

    # ylabels
    ax.set_yticks(np.arange(len(names)))
    ax.set_yticklabels(names)
    ax.set_ylabel('Flight')

    # xlabels
    time = np.linspace(0, 10800, 13)
    time_labels = [(mission.start_time + timedelta(seconds=x)).strftime('%H:%M') for x in time]
    ax.set_xticks(time)
    ax.set_xticklabels(time_labels, rotation=90)
    ax.set_xlabel('Mission Time')

    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys())

    fig.savefig('ato.png', dpi=600, bbox_inches='tight', facecolor='w')
    plt.show()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='ATO Generator')
    parser.add_argument('file')
    args = parser.parse_args()

    print(pathlib.Path.cwd(), flush=True)

    mission = dcs.Mission()
    mission.load_file(args.file)

    generate_ato(mission)
