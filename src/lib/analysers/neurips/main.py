import os
import json
from lib.common.exceptions import InvalidAnalyserConfigError
from lib.common.analyser import Analyser
from lib.common.etypes import Etype
from lib.common.util import vuevis_from_preds
from fastai.vision import load_learner, open_image


class NeuripsAnalyser(Analyser):
    def get_in_etype(self):
        return Etype.AnnotatedImageArray

    def get_out_etype(self):
        return Etype.Json

    def pre_analyse(self, config):
        pass

    def analyse_element(self, element, config):
        pass
