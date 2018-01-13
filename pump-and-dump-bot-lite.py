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

def get_status(pump_orderId):
	order = client.get_order( symbol=symbol_pump, orderId=pump_orderId)
	str_order = str(order)
	position_start = str_order.find('status') + 10
	position_end = str_order.find('\'',position_start)
	pump_order_status = str_order[position_start:position_end]
	return pump_order_status

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
	previousCoins = ['XLMBTC','OAXBTC','NAVBTC']
	previousOrderId = ['5279135','2705647','547266'] 

	if symbol_pump in previousCoins:				# if not new symbol, use index
		i = previousCoins.index(symbol_pump)
		if pump_orderId != previousOrderId[i]:		# new orderId must not be old
			return True
			print('yes')
		else:
			return False							# FAIL bc new = old
			print('no')
	else:
		return True			

from binance.client import Client
import time


secret_key = ''

api_key = ''

client = Client(api_key, secret_key)

PumpDump_coin = input('Enter Pump & Dump Coin: ')

start_time = time.time()

symbol_pump = PumpDump_coin.upper() + 'BTC'

rate = refreshRates()		# initial rate

sell_rate = rate * 1.2

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

standard_rate = get_standard_average()

order = client.order_market_buy( symbol = symbol_pump, quantity = qty)
print(order)


print("--- %s seconds ---" % (time.time() - start_time))