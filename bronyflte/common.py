"""common utility functions"""


def get_groups(mission, side='blue', category='plane'):
    """
    this function retrieves all of the groups from a side in the pydcs object
    by category.


    Parameters
    ----------
    mission: pydcs.Mission
    side: str
        {'blue', 'red'}
    category:
        {'plane', 'helicopter', 'ship'}

    Returns
    -------
    items: list
        list containing dictionaries of all groups contained in a category and side
        in a pydcs mission.
    """
    countries = mission.dict()['coalition'][side]['country']

    items = []
    for i, country in countries.items():

        cat = country.get(category)

        if cat:
            items += [x for j, x in cat['group'].items()]

    return items
