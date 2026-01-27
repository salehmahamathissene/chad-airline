from enum import Enum


class DeniedBoardingReason(Enum):
    OVERBOOKING = "overbooking"
    OPERATIONAL = "operational"
    SAFETY = "safety"
    DOCUMENTATION = "documentation"
    PASSENGER_FAULT = "passenger_fault"
