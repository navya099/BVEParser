import re
import os
import random
from typing import List

from loggermodule import logger
from .Structures.Expression import Expression
from OpenBveApi.Math.Math import NumberFormats
from .Structures.PositionedExpression import PositionedExpression
from OpenBveApi.System.TextEncoding import TextEncoding


class Parser1:
    def __init__(self):
        super().__init__()  # 💡 중요!
    def preprocess_split_into_expressions(self, file_name, lines, allow_rw_route_description,
                                          track_position_offset=0.0):
        expressions = []  # 기본 생성자를 사용할 경우
        e = 0
        # full-line rw comments
        if self.IsRW:
            for i in range(len(lines)):
                level = 0
                for j in range(len(lines[i])):
                    match lines[i][j]:
                        case '(':
                            level += 1

                        case ')':
                            level -= 1

                        case ';':
                            if level == 0:
                                lines[i] = lines[i][:j].rstrip()
                                j = len(lines[i])

                        case '=':
                            if level == 0:
                                j = len(lines[i])

        # parse
        for i in range(len(lines)):
            # Remove empty null characters
            # Found these in a couple of older routes, harmless but generate errors
            # Possibly caused by BVE-RR (DOS version)
            lines[i] = lines[i].replace("\0", "")
            if self.IsRW and allow_rw_route_description:
                # ignore rw route description
                if (
                        (lines[i].startswith("[") and lines[i].find("]") > 0)
                        or lines[i].startswith("$")
                ):

                    allow_rw_route_description = False
                    self.CurrentRoute.Comment = self.CurrentRoute.Comment.strip()
                else:
                    if len(self.CurrentRoute.Comment) != 0:
                        self.CurrentRoute.Comment += "\n"
                    self.CurrentRoute.Comment += lines[i]
                    continue

            # count expressions
            n = 0
            level = 0
            for j in range(len(lines[i])):
                match lines[i][j]:
                    case '(':
                        level += 1

                    case ')':
                        level -= 1

                    case ',':
                        if not self.IsRW and level == 0:
                            n += 1

                    case '@':
                        if self.IsRW and level == 0:
                            n += 1

            if self.SplitLineHack:
                matches = re.findall(r".Load", lines[i], re.IGNORECASE)
                if len(matches) > 1:
                    split_line = lines[i].split(',')
                    lines.pop(i)
                    for j in range(len(split_line)):
                        new_line = split_line[j].strip()
                        if len(new_line) > 0:
                            lines.insert(i, new_line)

            # create expressions
            # 파이썬에서는 불필요하여 제거

            a, c = 0, 0
            level = 0
            for j in range(len(lines[i])):
                match lines[i][j]:
                    case '(':
                        level += 1

                    case ')':
                        if self.Plugin.CurrentOptions.EnableBveTsHacks:
                            if level > 0:
                                # Don't decrease the level below zero, as this messes up
                                # when extra closing brackets are encountere
                                level -= 1
                            else:
                                logger.warning(
                                    f"Invalid additional closing parenthesis encountered at line {i} character {j} in file {file_name}")
                        else:
                            level -= 1

                    case ',':
                        if level == 0 and not self.IsRW:
                            t = lines[i][a:j].strip()
                            if t and not t.startswith(';'):
                                expressions.append(Expression(file_name, t, i + 1, c + 1, track_position_offset))

                            a = j + 1
                            c += 1

                    case '@':
                        if level == 1 and self.IsRW and self.Plugin.CurrentOptions.EnableBveTsHacks:
                            # BVE2 doesn't care if a bracket is unclosed, fixes various routefiles
                            level -= 1
                        elif level == 2 and self.IsRW and self.Plugin.CurrentOptions.EnableBveTsHacks:
                            k = j
                            while k > 0:
                                k -= 1
                                if lines[i][j] == '(':
                                    # Opening bracket has been used instead of closing bracket, again BVE2 ignores this
                                    level -= 2
                                    break
                                if not lines[i][k].isspace():
                                    # Bracket not found, and this isn't whitespace either, so break out
                                    break
                        if level == 0 and self.IsRW:
                            t = lines[i][a:j].strip()
                            if len(t) > 0 and not t.startswith(';'):
                                expressions.append(Expression(file_name, t, i + 1, c + 1, track_position_offset))

                            a = j + 1
                            c += 1

            if len(lines[i]) - a > 0:
                t = lines[i][a:].strip()
                if t and not t.startswith(';'):
                    expressions.append(Expression(file_name, t, i + 1, c + 1, track_position_offset))
        return expressions

    def preprocess_chr_rnd_sub(self, file_name, encoding, expressions):
        subs = []
        open_ifs = 0
        i = 0
        while i < len(expressions):
            epilog = f" at line {str(expressions[i].Line)} column {str(expressions[i].Column)} in file {expressions[i].File}"
            continue_with_next_expression = False
            for j in range(len(expressions[i].Text) - 1, -1, -1):
                if expressions[i].Text[j] == '$':
                    k = 0
                    for k in range(j + 1, len(expressions[i].Text)):
                        if expressions[i].Text[k] == '(':
                            break

                        if expressions[i].Text[k] == '/' or expressions[i].Text[k] == '\\':
                            k = len(expressions[i].Text) + 1
                            break
                    if k <= len(expressions[i].Text):
                        t = expressions[i].Text[j:k].rstrip()
                        l = 1

                        for h in range(k + 1, len(expressions[i].Text)):
                            match expressions[i].Text[h]:
                                case '(':
                                    l += 1

                                case ')':
                                    l -= 1
                                    if l < 0:
                                        continue_with_next_expression = True
                                        logger.error(f"Invalid parenthesis structure in {t} {epilog}")

                            if l <= 0:
                                break
                        if continue_with_next_expression:
                            break
                        if l != 0:
                            logger.error(f"Invalid parenthesis structure in {t} {epilog}")
                            break
                        s = expressions[i].Text[k + 1:h].strip()
                        match t.lower():
                            case "$if":
                                if j != 0:
                                    logger.error(f"The $If directive must not appear within another statement {epilog}")
                                else:
                                    try:
                                        num = float(s)  # Try to convert string s to a float
                                        open_ifs += 1
                                        expressions[i].Text = ""
                                        if num == 0.0:
                                            # Blank every expression until the matching $Else or $EndIf
                                            i += 1
                                            level = 1
                                            while i < len(expressions):
                                                if expressions[i].Text.lower().startswith("$if"):
                                                    expressions[i].Text = ""
                                                    level += 1
                                                elif expressions[i].Text.lower().startswith("$else"):
                                                    expressions[i].Text = ""
                                                    if level == 1:
                                                        level -= 1
                                                        break
                                                elif expressions[i].Text.lower().startswith("$endif"):
                                                    expressions[i].Text = ""
                                                    level -= 1
                                                    if level == 0:
                                                        open_ifs -= 1
                                                        break
                                                else:
                                                    expressions[i].Text = ""
                                                i += 1
                                            if level != 0:
                                                logger.error(f"$EndIf missing at the end of the file {epilog}")
                                        continue_with_next_expression = True


                                    except ValueError:
                                        logger.error(f"The $If condition does not evaluate to a number {epilog}")

                            case "$else":
                                # * Blank every expression until the matching $EndIf
                                expressions[i].Text = ""
                                if open_ifs != 0:
                                    i += 1
                                    level = 1
                                    while i < len(expressions):
                                        if expressions[i].Text.lower().startswith("$if"):
                                            expressions[i].Text = ""
                                            level += 1

                                        elif expressions[i].Text.lower().startswith("$else"):
                                            expressions[i].Text = ""
                                            if level == 1:
                                                logger.error(f"Duplicate $Else encountered {epilog}")

                                        elif expressions[i].Text.lower().startswith("$endif"):
                                            expressions[i].Text = ""
                                            level -= 1
                                            if level == 0:
                                                open_ifs -= 1
                                                break
                                        else:
                                            expressions[i].Text = ""
                                        i += 1
                                    if level != 0:
                                        logger.error(f"$EndIf missing at the end of the file {epilog}")
                                else:
                                    logger.error(f"$Else without matching $If encountered {epilog}")
                                continue_with_next_expression = True

                            case "$endif":
                                expressions[i].Text = ""
                                if open_ifs != 0:
                                    open_ifs -= 1
                                else:
                                    logger.error(f"$EndIf without matching $If encountered {epilog}")
                                continue_with_next_expression = True

                            case "$include":
                                if j != 0:
                                    logger.error(f"The $Include directive must not appear within another statement {epilog}")
                                    continue_with_next_expression = True

                                args = s.split(';')
                                args = [arg.strip() for arg in args]

                                count = (len(args) + 1) // 2
                                files = []
                                weights = []
                                offsets = []
                                weights_total = 0.0
                                for ia in range(count):
                                    file = ''
                                    offset = 0.0
                                    colon = args[2 * ia].find(':')
                                    if colon >= 0:
                                        file = args[2 * ia][:colon].rstrip()
                                        value = args[2 * ia][colon + 1:].lstrip()
                                        try:
                                            offset = float(value)
                                        except ValueError:
                                            continue_with_next_expression = True  # or any default value you want to assign in case of failure
                                            logger.error(f"The track position offset {value} is invalid in {t} {epilog}")
                                            break
                                    else:
                                        file = args[2 * ia]
                                        offset = 0.0

                                    try:
                                        files.append(os.path.join(os.path.dirname(file_name), file))
                                    except Exception as ex:
                                        continue_with_next_expression = True
                                        logger.error(f"The filename {file} contains invalid characters in {t} {epilog}")
                                        expressions.pop(i)
                                        i -= 1
                                        break

                                    offsets.append(offset)
                                    if not os.path.exists(files[ia]):
                                        continue_with_next_expression = True
                                        logger.error(f"The file {file} could not be found in {t} {epilog}")
                                        expressions.pop(i)
                                        i -= 1
                                        break

                                    if 2 * ia + 1 < len(args):
                                        success, out = NumberFormats.try_parse_double_vb6(args[2 * ia + 1])
                                        weights.append(out)
                                        if not success:
                                            continue_with_next_expression = True
                                            logger.error(f"A weight is invalid in {t} {epilog}")
                                            break
                                        if weights[ia] <= 0.0:
                                            continue_with_next_expression = True
                                            logger.error(f"A weight is not positive in {t} {epilog}")
                                            break
                                        weights_total += weights[ia]
                                    else:
                                        weights.append(1.0)
                                        weights_total += 1.0
                                if count == 0:
                                    continue_with_next_expression = True
                                    logger.error(f"No file was specified in {t} {epilog}")

                                if not continue_with_next_expression:
                                    number = random.random() * weights_total
                                    value = 0.0
                                    chosen_index = 0
                                    for ia in range(count):
                                        value += weights[ia]
                                        if value > number:
                                            chosen_index = ia
                                            break

                                    # Get the text encoding of our $Include file

                                    include_encoding = TextEncoding.get_system_encoding_from_file(files[chosen_index])
                                    if include_encoding != encoding:
                                        # If the encodings do not match, add a warning
                                        # This is not critical, but it's a bad idea to mix and match character
                                        # encodings within a routefile, as the auto-detection may sometimes be wrong
                                        logger.warning(f"The text encoding of the $Include file "
                                              f"{str(files[chosen_index])} does not match that of the base routefile.")
                                    with open(files[chosen_index], 'r', encoding=include_encoding) as f:
                                        lines = f.readlines()
                                    expr = self.preprocess_split_into_expressions(
                                        files[chosen_index], lines, False,
                                        offsets[chosen_index] + expressions[i].TrackPositionOffset)

                                    if len(expr) == 0:
                                        # 표현식이 없으면 제거
                                        expressions.pop(i)
                                    else:
                                        # 표현식이 있으면 교체
                                        expressions = expressions[:i] + expr + expressions[i + 1:]
                                    i -= 1
                                    continue_with_next_expression = True

                            case "$chr":
                                pass
                            case "$chr!":
                                pass
                            case "$chrascii":
                                pass
                            case "$rnd":
                                pass
                            case "$sub":
                                pass

                if continue_with_next_expression:
                    break
            i += 1
        # handle comments introduced via chr, rnd, sub
        # 기존 expressions 리스트에서 주석과 빈 줄 제거
        expressions = [
            expr for expr in expressions
            if expr.Text.strip() and not expr.Text.strip().startswith(';')
        ]

        return expressions

    def preprocess_sort_by_track_position(self, unitfactors: List[float],
                                          expressions: List[Expression]) -> List[Expression]:

        p = []
        n = 0
        a = -1.0
        number_check = not self.IsRW

        for i in range(len(expressions)):
            if self.IsRW:
                # only check for track positions in the railway section for RW routes
                if expressions[i].Text.startswith('[') and expressions[i].Text.endswith(']'):
                    s = expressions[i].Text[1:-1].strip()
                    number_check = s.lower() == "railway"
            if number_check:
                try:
                    x = float(expressions[i].Text)
                    x += expressions[i].TrackPositionOffset
                    if x >= 0.0:
                        if self.Plugin.CurrentOptions.EnableBveTsHacks:
                            match os.path.basename(expressions[i].File.lower()):
                                case "balloch - dumbarton central special nighttime run.csv":
                                    pass
                                case "balloch - dumbarton central summer 2004 morning run.csv":
                                    if x != 0 or a != 4125:
                                        # Misplaced comma in the middle of the line causes this to be interpreted as a track position
                                        a = x
                                case _:  # 기본 동작(c# default)
                                    a = x
                        else:
                            a = x
                    else:
                        logger.error(
                            f'Negative track position encountered at line {str(expressions[i].Line)}, column {str(expressions[i].Column)} in file {expressions[i].File}')
                except ValueError as ex:
                    p.append(PositionedExpression(a, expressions[i]))
        p.sort(key=lambda e: e.track_position)
        a = -1.0
        e = []  # Expression 객체를 담을 리스트

        for pe in p:
            if pe.track_position != a:
                a = pe.track_position
                # 트랙 위치를 유닛으로 나눠서 문자열 표현
                pos_str = str(a / unitfactors[-1])
                e.append(Expression('', pos_str, -1, -1, -1))

            e.append(pe.expression)

        expressions = e

        return expressions
