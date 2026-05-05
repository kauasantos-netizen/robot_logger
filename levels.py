import logging

END_LEVEL = 25
logging.addLevelName(END_LEVEL, "END")

def end(self, message, *args, **kwargs):
    if self.isEnabledFor(END_LEVEL):
        self._log(END_LEVEL, message, args, **kwargs)

def register():
    logging.Logger.end = end