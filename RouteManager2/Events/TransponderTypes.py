from enum import Enum


class TransponderTypes(Enum):
    """
    Attributes:
        AtcTrackStatus: Marks the status of ATC.
        AtcSpeedLimit:  Sets up an ATC speed limit
        AtsPTemporarySpeedLimit: Sets up an ATS-P temporary speed limit.
        AtsPPermanentSpeedLimit: Sets up an ATS-P permanent speed limit
        InternalAtsPTemporarySpeedLimit: For internal use inside the CSV/RW parser only.
    """
    AtcTrackStatus = -16777215
    AtcSpeedLimit = -16777214
    AtsPTemporarySpeedLimit = -16777213
    AtsPPermanentSpeedLimit = -16777212
    InternalAtsPTemporarySpeedLimit = -16777201

