# Fintra
A flask based interactive web application that informs users on the different types of investments, advises users on what investments best suit their preferences and tracks a user’s current investments

# Download and set-up

*** The following code snippets are for Windows ***

## Step 1:

Clone the Fintra repository onto your system. 

Navigate to an empty directory and open a terminal, then paste the following code:

git clone https://github.com/ndungu-kr/fintra.git

## Step 2:

In the same directory as the main.py file, create a virtual environment using the command:

py -m venv .venv

Activate your virtual environment if necessary using:

.venv\bin\Activate.bat

## Step 3:

You will now need to install the packages required for the application to run, use the following command:

python -m pip install -r requirements.txt

Upgrade your pip if need be using:

py -m pip install --upgrade pip

## Step 4:

Create a .env file in the same directory with the following details:

DB_SECRET_KEY=SECRET@123
cmc_api_key=<cmc_key_here>
oer_api_key=<oer_key_here>

The DB_SECRET_KEY can be anything.

## Step 5:

You will now need to get your personal API keys from Coin Market Cap and Open exchange rates.

### Coin Market Cap API

Sign up to coin market cap for devs by following this link: https://coinmarketcap.com/api/

Enter your credentials and select the basic (free) plan.

On your Overview page generate and copy your api key.

In your .env file replace <cmc_key_here> with your API key.

### Open Exchange Rates API

Sign up to open exchange rates by following this link: https://openexchangerates.org/signup/free

Fill in your credentials and sign up.

Navigate to App IDs and Generate New App ID.

Copy this key and replace <oer_key_here> with your key in your .env file.

## Step 6:

Run main.py and enjoy your free portfolio tracker!

# Troubleshooting

## Not found url error while importing stocks

If you are getting the following error:

Error retrieving stock info for <stock_ticker>: 404 Client Error: Not Found for url

Where <stock_ticker> is a stock code/ticker you should try updating your yfinance package.

While in your virtual environment, use the command:

pip install yfinance --upgrade --no-cache-dir

This command updates your yfinance package.

This works most of the time unless there is a problem with yfinance, if so please feel free to send me a messgae so that I can investigate.
