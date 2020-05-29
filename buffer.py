from queue import Queue

class ReadBuffer():
    
    def __init__(self, file_name, size):
        self.file = open(file_name, "r", encoding="UTF-8")
        self.buffer = Queue(size)
        self.size = size
        self.empty = False
        self.done = False
        self.line = ""
        self.readline()

    def readline(self):
        if self.done: return self.setInfo("")
        if self.empty:
            if not self.buffer.empty(): return self.setInfo(self.buffer.get())
            self.done = True
            return self.setInfo("")
        if self.buffer.empty():
            self.fillBuffer()
            if self.buffer.empty(): return self.setInfo("")
        return self.setInfo(self.buffer.get())
    
    def notDone(self):
        return not self.done

    def setInfo(self, line):
        self.line = line
        return line
    
    def fillBuffer(self):
        for _ in range(self.size):
            line = self.file.readline()
            if line == "":
                self.empty = True
                self.file.close()
                break
            self.buffer.put(line)

class ReadBufferWithPosting(ReadBuffer):

    def __init__(self, file_name, size):
        self.token = ""
        self.ids = {}
        ReadBuffer.__init__(self, file_name, size)
        
    def setInfo(self, line):
        self.line = line
        if line == "":
            self.token = ""
            self.ids.clear()
        else:
            sep = line.rfind(':')
            self.token = line[:sep]
            self.ids.clear()
            for posting in line[sep+1:].rstrip(";\n").split(";"):
                id_sep = posting.find(",")
                self.ids[int(posting[:id_sep])] = posting[id_sep:]

        return line
