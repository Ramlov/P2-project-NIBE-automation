# Remote Power Meter

[Project Description]

## Requirements

- Python 3.x
- Raspberry Pi (for RPi.GPIO)
- MySQL server (for mysql-connector-python)
- Other dependencies listed in `requirements.txt`

## Installation

1. Clone the repository or download the project files.
2. Install the required dependencies by running the following command in your Python environment:

```bash
pip install -r requirements.txt
```

## Usage
Connect the pulse to the Raspberry Pi Using a GPIO configured in `config.json`
Run the main.py script to collect pulse data from a sensor and update the pulse count.
Run the updatetime.py script once every day or so through crontab to update the time.

## Configuration
Update the configuration settings in `config.json`

## File Descriptions
- `pulse_detector.py`: Collects pulse data from GPIO and updates the pulse count in a threaded manner.
- `price.py`: Collects energy price for the periode. Returns price
- `network_checker.py`: Uses sockets to send a packet to Google's address, and specifies the DNS server as 8.8.8.8 using sockets. Returns True or False depending on if there is a response.
- `main.py`: Implements asynchronous threads to detect pulses at the GPIO, while another thread is responsible for submitting data to a database.
