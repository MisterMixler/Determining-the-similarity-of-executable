import os
import os.path

import idaapi
import idc 
import idautils
import ida_name
import ida_funcs
import ida_ua
from cfg_utils import *
import shutil

instr_in_funcitons = []
function_ea = []


def WriteStatistic():
	result = ''
	file, mode = None, 'w'
	if os.path.isfile('./../func_info.txt'):
		mode = 'a'
	file = open('./../func_info.txt', mode)
	#запись имени файла 
	file.write(idaapi.get_input_file_path().split('\\')[-1] + '\n')

	#запись инструкций функций
	i = 1
	for dict_ in instr_in_funcitons:
		result += f'funct{i} count='
		number = 1
		for instr, count in dict_.items():
			if number == len(dict_):
				result += f'{instr}*{count}\n'
			else:
				result += f'{instr}*{count},'
			number += 1
		i += 1

	result = str(len(instr_in_funcitons)) + '\n' + result
	file.write(result + 'address=')

	number = 1
	#записываем адресса функций
	for index, elem in enumerate(function_ea):
		if number == len(instr_in_funcitons):
			file.write(f'{elem[0]}\n')
		else:
			file.write(f'{elem[0]},')
		number += 1

	file.write('sum=')

	number = 1
	for index, elem in enumerate(function_ea):
		if number == len(instr_in_funcitons):
			file.write(f'{elem[1]}\n')
		else:
			file.write(f'{elem[1]},')
		number += 1

	file.write('END\n')
	file.close()


def GetStatistics(func):
	breakpoint()
	sum_bytes = 0
	#here we creating a list of addresses in the order they appear in the disassembly listing 
	list_instr_addrs = [instr_ea for instr_ea in idautils.Heads(func.start_ea, func.end_ea)]

	instr_dict = {}
	
	for instr_ea in list_instr_addrs:
		sum_bytes += idc.get_item_size(instr_ea)
		instr_name = ida_ua.ua_mnem(instr_ea)

		if instr_name in instr_dict:
			instr_dict[instr_name] += 1
		else:
			instr_dict[instr_name] = 1
			
	func_ea_and_instr_sum = [hex(func.start_ea), sum_bytes]
	function_ea.append(tuple(func_ea_and_instr_sum))
	instr_in_funcitons.append(instr_dict)


def main():
	#get all functions in the input binary
	breakpoint()
	func_list = [func for func in idautils.Functions()]
	
	#takes the name of file (after will create a direcotory for graph named like that)
	pathCFG = (idaapi.get_input_file_path().split('\\')[-1])[:-3]

	if(os.path.exists('./../graphs/' + pathCFG)):
		shutil.rmtree('./../graphs/' + pathCFG)

	os.mkdir('./../graphs/' + pathCFG)

	for beg_of_function in func_list:
		GetStatistics(ida_funcs.get_func(beg_of_function))

		#gets our graph
		function_nodes = getNodes(ida_funcs.get_func(beg_of_function))
		function_edges = getEdges(function_nodes)
		#creating digraph
		graph = Digraph(nodes=function_nodes, edges=function_edges)
		graph.generateDDList()

		dotFileName = './../graphs/' + pathCFG + '/' + str(hex(beg_of_function)[2:]) + '.txt'
		
		with open(dotFileName, 'w') as dotFile:
			dotFile.write(str(graph))
	WriteStatistic()


if __name__ == '__main__':
	main()
	print("Ended")


if "DO_EXIT" in os.environ:
    idc.qexit(1)