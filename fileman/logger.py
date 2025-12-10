
class Logger:
    DEFAULT_LOG_FILE = "logger.log"
    
    def __init__(self, _logfile_name="" ) -> None:
        
        if _logfile_name == "":
           self._logfile_name = self.DEFAULT_LOG_FILE
        else:
           self._logfile_name = _logfile_name
        
    def write_log(self, message: str, log_file="process.log")-> None:
        with open(log_file, 'a') as log:
             log.write(message + "\n")