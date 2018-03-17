from huobiServices.HuobiServices import *

class Huobi:
	def __init__(self):
		temp = get_accounts()
		self.accounts = temp['data'][0]['id']

	def ticker(self,symbol=''):
		return get_ticker(symbol)

	def depth(self,symbol,type):
		return get_depth(symbol, type)

	def trade(self,t_symbol,t_price,t_amount,t_type):
		return send_order(amount=t_amount,symbol=t_symbol,_type=t_type,price=t_price)

	def balance(self,coin_name):
		balancesData = get_balance()
		balancesData = balancesData['data']['list']
		for i in balancesData:
			if i['currency']==coin_name and i['type']=="trade":
				balanceData=i['balance']
				break
		return balanceData

	#通过订单id获取订单详情
	def get_order_by_id(self,order_id):
		return order_info(order_id)

	def cancel_order_by_id(self,order_id):
		return cancel_order(order_id)

	#获取huobi当前委托或历史委托订单信息
	def get_orders(self,coin_name,states,types):
		return orders_list(coin_name,states,types)

	#检查订单是否未成交
	def if_unfilled_order(self,order_id):
		return 0
