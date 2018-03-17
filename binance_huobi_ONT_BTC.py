from binance import Binance
from huobi import Huobi
import time
import json

binanceRestUrl = 'www.binance.com'

huobi_coin_name = 'ontbtc'
binance_coin_name = 'ONTBTC'

huobi_btc_name = 'btc'
binance_btc_name = 'BTC'
huobi_ont_name = 'ont'
binance_ont_name = 'ONT'

#设置一次买卖数量
num_per_trade = 50
#获取深度数据个数
binance_depth_size = 5
#最大交易次数
trade_time = 150
#设置卖出/买入比
ratio = 0.98
#设置利润
factor = 1.01
count = 0
# 终止程序的退出码
exit_code = 2
# 刷新时间
refreshTime = 1
# 操作等待时间
wait_time = 0.2
#设置查看的深度
depth_size = 5
# 设置btc的账户最小值
min_btc = 0.1

binance_instance = Binance()
huobi_instance = Huobi()

time.sleep(15)
while(trade_time):
	# 查询账户余额是否足够交易
	binance_btc_balance = binance_instance.balance(binance_btc_name)
	huobi_btc_balance = huobi_instance.balance(huobi_btc_name)
	binance_ont_balance = binance_instance.balance(binance_ont_name)
	huobi_ont_balance = huobi_instance.balance(huobi_ont_name)

	if float(binance_btc_balance) < min_btc or float(huobi_btc_balance) < min_btc:
		print("btc low!")
		time.sleep(60)
		continue

	if float(binance_ont_balance) <= 2*num_per_trade or float(huobi_ont_balance) <= 2*num_per_trade:
		print("ONT low!")
		time.sleep(60)
		continue

	count = count + 1
	huobi_ticker_data = huobi_instance.ticker(huobi_coin_name)
	huobi_depth_data = huobi_instance.depth(huobi_coin_name, 'step0')

	binance_ticker_data = binance_instance.ticker(binance_coin_name)
	binance_depth_data = binance_instance.depth(binance_coin_name, depth_size)

	huobi_sell = float(huobi_ticker_data['tick']['ask'][0])
	huobi_buy = float(huobi_ticker_data['tick']['bid'][0])
	binance_sell = float(binance_ticker_data['askPrice'])
	binance_buy = float(binance_ticker_data['bidPrice'])

	huobi_depth_buy = huobi_depth_data['tick']['bids'][:5]
	huobi_depth_sell = huobi_depth_data['tick']['asks'][:5]

	binance_depth_sell = binance_depth_data['asks']
	binance_depth_buy = binance_depth_data['bids']
	print('-----------------------------------------')
	print('num：' + str(count))
	print('币种对：' + binance_coin_name)
	print('binance_buy / huobi_sell = ' + str(binance_buy / huobi_sell))
	print('huobi_buy / binance_sell = ' + str(huobi_buy / binance_sell))
	print('trade time = ' + str(trade_time))
	#binance -> huobi
	binance_huobi_flag = 0
	for i in huobi_depth_buy:
		for j in binance_depth_sell:
			j[1] = float(j[1])
			j[0] = float(j[0])
			temp_factor = i[0] / j[0]
			if temp_factor>=factor and i[1]>=num_per_trade and j[1] >= num_per_trade:
				print('great factor = ' + str(temp_factor))
				binance_huobi_flag = 1
				we_sell_price = i[0]
				we_buy_price = j[0]
				break
		if binance_huobi_flag:			
			huobi_sell_data = huobi_instance.trade(huobi_coin_name, str(we_sell_price), num_per_trade*ratio, 'sell-limit')
			if 'err-code' in huobi_sell_data.keys():
				print(huobi_sell_data['err-code'])
				exit(exit_code)
			# 判断是否完全成交
			time.sleep(wait_time)
			huobi_sell_order_id = huobi_sell_data['data']
			huobi_sell_order_data = huobi_instance.get_order_by_id(huobi_sell_order_id)
			huobi_selled_amount = float(huobi_sell_order_data['data']['field-amount'])
			if huobi_selled_amount < 1.5:
				cancel_result = huobi_instance.cancel_order_by_id(huobi_sell_order_id)
				time.sleep(wait_time)
				huobi_cancel_order = huobi_instance.get_order_by_id(huobi_sell_order_id)
				if (huobi_cancel_order['data']['state'] == 'filled'):
					print('Cancel failed')
					binance_buy_data = binance_instance.trade(binance_coin_name, 'BUY', num_per_trade, str(we_buy_price))
				else:
					print('Cancel successfully')
					break
			elif huobi_selled_amount < num_per_trade*ratio-0.2:
				cancel_result = huobi_instance.cancel_order_by_id(huobi_sell_order_id)
				temp_num = int(huobi_selled_amount)
				binance_buy_data = binance_instance.trade(binance_coin_name, 'BUY', temp_num, str(we_buy_price))
			else:
				binance_buy_data = binance_instance.trade(binance_coin_name, 'BUY', num_per_trade, str(we_buy_price))
			if 'code' in binance_buy_data.keys():
				print('binance error!')
				exit(exit_code)

			print("huobi sell order = " + str(huobi_sell_data))
			print('binance buy order = ' + str(binance_buy_data))
			print('=========binance --> huobi=========')
			trade_time = trade_time - 1
			break

	if binance_huobi_flag:
		continue

	#huobi -> binance
	huobi_binance_flag = 0
	for i in binance_depth_buy:
		for j in huobi_depth_sell:
			i[1] = float(i[1])
			i[0] = float(i[0])
			temp_factor = i[0] / j[0]
			if temp_factor>=factor and i[1]>=num_per_trade and j[1]>=num_per_trade:
				print('great factor = ' + str(temp_factor))
				huobi_binance_flag = 1
				we_sell_price = i[0]
				we_buy_price = j[0]
				break
		if huobi_binance_flag:
			huobi_buy_data = huobi_instance.trade(huobi_coin_name, str(we_buy_price), num_per_trade, 'buy-limit')
			if 'err-code' in huobi_buy_data.keys():
				print(huobi_buy_data['err-code'])
				exit(exit_code)
			# 判断是否完全成交
			time.sleep(wait_time)
			huobi_buy_order_id = huobi_buy_data['data']
			huobi_buy_order_data = huobi_instance.get_order_by_id(huobi_buy_order_id)
			huobi_buyed_amount = float(huobi_buy_order_data['data']['field-amount'])
			if huobi_buyed_amount < 1.5:
				cancel_result = huobi_instance.cancel_order_by_id(huobi_buy_order_id)
				time.sleep(wait_time)
				huobi_cancel_order = huobi_instance.get_order_by_id(huobi_buy_order_id)
				if (huobi_cancel_order['data']['state'] == 'filled'):
					print('Cancel failed')
					binance_sell_data = binance_instance.trade(binance_coin_name, 'SELL', int(num_per_trade*ratio), str(we_sell_price))
				else:
					print('Cancel successfully')
					break
			elif huobi_buyed_amount < num_per_trade:
				huobi_instance.cancel_order_by_id(huobi_buy_order_id)
				temp_num = huobi_buyed_amount
				binance_sell_data = binance_instance.trade(binance_coin_name, 'SELL', int(temp_num*ratio), str(we_sell_price))
			else:
				binance_sell_data = binance_instance.trade(binance_coin_name, 'SELL', int(num_per_trade*ratio), str(we_sell_price))
			if 'code' in binance_sell_data.keys():
				print('binance error!')
				exit(exit_code)

			print("huobi buy order = " + str(huobi_buy_data))
			print('binance sell order = ' + str(binance_sell_data))
			print('=========huobi --> binance=========')
			trade_time = trade_time - 1
			break
	time.sleep(refreshTime)

exit(exit_code)