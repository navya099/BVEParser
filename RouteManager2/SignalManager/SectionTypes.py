from enum import Enum, auto


class SectionType(Enum):
    """The types of section
    Attribute:
        value_based: A section aspect may have any value
        index_based: Section aspect count upwards from zero (0,1,2,3....)
    """
    value_based = auto()
    index_based = auto()