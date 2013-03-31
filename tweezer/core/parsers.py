"""
Different parser utils for detecting file patterns and extracting information from them. 
"""
from parsley import makeGrammar, ParseError

def parse_tweebot_datalog_pattern(file_name):
    """
    Extracts useful information from a given file name. 
    
    :param String file_name: File name or path to be tested
    
    :return match: (Boolean) True if the file_name pattern was found

    :return infos: (dict) Additional information stored in the file name

    """
    
    data_parser = makeGrammar("""
        y = <digit{4}>:year -> int(year)
        mo = <digit{2}>:month -> int(month)
        d = <digit{2}>:day -> int(day)
        h = <digit{2}>:hour -> int(hour)
        mi = <digit{2}>:minute -> int(minute)
        sc = <digit{2}>:second -> int(second)
        t = <digit+>:trial -> int(trial)
        ext = '.' <'t' 'x' 't'>:ext -> str(ext)
        n = <('D' | 'd') 'a' 't' 'a' 'l' 'o' 'g'>:name -> str(name)
        s = '.' | '_' | ' '
        pattern = t:t s n:n s y:y s mo:mo s d:d s h:h s mi:mi s sc:sc s n ext:ext -> (t, n, y, mo, d, h, mi, sc, ext)
    """, {})

    try:
        infos = data_parser(file_name).pattern()
        match = True
    except ParseError, err:
        match = False

    return match, infos 
