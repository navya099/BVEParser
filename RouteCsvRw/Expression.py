
class Expression:
    def __init__(self,file: str,text: str, line: int, column: int, trackpositionoffset: float):
        self.file = file
        self.text = text
        self.line = line
        self.column = column
        self.trackpositionoffset = trackpositionoffset


    def convertrwtocsv(self, section: str, sectionalwaysprefix: bool) -> None:
        equals = self.text.find('=')
        if equals >= 0:
            # handle RW cycle syntax
            t = self.text[:equals]
            if section.lower() == "cycle" and sectionalwaysprefix:
                if numberformats.try_parse_double_vb6(t):
                    pass
#test
expression = Expression('a','sty4=35',141,52,1.4)
expression.convertrwtocsv('af33',False)
