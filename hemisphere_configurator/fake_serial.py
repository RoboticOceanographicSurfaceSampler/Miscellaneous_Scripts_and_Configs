class FakeSerial:
    def __init__(self):
        self.file = open("serial_data.txt", "w")
        self.read_data = ["JATT,TILTAID,ON\r\n", "JATT,GYROAID,ON\r\n", "$JATT,GYROAID,ON\r\n", "$JATT,TILTAID,OFF\r\n"]
        self.last_index = 0

    def write(self, data):
        index = data.find("NO")

        if index != -1:
            self.read_data = ["JATT,TILTAID,OFF\r\n", "JATT,GYROAID,OFF\r\n", "$JATT,GYROAID,OFF\r\n", "$JATT,TILTAID,OFF\r\n"]

        self.file.write(data)

    def readline(self):
        self.last_index += 1

        if self.last_index > len(self.read_data):
            return "\n"
        return self.read_data[self.last_index - 1]
