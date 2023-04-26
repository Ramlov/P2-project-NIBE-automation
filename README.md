# P2-project


The automatic heat pump controller is a project that is designed to regulate the temperature in a home by taking into account the cost of electricity. The system is built on a Raspberry Pi, which is used to monitor power usage. This information is then used by a Python script to collect energy prices from an API and calculate the optimal time for the heat pump to run based on the current electricity prices.

The NIBE uplink API is used to control the heat pump. A Python program has been written to interact with the API, which allows the heat pump to be turned on and off automatically based on the calculated optimal run time. This means that the system will automatically adjust the temperature of the home based on the current electricity prices, which can lead to significant cost savings for the homeowner.

Overall, this system is a complex integration of hardware and software that leverages advanced algorithms and APIs to optimize the heat pump's energy consumption in response to fluctuating energy prices. By using sophisticated techniques to calculate the optimal run time, the system can reduce energy costs and improve home comfort, making it a valuable addition to any energy-efficient home.




#File structure#
```
main
├─ .gitignore
├─ NIBE_API
│  ├─ .DS_Store
│  ├─ .NIBE_Uplink_API_Token_GET.json
│  ├─ example_data.txt
│  ├─ get_data.py
│  ├─ get_parameters_for_categories_for_systems.py
│  ├─ put_data.py
│  └─ requirements.txt
├─ NIBE_Automation
│  ├─ NIBE_Uplink_API_Token_PUT.json
│  ├─ config.json
│  ├─ energy_temp_data.py
│  ├─ main.py
│  ├─ push_data.py
│  ├─ relative_data.py
│  └─ rename_file.py
├─ README.md
├─ RPi
│  ├─ README.md
│  ├─ config.json
│  ├─ main.py
│  ├─ network_checker.py
│  ├─ price.py
│  ├─ pulse_detector.py
│  └─ requirements.txt
├─ testing
│  ├─ collectdata.py
│  └─ config.json
├─ webpage2
│  ├─ contact_us
│  │  ├─ index.html
│  │  └─ style.css
│  ├─ energy_consumption
│  │  ├─ Line-Graph.png
│  │  ├─ index.html
│  │  └─ style.css
│  ├─ energy_prices
│  │  ├─ index.html
│  │  └─ style.css
│  ├─ heating_schedule
│  │  ├─ heatingschedule.png
│  │  ├─ index.html
│  │  └─ style.css
│  ├─ index.html
│  ├─ savings
│  │  ├─ index.html
│  │  └─ style.css
│  ├─ settings
│  │  ├─ index.html
│  │  └─ style.css
│  └─ style.css
└─ website
   ├─ .NIBE_Uplink_API_Token_GET.json
   ├─ .NIBE_Uplink_API_Token_PUT.json
   ├─ __pycache__
   │  └─ helper_class.cpython-310.pyc
   ├─ app.py
   ├─ config.json
   ├─ helper_class.py
   ├─ request_token.py
   ├─ script_update_zero_price_thing.py
   ├─ static
   │  ├─ script.js
   │  └─ styles
   │     └─ style.css
   └─ templates
      ├─ index.html
      ├─ oauth2callback
      │  └─ index.php
      ├─ settings
      │  └─ settings.html
      └─ usage
         └─ chart.html
```
