import yaml
import json
import os

class Config:
    """Configuration loader class."""
    
    def __init__(self, config_file='config.yaml'):
        self._config = self.load_config(config_file)
    
    def load_config(self, config_file):
        """Load configuration from YAML or JSON file."""
        if config_file.endswith('.yaml') or config_file.endswith('.yml'):
            with open(config_file, 'r') as file:
                return yaml.safe_load(file)
        elif config_file.endswith('.json'):
            with open(config_file, 'r') as file:
                return json.load(file)
        else:
            raise ValueError("Unsupported configuration file format")

    def get(self, key, default=None):
        """Get a value from the configuration."""
        return self._config.get(key, default)

    def as_dict(self):
        """Return the configuration as a dictionary."""
        return self._config

# Load configuration (change 'config.yaml' to 'config.json' if needed)
config = Config(config_file='config.json').as_dict()
