import time
import sys
from datetime import datetime
import isodate
import logging
from pythonping import ping
import yaml
import os
from PyP100 import PyP100

CONFIG_PATH = '/etc/tapo-controller/config.yaml'
LOG_PATH = '/var/log/tapo-controller/app.log'

class TapoController:
  def __init__(self):
    self._config = self._load_config()
    self._logger = self._create_logger(self._config.get('log_level'))
    self._plug = self._connect_plug(self._config['plug'])

  def _load_config(self) -> dict:
    """
    Loads configuration from YAML file

    Returns:
    dict: Description of the return value
    """
    try:
      with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)
    except:
      raise IOError(f'Cannot open configuration file "{CONFIG_PATH}"')

  def _create_logger(self, log_level_str: str=None) -> logging.Logger:
    """
    Creates logger instance

    Parameters:
    - log_level_str (str): Log level

    Returns:
    logging.Logger: Logger instance
    """
    format = '%(asctime)s - %(levelname)s - %(message)s'
    datefmt = '%Y-%m-%d %H:%M:%S'

    # Configure the root logger for stdout
    logging.basicConfig(
      level = logging.NOTSET, # Will pass all log messages
      format = format,
      datefmt = datefmt,
    )

    logger = logging.getLogger()

    if (log_level_str is not None):
      # Make directory for log file if it doesn't exist
      os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

      # Convert the log level string to a numeric value
      log_level = getattr(logging, log_level_str.upper(), logging.NOTSET)

      if not isinstance(log_level, int):
        raise ValueError(f'Invalid log level: "{log_level_str}"')

      formatter    = logging.Formatter(format, datefmt)
      file_handler = logging.FileHandler(LOG_PATH)
      file_handler.setLevel(log_level)
      file_handler.setFormatter(formatter)

      logger.addHandler(file_handler)

    return logger

  def _is_online(self, ip: str) -> bool:
    """
    Checks if device with given IP address reacts to ping

    Parameters:
    - ip (str): IP address

    Returns:
    bool: Is online
    """
    pingResult = ping(ip, count=1, timeout=1)
    result = all(resultLine.success for resultLine in pingResult)
    self._logger.debug(f'Device with ip "{ip}" ' + {True: "is", False: "is not"}[result] + ' online')

    return result

  def _any_online(self) -> bool:
    """
    Returns True when any of observed devices are pingable

    Returns:
    bool: True when any of observed devices are pingable
    """
    return any(self._is_online(ip) for ip in self._config['check_ips'])

  def _connect_plug(self, config: dict) -> PyP100.P100:
    """
    Connects to the plug

    Returns:
    PyP100.P100: Plug instance
    """
    ip = config['ip']
    self._logger.info(f'Connecting to the plug with ip: "{ip}"')
    # All types of 1.. plugs have the same API for turning on and off
    plug = PyP100.P100(ip, config['username'], config['password']) #Creates a P100 plug object

    plug.handshake() # Creates the cookies required for further methods
    plug.login() # Sends credentials to the plug and creates AES Key and IV for further methods

    self._logger.info(f'Connected to the plug')

    return plug

  def _change_plug_status(self, status: bool):
    """
    Turns the plug on or off

    Parameters:
    - status (bool): Power status (True = on, False = off)
    """
    status_strings = {True: 'on', False: 'off'}
    status_string = status_strings[status]

    method_to_call = getattr(self._plug, 'turn' + status_string.capitalize())
    self._logger.info('Turning the plug ' + status_string)
    method_to_call()

  def run(self):
    """
    Runs the daemon
    """
    any_ips_online = False
    latest_online_time = None

    refresh_interval_seconds = isodate.parse_duration(self._config['refresh_interval']).total_seconds()
    offline_delay_interval = isodate.parse_duration(self._config['offline_delay_interval'])

    while True:
      try:
        any_ips_online_now = self._any_online()
        now = datetime.now()

        if any_ips_online_now:
          # Save latest known online time for determining if plug should be turned off after some time period
          latest_online_time = now
        elif not (latest_online_time is None) and (latest_online_time + offline_delay_interval) < now:
          # No device has been online (but was before) for period longer than offline_delay_interval
          self._change_plug_status(False) # Turn off
          latest_online_time = None

        if not any_ips_online and any_ips_online_now:
          self._change_plug_status(True) # Turn on

        any_ips_online = any_ips_online_now
        time.sleep(refresh_interval_seconds);
      except KeyboardInterrupt:
        # Graceful exit by Ctrl + C
        sys.exit()

def main():
  TapoController().run()

if __name__ == '__main__':
  main()

sys.exit()