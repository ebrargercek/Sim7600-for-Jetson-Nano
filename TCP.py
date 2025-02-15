import Jetson.GPIO as GPIO
import serial
import time
import logging

# Loglama ayarları
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Seri port ve güç anahtarı
SERIAL_PORT = '/dev/ttyUSB2'
BAUD_RATE = 115200
POWER_KEY = 6

# GSM/GPRS ayarları
APN = 'CMNET'
SERVER_IP = '118.190.93.84'
PORT = '2317'
MESSAGE = 'CAPELLA'

# GPIO başlatma ve temizleme fonksiyonları
def setup_gpio(power_key):
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(power_key, GPIO.OUT)

def cleanup_gpio():
    GPIO.cleanup()

# Güç yönetimi fonksiyonları
def power_on(power_key):
    logging.info('SIM7600G is starting...')
    setup_gpio(power_key)
    GPIO.output(power_key, GPIO.HIGH)
    time.sleep(2)
    GPIO.output(power_key, GPIO.LOW)
    time.sleep(20)
    ser.flushInput()
    logging.info('SIM7600G is ready')

def power_down(power_key):
    logging.info('SIM7600G is logging off...')
    GPIO.output(power_key, GPIO.HIGH)
    time.sleep(3)
    GPIO.output(power_key, GPIO.LOW)
    time.sleep(18)
    logging.info('Goodbye')
    cleanup_gpio()

# AT komut gönderme fonksiyonu
def send_at(command, expected_response, timeout):
    rec_buff = ''
    ser.write((command + '\r\n').encode())
    time.sleep(timeout)
    if ser.inWaiting():
        time.sleep(0.1)
        rec_buff = ser.read(ser.inWaiting()).decode()
        if expected_response not in rec_buff:
            logging.error(f"{command} ERROR")
            logging.error(f"{command} response: {rec_buff}")
            return False
        else:
            logging.info(rec_buff)
            return True
    else:
        logging.warning(f"{command} no response")
        return False

# Ana işlem bloğu
if __name__ == "__main__":
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
    ser.flushInput()

    try:
        power_on(POWER_KEY)
        
        # AT komutlarını sırayla gönder
        if send_at('AT+CSQ', 'OK', 1) and \
           send_at('AT+CREG?', '+CREG: 0,1', 1) and \
           send_at('AT+CPSI?', 'OK', 1) and \
           send_at('AT+CGREG?', '+CGREG: 0,1', 0.5) and \
           send_at(f'AT+CGSOCKCONT=1,"IP","{APN}"', 'OK', 1) and \
           send_at('AT+CSOCKSETPN=1', 'OK', 1) and \
           send_at('AT+CIPMODE=0', 'OK', 1) and \
           send_at('AT+NETOPEN', '+NETOPEN: 0', 5) and \
           send_at('AT+IPADDR', '+IPADDR:', 1) and \
           send_at(f'AT+CIPOPEN=0,"TCP","{SERVER_IP}",{PORT}', '+CIPOPEN: 0,0', 5):
            
            if send_at('AT+CIPSEND=0,', '>', 2):
                ser.write(MESSAGE.encode())
                if send_at(chr(26), 'OK', 5):  # 26 = CTRL+Z (hex 1A)
                    logging.info('Message sent successfully!')

            send_at('AT+CIPCLOSE=0', '+CIPCLOSE: 0,0', 15)
            send_at('AT+NETCLOSE', '+NETCLOSE: 0', 1)
        
        power_down(POWER_KEY)

    except Exception as e:
        logging.error(f'An error occurred: {e}')
    finally:
        if ser:
            ser.close()
        cleanup_gpio()
