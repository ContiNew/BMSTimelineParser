# BMSTimelineParser
##### BMS File Parser to detect timestamp, and relative postion(in bar) information of each note. 

## How to use
    import BMSTimelineParser as bp
    
    parser = bp.BMSTimelineParser("TC_7KHD.bms") # construct a parser object with filename
    parser.readWholeBar() # readWholeBar() to read all paragraphs in target BMS File.
    parser.turnOff() # turnOff() to close target BMS File.
    datagram = parser.extract_to_pandas() # extract the output to pandas.Datagram
    parser.extract_to_txt() # extract the output to .txt format
    parser.extract_to_csv() # extract the output to .csv format

## result form
|timestamp(ms)|BarNum(int)|location(0~1, float)|laneIdx(0~7, int)|note(Hex)|
|---|---|---|---|---|

* timestamp : literally timestamp of each note based on BPM and Beat information of BMS File
* BarNum : Bar number that note belongs to
* location : relative location information of note (in bar)
* laneIdx : lane information of note
* note : keysound information of note
