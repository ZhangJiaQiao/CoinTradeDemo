from binanceServices.client import Client

class Binance:
	def __init__(self):
		#填上用户的apikey和secretkey
		api_key = '' 
		api_secret = ''
		self.client = Client(api_key, api_secret)

	def ticker(self,symbol=''):
		return self.client.get_orderbook_ticker(symbol=symbol)

	def depth(self,symbol,size):
		return self.client.get_order_book(symbol=symbol,limit=size)

	def trade(self,t_symbol,t_side,t_quantity,t_price):
		return self.client.order_limit(recvWindow=60000,symbol=t_symbol,
				side=t_side,quantity=t_quantity,price=t_price)

	def test_trade(self,t_symbol,t_side,t_quantity,t_price):
		return self.client.create_test_order(symbol=t_symbol,side=t_side,quantity=t_quantity,
				price=t_price,type='LIMIT',timeInForce='GTC',recvWindow=60000)

	def balance(self,coin_name):
		data = self.client.get_account(recvWindow='60000')
		balancesData = data['balances']
		for i in balancesData:
			if i['asset']==coin_name:
				balanceData = i['free']
				break
		return balanceData