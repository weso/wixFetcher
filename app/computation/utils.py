__author__ = 'Miguel'


def is_same_country(country_name_1, country_name_2):
    if country_name_1.lower() == country_name_2.lower():
        return True
    if "korea" in country_name_1.lower() and "korea" in country_name_2.lower():
        return True
    return False


def is_same_component(component_name_1, component_name_2):
    if component_name_1.lower() == component_name_2.lower():
        return True
    if "communications" in component_name_1.lower() and "communications" in component_name_2.lower():
        return True
    if "access" in component_name_1.lower() and "access" in component_name_2.lower():
        return True
    if "education" in component_name_1.lower() and "education" in component_name_2.lower():
        return True
    if "free" in component_name_1.lower() and "free" in component_name_2.lower():
        return True
    if "content" in component_name_1.lower() and "content" in component_name_2.lower():
        return True
    if "economic" in component_name_1.lower() and "economic" in component_name_2.lower():
        return True
    if "political" in component_name_1.lower() and "political" in component_name_2.lower():
        return True
    if "social" in component_name_1.lower() and "social" in component_name_2.lower():
        return True
    return False


def is_same_subindex(subindex_name_1, subindex_name_2):
    if subindex_name_1.lower() == subindex_name_2.lower():
        return True
    if "relevant" in subindex_name_1.lower() and "relevant" in subindex_name_2.lower():
        return True
    return False
