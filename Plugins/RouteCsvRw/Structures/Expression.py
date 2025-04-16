from OpenBveApi.Math.Math import NumberFormats
class Expression:
    def __init__(self,file: str,text: str, line: int, column: int, trackpositionoffset: float) -> list:
        self.File = file
        self.Text = text
        self.Line = line
        self.Column = column
        self.TrackPositionOffset = trackpositionoffset


    def convertrwtocsv(self, section: str, sectionalwaysprefix: bool) -> None:
        equals = self.text.find('=')
        if equals >= 0:
            # handle RW cycle syntax
            t = self.text[:equals]
            if section.lower() == "cycle" and sectionalwaysprefix:
                if numberformats.TryParseDoubleVb6(t):
                    pass

