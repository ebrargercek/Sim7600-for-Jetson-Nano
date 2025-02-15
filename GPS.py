import Jetson.GPIO as GPIO
import serial
import time
import logging

# Loglama ayarları
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Seri port ve güç anahtarı konfigürasyonu
SERIAL_PORT = '/dev/ttyUSB2'
BAUD_RATE = 115200
POWER_KEY = 6

# Seri portu açma
ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
ser.flushInput()

def send_at(command, expected_response, timeout):
    """AT komutunu gönderir ve cevabı kontrol eder."""
    rec_buff = ''
    ser.write((command + '\r\n').encode())
    time.sleep(timeout)
    
    while ser.inWaiting():
        time.sleep(0.03)
        rec_buff += ser.read(ser.inWaiting()).decode()
    
    if rec_buff:
        if expected_response not in rec_buff:
            logging.error(f"{command} ERROR: {rec_buff}")
            return False
        else:
            logging.info(f"{command} response: {rec_buff}")
            return True
    else:
        logging.warning(f"{command} no response")
        return False


def get_gps_position():
    """GPS konumunu alır."""
    logging.info('Starting GPS session...')
    
    if not send_at('AT+CGPS=1,1', 'OK', 5):
        logging.error('Failed to start GPS session')
        return False

    time.sleep(5)
    
    start_time = time.time()
    while True:
        if send_at('AT+CGPSINFO', '+CGPSINFO: ', 5):
            rec_buff = ser.read(ser.inWaiting()).decode()
            if ',,,,,,' in rec_buff:
                logging.info('GPS is not ready')
                time.sleep(2)
            else:
                logging.info(f'GPS Position: {rec_buff}')
                break
        else:
            logging.error('Error reading GPS info')
            break

        time.sleep(1.5)

    send_at('AT+CGPS=0', 'OK', 5)
    time_count = time.time() - start_time
    logging.info(f"GPS konumu alma süresi: {time_count:.2f} saniye")
    return True


def power_on():
    """Modülü açar."""
    logging.info('SIM7600G is starting...')
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(POWER_KEY, GPIO.OUT)
    time.sleep(0.1)
    GPIO.output(POWER_KEY, GPIO.HIGH)
    time.sleep(2)
    GPIO.output(POWER_KEY, GPIO.LOW)
    time.sleep(20)
    ser.flushInput()
    logging.info('SIM7600G is ready')

def power_down():
    """Modülü kapatır."""
    logging.info('SIM7600G is logging off...')
    GPIO.output(POWER_KEY, GPIO.HIGH)
    time.sleep(3)
    GPIO.output(POWER_KEY, GPIO.LOW)
    time.sleep(18)
    logging.info('Goodbye')

try:
    power_on()
    get_gps_position()
except Exception as e:
    logging.error(f"An error occurred: {e}")
finally:
    if ser:
        ser.close()
    power_down()
    GPIO.cleanup()
