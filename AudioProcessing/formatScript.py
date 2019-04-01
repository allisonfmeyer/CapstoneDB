inputL = [(42.0, 2.0), (42.0, 2.0), (49.0, 2.0), (49.0, 2.0), 
(51.0, 2.0), (51.0, 2.0), (49.0, 4.0), 
(47.0, 2.0), (47.0, 2.0), (46.0, 2.0), (46.0, 2.0), 
(44.0, 2.0), (44.0, 2.0), (42.0, 4.0), 
(49.0, 2.0), (49.0, 2.0), (47.0, 2.0), (47.0, 2.0), 
(46.0, 2.0), (46.0, 2.0), (44.0, 4.0), 
(49.0, 2.0), (49.0, 2.0), (47.0, 2.0), (47.0, 2.0), 
(46.0, 2.0), (46.0, 2.0), (44.0, 4.0), 
(42.0, 2.0), (42.0, 2.0), (49.0, 2.0), (49.0, 2.0), 
(51.0, 2.0), (51.0, 2.0), (49.0, 4.0), 
(47.0, 2.0), (47.0, 2.0), (46.0, 2.0), (46.0, 2.0), 
(44.0, 2.0), (44.0, 2.0), (42.0, 4.0)]


pianoNoteMap = {42:"D", 44: "E", 46: "F", 47: "G", 49: "A", 51: "B"}

def convertToString(L):
    result = ""
    count = 0
    measureCount = 0
    for (freq, duration) in L:
        num = duration//2
        count += num
        note = pianoNoteMap[int(freq)]
        if(count == 4):
            measureCount += 1
            if(num != 1):
                result = result + note + str(int(num)) + "|"
            else:
                result = result + note + "|"
            count = 0
        else:
            if(num != 1):
                result = result + note + str(int(num)) + " "
            else:
                result = result + note + " "
        if(measureCount == 4):
            result += "n "
            measureCount = 0
    result = result[:-2]
    result += "]n"
    return result

a = (convertToString(inputL))
print(convertToString(inputL))
b = "D D A A|B B A2|G G F F|E E D2|n A A G G|F F E2|A A G G|F F E2|n D D A A|B B A2|G G F F|E E D2|]n"
print(a == b)