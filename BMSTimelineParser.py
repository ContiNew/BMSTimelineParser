import pandas as pd
import os  


class BMSTimelineParser:
    
    def __init__(self,filename:str, encode:str='utf-8'):
        self.bmsFile = open(filename, "rt", encoding=encode) # bms 파일 오픈 
        self.bmsFile.seek(0)
        curTxt = self.bmsFile.readline()
        while(not curTxt.startswith("#BPM")):
            curTxt = self.bmsFile.readline()
        self.BPM = int(curTxt.split(" ")[1]) # BPM 저장
        self.SPB = (1/(self.BPM/60)) # 1 박자당(4분 음표)소요 되는 시간 계산
        self.BPBar_default = 4 # 마디당 박자는 2번 채널을 쓰지 않았을 경우 4/4 이므로
        self.noteInfoList = []

        curTxt = self.bmsFile.readline()
        while(not curTxt.startswith("*---------------------- MAIN DATA FIELD")):
            curTxt = self.bmsFile.readline() #offset을 미룬다 
        
    
    def readOneBar(self):
        beatPerBar = self.findBeatPerBar() # 우선 마디당 박자를 구한다. 
        curTxt = self.bmsFile.readline() # 먼저 읽는다
        while(not curTxt.startswith("#") and not curTxt==""): # 레인 데이터를 찾을때 까지 readline
              curTxt = self.bmsFile.readline() 
        if(curTxt==""): return -1 # eof를 만나면 자동종료

        curBar = int(curTxt[1:4]) # 현재 탐색중인 마디 
        while(not curTxt.startswith("\n")): # 다음 마디로 넘어갈때까지 읽는다.(개행 넘어갈 때 까지)
            splittedTxt = curTxt.split(':') # : 를 기준으로 오브젝트 데이터를 나눈다.
            curLane = self.checkLaneNumber(int(splittedTxt[0][4:])) # 현재 탐색중인 채널 
            if(curLane==-1): #노트 이외의 정보는 수집하지 않는다. 
                curTxt = self.bmsFile.readline()
                continue
            notesInLane = []
            for i in range(0, len(splittedTxt[1][:-1]),2):# [:-1] 이용해서 개행문자는 입력 안받음
                notesInLane.append(splittedTxt[1][:-1][i:i+2]) # 레인 안에 노트를 길이가 2인 문자열 형태로 집어넣음
            self.addNoteInfo(curBar,curLane,notesInLane,beatPerBar) # 현재 마디, 현재 레인번호, 현재 레인의 노트리스트, 마디당 박자를 입력
            curTxt = self.bmsFile.readline() # 다음 라인으로
        return 0 # 정상 종료
    
    def readWholeBar(self): # 모든 마디를 다 읽어내는 함수
        while(self.readOneBar()==0):
            continue

    def extract_to_txt(self):
        sortedNoteInfoList = sorted(self.noteInfoList,key=lambda l:l[0]) #timestamp 순으로 오름차 정렬
        os.makedirs('note_txt', exist_ok=True)  
        f = open( "note_txt/noteinfo.txt", "+wt")
        f.write("timestamp, barNum, location, laneIdx, note\n")
        for noteInfo in sortedNoteInfoList:
            f.writelines(",".join(list(map(str,noteInfo))))
            f.write('\n')
        f.close()

    def extract_to_pandas(self)->pd.DataFrame:
        sortedNoteInfoList = sorted(self.noteInfoList,key=lambda l:l[0]) #timestamp 순으로 오름차 정렬
        dataframe = pd.DataFrame(sortedNoteInfoList,columns=("timestamp", "barNum", "location", "laneIdx", "note"))
        return dataframe
    
    def extract_to_csv(self):
        os.makedirs('note_csv', exist_ok=True)  
        self.extract_to_pandas().to_csv('note_csv/noteinfo.csv')     
                
    def findBeatPerBar(self): # 마디당 박자를 찾아주는 함수
        offset = self.bmsFile.tell()
        curTxt = self.bmsFile.readline() # 먼저 읽는다
        while(not curTxt.startswith("#") and not curTxt==""): # 레인 데이터를 찾을때 까지 readline
              curTxt = self.bmsFile.readline() 
        if(curTxt==""): return -1 # eof를 만나면 자동종료

        while(not curTxt.startswith("\n")): # 다음 마디로 넘어갈때까지 읽는다.(개행 넘어갈 때 까지)
            splittedTxt = curTxt.split(':') # : 를 기준으로 오브젝트 데이터를 나눈다.
            curLane = int(splittedTxt[0][4:6]) # 현재 탐색중인 채널 
            if(curLane == 2): # 마디 채널에 변동이 있을 경우 
                newBeatPerBar = float(splittedTxt[1])
                newBeatPerBar *= self.BPBar_default
                self.bmsFile.seek(offset) #읽기전 상태로 돌린다 
                return newBeatPerBar # 새로운 마디당 박자를 리턴
            curTxt = self.bmsFile.readline()
            
        self.bmsFile.seek(offset) #읽기전 상태로 돌린다 
        return self.BPBar_default # 아닌 경우 기본값을 리턴
    
    def addNoteInfo(self, barNum:int,curLane:int, notesInLane:list[str], beatPerBar=None): # 노트 정보를 레인단위로 객체내에 저장.
        if(beatPerBar==None): beatPerBar = self.BPBar_default
        grid = len(notesInLane)
        elem_count = 0
        for note in notesInLane:
            if(note != "00"):
                location = elem_count/grid # 노트의 상대위치
                timestamp = (barNum+location) * (beatPerBar * self.SPB) * 1000
                # (마디 번호 + 마디내 위치) * (마디당 박자 * 박자당 시간) * ms 단위 변환 (1s = 1000ms)
                noteInfo = [timestamp, barNum, location, curLane, note]
                # 타임스탬프, 마디번호, 노트의 마디내 상대적 위치, 레인번호, 노트 심볼(키음) 
                self.noteInfoList.append(noteInfo)
            elem_count += 1
                    
    def turnOff(self):
        self.bmsFile.close()
                    
    @staticmethod
    def checkLaneNumber(channel:int)->int:
        cases = { 11:1, 12:2, 13:3, 14:4, 15:5, 16:0, 18:6, 19:7}
        if(channel in cases): return cases[channel]
        else : return -1
        
        
                
            
        

        
            
            
        

            
            
