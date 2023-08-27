from .log_interface import rise_warning


def set_attributes(my_object, attributes_dict):
    for key, value in attributes_dict.items():
        if key in my_object.__dict__:
            setattr(my_object, key, value)
        else:
            rise_warning(
                "trying to set a non existing attribute "
                + str(key)
                + " in "
                + str(type(my_object))
            )
    return 0
