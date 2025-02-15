#!/usr/bin/python

import Jetson.GPIO as GPIO
import serial
import time
import logging

# Loglama ayarları
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Seri port ve güç anahtarı
SERIAL_PORT = "/dev/ttyUSB2"
BAUD_RATE = 115200
POWER_KEY = 6
PHONE_NUMBER = ''  # Değiştirilmesi gereken telefon numarası
TEXT_MESSAGE = 'ACİL DURUM VAR!'

def send_at(command, expected_response, timeout):
    rec_buff = ''
    ser.write((command + '\r\n').encode())
    time.sleep(timeout)
    
    if ser.inWaiting():
        time.sleep(0.01)
        rec_buff = ser.read(ser.inWaiting())
    
    if rec_buff:
        response = rec_buff.decode()
        if expected_response not in response:
            logging.error(f"{command} ERROR")
            logging.error(f"{command} response: {response}")
            return False
        else:
            logging.info(response)
            return True
    else:
        logging.warning(f"{command} no response")
        return False

def send_short_message(phone_number, text_message):
    logging.info("Setting SMS mode...")
    if not send_at("AT+CMGF=1", "OK", 1):
        logging.error("Failed to set SMS mode")
        return False

    logging.info("Sending Short Message")
    if send_at(f'AT+CMGS="{phone_number}"', ">", 2):
        ser.write(text_message.encode())
        ser.write(b'\x1A')  # Ctrl+Z ASCII kodu
        if send_at("", "OK", 20):
            logging.info("Message sent successfully")
            return True
        else:
            logging.error("Failed to send message")
    else:
        logging.error("Failed to initiate message sending")
    return False

def receive_short_message():
    logging.info("Setting SMS mode...")
    if not send_at('AT+CMGF=1', 'OK', 1):
        logging.error("Failed to set SMS mode")
        return False
    
    if not send_at('AT+CPMS="SM","SM","SM"', 'OK', 1):
        logging.error("Failed to set SMS storage")
        return False
    
    if send_at('AT+CMGR=1', '+CMGR:', 2):
        rec_buff = ser.read(ser.inWaiting()).decode()
        logging.info(f"Message received: {rec_buff}")
        return True
    else:
        logging.error("Failed to read message")
        return False

def power_on():
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
    logging.info('SIM7600G is logging off...')
    GPIO.output(POWER_KEY, GPIO.HIGH)
    time.sleep(3)
    GPIO.output(POWER_KEY, GPIO.LOW)
    time.sleep(18)
    logging.info('Goodbye')

if __name__ == "__main__":
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
        ser.flushInput()

        power_on()
        logging.info('Sending Short Message Test:')
        send_short_message(PHONE_NUMBER, TEXT_MESSAGE)
        logging.info('Receive Short Message Test:\n')
        logging.info(f'Please send message to phone {PHONE_NUMBER}')
        receive_short_message()
    except KeyboardInterrupt:
        logging.info('Interrupted by user')
    except Exception as e:
        logging.error(f'An error occurred: {e}')
    finally:
        if ser and ser.is_open:
            ser.close()
        power_down()
        GPIO.cleanup()
        logging.info('GPIO cleaned up and serial connection closed.')
