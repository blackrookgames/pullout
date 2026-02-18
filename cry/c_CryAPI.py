all = ['CryAPI']
    
import json as _json

from typing import\
    Any as _Any

import engine.helper as _helper

class CryAPI:
    """
    Represents information about an API key
    """

    #region init

    def __init__(self, path:_Any):
        """
        Initializer for CryAPI
        
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
            raise _helper.CLIError("Could not find the API key.")
        self.__key = key
        # secret
        secret = None
        if 'privateKey' in data:
            secret = str(data['privateKey'])
        if secret is None:
            raise _helper.CLIError("Could not find the secret.")
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
    def __loadjson(cls, path:_Any):
        try:
            with open(str(path), 'r') as f:
                return _json.load(f)
        except Exception as _e:
            e = _helper.CLIError(_e)
        raise e

    #endregion