import copy
import itertools
from math import inf

from numpy import minimum, argmin

count = 0

class Node:
    def __init__(self):
        self.tnode = 0
        self.dnode = 0
        self.before_drone = []
        self.after_drone = []

class Individual:
    def __init__(self):
        self.F_value = 0  # 目标函数（成本）
        self.X = []  # 解的集合
        self.complete = []  # 完整方案

    def create_one(self):
        one = Individual()
        return one

    def copy_one(self, parent):
        child = Individual()
        child.X = copy.deepcopy(parent.X)
        child.F_value = copy.deepcopy(parent.F_value)
        return child

    def assign_drone(self,idvi,disMatrix,alpha,kappa):

        N = []  #  存放每个节点的信息
        self.F_value = 0  # 目标函数（成本）
        self.X = []  # 解的集合
        self.complete = []

        idv_copy = copy.deepcopy(idvi)
        n = len(idv_copy)
        complete_n = disMatrix.shape[0] + 1
        # idv_copy[n-1] = n-1
        if idv_copy[n-1] == 0:
            idv_copy[n-1] = complete_n - 1
        Land = [0] * complete_n
        total_cost = 0  # 单独写成一个方法

        # 改成完整的数组大小
        T = [[inf] * complete_n for _ in range(complete_n)]  # 两点之间的距离
        M = [[-99] * complete_n for _ in range(complete_n)]  # 两点之间是否有无人机

        for i in range(0,len(idv_copy)-1):
            for j in range(i+1,len(idv_copy)):
                if j == i+1:  # 如果两个点相邻
                    if j == n-1 and idv_copy[j] == complete_n - 1:
                        T[i][j] = disMatrix[idv_copy[i]][0]
                        M[idv_copy[i]][idv_copy[j]] = -1
                    else:
                        T[i][j] = disMatrix[idv_copy[i]][idv_copy[j]]
                        M[idv_copy[i]][idv_copy[j]] = -1
                else:
                    if j == n-1 and idv_copy[j] == complete_n - 1:
                        for k in range(i + 1, j):  # 若两个点之间有其他节点
                            Tk1 = (disMatrix[idv_copy[i]][idv_copy[k]] + disMatrix[idv_copy[k]][0]) / alpha
                            if Tk1 <= kappa:
                                t1 = 0
                                t2 = 0

                                t1 = sum(disMatrix[idv_copy[l]][idv_copy[l + 1]] for l in range(i, k - 1))

                                t2 = sum(disMatrix[idv_copy[l]][idv_copy[l + 1]] for l in range(k + 1, j - 1)) + disMatrix[idv_copy[j - 1]][0]

                                Tk2 = t1 + t2 + (disMatrix[idv_copy[k - 1]][0] if k + 1 == n - 1 else disMatrix[idv_copy[k - 1]][idv_copy[k + 1]])

                                if Tk2 <= kappa:
                                    Tk = max(Tk1, Tk2)
                                    if Tk < T[i][j]:
                                        T[i][j] = Tk
                                        M[idv_copy[i]][idv_copy[j]] = idv_copy[k]
                                        Land[j] = 1
                    else:
                        for k in range(i + 1, j):  # 若两个点之间有其他节点
                            Tk1 = (disMatrix[idv_copy[i]][idv_copy[k]] + disMatrix[idv_copy[k]][idv_copy[j]]) / alpha
                            if Tk1 <= kappa:
                                t1 = 0
                                t2 = 0
                                for l in range(i, k - 1):
                                    t1 = t1 + disMatrix[idv_copy[l]][idv_copy[l + 1]]
                                for l in range(k + 1, j):
                                    t2 = t2 + disMatrix[idv_copy[l]][idv_copy[l + 1]]
                                Tk2 = t1 + t2 + disMatrix[idv_copy[k - 1]][idv_copy[k + 1]]
                                if Tk2 <= kappa:
                                    Tk = max(Tk1, Tk2)
                                    if Tk < T[i][j]:
                                        T[i][j] = Tk
                                        M[idv_copy[i]][idv_copy[j]] = idv_copy[k]
                                        Land[j] = 1

        V = [0] * n
        P = [-1] * n

        V[0] = 0  # 第一个节点处花费的时间成本为0
        for i in range(1,n):
            VV = []
            for k in range(0, i):
                vv = V[k] + T[k][i]
                VV.append(vv)
            V[i] = min(VV)
            P[i] = idv_copy[argmin(VV)]

        combined_nodes = []  # 卡车无人机都访问的节点
        current_idx = n-1  # 从最后一个节点反推方案
        current = idv_copy[current_idx]
        while current != -1:
            combined_nodes.insert(0,current)
            current_idx = idv_copy.index(current)
            current = P[current_idx]

        truck_route = []
        drone_only_nodes = []  # 无人机服务节点
        drone_route = []
        sorties = []  # 存储无人机架次
        drone_route.append(combined_nodes[0])

        for ii in range(0,len(combined_nodes)-1):
            j1 = combined_nodes[ii]
            j2 = combined_nodes[ii + 1]
            if M[j1][j2] != -1:
                if j2 == complete_n-1:
                    s = [drone_route[-1], M[j1][j2], 0]
                    drone_only_nodes.append(M[j1][j2])
                    drone_route.append(M[j1][j2])
                else:
                    s = [drone_route[-1], M[j1][j2], j2]
                    drone_only_nodes.append(M[j1][j2])
                    drone_route.append(M[j1][j2])

                sorties.append(s)
            if j2 == complete_n-1:
                drone_route.append(0)
            else:
                drone_route.append(j2)

        for value in drone_only_nodes:
            while value in idv_copy:
                idv_copy.remove(value)

        if idv_copy[-1] == complete_n-1:
            idv_copy[-1] = 0
        self.X.append(idvi)
        self.complete.append([idv_copy, sorties])

        # 不要第二层染色体
        # self.X.append([idv_copy, sorties])
        self.F_value = V[len(idvi)-1]
        return [self.X, self.F_value, self.complete]

    # def exact_partitioning2(self, V, tsp, depot, alpha):
    def exact_partitioning2(self,idvi,disMatrix,alpha,kappa):
        global count
        count += 1
        evaluate_time = count
        depot = 0
        T = {}
        M = {}
        D = {}
        truck = {}
        Dres = 0
        Mdrone = {}
        route = {}
        idv_copy = copy.deepcopy(idvi[:-1])
        n = len(idv_copy)

        for drone in range(1, n):
            for start in reversed(range(0, drone)):
                for end in range(drone + 1, n):
                    # 计算无人机成本
                    drone_cost = (disMatrix[idv_copy[start]][idv_copy[drone]] + disMatrix[idv_copy[drone]][end]) / alpha
                    # drone_cost = d_cost(V[tsp[start]], V[tsp[drone]], alpha) + d_cost(V[tsp[drone]], V[tsp[end]], alpha)
                    if start == drone - 1 and end == drone + 1:  # SUM(k − 1, k + 1, k)
                        truck[start, end, drone] = disMatrix[idv_copy[start]][idv_copy[end]]
                    if end > drone + 1 and start == drone - 1:
                        truck[start, end, drone] = disMatrix[idv_copy[end-1]][idv_copy[end]] + truck[start, end - 1, drone]
                    if end >= drone + 1 and start < drone - 1:
                        truck[start, end, drone] = disMatrix[idv_copy[start]][idv_copy[start + 1]] + truck[start + 1, end, drone]
                    T[start, drone, end] = max(drone_cost, truck[start, end, drone])

        for drone in reversed(range(2, n)):
            for start in reversed(range(1, drone)):
                for end in range(0, start):
                    drone_cost = (disMatrix[idv_copy[start]][idv_copy[drone]] + disMatrix[idv_copy[drone]][end]) / alpha
                    if end == 0:
                        if start == drone - 1 and drone == n - 1:
                            truck[start, end, drone] = disMatrix[idv_copy[start]][idv_copy[end]]
                        if start == drone - 1 and drone != n - 1:
                            truck[start, end, drone] = disMatrix[idv_copy[n-1]][idv_copy[0]] + truck[start, n - 1, drone]
                        if start < drone - 1:
                            truck[start, end, drone] = disMatrix[idv_copy[start]][idv_copy[start+1]] + truck[start + 1, end, drone]
                    else:
                        truck[start, end, drone] = disMatrix[idv_copy[end-1]][idv_copy[end]] + truck[start, end - 1, drone]
                    T[start, drone, end] = max(drone_cost, truck[start, end, drone])

        for drone in range(0, n - 2):
            for end in range(drone + 1, n - 1):
                for start in reversed(range(end + 1, n)):
                    drone_cost = (disMatrix[idv_copy[start]][idv_copy[drone]] + disMatrix[idv_copy[drone]][end]) / alpha
                    if start == n - 1:
                        if end == drone + 1:
                            if drone == 0:
                                truck[start, end, drone] = disMatrix[idv_copy[start]][idv_copy[end]]
                            else:
                                truck[start, end, drone] = disMatrix[idv_copy[start]][idv_copy[0]] + truck[0, end, drone]
                        else:
                            truck[start, end, drone] = disMatrix[idv_copy[end-1]][idv_copy[end]] + truck[start, end - 1, drone]
                    else:
                        truck[start, end, drone] = disMatrix[idv_copy[start]][idv_copy[start+1]] + truck[start + 1, end, drone]
                    T[start, drone, end] = max(drone_cost, truck[start, end, drone])

        for (i, j) in itertools.permutations(range(n), 2):
            M[i, j] = float('inf')
            if i < j:
                if i + 1 == j:
                    M[i, j] = disMatrix[idv_copy[i]][idv_copy[j]]
                for k in range(i + 1, j):
                    if M[i, j] > T[i, k, j]:
                        M[i, j] = T[i, k, j]
                        Mdrone[idv_copy[i], idv_copy[j]] = [idv_copy[k]]
            else:
                for k in range(i + 1, n):
                    if M[i, j] > T[i, k, j]:
                        M[i, j] = T[i, k, j]
                        Mdrone[idv_copy[i], idv_copy[j]] = [idv_copy[k]]
                for k in range(0, j):
                    if M[i, j] > T[i, k, j]:
                        M[i, j] = T[i, k, j]
                        Mdrone[idv_copy[i], idv_copy[j]] = [idv_copy[k]]
                M[n - 1, 0] = disMatrix[idv_copy[n-1]][idv_copy[0]]

        for i in range(idv_copy.index(depot) + 1, idv_copy.index(depot) + n + 1):
            D[depot, idv_copy[i % n]] = float('inf')
            Dres = float('inf')
            D[depot, depot] = 0
            route[depot, depot] = [[depot]]
            for j in range(idv_copy.index(depot), i):
                if j % n != i % n:
                    d = M[j % n, i % n] + D[depot, idv_copy[j % n]]
                    r = route[depot, idv_copy[j % n]] + [[idv_copy[j % n], idv_copy[i % n]]]
                    if i == idv_copy.index(depot) + n:
                        if Dres > d:
                            Dres = d
                            route[depot, depot] = r

                    else:
                        if D[depot, idv_copy[i % n]] > d:
                            D[depot, idv_copy[i % n]] = d
                            route[depot, idv_copy[i % n]] = r

        pathlen = len(route[depot, depot])
        path = []
        for i in range(pathlen - 1):
            path = path + route[depot, depot][i + 1]
            if (route[depot, depot][i + 1][0], route[depot, depot][i + 1][1]) in Mdrone:
                path = path + [Mdrone[route[depot, depot][i + 1][0], route[depot, depot][i + 1][1]]]
            else:
                path = path + [[]]

        label = {i: "truck" for i in idv_copy}
        for i in path:
            if type(i) == int:
                label[i] = "combined"
            else:
                if len(i) > 0:
                    label[i[0]] = "drone"

        dset = set()
        for i in range(len(path)):
            if type(path[i]) == list and len(path[i]) == 1:
                dset.add(path[i][0])
        solution = [label,dset]
        # return Dres, label, dset, evaluate_time
        return [idv_copy,Dres,solution]

    def optimize(self,idvi,f_value,disMatrix,alpha,kappa):
        cost = f_value
        truck_route = idvi[0].copy()
        drone_sortie = idvi[1].copy()
        for i in range(len(drone_sortie)-1):  # 遍历无人机架次
            if drone_sortie[i][2] == drone_sortie[i+1][0]:  # 两个架次相邻
                drone_cost1 = (disMatrix[drone_sortie[i][0]][drone_sortie[i][1]] + disMatrix[drone_sortie[i][1]][drone_sortie[i][2]])/alpha  # 第一个架次的时间
                drone_cost2 = (disMatrix[drone_sortie[i+1][0]][drone_sortie[i+1][1]] + disMatrix[drone_sortie[i+1][1]][drone_sortie[i+1][2]])/alpha  # 第二个架次的时间
                idx1 = truck_route.index(drone_sortie[i][0])
                idx2 = truck_route.index(drone_sortie[i][2])
                idx3 = truck_route.index(drone_sortie[i+1][0])
                idx4 = truck_route.index(drone_sortie[i+1][2])
                if idx4 == 0:
                    idx4 = len(truck_route) - 1
                truck_cost1 = 0
                truck_cost2 = 0
                for idx in range(idx1,idx2):
                    truck_cost1 += disMatrix[truck_route[idx]][truck_route[idx + 1]]
                for idx in range(idx3,idx4):
                    truck_cost2 += disMatrix[truck_route[idx]][truck_route[idx + 1]]
                operation_cost = max(drone_cost1, truck_cost1) + max(drone_cost2, truck_cost2)

                # 方案一，把第二个架次合并到第一个中
                cost1 = max((disMatrix[drone_sortie[i][0]][drone_sortie[i][1]] + disMatrix[drone_sortie[i][1]][drone_sortie[i+1][1]])/alpha, truck_cost1 + disMatrix[truck_route[idx2]][drone_sortie[i+1][1]])
                cost2 = truck_cost2 - disMatrix[truck_route[idx3]][truck_route[idx3+1]] + disMatrix[drone_sortie[i+1][1]][truck_route[idx3+1]]
                plan1_cost = cost1 + cost2

                # 方案二，把第一个架次合并到第二个中
                cost3 = truck_cost1 - disMatrix[truck_route[idx2-1]][truck_route[idx2]] + disMatrix[truck_route[idx2-1]][drone_sortie[i][1]]
                cost4 = max((disMatrix[drone_sortie[i][1]][drone_sortie[i+1][1]] + disMatrix[drone_sortie[i+1][1]][drone_sortie[i+1][2]])/alpha, truck_cost2 + disMatrix[drone_sortie[i][1]][truck_route[idx3]])
                plan2_cost = cost3 + cost4

                if plan1_cost < operation_cost and plan1_cost < plan2_cost:
                    # 用方案一代替原方案
                    truck_route.insert(idx3+1, drone_sortie[i+1][1])
                    drone_sortie[i + 1] = [drone_sortie[i][0], drone_sortie[i][1], drone_sortie[i + 1][1]]
                    drone_sortie[i] = [0, 0, 0]
                    cost = cost - operation_cost + plan1_cost
                if plan2_cost < operation_cost and plan2_cost < plan1_cost:
                    # 用方案二代替原方案
                    truck_route.insert(idx2, drone_sortie[i][1])
                    drone_sortie[i + 1] = [drone_sortie[i][1], drone_sortie[i + 1][1], drone_sortie[i + 1][2]]
                    drone_sortie[i] = [0, 0, 0]
                    # drone_sortie[i + 1] = [drone_sortie[i][1], drone_sortie[i + 1][1], drone_sortie[i + 1][2]]
                    cost = cost - operation_cost + plan2_cost

        drone_sortie = [x for x in drone_sortie if x != [0, 0, 0]]
        self.X = [truck_route, drone_sortie]
        self.F_value = cost
        return [self.X,self.F_value]

