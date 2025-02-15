Devices and Components


**1-Jetson GPIO**
Jetson platform is a powerful development platform developed by NVIDIA, used for AI and robotics projects. 
The GPIO (General Purpose Input/Output) pins are used to control physical devices on this platform.
In this project, the Jetson GPIO module is used for power management of the SIM7600G GSM module.


**2-SIM7600G GSM Module**
The SIM7600G is a 4G LTE capable GSM module.
It provides services such as making phone calls, sending SMS, and establishing data connections.
In this project, AT commands are used to control the power on/off of the GSM module and to make phone calls.
Connection Type: Serial port (UART)
Supported Connections: 4G LTE, 3G, 2G
Features: Phone calls, SMS, data transmission, internet connectivity


**3-Jetson Nano**
The Jetson Nano is a small, low-cost development board produced by NVIDIA. 
It is designed for robotics projects, AI applications, and deep learning tasks.
In this project, Jetson Nano's GPIO pins are used to control the SIM7600G GSM module.
Features: ARM Cortex-A57 CPU, 128 CUDA cores GPU, 4GB RAM, Linux-based operating system
Connection Types: USB, Ethernet, GPIO


**4-Serial Port (UART)**
The serial port is a communication method used for data transmission between devices.
In this project, a serial connection (UART) is used to communicate with the SIM7600G GSM module. 
The module is controlled using AT commands.
Connection: /dev/ttyUSB2
Baud Rate: 115200


**5-Jetson GPIO and Power Control**
Jetson GPIO is used for controlling various physical components. 
In this project, one of the GPIO pins is used to control the power switch of the SIM7600G GSM module. 
This is essential for turning the module on and off.
Pin: GPIO 6 (Power Key)


