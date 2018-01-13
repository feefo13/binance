'''
https://github.com/ccxt/ccxt/issues/663
'''

def refreshRates():

	prices = str(client.get_all_tickers())
	position = prices.find(symbol_pump)
	prices_start = prices.find('0.',position)	# error if alt is worth more than 1 btc
	prices_end = prices_start + 10
	rate = float(prices[prices_start:prices_end])	# current alt coin rate
	return rate

def get_balance():
	balance = client.get_asset_balance(asset='BTC')
	str_balance = str(balance)
	position_start = str_balance.find('free') + 8
	position_end = str_balance.find('\'', position_start)
	bal = str_balance[position_start:position_end]

	return bal
	# balance = {'asset': 'BTC', 'free': '0.00002994', 'locked':'0.00000000'}

def get_standard_average():

	klines = client.get_historical_klines(symbol_pump, Client.KLINE_INTERVAL_30MINUTE, "2 hours ago UTC")
	str_kline = str(klines)

	position_start = str_kline.find('0.')
	position_end = position_start + 10
	low = float(str_kline[position_start:position_end])

	position_start = str_kline.find('0.',position_end)
	position_end = position_start + 10
	high = float(str_kline[position_start:position_end])

	avg1 = (low + high)/2

	position_end = str_kline.find('[',position_end)
	position_start = str_kline.find('0.',position_end)
	position_end = position_start + 10
	low = float(str_kline[position_start:position_end])

	position_start = str_kline.find('0.',position_end)
	position_end = position_start + 10
	high = float(str_kline[position_start:position_end])

	avg2 = (low + high)/2

	position_end = str_kline.find('[',position_end)
	position_start = str_kline.find('0.',position_end)
	position_end = position_start + 10
	low = float(str_kline[position_start:position_end])

	position_start = str_kline.find('0.',position_end)
	position_end = position_start + 10
	high = float(str_kline[position_start:position_end])

	avg3 = (low + high)/2

	position_end = str_kline.find('[',position_end)
	position_start = str_kline.find('0.',position_end)
	position_end = position_start + 10
	low = float(str_kline[position_start:position_end])

	position_start = str_kline.find('0.',position_end)
	position_end = position_start + 10
	high = float(str_kline[position_start:position_end])

	avg4 = (low + high)/2

	standard_rate = (avg1 + avg2 + avg3 + avg4)/4
	return standard_rate

# get orderID from last buy; empty means new & nonexistent 
def get_pump_orderId():

	orders = client.get_all_orders(symbol=symbol_pump)		
	str_orders = str(orders)
	str_orders2 = str_orders[-335:] # Each order is 335 characters
	position_start = str_orders2.find('orderId') + 10
	position_end = str_orders2.find(',', position_start)
	pump_orderId = str_orders2[position_start:position_end]
	return pump_orderId

def audit_OrderId(pump_orderId):

	if symbol_pump in previousCoins:				# if not new symbol, use index
		i = previousCoins.index(symbol_pump)
		if pump_orderId != previousOrderId[i]:		# new orderId must not be old
			return True
			print('yes')
		else:
			return False							# FAIL bc new = old
			print('no')
	else:
		return True									# new symbol = pass!

def get_status(pump_orderId):
	order = client.get_order( symbol=symbol_pump, orderId=pump_orderId)
	str_order = str(order)
	position_start = str_order.find('status') + 10
	position_end = str_order.find('\'',position_start)
	pump_order_status = str_order[position_start:position_end]
	return pump_order_status



from binance.client import Client
#from binance.enums import *

secret_key = ''
api_key = ''
client = Client(api_key, secret_key)

PumpDump_coin = input('Enter Pump & Dump Coin: ')
symbol_pump = PumpDump_coin.upper() + 'BTC'


rate = refreshRates()		#rate initially during pump

# define function to adjust in real-time? (hi = 1.5, med = 1.35, lo = 1.2)

sell_rate = rate * 1.2		# DJ knobs/buttons with midi signal (automated + guidance)

# load current btc balance; along with the past orderId for transactioned coins (nav,xlm,oax)
previousCoins = ['XLMBTC','OAXBTC','NAVBTC']
previousOrderId = ['5279135','2705647','547266'] 	#nav is now 749040

#balance =  0.00002994		# current btc
						
balance = get_balance()

wall = True					# filters out lot_size error invoking order (min qty not met)
while(wall):
	if float(balance) < 0.001:
		issue = input("There is not enough BTC in available funds")
	else:
		wall = False

qty = float(balance) / rate	# current btc balance / current rate of alt = (max) qty desired to buy in alt
qty = qty * 0.99			# to prevent overspending error
qty_rounded_down = float(format(qty, '.8f')) 

# use limit buy instead of market buy due to rapid price increase
# compare to average of 2 hours leading up to pump (before price) usually 100% increase
# depending on previous researched gain rate by x time; cancel order if joined late

standard_rate = get_standard_average()

order = client.order_market_buy( symbol = symbol_pump, quantity = qty)
print(order)

# depending on buy rate ( by JSON return )... sell_rate = rate * 1.2
# depending on qty bought... ?

# if this returns orderid, delete get_pump_orderId() and skip first 2 walls... go to check status

pump_orderId = get_pump_orderId()	

wall = True		# filters out empty order list
while(wall):
	if pump_orderId == '':
		pump_orderId = get_pump_orderId()
	else:
		wall = False

wall = True		# filters out previous orders
while(wall):
	if not audit_OrderId(pump_orderId):
		pump_orderId = get_pump_orderId()
	else:
		wall = False

# cant be empty or previous so = new & valid
	# test audit (should be infinite loop bc there exists no new pump buy orders)

# check status if filled then place sell limit order else... loop
wall = True      # filters out unfilled status response
while(wall):
	status = get_status(pump_orderId)
	if status == 'FILLED':
		wall = False

order = client.order_limit_sell(
    symbol=symbol_pump,
    quantity=qty,
    price=sell_rate)

print(order)


print(standard_rate)
print(rate)

# timestamp issue means adjust date/time to update internet time

'''

coin 	orderId
XLM 5279135
OAX 2705647
NAV	547266

order = client.create_order( symbol=symbol_pump, side=Client.SIDE_SELL, type=Client.ORDER_TYPE_MARKET, quantity=0.1)
~1.5s
{'side': 'SELL', 'price': '0.00000000', 'executedQty': '0.10000000', 'timeInForce': 'GTC', 'origQty': '0.10000000', 'clientOrderId': 'NnN42h2r8dy43VHNslNfBU', 'symbol': 'NAVBTC', 'status': 'FILLED', 'orderId': 749040, 'transactTime': 1515741329378, 'type': 'MARKET'}

take the pump_orderId 'orderId': 749040,

{'time': 1515741329378, 'side': 'SELL', 'stopPrice': '0.00000000', 'origQty': '0.10000000', 'orderId': 749040, 'icebergQty': '0.00000000', 'status': 'FILLED', 'price': '0.00000000', 'clientOrderId': 'NnN42h2r8dy43VHNslNfBU', 'timeInForce': 'GTC', 'isWorking': True, 'symbol': 'NAVBTC', 'executedQty': '0.10000000', 'type': 'MARKET'}



80 	XLM/BTC 	1 	XLM 	0.00000001 	BTC 	0.001 	

95 	NAV/BTC 	1 	NAV 	0.0000001 	BTC 	0.001

36 	OAX/BTC 	1 	OAX 	0.00000001 	BTC 	0.001

# withdraw 100 ETH
# check docs for assumptions around withdrawals
from binance.exceptions import BinanceAPIException, BinanceWithdrawException
try:
    result = client.withdraw(
        asset='ETH',
        address='<eth_address>',
        amount=100)
except BinanceAPIException as e:
    print(e)
except BinanceWithdrawException as e:
    print(e)
else:
    print("Success")

klines = client.get_historical_klines("NAVBTC", Client.KLINE_INTERVAL_30MINUTE, "2 hours ago UTC")

[[1515738600000, '0.00027380', '0.00028880', '0.00026900', '0.00028050', '48914.01000000', 1515740399999, '13.46834552', 520, '23666.00000000', '6.54861990', '0'],
					LOW,		HIGH		  WICK_LOW		WICK_HIGH
  [1515740400000, '0.00027650', '0.00028400', '0.00027450', '0.00028070', '26096.90000000', 1515742199999, '7.27846566', 427, '10583.91000000', '2.95231700', '0'],

  [1515742200000, '0.00028070', '0.00029200', '0.00028050', '0.00029200', '49142.01000000', 1515743999999, '14.04783433', 781, '22590.89000000', '6.47341252', '0'],

  [1515744000000, '0.00029050', '0.00029200', '0.00029050', '0.00029050', '254.73000000', 1515745799999, '0.07412872', 6, '17.15000000', '0.00500780', '0']]


'''

