# P2-project


The automatic heat pump controller is a project that is designed to regulate the temperature in a home by taking into account the cost of electricity. The system is built on a Raspberry Pi, which is used to monitor power usage. This information is then used by a Python script to collect energy prices from an API and calculate the optimal time for the heat pump to run based on the current electricity prices.

The NIBE uplink API is used to control the heat pump. A Python program has been written to interact with the API, which allows the heat pump to be turned on and off automatically based on the calculated optimal run time. This means that the system will automatically adjust the temperature of the home based on the current electricity prices, which can lead to significant cost savings for the homeowner.

Overall, this system is a complex integration of hardware and software that leverages advanced algorithms and APIs to optimize the heat pump's energy consumption in response to fluctuating energy prices. By using sophisticated techniques to calculate the optimal run time, the system can reduce energy costs and improve home comfort, making it a valuable addition to any energy-efficient home.


# Media Convarage:
<a href="https://www.tv2nord.dk/aalborg/sparer-7000-paa-genialt-varmpepumpetrick">TV2 Nord article</a> <br>

<a href="https://ing.dk/artikel/podcast-ingenioer-halverer-varmeregningen-med-hjemmebygget-lager-til-varmepumpen">Ingeniøren - Podcast</a>

## File structure
```
📦 NIBE Automation
├─ .gitignore
├─ NIBE_API
│  ├─ .DS_Store
│  ├─ example_data.txt
│  ├─ get_data.py
│  ├─ get_parameters_for_categories_for_systems.py
│  ├─ put_data.py
│  ├─ request_token.py
│  └─ requirements.txt
├─ NIBE_Automation
│  ├─ config.json
│  ├─ data.csv
│  ├─ energy_price.py
│  ├─ main.py
│  ├─ push_data.py
│  └─ rename_file.py
├─ README.md
├─ RPi
│  ├─ README.md
│  ├─ config.json
│  ├─ main.py
│  ├─ network_checker.py
│  ├─ price.py
│  ├─ pulse_detector.py
│  ├─ requirements.txt
│  └─ updatetime.py
├─ testing
│  ├─ config.json
│  ├─ testdata.py
│  └─ usage.csv
└─ website
   ├─ .DS_Store
   ├─ app.py
   ├─ config.json
   ├─ helper_class.py
   ├─ latency.txt
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
