
def write_log(message: str, log_file:str ="process.log", verbose:bool=False
              , append:bool=True)-> None:
    mode = 'a' if append else 'w'
    with open(log_file, mode) as log:
        log.write(message + "\n")
        if verbose:
            print(message)