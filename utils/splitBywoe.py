# -*- coding: utf-8 -*-
from .simpleMethods import *
import numpy as np
import copy
import math

class splitBywoe(simpleMethods):
    def __init__(self,x,y):
        simpleMethods.__init__(self,x) 
        self.y = y
        self.cut_range = []
            
    def fit(self, bad=1,trend='up',num_split=None, minwoe=None):
        '''
        :param bad: 坏样本标记，默认label=1为坏样本
        :param trend: 趋势参数，up为woe递增，down为woe递减，默认为None，不考虑趋势，取woe最大的切分点
        :param num_split: 最大切割点数,不包含最大最小值
        :param minwoe: 最小分裂所需woe
        :return: numpy array -- 切割点数组
        '''
        self.value = np.array(self.y)
        self.allbad = len(self.value[self.value==bad])  # 好样本总数
        self.allgood = len(self.value)-self.allbad      # 坏样本总数

        n = 20 if len(self.x) >= 10 else len(self.x)
        self.equalSize(n)
        candidate = []
        for r in self.range_dict:
            candidate.append(r[0])
            candidate.append(r[1])
        self.candidate = sorted(list(set(candidate)))
        cut = self.__find_cut(list(range(len(self.candidate))), bad=bad, trend=trend)
        self.cut_range = [cut]
        #self.cut_range = self.find_cut(bad=bad,trend=trend)  # 第一个切割点

        while True:
            cut_list = self.find_cut(cut_list=self.cut_range,bad=bad,trend=trend,minwoe=minwoe)
            if len(cut_list)>0:
                for c in cut_list:
                    self.cut_range.append(c)
                    self.cut_range = sorted(list(set(self.cut_range)))
            else:
                break

            if num_split:
                if len(set(self.cut_range)) >= num_split:
                    break

        self.cut_range.append(self.candidate[0])
        self.cut_range.append(self.candidate[-1])
        self.bins = np.array(sorted(list(set(self.cut_range))))
        
    
    def find_cut(self,cut_list=[],bad=1,trend='up',minwoe=None):
        '''
        基于最大woe分裂切割
        :param cut_list: 已分裂的结点
        :param bad: 坏样本标记，默认label=1为坏样本
        :param trend: 趋势参数，up为woe递增，down为woe递减，默认为None，不考虑趋势，取woe最大的切分点
        :param minwoe: 最小分裂所需woe
        :return: 新的一个最大切割点
        '''
        cuts = []
        if cut_list == []:
            return []
        else:
            candidate = []
            point_ind = []
            for i,c in enumerate(self.candidate):
                if c in cut_list:
                    point_ind.append(i)
                else:
                    candidate.append(i)
            cut = self.__find_cut(candidate, point_ind, bad=bad, trend=trend, minwoe=minwoe)

            if cut not in self.cut_range and cut!= None:
                cuts.append(cut)
        return cuts

    def __find_cut(self,candidate_ind,point_ind=[],bad=1,trend='up',minwoe=0):
        result_cut = None
        result_woe = None
        if not minwoe:
            minwoe=0
        pidx = 0
        candidate_pair = []
        for i in candidate_ind:
            if i == len(self.candidate)-1:
                endv = self.candidate[-1]+1
            else:
                endv = self.candidate[-1]
            if i!=0 and i!=len(self.candidate)-1:
                if point_ind == []:
                    candidate_pair.append((self.candidate[0],self.candidate[i],endv))
                else:
                    if self.candidate[i]<point_ind[pidx]:
                        candidate_pair.append((self.candidate[0], self.candidate[i], self.candidate[point_ind[pidx]]))
                    elif self.candidate[i]>point_ind[pidx]:
                        if pidx != len(point_ind)-1:
                            pidx+=1
                        candidate_pair.append((point_ind[pidx], self.candidate[i], endv))

        compare_woe = {}
        for i in range(len(candidate_pair)):
            x_up = self.x[(self.x<candidate_pair[i][1]) & (self.x>=candidate_pair[i][0])]
            v_up = self.value[(self.x<candidate_pair[i][1]) & (self.x>=candidate_pair[i][0])]
            x_down = self.x[(self.x<candidate_pair[i][2]) & (self.x>=candidate_pair[i][1])]
            v_down = self.value[(self.x<candidate_pair[i][2]) & (self.x>=candidate_pair[i][1])]


            woe_up = self._cal_woe(v_up,bad=bad)
            woe_down = self._cal_woe(v_down, bad=bad)
            if trend == 'up':
                woe_sub = woe_up - woe_down
            elif trend == 'down':
                woe_sub = woe_down - woe_up
            else:
                woe_sub = abs(woe_down - woe_up)
            if woe_sub-minwoe>0:
                compare_woe[candidate_pair[i][1]] = woe_sub

        for c in compare_woe:
            if not result_woe:
                result_woe = woe_sub
                result_cut = c
            elif woe_sub > result_woe and c not in self.cut_range:
                result_woe = woe_sub
                result_cut = c
        #print(candidate_pair)
        #print(self.candidate)
        #print(candidate_ind,point_ind, result_cut, result_woe)
        return result_cut