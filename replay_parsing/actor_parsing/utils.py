_DEFAULT_COORDS_DICT = {'x': None,
                        'y': None,
                        'z': None}

_DEFAULT_RB_STATE = {'angular_velocity': _DEFAULT_COORDS_DICT,
                     'linear_velocity': _DEFAULT_COORDS_DICT,
                     'location': _DEFAULT_COORDS_DICT,
                     'rotation': {'w': None, 'x': None, 'y': None, 'z': None},
                     'is_sleeping': False}

_DEFAULT_RB_STATE_SPLIT = {'angular_velocity_x': None, 'angular_velocity_y': None, 'angular_velocity_z': None,
                           'linear_velocity_x': None, 'linear_velocity_y': None, 'linear_velocity_z': None,
                           'location_x': None, 'location_y': None, 'location_z': None,
                           'rotation_w': None, 'rotation_x': None, 'rotation_y': None, 'rotation_z': None,
                           'is_sleeping': False}


def split_physical_properties_by_axes(data: dict):
    """
    car_data has the initial structure equal to:
        {'angular_velocity': {'x': 0, 'y': 0, 'z': 0},
         'linear_velocity': {...},
         'rotation': {...},
         'location': {...},
         'sleeping': True/False}

    This method returns a new dictionary with the structure:
        {'angular_velocity_x': 0, '..._y': 0, '..._z': 0,
         'linear_velocity_x': 0, '..._y': 0, '..._z': 0,
         'rotation_x': 0, '..._y': 0, '..._z': 0
         'location_x': 0, '..._y': 0, '..._z': 0}

    NOTE: The rotation data is comprised of quaternions.
    """
    new_data = {}

    if 'sleeping' in data.keys():
        # Don't see the point in this attribute, yet.
        new_data['is_sleeping'] = data['sleeping']
        del data['sleeping']

    for property_name, axes_values in data.items():
        if axes_values is not None:
            for axis, value in axes_values.items():
                new_data[property_name + "_" + str(axis)] = round(value, 3)
        else:
            new_data[property_name + "_x"] = None
            new_data[property_name + "_y"] = None
            new_data[property_name + "_z"] = None

    return new_data


def handle_default(value: dict):
    """
    This should ONLY be used for attribute values in the format {'Type': 0}.
    E.g. {'Byte': 0}, {'Int': 0}, {'Boolean': True}
    """
    return list(value.values())[0] if value is not None else None


def handle_coords_dict(value: dict):
    """
    This should ONLY be used for attribute values in the format {'Name': {'x': 0, 'y': 0, 'z': 0}}
    """
    return list(value.values())[0] if value is not None else _DEFAULT_COORDS_DICT


def extract_player_id(player_ids: dict):
    """
    Create a unique player ID that combines their platform and their online ID into one integer.

    :param player_ids: A dictionary with the structure {'local_id': xxx, 'remote_id': xxx, 'system_id': xxx}.
    :return: A new unique id consisting of PLATFORM_ID directly followed by PLAYER_ID.

    E.g. A steam player with a steam ID 54321 would have a unique ID 154321, because the steam PLATFORM_ID is 1.
    """
    player_ids = player_ids.get('UniqueId', None)
    if player_ids is not None:
        player_platform_id = player_ids['system_id']

        player_id = list(player_ids['remote_id'].values())[0]
        if isinstance(player_id, dict):
            player_id = player_id['online_id']

        return str(player_platform_id) + str(player_id)
    else:
        return str(-1)


def handle_rb_state(rb_state: dict):
    if rb_state is not None:
        new_rb_state = rb_state.get('RigidBody', None)
        if new_rb_state is not None and 'sleeping' in new_rb_state:
            new_rb_state['is_sleeping'] = new_rb_state['sleeping']
            del new_rb_state['sleeping']
    else:
        new_rb_state = _DEFAULT_RB_STATE

    return new_rb_state


def handle_rb_state_split(rb_state: dict):
    new_rb_state = rb_state.get('RigidBody', None) if rb_state is not None else None
    return split_physical_properties_by_axes(new_rb_state) if new_rb_state is not None else _DEFAULT_RB_STATE_SPLIT


def handle_player_info(player_info: dict):
    player_info = player_info.get('ActiveActor', None) if player_info is not None else None
    return player_info.get('actor', -1) if player_info is not None and player_info.get('active', False) else -1
