# fxcmBot
A trading bot for FXCM broker platform

## How to install
### Install miniconda
- Go to https://conda.io/en/latest/miniconda.html
- Install miniconda for Python 3.8
### Create a conda environment
- `conda create -n fxcm python`
- `conda activate fxcm`
### Install all dependencies
- `pip install fxcmpy`
- `pip install socketio-client`
- `pip install matplotlib`
- `pip install configparser`
- Install all other dependencies that I may have forget

## How to use
### Start bot
#### Production mode
`python3 bot.py [config file]` with config files in `config` folder (`fxcm.cfg` is not a bot-formated config file).

#### Development mode
`python3 botDev.py [config file]` with config files in `config` folder (`fxcm.cfg` is not a bot-formated config file).
The dev mode enable you to modify and restart the bot without waiting for fxcmpy to reconnect to the API (~20s each time).

### Config file
#### test_mode
Ether `true` for backtesting mode or `false` for realtime mode. 
#### stream_period
In millisecond, the time between each call to the algorithm with a new candle.
#### start_date
Start date for the backtesting mode
#### end_date
End date for the backtesting mode
