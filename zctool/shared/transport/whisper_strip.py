#!/usr/bin/python
import io

class WhisperStrip(object):
    def __init__(self, strip_id, file_size, block_size, strip_length):
        self.strip_id = strip_id
        self.file_size = file_size
        self.block_size = block_size
        self.strip_length = strip_length
        self.finished = False
        strip_size = block_size * strip_length
        self.position = strip_id * strip_size
        if (file_size - self.position) < strip_size:
            ##last strip
            self.length = file_size - self.position
            if 0 == (self.length%self.block_size):
                self.block_count = self.length/self.block_size
            else:
                self.block_count = ((self.length - self.length%self.block_size)/self.block_size) + 1
        else:
            self.length = strip_size
            self.block_count = strip_length
        self.mark = []
        for i in range(self.block_count):
            self.mark.append(False)

        self.stream = io.BytesIO(bytearray(self.length))
        self.writer = io.BufferedRandom(self.stream)
        self.content = ""

    def writeBlock(self, block_id, data):
        if self.finished:
            return True
        block_offset = block_id%self.strip_length
        if self.mark[block_offset]:
          return True
        pos_offset = block_offset * self.block_size
        self.writer.seek(pos_offset)
        self.writer.write(data)
        self.mark[block_offset] = True
        for mark in self.mark:
            if not mark:
                break
        else:
            ##all finished            
            self.writer.flush()
            self.content = self.stream.getvalue()
            self.writer.close()
            self.finished = True
        return True

    def isFinished(self):
        return self.finished

    def getLength(self):
        return self.length

    def getData(self):
        return self.content

    def getPosition(self):
        return self.position
    
