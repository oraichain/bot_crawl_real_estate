
from abc import ABC, abstractmethod

from utils.text_preprocessor import TextPreprocessor

class BaseExtractor(ABC):

    def __init__(self, do_preprocess=False):
        self.do_preprocess = do_preprocess
        if do_preprocess:
            self.preprocess_text = TextPreprocessor()
