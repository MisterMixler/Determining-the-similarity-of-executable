import argparse
import os
import networkx
import shutil 

script_py = ".\\graphmaker\\cfg_gen.py" # Название скрипта сюда
graph_dir = "./graphs"
list_name_files = []
results = {}
graphs = {}


def ParseFromFile(dir):
    file_dictionary = {} #rename
    end = "END"
    file_name = ""
    #файл, в котором содержатся все функции исполняемых файлов
    file_name = "./func_info.txt"
    
    with open(file_name) as file:
        for line in file:
            line = line[:len(line)-1] #Убрали \n
            if "exe" in line:
                file_dictionary[line] = []
                file_name = line
                list_name_files.append(file_name)
                continue
            elif end in line:
                continue
            else:
                # 2
                count_func = int(line)# количество функций

                
                #-------------------------------------------
                file_dictionary[file_name].append([])
                for c in range(count_func): 
                    line_ = file.readline()
                    line_ = line_[line_.find("=")+1:len(line_)-1]
                    operations_arr = [s for s in line_.split(",")] #массив инструкций функции
                    file_dictionary[file_name][0].append([])
                    file_dictionary[file_name][0][c] = {}
                    for operation in operations_arr:
                        func_, count_ = operation.split("*")
                        file_dictionary[file_name][0][c][func_] = int(count_)
                #-------------------------------------------

                for _ in range(2):
                    line_ = file.readline()
                    line_ = line_[line_.find("=")+1:len(line_)-1]
                    file_dictionary[file_name].append([s for s in line_.split(",")])
    return file_dictionary


def AnalizeFiles(dir):
    file_dictionary = ParseFromFile(dir)

    main_list = file_dictionary[list_name_files[0]]#будем сравнивать первый файл со всеми остальными

    for elem in main_list[1]:
        results[str(elem)] = [[], [],]#инструкции для каждой функции.

    for i in range(1, len(list_name_files)):
        CompareFiles(main_list, file_dictionary[list_name_files[i]], i)


def CompareFiles(first_func_list, second_func_list, i):
    status_instr, first_file_index, second_file_index = 0, 0, 0
    for j in range(len(first_func_list[0])):
        for k in range(len(second_func_list[0])):
            count_elems = len(set(first_func_list[0][j] | second_func_list[0][k]))
            sum_percent = 0
            for inst_in_first, inst_in_main_count in first_func_list[0][j].items():
                if inst_in_first in second_func_list[0][k]:
                    value_other = int(second_func_list[0][k][inst_in_first])
                    value_main = int(inst_in_main_count)
                    if value_main == value_other:
                        percent_ = 100
                    elif value_main > value_other:
                        percent_ = (value_other/value_main) * 100
                    else:
                        percent_ = (value_main/value_other) * 100
                    #обработка ошибок
                    if percent_ > 100:
                        percent_ = 0

                    sum_percent += percent_
            main_percent = (sum_percent / count_elems)#Получаем проценты в целом
            if main_percent > status_instr:
                status_instr = main_percent
                first_file_index = j
                second_file_index = k 

        if status_instr > 0:
            sum_main =  int(first_func_list[2][first_file_index]) 
            sum_other = int(second_func_list[2][second_file_index])
            if sum_main == sum_other:
                per = 100
            elif sum_main > sum_other:
                per = (sum_other/sum_main) * 100
            else:
                per = (sum_main/sum_other) * 100
            if per > 100:
                per = 0

            #записываем насколько похожи функции
            results[str(first_func_list[1][j])][0].append([per, status_instr, 0])
            results[str(first_func_list[1][j])][1].append([first_func_list[1][first_file_index], list_name_files[i], second_func_list[1][second_file_index]])
        else:
            results[str(first_func_list[1][j])][0].append([0, 0, 0])
            results[str(first_func_list[1][j])][1].append([first_func_list[1][first_file_index], None, None])
        status_instr = 0


def ParseGraph():
    list_dirs = None
    list_files = []

    flag = 0
    for root, dirs, files in os.walk(graph_dir):  
        if flag == 0:
            list_dirs = dirs
            flag = 1
        else:
            list_files.append(files)

     
    for ind, dir_ in enumerate(list_dirs):
        graphs[dir_] = {}
        for file in list_files[ind]:
            graphs[dir_][file] = []
            f = open( f'./graphs/{dir_}/{file}', 'r')
            for line in f:
                index = line.find('->')
                if index != -1:
                    left_part = int(line[2:index - 1])
                    right_part = int(line[index + 4:])
                    graphs[dir_][file].append([right_part, left_part])
            f.close()


def GraphAnalyze():
    graph1 = networkx.Graph()
    graph2 = networkx.Graph()
    for key, value in results.items():
        for i in range(len(value[0])):
            ea_s = value[1][i]
            percent = 0
            if len(graphs[(list_name_files[0])[:-4]][(ea_s[0])[2:] + '.txt']) != 0 and len(graphs[(ea_s[1])[:-4]][(ea_s[2])[2:] + '.txt']) != 0:
                for elems in graphs[(list_name_files[0])[:-4]][(ea_s[0])[2:] + '.txt']:
                    graph1.add_edge(int(elems[0]), int(elems[1]))

                for elems in graphs[(ea_s[1])[:-4]][(ea_s[2])[2:] + '.txt']:
                    graph2.add_edge(int(elems[0]), int(elems[1]))
                #что-то вроде аналога расстоянию Левенштейна для строк
                cost = networkx.graph_edit_distance(graph1, graph2, timeout=3)

                if cost is None:
                    percent = 0
                elif cost == 0:
                    percent = 100
                elif cost < 10:
                    percent = 80
                elif cost < 30:
                    percent = 60
                elif cost < 50:
                    percent = 40
                elif cost < 80:
                    percent = 20
                else:
                    percent = 0

                graph1.clear()
                graph2.clear()
            else:
                percent = 100

            tmp = value[0][i]
            similarity = (tmp[0] + tmp[1] + percent) / 3
            value[0][i][2] = similarity



def PrintResult():
    first_space = len(f'{list_name_files[0]}')-1
    second_space = len(f'{list_name_files[1]}')-1
    print("_____________________________________________________")
    print(f"|Func in {list_name_files[0]} |Func in {list_name_files[1]} |Similarity |")
    for key, value in results.items():
        for i in range(len(value[0])):
            print("-----------------------------------------------------")
            tmp = value[1][i]
            third_space = 8 - len(f"{value[0][i][2]:.2f}")
            print(f'|{tmp[0]}'," "*first_space, f'|{tmp[2]}'," "*second_space,
                  f'|{value[0][i][2]:.2f}%', " "* third_space,"|") 
    print("-----------------------------------------------------")      


def main():
    global script_py
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-f', '--folder', required=True, help='folder')
    dir = parser.parse_args().folder

    # if(os.path.exists(graph_dir)):
    #     print("Всё приходится за ними прибирать...\nУдаление папки 'graphs'")
    #     try:
    #         shutil.rmtree(graph_dir)
    #     except OSError as e:
    #         print("Error: %s : %s" % (graph_dir, e.strerror))

    # if(os.path.exists("./compare/Ponce.cfg")):
    #     os.remove("./compare/Ponce.cfg")

    # os.mkdir(graph_dir)
    
    # os.system(f'python idahunt.py --inputdir .\\{dir} --analyse --filter "filters\\names.py -a 32 -v"')
    # os.system(f'python idahunt.py --inputdir .\\{dir} --filter "filters\\names.py -a 32 -v" --scripts {script_py}')
    
    AnalizeFiles(dir)
    ParseGraph()
    GraphAnalyze()
    PrintResult()


if __name__ == "__main__":
    main()


