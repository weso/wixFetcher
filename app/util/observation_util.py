__author__ = 'Miguel'
__date__ = '17/09/2014'

from webindex.domain.model.observation.observation import *


class ObservationUtil(object):

    @staticmethod
    def are_equivalent_observations(obs1, obs2):
        if obs1.ref_area == obs2.ref_area \
                and obs1.ref_year == obs2.ref_year \
                and obs1.ref_indicator == obs2.ref_indicator:
            return True
        return False