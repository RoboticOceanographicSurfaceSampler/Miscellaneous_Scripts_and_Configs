import sys
import serial
import time
from fake_serial import FakeSerial

DISABLE_TILT_ASSIST = "$JATT,TILTAID,NO\r\n"
ENABLE_TILT_ASSIST = "$JATT,TILTAID,YES\r\n"
QUERY_TILT_ASSIST = "$JATT,TILTAID\r\n"

DISABLE_GYRO_ASSIST = "$JATT,GYROAID,NO\r\n"
ENABLE_GYRO_ASSIST = "$JATT,GYROAID,YES\r\n"
QUERY_GYRO_ASSIST = "$JATT,GYROAID\r\n"

SAVE_COMMAND = "$JSAVE\r\n"

READ_TIMEOUT = 10  # Seconds before exiting if can't read back data


def get_gyro_and_tilt_aid_status(hemisphere):
    hemisphere.write(QUERY_GYRO_ASSIST)
    time.sleep(0.5)
    hemisphere.write(QUERY_TILT_ASSIST)
    time.sleep(0.5)

    gyroaid_status = None
    tiltaid_status = None

    start_time = time.time()
    while (time.time() - start_time) < READ_TIMEOUT:
        data = hemisphere.readline()

        index = data.find("JATT")

        if index != -1:
            split = data.split(",")
            status = split[2].split("\r\n")[0]

            if status == "OK":
                continue

            status = (status == "YES")
            if split[1] == "GYROAID":
                gyroaid_status = "Enabled" if status else "Disabled"
            elif split[1] == "TILTAID":
                tiltaid_status = "Enabled" if status else "Disabled"

        if (gyroaid_status is not None) and (tiltaid_status is not None):
            break

    return {"gyroaid_status": gyroaid_status, "tiltaid_status": tiltaid_status}


def configure_hemisphere_smoothing(port, baud, smoothing_enabled):
    hemisphere = None

    try:
        if port == "/dev/ttyFake":
            hemisphere = FakeSerial()
        else:
            hemisphere = serial.Serial(port=port, baudrate=baud)
    except:
        print "Could not open port " + str(port) + ". Exiting..."
        exit()

    print "Getting current GYROAID and TILTAID status..."
    statuses = get_gyro_and_tilt_aid_status(hemisphere)
    print "Current GYROAID status:", statuses["gyroaid_status"]
    print "Current TILTAID status:", statuses["tiltaid_status"]

    print ""

    if smoothing_enabled:
        print "Enabling tilt and gyro assist..."
        hemisphere.write(ENABLE_TILT_ASSIST)
        time.sleep(0.5)
        hemisphere.write(ENABLE_GYRO_ASSIST)
        time.sleep(0.5)
    else:
        print "Disabling tilt and gyro assist..."
        hemisphere.write(DISABLE_TILT_ASSIST)
        time.sleep(0.5)
        hemisphere.write(DISABLE_GYRO_ASSIST)
        time.sleep(0.5)

    print "Saving new config to GPS..."
    hemisphere.write(SAVE_COMMAND)

    print ""

    print "Getting new GYROAID and TILTAID status..."
    statuses = get_gyro_and_tilt_aid_status(hemisphere)
    print "New GYROAID status:", statuses["gyroaid_status"]
    print "New TILTAID status:", statuses["tiltaid_status"]

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print "## Hemisphere Smoothing Script Usage ##"
        print "python hemisphere_smoothing.py [port] [baud] [Enabled/Disabled]"
        print "Example: python hemisphere_smoothing.py /dev/ttyGPS 19200 Enabled"
    else:
        configure_hemisphere_smoothing(sys.argv[1], sys.argv[2], sys.argv[3] == "Enabled")

