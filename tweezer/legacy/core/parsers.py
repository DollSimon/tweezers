"""
Different parser utils for detecting file patterns and extracting information from them.
"""
import os
import datetime
from collections import namedtuple

from parsley import makeGrammar, ParseError

from tweezer.legacy.ixo2.os_ import get_parent_directory


def parse_tweezer_file_name(file_name, parser='bot_data'):
    """
    Extracts metadata from a tweezer file name

    :param file_name: (path) of the corresponding tweezer file

    :param parser: (str) that specifies the file type to be parsed

    :return FileInfo: (namedtuple) that carries the trial, subtrial and date of the corresponding tdms file
    """
    name = os.path.basename(file_name)
    file_info = namedtuple('FileInfo', ['trial', 'subtrial', 'date'])

    base_grammar = makeGrammar("""
        # date related patterns
        y = <digit{4}>:year -> int(year)
        mo = <digit{2}>:month -> int(month)
        d = <digit{2}>:day -> int(day)
        h = <digit{2}>:hour -> int(hour)
        mi = <digit{2}>:minute -> int(minute)
        sc = <digit{2}>:second -> int(second)

        # trial and subtrial information
        t = <digit+>:trial -> str(trial)
        sub = <letter{1}>:subtrial -> str(subtrial)

        # separator
        s = '.' | '_' | ' '
    """, {})

    if parser is 'bot_data':
        name_parser = makeGrammar("""
            n = <('D' | 'd') 'a' 't' 'a' 'l' 'o' 'g'>:name -> str(name)
            ext = '.' <'t' 'x' 't'>:ext -> str(ext)
            pattern = (<t '_' sub> | t):name s n s y:y s mo:mo s d:d s h:h s mi:mi s sc:sc s n ext -> (name, y, mo, d, h, mi, sc)
            """, {}, extends = base_grammar)
    elif parser is 'bot_log':
        name_parser = makeGrammar("""
            twb = <('T' | 't') 'w' 'e' 'e' ('b' | 'B') 'o' 't'>:tweebot -> str(tweebot)
            log = <twb ('L' | 'l') 'o' 'g'>:log -> str(log)
            ext = '.' <'t' 'x' 't'>:ext -> str(ext)
            pattern = (<t '_' sub> | t):name s log s y:y s mo:mo s d:d s h:h s mi:mi s sc:sc ext -> (name, y, mo, d, h, mi, sc)
            """, {}, extends = base_grammar)
    elif parser is 'bot_tdms':
        name_parser = makeGrammar("""
            ext = '.' <'t' 'd' 'm' 's'>:ext -> str(ext)
            pattern = (<t '_' sub> | t):name s y:y s mo:mo s d:d s h:h s mi:mi s sc:sc ext -> (name, y, mo, d, h, mi, sc)
            """, {}, extends = base_grammar)
    elif parser is 'bot_andor':
        name_parser = makeGrammar("""
            ms = <digit{2, 3}>:microsecond -> int(microsecond)
            and = <'a' 'n' 'd' 'o' 'r'>:andor -> str(andor)
            ssh = <('S' | 's') 'n' 'a' 'p' 's' 'h' 'o' 't'>
            ext = '.' <'p' 'n' 'g'>:ext -> str(ext)
            pattern = (<t '_' sub> | t):name s ssh s{2} y:y s mo:mo s d:d s h:h s mi:mi s sc:sc s ms:ms s and ext -> (name, y, mo, d, h, mi, sc, ms)
            """, {}, extends = base_grammar)
    elif parser is 'bot_ccd':
        name_parser = makeGrammar("""
            ms = <digit{2, 3}>:microsecond -> int(microsecond)
            ccd = <'c' 'c' 'd'>:ccd -> str(ccd)
            ssh = <('S' | 's') 'n' 'a' 'p' 's' 'h' 'o' 't'>
            ext = '.' <'p' 'n' 'g'>:ext -> str(ext)
            pattern = (<t '_' sub> | t):name s ssh s{2} y:y s mo:mo s d:d s h:h s mi:mi s sc:sc s ms:ms s ccd ext -> (name, y, mo, d, h, mi, sc, ms)
            """, {}, extends = base_grammar)
    elif parser is 'man_data':
        name_parser = makeGrammar("""
            # ending
            txt = <'t' 'x' 't'>:txt -> str(txt)
            gro = <'g' 'r' 'o' 'o' 'v' 'y'>:groovy -> str(groovy)
            wgr = <'w' 'h' 'o' 'l' 'e' '.' gro>
            png = <'p' 'n' 'g'>:png -> str(png)
            jpg = <('j' 'e' 'p' 'g' | 'j' 'p' 'g')>:jpg -> str(jpg)
            avi = <'a' 'v' 'i'>:avi -> str(avi)
            csv = <'c' 's' 'v'>:csv -> str(csv)
            fts = <'f' 'i' 't' 's'>:fts -> str(fts)
            tif = <'t' 'i' ('f' 'f' | 'f')>:tif -> str(tif)
            tdms = <'t' 'd' 'm' 's'>:tdms -> str(tdms)
            tdms_index = <'t' 'd' 'm' 's' '_' 'i' 'n' 'd' 'e' 'x'>:tdms_index -> str(tdms_index)
            end = '.' (txt | gro | png | jpg | wgr | tdms | avi | tif | csv | tdms_index)

            pattern = (<t '_' sub> | t):name end:ext -> (name, ext)
            """, {}, extends = base_grammar)
    elif parser is 'man_pics':
        name_parser = makeGrammar("""
            # ending
            txt = <'t' 'x' 't'>:txt -> str(txt)
            gro = <'g' 'r' 'o' 'o' 'v' 'y'>:groovy -> str(groovy)
            wgr = <'w' 'h' 'o' 'l' 'e' '.' gro>
            png = <'p' 'n' 'g'>:png -> str(png)
            jpg = <('j' 'e' 'p' 'g' | 'j' 'p' 'g')>:jpg -> str(jpg)
            avi = <'a' 'v' 'i'>:avi -> str(avi)
            csv = <'c' 's' 'v'>:csv -> str(csv)
            fts = <'f' 'i' 't' 's'>:fts -> str(fts)
            tif = <'t' 'i' ('f' 'f' | 'f')>:tif -> str(tif)
            tdms = <'t' 'd' 'm' 's'>:tdms -> str(tdms)
            tdms_index = <'t' 'd' 'm' 's' '_' 'i' 'n' 'd' 'e' 'x'>:tdms_index -> str(tdms_index)
            end = '.' (txt | gro | png | jpg | wgr | tdms | avi | tif | csv | tdms_index)

            pattern = (<t '_' sub> | t):name end:ext -> (name, ext)
            """, {}, extends = base_grammar)
    elif parser is 'tc_psd':
        name_parser = makeGrammar("""
            # ending
            txt = <'t' 'x' 't'>:txt -> str(txt)
            gro = <'g' 'r' 'o' 'o' 'v' 'y'>:groovy -> str(groovy)
            wgr = <'w' 'h' 'o' 'l' 'e' '.' gro>
            png = <'p' 'n' 'g'>:png -> str(png)
            jpg = <('j' 'e' 'p' 'g' | 'j' 'p' 'g')>:jpg -> str(jpg)
            avi = <'a' 'v' 'i'>:avi -> str(avi)
            csv = <'c' 's' 'v'>:csv -> str(csv)
            fts = <'f' 'i' 't' 's'>:fts -> str(fts)
            tif = <'t' 'i' ('f' 'f' | 'f')>:tif -> str(tif)
            tdms = <'t' 'd' 'm' 's'>:tdms -> str(tdms)
            tdms_index = <'t' 'd' 'm' 's' '_' 'i' 'n' 'd' 'e' 'x'>:tdms_index -> str(tdms_index)
            end = '.' (txt | gro | png | jpg | wgr | tdms | avi | tif | csv | tdms_index)

            pattern = 'P' 'S' 'D' s <t '_' sub> | t):name end:ext -> (name, ext)
            """, {}, extends = base_grammar)
    elif parser is 'man_track':
        name_parser = makeGrammar("""
            # ending
            txt = <'t' 'x' 't'>:txt -> str(txt)
            gro = <'g' 'r' 'o' 'o' 'v' 'y'>:groovy -> str(groovy)
            wgr = <'w' 'h' 'o' 'l' 'e' '.' gro>
            png = <'p' 'n' 'g'>:png -> str(png)
            jpg = <('j' 'e' 'p' 'g' | 'j' 'p' 'g')>:jpg -> str(jpg)
            avi = <'a' 'v' 'i'>:avi -> str(avi)
            csv = <'c' 's' 'v'>:csv -> str(csv)
            fts = <'f' 'i' 't' 's'>:fts -> str(fts)
            tif = <'t' 'i' ('f' 'f' | 'f')>:tif -> str(tif)
            tdms = <'t' 'd' 'm' 's'>:tdms -> str(tdms)
            tdms_index = <'t' 'd' 'm' 's' '_' 'i' 'n' 'd' 'e' 'x'>:tdms_index -> str(tdms_index)
            end = '.' (txt | gro | png | jpg | wgr | tdms | avi | tif | csv | tdms_index)

            pattern = <t '_' sub> | t):name end:ext -> (name, ext)
            """, {}, extends = base_grammar)
    try:
        infos = name_parser(name).pattern()
        if '_' in infos[0]:
            trial, subtrial = infos[0].split('_')
        else:
            trial, subtrial = infos[0], None

        try:
            date = datetime.datetime(*infos[1:8])
        except TypeError:
            date = None

        result = file_info(trial, subtrial, date)

    except ParseError:
        result = file_info(None, None, None)

    return result


def parse_tweebot_tdms_file_name(file_name):
    """
    Extract metadata from file name

    :param file_name: (path) name of a tweebot tdms file

    :return FileInfo: (namedtuple) that carries the trial, subtrial and date of the corresponding tdms file
    """
    data_parser = makeGrammar("""
        y = <digit{4}>:year -> int(year)
        mo = <digit{2}>:month -> int(month)
        d = <digit{2}>:day -> int(day)
        h = <digit{2}>:hour -> int(hour)
        mi = <digit{2}>:minute -> int(minute)
        sc = <digit{2}>:second -> int(second)
        t = <digit+>:trial -> str(trial)
        sub = <letter{1}>:subtrial -> str(subtrial)
        ext = '.' <'t' 'd' 'm' 's'>:ext -> str(ext)
        s = '.' | '_' | ' '
        pattern = (<t '_' sub> | t):name s y:y s mo:mo s d:d s h:h s mi:mi s sc:sc ext -> (name, y, mo, d, h, mi, sc)
    """, {})

    file_info = namedtuple('FileInfo', ['trial', 'subtrial', 'date'])

    try:
        infos = data_parser(file_name).pattern()
        if '_' in infos[0]:
            trial, subtrial = infos[0].split('_')
        else:
            trial, subtrial = infos[0], None

        date = datetime.datetime(*infos[1:7])
        result = file_info(trial, subtrial, date)

    except ParseError:
        result = file_info(None, None, None)

    return result


def parse_tweebot_datalog_file_name(file_name):
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
        t = <digit+>:trial -> str(trial)
        sub = <letter{1}>:subtrial -> str(subtrial)
        ext = '.' <'t' 'x' 't'>:ext -> str(ext)
        n = <('D' | 'd') 'a' 't' 'a' 'l' 'o' 'g'>:n -> str(n)
        s = '.' | '_' | ' '
        pattern = (<t '_' sub> | t):name s n s y:y s mo:mo s d:d s h:h s mi:mi s sc:sc s n ext -> (name, y, mo, d, h, mi, sc)
    """, {})

    file_info = namedtuple('FileInfo', ['trial', 'subtrial', 'date'])

    try:
        infos = data_parser(file_name).pattern()
        if '_' in infos[0]:
            trial, subtrial = infos[0].split('_')
        else:
            trial, subtrial = infos[0], None

        date = datetime.datetime(*infos[1:7])
        result = file_info(trial, subtrial, date)

    except ParseError:
        result = file_info(None, None, None)

    return result


def parse_tweebot_log_file_name(file_name):
    """
    Extract metadata from file name

    :param file_name: (path) name of a tweebot log file of type "18.TweeBotLog.2013.02.19.22.43.07.txt"

    :return FileInfo: (namedtuple) that carries the trial, subtrial and date of the corresponding log file
    """
    data_parser = makeGrammar("""
        y = <digit{4}>:year -> int(year)
        mo = <digit{2}>:month -> int(month)
        d = <digit{2}>:day -> int(day)
        h = <digit{2}>:hour -> int(hour)
        mi = <digit{2}>:minute -> int(minute)
        sc = <digit{2}>:second -> int(second)
        t = <digit+>:trial -> str(trial)
        sub = <letter{1}>:subtrial -> str(subtrial)
        twb = <('T' | 't') 'w' 'e' 'e' ('b' | 'B') 'o' 't'>:tweebot -> str(tweebot)
        log = <twb ('L' | 'l') 'o' 'g'>:log -> str(log)
        ext = '.' <'t' 'x' 't'>:ext -> str(ext)
        s = '.' | '_' | ' '
        pattern = (<t '_' sub> | t):name s log s y:y s mo:mo s d:d s h:h s mi:mi s sc:sc ext -> (name, y, mo, d, h, mi, sc)
    """, {})

    file_info = namedtuple('FileInfo', ['trial', 'subtrial', 'date'])

    try:
        infos = data_parser(file_name).pattern()
        if '_' in infos[0]:
            trial, subtrial = infos[0].split('_')
        else:
            trial, subtrial = infos[0], None

        date = datetime.datetime(*infos[1:7])
        result = file_info(trial, subtrial, date)

    except ParseError:
        result = file_info(None, None, None)

    return result


def classify(file_path):
    """
    Infers the file type of a tweezer data file from its name.

    :param String file_path: File path, including name of course, to be tested

    :return file_type: (String) classifier of the file
    """
    base_name = os.path.basename(file_path)

    try:
        parent_dir = get_parent_directory(file_path)
    except IndexError:
        parent_dir = ''

    file_name = '/'.join([parent_dir, base_name])

    type_grammar = makeGrammar("""
        # separator
        s = '.' | '_' | ' '
        ps = '/'
        path = <(letterOrDigit | '_' | ' ' | '.')*>:path -> str(path)
        andor_path = <(letterOrDigit | '_' | ' ' )*>:andor_path -> str(andor_path)

        # beginning
        t = <digit+>:trial -> int(trial)

        # ending
        txt = <'t' 'x' 't'>:txt -> str(txt)
        gro = <'g' 'r' 'o' 'o' 'v' 'y'>:groovy -> str(groovy)
        wgr = <'w' 'h' 'o' 'l' 'e' '.' gro>
        png = <'p' 'n' 'g'>:png -> str(png)
        jpg = <('j' 'e' 'p' 'g' | 'j' 'p' 'g')>:jpg -> str(jpg)
        avi = <'a' 'v' 'i'>:avi -> str(avi)
        csv = <'c' 's' 'v'>:csv -> str(csv)
        fts = <'f' 'i' 't' 's'>:fts -> str(fts)
        tif = <'t' 'i' ('f' 'f' | 'f')>:tif -> str(tif)
        tdms = <'t' 'd' 'm' 's'>:tdms -> str(tdms)
        tdms_index = <'t' 'd' 'm' 's' '_' 'i' 'n' 'd' 'e' 'x'>:tdms_index -> str(tdms_index)
        end = '.' (txt | gro | png | jpg | wgr | tdms | avi | tif | csv | tdms_index)

        # date and time
        y = <digit{4}>:year -> int(year)
        mo = <digit{2}>:month -> int(month)
        d = <digit{2}>:day -> int(day)
        h = <digit{2}>:hour -> int(hour)
        mi = <digit{2}>:minute -> int(minute)
        sc = <digit{2}>:second -> int(second)
        ms = <digit{2, 3}>:microsecond -> int(microsecond)
        date = y:y s mo:mo s d:d s h:h s mi:mi s sc:sc -> (y, mo, d, h, mi, sc)

        # names
        twb = <('T' | 't') 'w' 'e' 'e' ('b' | 'B') 'o' 't'>:tweebot -> str(tweebot)
        dat = <('D' | 'd') 'a' 't' 'a' 'l' 'o' 'g'>:data -> str(data)
        log = <twb ('L' | 'l') 'o' 'g'>:log -> str(log)
        sts = <twb ('S' | 's') 't' 'a' 't' 's'>:stats -> str(stats)
        foc = <('F' | 'f') 'o' 'c' 'u' 's'>:focus -> str(focus)
        sta = <('S' | 's') 't' 'a' 'g' 'e'>:stage -> str(stage)
        fst = <foc 's' 'i' 'n' 'g' sta>
        fuf = <'f' 'u' 'l' 'l' foc>
        ref = <'r' 'e' foc>
        ftb = <foc 't' 'a' 'b' 'l' 'e'>
        sct = <('S' | 's') 'a' 'v' 'e' 'd' twb ('S' | 's') 'c' 'r' 'i' 'p' 't'>
        ccd = <'c' 'c' 'd'>:ccd -> str(ccd)
        and = <'a' 'n' 'd' 'o' 'r'>:andor -> str(andor)
        ssh = <('S' | 's') 'n' 'a' 'p' 's' 'h' 'o' 't'>
        cal = <'c' 'a' 'l' 'i' 'b' 'r' 'a' 't' 'i' 'o' 'n'>
        vid = <'v' 'i' 'd' 'e' ('o' 's' | 'o')>
        tpx = <('a' 'o' 'd' | 'p' 'm') '2' 'p' 'i' 'x'>
        clb = <'c' 'a' 'l' 'i' 'b'>
        tmp = <'t' 'e' 'm' 'p' 'l' 'a' 't' ('e' 's' | 'e')>
        flw = <'f' 'l' 'o' 'w' 'c' 'e' 'l' 'l'>
        pcs = <'p' 'i' 'c' 't' 'u' 'r' ('e' 's' | 's')>
        trc = <'t' 'r' 'a' 'c' 'k' 'i' 'n' 'g'>

        # bot file patterns
        bot_data = <path ps t s dat s date s dat end> -> 'BOT_DATA'
        bot_log = <path ps t s log s date end> -> 'BOT_LOG'
        bot_stats = <path ps t s sts end> -> 'BOT_STATS'
        bot_focus = <path ps fst s (fuf | ref) t s ftb end> -> 'BOT_FOCUS'
        bot_script = <path ps t s sct s date end> -> 'BOT_SCRIPT'
        bot_ccd = <path ps t s ssh s{2} date s ms s ccd end> -> 'BOT_CCD'
        bot_andor = <path ps t s ssh s{2} date s ms s and end> -> 'BOT_ANDOR'
        bot_tdms = <path ps t s date '.' tdms> -> 'BOT_TDMS'
        bot_tdms_index = <path ps t s date '.' tdms_index> -> 'BOT_TDMS_INDEX'

        # manual file patterns
        man_data = <'d' 'a' 't' 'a' ps (t '_' <letter+> | t) end> -> 'MAN_DATA'

        man_pm_dc_v = <path ps ('P' 'M' | 'p' 'm') s cal s vid end> -> 'MAN_PM_DIST_CAL_VID'
        man_pm_dc_r = <path ps ('P' 'M' | 'p' 'm') s cal s clb s tpx end> -> 'MAN_PM_DIST_CAL_RES'
        man_pm_dc_m = <path ps ('P' 'M' | 'p' 'm') s cal s <'p' 'm' '2' 'p'> end> -> 'MAN_PM_DIST_CAL_MAT'

        man_aod_dc_v = <path ps ('A' 'O' 'D' | 'a' 'o' 'd') s cal s vid end> -> 'MAN_AOD_DIST_CAL_VID'
        man_aod_dc_r = <path ps ('A' 'O' 'D' | 'a' 'o' 'd') s cal s clb s tpx end> -> 'MAN_AOD_DIST_CAL_RES'
        man_aod_dc_m = <path ps ('A' 'O' 'D' | 'a' 'o' 'd') s cal s <'a' 'o' 'd' '2' 'p'> end> -> 'MAN_AOD_DIST_CAL_MAT'

        man_dc_tmp = <path ps cal s tmp s <'d' 'b'> s <'t' 'b'> end> -> 'MAN_DIST_CAL_TMP'
        man_vid = <vid ps (t '_' <letter+> | t) '.' avi> -> 'MAN_VID'
        man_flow = <flw ps (t '_' <letter+> | t) '.' csv > -> 'MAN_FLOW'
        man_pics = <pcs ps (t '_' <letter+> | t) '.' jpg > -> 'MAN_PICS'
        man_track = <trc ps (t '_' <letter+> | t) '.' csv > -> 'MAN_TRACK'
        man_tmp = <tmp ps (t '_' <letter+> | t) '.' tif > -> 'MAN_TMP'

        # general file patterns
        tc_ts = <path ps 'T' 'S' s (t '_' <letter+> | t) '.' 'txt'> -> 'TC_TS'
        tc_psd = <path ps 'P' 'S' 'D' s (t '_' <letter+> | t) '.' 'txt'> -> 'TC_PSD'
        andor_vid = <andor_path ps andor_path <'.' fts>> -> 'ANDOR_VID'

        type = (man_data |
            man_pm_dc_v |
            man_pm_dc_r |
            man_pm_dc_m |
            man_aod_dc_v |
            man_aod_dc_r |
            man_aod_dc_m |
            man_dc_tmp |
            man_vid |
            man_flow |
            man_pics |
            man_track |
            man_tmp |
            tc_ts |
            tc_psd |
            andor_vid |
            bot_data |
            bot_log |
            bot_stats |
            bot_focus |
            bot_script |
            bot_ccd |
            bot_tdms |
            bot_tdms_index |
            bot_andor ):type -> str(type)

        pattern = type:type -> str(type)
    """, {})

    try:
        file_type = type_grammar(file_name).pattern()
    except ParseError:
        file_type = 'UNKNOWN'

    return file_type


def classify_all(files):
    """
    Infers the file type of a tweezer data file from its name.

    :param String file_path: File path, including name of course, to be tested

    :return file_type: (String) classifier of the file
    """
    type_grammar = makeGrammar("""
        # separator
        s = '.' | '_' | ' '
        ps = '/'
        path = <(letterOrDigit | '_' | ' ' | '.')*>:path -> str(path)
        andor_path = <(letterOrDigit | '_' | ' ' )*>:andor_path -> str(andor_path)

        # beginning
        t = <digit+>:trial -> int(trial)

        # ending
        txt = <'t' 'x' 't'>:txt -> str(txt)
        gro = <'g' 'r' 'o' 'o' 'v' 'y'>:groovy -> str(groovy)
        wgr = <'w' 'h' 'o' 'l' 'e' '.' gro>
        png = <'p' 'n' 'g'>:png -> str(png)
        jpg = <('j' 'e' 'p' 'g' | 'j' 'p' 'g')>:jpg -> str(jpg)
        avi = <'a' 'v' 'i'>:avi -> str(avi)
        csv = <'c' 's' 'v'>:csv -> str(csv)
        fts = <'f' 'i' 't' 's'>:fts -> str(fts)
        tif = <'t' 'i' ('f' 'f' | 'f')>:tif -> str(tif)
        tdms = <'t' 'd' 'm' 's'>:tdms -> str(tdms)
        tdms_index = <'t' 'd' 'm' 's' '_' 'i' 'n' 'd' 'e' 'x'>:tdms_index -> str(tdms_index)
        end = '.' (txt | gro | png | jpg | wgr | tdms | avi | tif | csv | tdms_index)

        # date and time
        y = <digit{4}>:year -> int(year)
        mo = <digit{2}>:month -> int(month)
        d = <digit{2}>:day -> int(day)
        h = <digit{2}>:hour -> int(hour)
        mi = <digit{2}>:minute -> int(minute)
        sc = <digit{2}>:second -> int(second)
        ms = <digit{2, 3}>:microsecond -> int(microsecond)
        date = y:y s mo:mo s d:d s h:h s mi:mi s sc:sc -> (y, mo, d, h, mi, sc)

        # names
        twb = <('T' | 't') 'w' 'e' 'e' ('b' | 'B') 'o' 't'>:tweebot -> str(tweebot)
        dat = <('D' | 'd') 'a' 't' 'a' 'l' 'o' 'g'>:data -> str(data)
        log = <twb ('L' | 'l') 'o' 'g'>:log -> str(log)
        sts = <twb ('S' | 's') 't' 'a' 't' 's'>:stats -> str(stats)
        foc = <('F' | 'f') 'o' 'c' 'u' 's'>:focus -> str(focus)
        sta = <('S' | 's') 't' 'a' 'g' 'e'>:stage -> str(stage)
        fst = <foc 's' 'i' 'n' 'g' sta>
        fuf = <'f' 'u' 'l' 'l' foc>
        ref = <'r' 'e' foc>
        ftb = <foc 't' 'a' 'b' 'l' 'e'>
        sct = <('S' | 's') 'a' 'v' 'e' 'd' twb ('S' | 's') 'c' 'r' 'i' 'p' 't'>
        ccd = <'c' 'c' 'd'>:ccd -> str(ccd)
        and = <'a' 'n' 'd' 'o' 'r'>:andor -> str(andor)
        ssh = <('S' | 's') 'n' 'a' 'p' 's' 'h' 'o' 't'>
        cal = <'c' 'a' 'l' 'i' 'b' 'r' 'a' 't' 'i' 'o' 'n'>
        vid = <'v' 'i' 'd' 'e' ('o' 's' | 'o')>
        tpx = <('a' 'o' 'd' | 'p' 'm') '2' 'p' 'i' 'x'>
        clb = <'c' 'a' 'l' 'i' 'b'>
        tmp = <'t' 'e' 'm' 'p' 'l' 'a' 't' ('e' 's' | 'e')>
        flw = <'f' 'l' 'o' 'w' 'c' 'e' 'l' 'l'>
        pcs = <'p' 'i' 'c' 't' 'u' 'r' ('e' 's' | 's')>
        trc = <'t' 'r' 'a' 'c' 'k' 'i' 'n' 'g'>

        # bot file patterns
        bot_data = <path ps t s dat s date s dat end> -> 'BOT_DATA'
        bot_log = <path ps t s log s date end> -> 'BOT_LOG'
        bot_stats = <path ps t s sts end> -> 'BOT_STATS'
        bot_focus = <path ps fst s (fuf | ref) t s ftb end> -> 'BOT_FOCUS'
        bot_script = <path ps t s sct s date end> -> 'BOT_SCRIPT'
        bot_ccd = <path ps t s ssh s{2} date s ms s ccd end> -> 'BOT_CCD'
        bot_andor = <path ps t s ssh s{2} date s ms s and end> -> 'BOT_ANDOR'
        bot_tdms = <path ps t s date '.' tdms> -> 'BOT_TDMS'
        bot_tdms_index = <path ps t s date '.' tdms_index> -> 'BOT_TDMS_INDEX'

        # manual file patterns
        man_data = <'d' 'a' 't' 'a' ps (t '_' <letter+> | t) end> -> 'MAN_DATA'

        man_pm_dc_v = <path ps ('P' 'M' | 'p' 'm') s cal s vid end> -> 'MAN_PM_DIST_CAL_VID'
        man_pm_dc_r = <path ps ('P' 'M' | 'p' 'm') s cal s clb s tpx end> -> 'MAN_PM_DIST_CAL_RES'
        man_pm_dc_m = <path ps ('P' 'M' | 'p' 'm') s cal s <'p' 'm' '2' 'p'> end> -> 'MAN_PM_DIST_CAL_MAT'

        man_aod_dc_v = <path ps ('A' 'O' 'D' | 'a' 'o' 'd') s cal s vid end> -> 'MAN_AOD_DIST_CAL_VID'
        man_aod_dc_r = <path ps ('A' 'O' 'D' | 'a' 'o' 'd') s cal s clb s tpx end> -> 'MAN_AOD_DIST_CAL_RES'
        man_aod_dc_m = <path ps ('A' 'O' 'D' | 'a' 'o' 'd') s cal s <'a' 'o' 'd' '2' 'p'> end> -> 'MAN_AOD_DIST_CAL_MAT'

        man_dc_tmp = <path ps cal s tmp s <'d' 'b'> s <'t' 'b'> end> -> 'MAN_DIST_CAL_TMP'
        man_vid = <vid ps (t '_' <letter+> | t) '.' avi> -> 'MAN_VID'
        man_flow = <flw ps (t '_' <letter+> | t) '.' csv > -> 'MAN_FLOW'
        man_pics = <pcs ps (t '_' <letter+> | t) '.' jpg > -> 'MAN_PICS'
        man_track = <trc ps (t '_' <letter+> | t) '.' csv > -> 'MAN_TRACK'
        man_tmp = <tmp ps (t '_' <letter+> | t) '.' tif > -> 'MAN_TMP'

        # general file patterns
        tc_ts = <path ps 'T' 'S' s (t '_' <letter+> | t) '.' 'txt'> -> 'TC_TS'
        tc_psd = <path ps 'P' 'S' 'D' s (t '_' <letter+> | t) '.' 'txt'> -> 'TC_PSD'
        andor_vid = <andor_path ps andor_path <'.' fts>> -> 'ANDOR_VID'

        type = (man_data |
            man_pm_dc_v |
            man_pm_dc_r |
            man_pm_dc_m |
            man_aod_dc_v |
            man_aod_dc_r |
            man_aod_dc_m |
            man_dc_tmp |
            man_vid |
            man_flow |
            man_pics |
            man_track |
            man_tmp |
            tc_ts |
            tc_psd |
            andor_vid |
            bot_data |
            bot_log |
            bot_stats |
            bot_focus |
            bot_script |
            bot_ccd |
            bot_tdms |
            bot_tdms_index |
            bot_andor ):type -> str(type)

        pattern = type:type -> str(type)
    """, {})

    file_types = list()
    for f in files:
        base_name = os.path.basename(f)

        try:
            parent_dir = get_parent_directory(f)
        except IndexError:
            parent_dir = ''

        file_name = '/'.join([parent_dir, base_name])

        try:
            file_type = type_grammar(file_name).pattern()
            file_types.append(file_type)
        except ParseError:
            file_type = 'UNKNOWN'
            file_types.append(file_type)

    return file_types


def main():
    files = ['path/39.Datalog.2013.02.20.04.14.20.datalog.txt',
        '39.Datalog.2013.02.20.04.14.20.datalog.txt',
        'path/56.TweeBotLog.2013.02.20.08.55.15.txt',
        'path/1.SavedTweeBotScript.2013.02.19.17.04.25.whole.groovy',
        'path/18.SavedTweeBotScript.2013.02.19.17.04.25.whole.groovy',
        '/Users/jahnel/code/example_data/tweebot/snapshots.andor/20.Snapshot..2013.02.19.23.32.30.254.andor.png',
        'path/TS_4_d.txt', 'path/TS_5.txt', 'path/TS_10.txt', 'data/18_2013_05_19_17_18_07.tdms']

    for f in files:
        print(classify(f))


if __name__ == '__main__':
    main()
