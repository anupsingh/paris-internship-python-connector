
def type_prioriy(type=None):
    return [type, int, float, str]

def auto_type(value, type=None):
    types = type_prioriy(type)
    for t in types:
        try:
            if t is not None:
                t(value)
                return t
        except:
            pass
    return types[-1]

def auto_type_list(values, type=None):
    types = type_prioriy(type)
    return types[max([types.index(auto_type(value, type)) for value in values])]
    
