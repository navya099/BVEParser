from OpenBveApi.Math.Math import NumberFormats
from loggermodule import logger


class Expression:
    def __init__(self, file: str, text: str, line: int, column: int, trackpositionoffset: float):
        self.File = file
        self.Text = text
        self.Line = line
        self.Column = column
        self.TrackPositionOffset = trackpositionoffset

    def convert_rw_to_csv(self, section: str, section_always_prefix: bool) -> None:
        equals = self.Text.find('=')
        if equals >= 0:
            # handle RW cycle syntax
            t = self.Text[:equals]
            if section.lower() == "cycle" and section_always_prefix:
                success, b = NumberFormats.try_parse_double_vb6(t)
                if success:
                    t = f".Ground({b})"
            elif section.lower() == "signal" and section_always_prefix:
                success, b = NumberFormats.try_parse_double_vb6(t)
                if success:
                    t = f".Void({b})"
            # convert RW style into CSV style
            self.Text = t + " " + self.Text[equals + 1:]

    def separate_commands_and_arguments(self, culture: None,
                                        raise_errors: bool, isrw: bool, current_section: str):
        opening_error = False
        closing_error = False
        i = 0
        first_closing_bracket = 0
        from Plugins.RouteCsvRw.Plugin import Plugin
        if Plugin.CurrentOptions.EnableBveTsHacks:
            if self.Text.lower().startswith("train. "):
                # HACK: Some Chinese routes seem to have used a space between Train. and the rest of the command
                # e.g. Taipei Metro. BVE4/ 2 accept this......
                self.Text = "Train." + self.Text[7:]
            elif self.Text.lower().startswith("Texture. Background "):
                # Same hack as above, found in Minobu route for BVE2
                self.Text = "Texture.Background" + self.Text[19:]
            elif self.Text.lower().startswith(")height(0)"):
                self.Text = "Texture.Background" + self.Text[9:]

            if isrw and current_section.lower() == "track":
                # Removes misplaced track position indicies from the end of a command in the Track section
                idx = self.Text.rfind(')')
                if idx != -1 and idx != len(self.Text):
                    s = self.Text[idx + 1:].strip()
                    sucess, _ = NumberFormats.try_parse_double_vb6(s)
                    self.Text = self.Text[:idx].strip()

            if isrw and self.Text.endswith("))"):
                opening_brackets = self.Text.count('(')
                closing_brackets = self.Text.count(')')
                # Remove obviously wrong double-ending brackets
                if closing_brackets == opening_brackets + 1 and self.Text.endswith('))'):
                    self.Text = self.Text[:-1]

            if self.Text.lower().startswith('route.comment') and "(c)" in self.Text.lower():
                # Some BVE4 routes use this instead of the copyright symbol
                self.Text = self.Text.replace("(C)", "©")
                self.Text = self.Text.replace("(c)", "©")

            from Plugins.RouteCsvRw.CsvRwRouteParser import Parser
            if isrw and Parser.EnabledHacks.AggressiveRwBrackets:
                # Attempts to aggressively discard *anything* encountered after a closing bracket
                c = self.Text.find(')')
                while c > len(self.Text):
                    if self.Text[c] == '=':
                        break
                    if not self.Text[c].isspace():
                        self.Text = self.Text[c:]
                        break
                    c += 1
        while i < len(self.Text):
            if self.Text[i] == '(':
                found = False
                argument_index = 0
                i += 1
                while i < len(self.Text):
                    if self.Text[i] == ',' or self.Text[i] == ';':
                        # only check parenthesis in the station name field-
                        # The comma and semi-colon are the argument separators
                        argument_index += 1

                    if self.Text[i] == '(':
                        if raise_errors and not opening_error:
                            match argument_index:
                                case 0:
                                    if self.Text.startswith('sta'):
                                        self.Text = self.Text[:i] + "[" + self.Text[i + 1:]
                                    if (self.Text.lower().startswith('marker') or
                                            self.Text.lower().startswith('announce') or
                                            '.load' in self.Text.lower()):
                                        '''
                                        HACK: In filenames, temp replace with an invalid but known character
                                        Opening parenthesis are fortunately simpler than closing, see notes below.
                                        '''
                                        self.Text = self.Text[:i] + "<" + self.Text[i + 1:]

                                    else:
                                        logger.error(f'Invalid opening parenthesis encountered at line {str(self.Line)},'
                                              f'column {str(self.Column)} in file{self.File}')
                                        opening_error = True

                                case 5:  # arrival sound
                                    pass
                                case 10:  # eparture sound
                                    if self.Text.lower().startswith('sta'):
                                        self.Text = self.Text[:i] + "<" + self.Text[i + 1:]
                                    else:
                                        logger.error(f'Invalid opening parenthesis encountered at line {str(self.Line)},'
                                              f'column {str(self.Column)} in file{self.File}')
                                        opening_error = True
                                case _:
                                    logger.error(f'Invalid opening parenthesis encountered at line {str(self.Line)},'
                                          f'column {str(self.Column)} in file{self.File}')
                                    opening_error = True

                    elif self.Text[i] == ')':
                        match argument_index:
                            case 0:
                                if self.Text.startswith('sta') and i != len(self.Text):
                                    self.Text = self.Text[:i] + "]" + self.Text[i + 1:]
                                    continue
                                if (
                                        (self.Text.lower().startswith("marker") or self.Text.lower().startswith(
                                            "announce")) and i != len(self.Text)
                                ) or (
                                        ".load" in self.Text.lower() and "<" in self.Text and i > 18 and i != len(
                                    self.Text) - 1
                                ):
                                    # 조건에 맞을 때 수행할 코드

                                    '''
                                    HACK: In filenames, temp replace with an invalid but known character
                                    Note that this is a PITA in object folder names when the creator has used 
                                    the alternate .Load() format as this contains far more brackets
                                    e.g.
                                    .Rail(0).Load(kcrmosr(2009)\rail\c0.csv)
                                    We must keep the first and last closing parenthesis intact here
                                    '''
                                    self.Text = self.Text[:i] + ">" + self.Text[i + 1:]
                                    continue
                            case 5:  # arrival sound
                                pass
                            case 10:  # eparture sound
                                if self.Text.lower().startswith('sta') and i != len(self.Text):
                                    self.Text = self.Text[:i] + ">" + self.Text[i + 1:]
                                    continue
                        found = True
                        first_closing_bracket = i
                        break
                    i += 1

                if not found:
                    if raise_errors and not closing_error:
                        logger.error(f'Missing closing parenthesis encountered at line {str(self.Line)},'
                              f'column {str(self.Column)} in file{self.File}')
                        closing_error = True

                    self.Text += ")"
            elif self.Text[i] == ')':
                if raise_errors and not closing_error:
                    logger.error(f'Invalid closing parenthesis encountered at line {str(self.Line)},'
                          f'column {str(self.Column)} in file{self.File}')
                    closing_error = True
            elif self.Text[i].isspace():
                # 공백 문자일 때의 처리
                if i >= len(self.Text) - 1 or not self.Text[i + 1].isspace():
                    break
            i += 1
        if first_closing_bracket != 0 and first_closing_bracket < len(self.Text) - 1:
            if self.Text[first_closing_bracket + 1] not in (' ', '.', ';'):
                # Do something
                self.Text = self.Text[:first_closing_bracket + 1] + " " + self.Text[first_closing_bracket + 1:]
                i = first_closing_bracket

        if i < len(self.Text):
            # white space was found outside of parentheses
            a = self.Text[:i]
            if '(' in a and ')' in a:
                # indices found not separated from the command by spaces
                command = self.Text[:i].rstrip()
                argument_sequence = self.Text[i + 1:].lstrip()
                if argument_sequence.startswith('(') and argument_sequence.endswith(')'):
                    # arguments are enclosed by parentheses
                    argument_sequence = argument_sequence[1:-1].strip()
                elif argument_sequence.startswith('('):
                    # only opening parenthesis found
                    if raise_errors and not closing_error:
                        logger.error(f'Missing closing parenthesis encountered at line {str(self.Line)}'
                              f'column {str(self.Column)} in file{self.File}')
                    argument_sequence = argument_sequence[1:].lstrip()
            else:
                # no indices found before the space
                if i < len(self.Text) - 1 and self.Text[i + 1] == '(':
                    # opening parenthesis follows the space
                    j = self.Text.find(')', i + 1)
                    if j > i + 1:
                        # closing parenthesis found
                        if j == len(self.Text) - 1:
                            # only closing parenthesis found at the end of the expression
                            command = self.Text[:i].rstrip()
                            argument_sequence = self.Text[i + 2:j - 2].strip()
                        else:
                            # detect border between indices and arguments
                            found = False
                            command = None
                            argument_sequence = None

                            for k in range(j +1, len(self.Text)):
                                if self.Text[k].isspace():
                                    command = self.Text[:k].rstrip()
                                    argument_sequence = self.Text[k + 1:].lstrip()
                                    found = True
                                    break
                                if self.Text[k] == '(':
                                    command = self.Text[:k].rstrip()
                                    argument_sequence = self.Text[k:].lstrip()
                                    found = True
                                    break

                            if not found:
                                if raise_errors and not opening_error and not closing_error:
                                    logger.error(f'Invalid syntax encountered at line {str(self.Line)},'
                                          f'column {str(self.Column)} in file{self.File}')
                                    closing_error = True

                                command = self.Text
                                argument_sequence = ''

                            if argument_sequence.startswith('(') and argument_sequence.endswith(')'):
                                # arguments are enclosed by parentheses
                                argument_sequence = argument_sequence[1:-1].strip()
                            elif argument_sequence.startswith('('):
                                # only opening parenthesis found
                                if raise_errors and not closing_error:
                                    logger.error(f'Missing closing parenthesis encountered at line {str(self.Line)},'
                                          f'column {str(self.Column)} in file{self.File}')
                                argument_sequence = argument_sequence[1:].lstrip()
                    else:
                        # no closing parenthesis found
                        if raise_errors and not closing_error:
                            logger.error(f'Missing closing parenthesis encountered at line {str(self.Line)},'
                                  f'column {str(self.Column)} in file{self.File}')
                        command = self.Text[:i].rstrip()
                        argument_sequence = self.Text[i + 2:].lstrip()
                else:
                    # no index possible
                    command = self.Text[:i].rstrip()
                    argument_sequence = self.Text[i + 1:].lstrip()
                    if argument_sequence.startswith('(') and argument_sequence.endswith(')'):
                        # arguments are enclosed by parentheses
                        argument_sequence = argument_sequence[1:-1].strip()
                    elif argument_sequence.startswith('('):
                        # only opening parenthesis found
                        if raise_errors and not closing_error:
                            logger.error(f'Missing closing parenthesis encountered at line {str(self.Line)},'
                                  f'column {str(self.Column)} in file{self.File}')
                        argument_sequence = argument_sequence[1:].lstrip()
        else:
            # no single space found
            if self.Text.endswith(')'):
                i = self.Text.rfind('(')
                if i >= 0:
                    command = self.Text[:i].rstrip()
                    argument_sequence = self.Text[i + 1:-1].strip()
                    text_lower = self.Text.lower()
                    if (text_lower.startswith("sta") or
                            text_lower.startswith("marker") or
                            text_lower.startswith("announce") or
                            ".load" in text_lower):
                        # put back any temp removed brackets
                        argument_sequence = argument_sequence.replace('<', '(')
                        argument_sequence = argument_sequence.replace('>', ')')
                        if argument_sequence.endswith(')'):
                            argument_sequence.rstrip(')')
                else:
                    command = self.Text
                    argument_sequence = ''
            else:
                i = self.Text.find('(')
                if i >= 0:
                    if raise_errors and not closing_error:
                        logger.error(f'Missing closing parenthesis encountered at line {str(self.Line)},'
                              f'column {str(self.Column)} in file{self.File}')
                    command = self.Text[:i].rstrip()
                    argument_sequence = self.Text[i + 1:].lstrip()
                else:
                    if raise_errors:
                        i = self.Text.find(')')
                        if i >= 0 and not closing_error:
                            logger.error(f'Invalid closing parenthesis encountered at line {str(self.Line)},'
                                  f'column {str(self.Column)} in file{self.File}')
                    command = self.Text
                    argument_sequence = ''

        # invalid trailing characters
        if command.endswith(';'):
            if raise_errors:
                logger.error(f'Invalid trailing semicolon encountered at line {str(self.Line)},'
                      f'column {str(self.Column)} in file{self.File}')
            while command.endswith(";"):
                command = command[:-1]

        return command, argument_sequence