from domain.ticket.denied_boarding import DeniedBoardingReason
from domain.regulation.eu261_compensation import Eu261Compensation


def evaluate_denied_boarding(reason, distance_km):
    if reason == DeniedBoardingReason.PASSENGER_FAULT:
        return None

    if distance_km <= 1500:
        return Eu261Compensation(250)

    if distance_km <= 3500:
        return Eu261Compensation(400)

    return Eu261Compensation(600)
