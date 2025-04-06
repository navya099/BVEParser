import re
import os
import random
from unittest import case
from xxsubtype import bench

import chardet

from .Structures.Expression import Expression
from  OpenBveApi.Math.Math import NumberFormats

def detect_encoding(path):
    # 파일을 열어 일부를 읽어서 인코딩을 감지합니다
    with open(path, 'rb') as file:
        raw_data = file.read(10000)  # 처음 10000 바이트를 읽어봄
        result = chardet.detect(raw_data)  # 인코딩 탐지
        return result['encoding']

class PreprocessMixin:
    def PreprocessSplitIntoExpressions(self, file_name, lines, allow_rw_route_description, track_position_offset=0.0):
        expressions = [Expression('','',0,0,0.0) for _ in range(4096)]  # 기본 생성자를 사용할 경우
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
            #Remove empty null characters
            #Found these in a couple of older routes, harmless but generate errors
	    #Possibly caused by BVE-RR (DOS version)
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
                
            #count expressions
            n = 0
            level = 0
            for j in range(len(lines[i])):
                match lines[i][j]:
                    case '(':
                        level += 1

                    case ')':
                        level -= 1

                    case ',':
                        if not self.IsRW  and level == 0:
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
                            
            #create expressions
            m = e+ n +1
            while m >= len(expressions):
                expressions.extend([None] * len(expressions))  # 크기를 2배로 확장

            a, c = 0, 0
            level = 0
            for j in range(len(lines[i])):
                match lines[i][j]:
                    case '(':
                        level += 1

                    case ')':
                        if self.Plugin.CurrentOptions.EnableBveTsHacks:
                            if level > 0:
                                #Don't decrease the level below zero, as this messes up when extra closing brackets are encountere
                                level -= 1
                            else:
                                print(f"Invalid additional closing parenthesis encountered at line {i} character {j} in file {file_name}")
                        else:
                            level -= 1

                    case ',':
                        if level == 0 and not self.IsRW:
                            t = lines[i][a:j].strip()
                            if t and not t.startswith(';'):
                                expressions[e] = Expression(file_name, t, i + 1, c + 1, track_position_offset)
                                e += 1
                            a = j + 1
                            c += 1

                    case '@':
                        if level == 1 and self.IsRW and self.Plugin.CurrentOptions.EnableBveTsHacks:
                            #BVE2 doesn't care if a bracket is unclosed, fixes various routefiles
                            level -= 1
                        elif level == 2 and self.IsRW and self.Plugin.CurrentOptions.EnableBveTsHacks:
                            k = j
                            while k > 0:
                                k -=1
                                if lines[i][j] == '(':
                                    #Opening bracket has been used instead of closing bracket, again BVE2 ignores this
                                    level -= 2
                                    break
                                if not lines[i][k].isspace():
                                    #Bracket not found, and this isn't whitespace either, so break out
                                    break
                        if level == 0 and  self.IsRW:
                            t = lines[i][a:j].strip()
                            if len(t) > 0 and not t.startswith(';'):
                                expressions[e] = Expression(file_name, t, i + 1, c + 1, track_position_offset)
                                e += 1
                            a = j + 1
                            c += 1

            
            if len(lines[i]) - a > 0:
                t = lines[i][a:].strip()
                if len(t) > 0 and not t.startswith(';'):
                    expressions[e] = Expression(file_name, t, i + 1, c + 1, track_position_offset)
                    e += 1

        expressions = expressions[:e]
        return expressions


    def PreprocessChrRndSub(self, FileName, Encoding, Expressions):
        Subs = [""] * 16
        openIfs = 0
        for i in range (len(Expressions)):
            Epilog = f" at line {str(Expressions[i].Line)} column {str(Expressions[i].Column)} in file {Expressions[i].File}"
            continueWithNextExpression = False
            for j in range(len(Expressions[i].Text) - 1):
                if Expressions[i].Text[j] == '$':
                    k = 0
                    for k in range(j + 1, len(Expressions[i].Text)):
                        if Expressions[i].Text[k] == '(':
                            break

                        if Expressions[i].Text[k] == '/' or Expressions[i].Text[k] == '\\':
                            k = len(Expressions[i].Text) + 1
                            break
                    if k <= len(Expressions[i].Text):
                        t = Expressions[i].Text[j:k].rstrip()
                        l,h = 1,0
                        h = k +1
                        for h in range(k + 1, len(Expressions[i].Text)):
                            match Expressions[i].Text[h]:
                                case '(':
                                    l += 1

                                case ')':
                                    l -= 1
                                    if l < 0:
                                        continueWithNextExpression = True
                                        print(f"Invalid parenthesis structure in {t} {Epilog}")

                            if l <= 0:
                                break
                        if continueWithNextExpression:
                            break
                        if l != 0:
                            print(f"Invalid parenthesis structure in {t} {Epilog}")
                            break
                        s = Expressions[i].Text[k + 1:h].strip()
                        match t.lower():
                            case "$if":
                                if j != 0:
                                    print(f"The $If directive must not appear within another statement {Epilog}")
                                else:
                                    try:
                                        num = float(s)  # Try to convert string s to a float
                                        openIfs += 1
                                        Expressions[i].Text = ""
                                        if num == 0.0:
                                            #Blank every expression until the matching $Else or $EndIf
                                            i += 1
                                            level = 1
                                            while i < len(Expressions):
                                                if Expressions[i].Text.lower().startswith("$if"):
                                                    Expressions[i].Text = ""
                                                    level += 1
                                                elif Expressions[i].Text.lower().startswith("$else"):
                                                    Expressions[i].Text = ""
                                                    if level == 1:
                                                        level -= 1
                                                        break
                                                elif Expressions[i].Text.lower().startswith("$endif"):
                                                    Expressions[i].Text = ""
                                                    level -= 1
                                                    if level == 0:
                                                        openIfs -= 1
                                                        break
                                                else:
                                                    Expressions[i].Text = ""
                                                i += 1
                                            if level != 0:
                                                print("$EndIf missing at the end of the file" + Epilog)
                                        continueWithNextExpression = True


                                    except ValueError:
                                        print("The $If condition does not evaluate to a number" + Epilog)

                                    continueWithNextExpression = True

                            case "$else":
                                # * Blank every expression until the matching $EndIf
                                Expressions[i].Text = ""
                                if openIfs != 0:
                                    i += 1
                                    level = 1
                                    while i < len(Expressions):
                                        if Expressions[i].Text.lower().startswith("$if"):
                                            Expressions[i].Text = ""
                                            level += 1
                                            break
                                        elif Expressions[i].Text.lower().startswith("$else"):
                                            Expressions[i].Text = ""
                                            if level == 1:
                                                print("Duplicate $Else encountered" + Epilog)

                                        elif Expressions[i].Text.lower().startswith("$endif"):
                                            Expressions[i].Text = ""
                                            level -= 1
                                            if level == 0:
                                                openIfs -= 1
                                                break
                                        else:
                                            Expressions[i].Text = ""
                                        i += 1
                                    if level != 0:
                                        print("$EndIf missing at the end of the file" + Epilog)
                                else:
                                    print("$Else without matching $If encountered" + Epilog)
                                continueWithNextExpression = True

                            case "$endif":
                                Expressions[i].Text = ""
                                if openIfs != 0:
                                    openIfs -= 1
                                else:
                                    print("$EndIf without matching $If encountered" + Epilog)
                                continueWithNextExpression = True


                            case "$include":
                                if j != 0:
                                    print("The $Include directive must not appear within another statement" + Epilog)
                                    continueWithNextExpression = True
                                    break
                                args = s.split(';')
                                for ia in range(len(args)):
                                    args[ia] = args[ia].strip()
                                count = (len(args) + 1) // 2
                                files = [None] * count
                                weights = [0.0] * count
                                offsets = [0.0] * count
                                weightsTotal = 0.0
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
                                            continueWithNextExpression = True # or any default value you want to assign in case of failure
                                            print("The track position offset " + value + " is invalid in " + t + Epilog)
                                            break
                                    else:
                                        file = args[2 * ia]
                                        offset = 0.0

                                    try:
                                        files[ia] = os.path.join(os.path.dirname(FileName), file)
                                    except Exception as ex:
                                        continueWithNextExpression = True
                                        print( "The filename " + file + " contains invalid characters in " + t + Epilog)
                                        for ta in range(i , len(Expressions) -1):
                                            Expressions[ta] = Expressions[ta +1]
                                        Expressions = Expressions[:-1]
                                        i -= 1
                                        break

                                    offsets[ia] = offset
                                    if not os.path.exists(files[ia]):
                                        continueWithNextExpression = True
                                        print("The file {file} could not be found in {t} {Epilog}")
                                        for ta in range(i, len(Expressions) - 1):
                                            Expressions[ta] = Expressions[ta + 1]
                                        Expressions = Expressions[:-1]
                                        i -= 1
                                        break

                                    if 2 * ia + 1 < len(args):
                                        if not NumberFormats.TryParseDoubleVb6(args[2 * ia + 1]):
                                            continueWithNextExpression = True
                                            print("A weight is invalid in " + t + Epilog)
                                            break
                                        if weights[ia] <= 0.0:
                                            continueWithNextExpression = True
                                            print("A weight is not positive in " + t + Epilog)
                                            break
                                        weightsTotal += weights[ia]
                                    else:
                                        weights[ia]  = 1.0
                                        weightsTotal += 1.0
                                if count == 0:
                                    continueWithNextExpression = True
                                    print("No file was specified in " + t + Epilog)

                                if not continueWithNextExpression:
                                    number = random.random() * weightsTotal
                                    value = 0.0
                                    chosenIndex = 0
                                    for ia in range(count):
                                        value += weights[ia]
                                        if value > number:
                                            chosenIndex = ia
                                            break
                                    includeEncoding = detect_encoding(files[chosenIndex])
                                    if includeEncoding != Encoding and includeEncoding != Encoding:
                                        # If the encodings do not match, add a warning
                                        # This is not critical, but it's a bad idea to mix and match character encodings within a routefile, as the auto-detection may sometimes be wrong
                                        print("The text encoding of the $Include file " + files[chosenIndex] + " does not match that of the base routefile.")
                                    with open(files[chosenIndex], 'r', encoding=includeEncoding) as f:
                                        lines = f.readlines()
                                    expr = self.PreprocessSplitIntoExpressions(files[chosenIndex], lines, False, offsets[chosenIndex] + Expressions[i].TrackPositionOffset)
                                    length = len(Expressions)
                                    if len(expr) == 0:
                                        # 표현식이 비었으면 현재 i 위치 요소 삭제
                                        for ia in range(i, length - 1):
                                            Expressions[ia] = Expressions[ia + 1]
                                        length -= 1
                                        Expressions = Expressions[:length]
                                    else:
                                        insert_count = len(expr)
                                        new_length = length + insert_count - 1

                                        # Expressions 리스트 확장
                                        Expressions += [None] * (insert_count - 1)

                                        # 뒤에서 앞으로 기존 요소들 이동
                                        for ia in range(new_length - 1, i + insert_count - 1, -1):
                                            Expressions[ia] = Expressions[ia - insert_count + 1]

                                        # 새 표현식 삽입
                                        for ia in range(insert_count):
                                            Expressions[i + ia] = expr[ia]

                                        length = new_length

                                    i -= 1
                                    continueWithNextExpression = True

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

                if continueWithNextExpression:
                    break
        #// handle comments introduced via chr, rnd, sub
        length = len(Expressions)
        for i in range(length):
            Expressions[i].Text = Expressions[i].Text.strip()
            if len(Expressions[i].Text) != 0:
                if Expressions[i].Text[0] == ';':
                    for j in range(i, len(length)- 1):
                        Expressions[j] =  Expressions[j +1 ]
                    length -= 1
                    i -= 1
            else:
                for j in range(i, len(length) - 1):
                    Expressions[j] = Expressions[j + 1 ]
                length -= 1
                i -= 1
        if length != len(Expressions):
            Expressions = Expressions[:length]



        return Expressions