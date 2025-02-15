import Jetson.GPIO as GPIO
import serial
import time
import logging


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')



PHONE_NUMBER = ''   
POWER_KEY = 6
BAUD_RATE = 115200
SERIAL_PORT = '/dev/ttyUSB2'

# Seri port yapılandırması
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
    ser.flushInput()
except serial.SerialException as e:
    logging.error(f"Seri port açma hatası: {e}")
    raise

def send_at(command, expected_response, timeout):
    """AT komutunu gönderir ve cevabı kontrol eder."""
    rec_buff = ''
    try:
        ser.write((command + '\r\n').encode())
        time.sleep(timeout)
        
        if ser.inWaiting():
            time.sleep(0.01)
            rec_buff = ser.read(ser.inWaiting()).decode()
        
        if expected_response not in rec_buff:
            logging.error(f"{command} ERROR: {rec_buff}")
            return False
        else:
            logging.info(f"{command} response: {rec_buff}")
            return True
    except Exception as e:
        logging.error(f"AT komutu gönderme hatası: {e}")
        return False

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

def make_call(phone_number):
    """Telefon araması başlatır ve kapatır."""
    if send_at(f'ATD{phone_number};', 'OK', 1):
        logging.info('Calling...')
        time.sleep(100)  # Aramanın 100 saniye sürmesini bekler
        send_at('AT+CHUP', 'OK', 1)  # Çağrıyı kapatır
        logging.info('Call disconnected')
    else:
        logging.error('Failed to initiate call')

try:
    power_on()
    make_call(PHONE_NUMBER)
except Exception as e:
    logging.error(f"An error occurred: {e}")
finally:
    power_down()
    if ser:
        ser.close()
    GPIO.cleanup()
