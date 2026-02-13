all = ['APIInfo']

import json as _json

from .c_CLIError import\
    CLIError as _CLIError

class APIInfo:
    """
    Represents information about an API key
    """

    #region init

    def __init__(self, path):
        """
        Initializer for APIInfo
        
        :param path:
            Path to JSON file
        :raise CLIError:
            An error occurred
        """
        data = self.__loadjson(path)
        # key
        key = None
        if 'name' in data:
            key = str(data['name'])
        if key is None:
            raise _CLIError("Could not find the API key.")
        self.__key = key
        # secret
        secret = None
        if 'privateKey' in data:
            secret = str(data['privateKey'])
        if secret is None:
            raise _CLIError("Could not find the secret.")
        self.__secret = secret

    #endregion

    #region properties

    @property
    def key(self):
        """
        API Key
        """
        return self.__key

    @property
    def secret(self):
        """
        Secret
        """
        return self.__secret
            
    #endregion

    #region helper methods

    @classmethod
    def __loadjson(cls, path):
        try:
            with open(str(path), 'r') as f:
                return _json.load(f)
        except Exception as _e:
            e = _CLIError(_e)
        raise e

    #endregion