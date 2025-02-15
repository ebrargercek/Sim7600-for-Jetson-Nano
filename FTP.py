import Jetson.GPIO as GPIO
import serial
import time
import logging


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


SERIAL_PORT = '/dev/ttyUSB2’
BAUD_RATE = 115200
POWER_KEY = 6

# FTP konfigürasyonu
FTP_USER_NAME = 'capella'
FTP_USER_PASSWORD = 'capella2024'
FTP_SERVER = '113.81.235.52'
DOWNLOAD_FILE_NAME = 'index.htm'
UPLOAD_FILE_NAME = 'index.htm'

# Seri portu açma
ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
ser.flushInput()

def send_at(command, expected_response, timeout):
    """AT komutunu gönderir ve cevabı kontrol eder."""
    rec_buff = ''
    ser.write((command + '\r\n').encode())
    time.sleep(timeout)
    
    if ser.inWaiting():
        time.sleep(0.1)
        rec_buff = ser.read(ser.inWaiting())
    
    if rec_buff:
        response = rec_buff.decode()
        if expected_response not in response:
            logging.error(f"{command} ERROR: {response}")
            return False
        else:
            logging.info(response)
            return True
    else:
        logging.warning(f"{command} no response")
        return False

def configure_ftp(server, u_name, u_password):
    """FTP yapılandırmasını yapar."""
    send_at('AT+CFTPPORT=21', 'OK', 1)
    send_at('AT+CFTPMODE=1', 'OK', 1)
    send_at('AT+CFTPTYPE=A', 'OK', 1)
    send_at(f'AT+CFTPSERV="{server}"', 'OK', 1)
    send_at(f'AT+CFTPUN="{u_name}"', 'OK', 1)
    send_at(f'AT+CFTPPW="{u_password}"', 'OK', 1)

def download_from_ftp(file_name):
    """FTP'den dosya indirir."""
    logging.info('Downloading file from FTP...')
    send_at(f'AT+CFTPGETFILE="{file_name}",0', 'OK', 1)

def upload_to_ftp(file_name):
    """FTP'ye dosya yükler."""
    logging.info('Uploading file to FTP...')
    send_at(f'AT+CFTPGETFILE="{file_name}",0', 'OK', 1)

def power_on():
    """Modülü açar."""
    logging.info('SIM7600X is starting...')
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
    GPIO.cleanup()

try:
    power_on()
    configure_ftp(FTP_SERVER, FTP_USER_NAME, FTP_USER_PASSWORD)
    time.sleep(0.5)
    logging.info(f'Downloading file from "{FTP_SERVER}"...')
    download_from_ftp(DOWNLOAD_FILE_NAME)
    time.sleep(1)
    logging.info(f'Uploading file to "{FTP_SERVER}"...')
    upload_to_ftp(UPLOAD_FILE_NAME)
except KeyboardInterrupt:
    logging.info("Operation interrupted by user")
except Exception as e:
    logging.error(f"An error occurred: {e}")
finally:
    if ser:
        ser.close()
    power_down()
