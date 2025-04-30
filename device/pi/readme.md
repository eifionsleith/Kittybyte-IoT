## SETUP
- Transfer src to the pi `rsync -avz src pi@ipaddr:Kittybyte-Pi`
    - mkdir via ssh first if needed
- pip3 install pydantic schedule
- Update hardcoded values inside `main.py` to reflect your environment
    - mqtt host, mqtt port, mqtt token, arduino port if necessary
    - This is not ideal, needs to be moved to a configuration file
- Run `main.py` with python3 `python3 ~/Kittybyte-Pi/src/main.py`
- CTRL+C to stop

## TODOs
- Move hardcoded variables to a configuration file, using ConfigHandler
- Implement logic for dispensing - take distance reading, move motor X turns, take another reading, report success
- Implement logic for AI detection unlocking dispensing
- Implement backend logging for feeding events, inc. video or image(s)
- Provisioning logic, stretch goal

