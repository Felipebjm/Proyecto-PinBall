# Proyecto PINBALL

import network
from microdot.microdot import Microdot
from machine import I2C,Pin, Timer, ADC
import time
import pcf8574  # Libreria para manejo del expansor io pcf8574 micropython-pcf8574 de mcauser
from servo import Servo  # Libreria del servor micropython-servo 1.0.1

########################################################################
# INICIALIZACIONES
########################################################################

print("INICIANDO PINBALL FELIPE BEJARANO")
Z1_SW_PIN = (11)   # Switch zona1 ACTIVO EN ALTO
Z2_SW_PIN = (10)   # Switch zona2 ACTIVO EN ALTO
Z3_SW_PIN = (9)   # Switch zona3 ACTIVO EN ALTO
Z4_SW_PIN = (8)   # Switch zona4 ACTIVO EN ALTO
Z5_SW_PIN = (7)   # Switch zona5 ACTIVO EN ALTO
Z1_LED_PORT = (0)   # Switch zona1  ACTIVO EN BAJO
Z2_LED_PORT = (1)   # Switch zona2 ACTIVO EN BAJO
Z3_LED_PORT = (2)   # Switch zona3 ACTIVO EN BAJO
Z4_LED_PORT = (3)   # Switch zona4 ACTIVO EN BAJO
Z5_LED_PORT = (4)   # Switch zona5 ACTIVO EN BAJO
CAMBIO_JUGADOR_PIN = (5)  # Switch cambio de jugador activo en ALTO
JUGADOR_1_LED_PIN = (27) # Led pin del jugador 1
JUGADOR_2_LED_PIN = (26) # Led pin del jugador 2
SELECCION_JUGADOR_PIN = (28)  # Pin del potenciometro para seleccion de jugador

Z1_SENSOR = Pin(Z1_SW_PIN, mode=Pin.IN, pull=Pin.PULL_DOWN)  # Sensor zona 1 ACTIVO EN ALTO
Z2_SENSOR = Pin(Z2_SW_PIN, mode=Pin.IN, pull=Pin.PULL_DOWN)  # Sensor zona 2 ACTIVO EN ALTO
Z3_SENSOR = Pin(Z3_SW_PIN, mode=Pin.IN, pull=Pin.PULL_DOWN)  # Sensor zona 3 ACTIVO EN ALTO
Z4_SENSOR = Pin(Z4_SW_PIN, mode=Pin.IN, pull=Pin.PULL_DOWN)  # Sensor zona 4 ACTIVO EN ALTO
Z5_SENSOR = Pin(Z5_SW_PIN, mode=Pin.IN, pull=Pin.PULL_DOWN)  # Sensor zona 5 ACTIVO EN ALTO
CAMBIO_JUGADOR = Pin(CAMBIO_JUGADOR_PIN, mode=Pin.IN, pull=Pin.PULL_DOWN) # Sensor cambio jugador ACTIVO EN ALTO
LED_JUGADOR_1 = Pin(JUGADOR_1_LED_PIN, mode=Pin.OUT) # Led jugador 1, ACTIVO EN BAJO
LED_JUGADOR_2 = Pin(JUGADOR_2_LED_PIN, mode=Pin.OUT) # Led jugador 2, ACTIVO EN BAJO
SELECCION_JUGADOR = ADC(SELECCION_JUGADOR_PIN) # Sensor potenciometro seleccion de jugador para la UI

SERVO_PIN = (14) # Pin control servomotor
#SERVO_LIBERACION = Servo(pin_id=SERVO_PIN)  # Objeto control servomotor de liberacion
status_led = machine.Pin("LED", machine.Pin.OUT)
myTimer = Timer()
SERVO_LIBERACION = Servo(pin_id=SERVO_PIN)  # Objeto control servomotor de liberacion
SERVO_LIBERACION.write(0)  # Ajusta en 0 servomotores  0 = 0 grados
SERVO_LIBERACION_TIME = (2) /180  # Tiempo en segunodos que dura liverandose la bola  
time.sleep(1)
#SERVO_LIBERACION.write(180) 
for i in range(180):
  SERVO_LIBERACION.write(i)
  time.sleep(SERVO_LIBERACION_TIME)
time.sleep(1)
SERVO_LIBERACION.write(0) 

# Genera un parpadeo en el puerto, por un tiempo especifico y a una frecuencia de X por segundo.
def parpadeoLed(puerto,tiempo,frecuencia,zona_especial=False):
  i = 0
  parpadeos = int(tiempo / frecuencia)
  while (i <= parpadeos):
    #Parpadea
    if zona_especial == True:
      pcf.toggle(0)
      pcf.toggle(1)
      pcf.toggle(2)
      pcf.toggle(3)
      pcf.toggle(4)
    else:
      pcf.toggle(puerto)  # Cambia de 1 a 0 o 0 a 1 el puerto x
    
    time.sleep(frecuencia)
    i = i + 1  

  if zona_especial == True:
    pcf.pin(0,1)
    pcf.pin(1,1)
    pcf.pin(2,1)
    pcf.pin(3,1)
    pcf.pin(4,1)
  else:
    pcf.pin(puerto,1)  # Cambia de 1 a 0 o 0 a 1 el puerto x

# Parámetros de setup del expansor IO pcf8574
i2c_interface = (0)
sdapin = Pin(16)  # Pin usado para sda del i2c
sclpin = Pin(17)  # Pin usado para scl del i2c
i2c_addr = (0x20)  # Direccion i2c del expansor IO

# Inicialiación del bus i2c al que está conectado e pcf8574
#i2c = I2C(i2c_interface, scl=sclpin, sda=sdapin, freq=100000)  # Este es por si se ocupa poner la frecuencia ,pero se utiliza la de defecto
i2c = I2C(i2c_interface, scl=sclpin, sda=sdapin)  # El bus i2c queda en el objeto i2c

# Inicialización y creación del objeto para uso del pcf8574
pcf = pcf8574.PCF8574(i2c, i2c_addr)

# Funcion check sirve ver si el pcf8574 está conectado al bus.  Si no conectado tira excepcion
try:
  pcf.check()  
except:
  print("ERROR grave. Expansor IO no conectado!")

# Por sirve para setiar todos los puertos del pcf de un solo.  Un 0xff es igual que 11111111 que significa todos encendidos
# si se manda 0x00 es 00000000 que significa todos apagados
pcf.port = 0xff

ESTADO_INICIAL = True
estado_inicial_inicio = True
ESTADO_ESPERA_JUGADOR = False
estado_espera_jugador_inicio = True
ESTADO_PARTIDA = False
estado_partida_inicio = True
ESTADO_LIBERACION = False
estado_liberacion_inicio = True
PUNTAJE_A = 1  # Cantidad puntos de anotacion en z1,z2,z3,z4
PUNTAJE_B = 2  # Cantidad puntos de anotacion en z5
TIMEOUT_PARTIDA = 20  # Tiempo que transcurrira en segundos antes de que la partida se considere no anotada (en caso de que la bola no caiga en una zona)
TIME_PUNTOS_EXTRA = 10 #El maximo de tiempo que debe de transcurrir para obtener puntos extra
PARTIDAS_POR_JUEGO = 2 # Total de partidas que se jugaran, 1 por jugador.  Cada partida tiene 3 

wifi_conectado = False # Bandera wifi conectado
pc_conectado = False # Bandera pc conectada

modo_cambio_jugador_manual = True # Modo manual de cambio de jugador
tiempo_inicio_jugada = 0  # Tiempo en que inicio partida, cuando se da cambio de jugador ya sea manual o auto
tiempo_fin_jugada = 0 # Tiempo final de la partida, cuando se volvio a presionar cambio de jugador o automatico
puntaje_partida = 0 # Total de puntos de la partida
jugador_actual = 0  # Numero jugador actual
jugador_seleccionado = 1 # Jugador seleccionado en potenciometro para la UI
contador_jugada = 1 # Contador de jugadas por partida para un jugador... son 3 intentos por partida
contador_partidas = 1 # Contador de partidas totales del juego... deben ser dos en total. Cada partida tiene 3 jugadas o juegos.
puntajes = [0,0,0,0,0,0] # Lista con puntajes por jugador pj1j1 pj2j1 pj3j1 pj1j2 pj2j2 pj3j2
puntajes_permanentes = [0,0,0,0,0,0] # Puntajes que no se resetean entre partidas

#######################################################################
# Funcion principal de la maquina de estados
#######################################################################
def main_process(timer):
  global ESTADO_INICIAL
  global ESTADO_ESPERA_JUGADOR
  global ESTADO_PARTIDA
  global ESTADO_LIBERACION
  global estado_inicial_inicio
  global estado_espera_jugador_inicio
  global estado_partida_inicio
  global estado_liberacion_inicio    
  global pc_conectado
  global wifi_conectado
  global jugador_actual
  global jugador_seleccionado
  global tiempo_inicio_jugada
  global tiempo_fin_jugada
  global puntaje_partida
  global contador_jugada
  global contador_partidas
  global puntajes
  global puntajes_permanentes
  

  if SELECCION_JUGADOR.read_u16() < 32768:
    jugador_seleccionado = 1
  else:
    jugador_seleccionado = 2

  if wifi_conectado == True and pc_conectado == True:
    status_led.toggle() 



  # Apenas arranca el hardware, es para revisar que haya wifi y que la aplicacion de Python esté respondiendo
  if ESTADO_INICIAL== True:
    jugador_actual = 0
    contador_partidas = 1
    contador_jugada = 1
    puntajes = [0,0,0,0,0,0]
    if estado_inicial_inicio == True:
      print("Estado INICIAL")
      estado_inicial_inicio = False
    LED_JUGADOR_1.value(0)
    LED_JUGADOR_2.value(0)  
    if wifi_conectado == False or pc_conectado == False:
      status_led.value(1)   # El led del pico queda fijo si no hay wifi y la app de pc no responde
    else:
      ESTADO_INICIAL = False
      ESTADO_ESPERA_JUGADOR = True
      estado_inicial_inicio = True

  # Espera que la UI diga el jugador que arranca
  if ESTADO_ESPERA_JUGADOR == True:
    if estado_espera_jugador_inicio == True:
      print("Estado ESPERA_JUGADOR")
      estado_espera_jugador_inicio = False

    LED_JUGADOR_1.value(1)
    LED_JUGADOR_2.value(1)    
    if jugador_actual != 0:  # Jugador inicial en 0 significa que la ui no ha mandado jugador.
      print("Jugador de inicio recibido desde UI: ", jugador_actual)
      ESTADO_ESPERA_JUGADOR = False
      ESTADO_PARTIDA = True
      estado_espera_jugador_inicio = True 

  # Estado de juego de las partidas tanto para jugador 1 y 2
  if ESTADO_PARTIDA == True:
    if estado_partida_inicio == True:
      print("Estado PARTIDA. Jugador # ",jugador_actual," Partida: ", contador_partidas, " Juego: ",contador_jugada)    
      tiempo_inicio_jugada = time.ticks_ms() 
      estado_partida_inicio = False
    
    if jugador_actual == 1:
      LED_JUGADOR_1.value(0)  # Activo en bajo
      LED_JUGADOR_2.value(1)  # Activo en bajo
    if jugador_actual == 2:
      LED_JUGADOR_1.value(1)  # Activo en bajo
      LED_JUGADOR_2.value(0)  # Activo en bajo

    if contador_jugada < 4:
      if (Z1_SENSOR.value() == 1):
        parpadeoLed(Z1_LED_PORT,2,0.3) # Parpadea 5 segundos a 2 Hz
        puntaje_partida = puntaje_partida + PUNTAJE_A
        if jugador_actual == 1:
          puntajes[contador_jugada - 1 ] = PUNTAJE_A
        if jugador_actual == 2:
          puntajes[contador_jugada + 2 ] = PUNTAJE_A
        print("     Jugador #",jugador_actual," anota Z1 ",PUNTAJE_A,". Total partida: ",puntaje_partida)
        tiempo_inicio_jugada = time.ticks_ms()
        contador_jugada = contador_jugada + 1  
        ESTADO_PARTIDA = False
        ESTADO_LIBERACION = True
        estado_partida_inicio = True  
##############################
      if(Z2_SENSOR.value() == 1):  
        parpadeoLed(Z2_LED_PORT,2,0.3) # Parpadea 5 segundos a 2 Hz
        puntaje_partida = puntaje_partida + PUNTAJE_A
        if jugador_actual == 1:
          puntajes[contador_jugada - 1 ] = PUNTAJE_A
        if jugador_actual == 2:
          puntajes[contador_jugada + 2 ] = PUNTAJE_A
        print("     Jugador #",jugador_actual," anota Z2 ",PUNTAJE_A,". Total partida: ",puntaje_partida)
        tiempo_inicio_jugada = time.ticks_ms()
        contador_jugada = contador_jugada + 1  
        ESTADO_PARTIDA = False
        ESTADO_LIBERACION = True
        estado_partida_inicio = True    

      if(Z3_SENSOR.value() == 1):
        parpadeoLed(Z3_LED_PORT,2,0.3) # Parpadea 5 segundos a 2 Hz
        puntaje_partida = puntaje_partida + PUNTAJE_A
        if jugador_actual == 1:
          puntajes[contador_jugada - 1 ] = PUNTAJE_A
        if jugador_actual == 2:
          puntajes[contador_jugada + 2 ] = PUNTAJE_A        
        print("     Jugador #",jugador_actual," anota Z3",PUNTAJE_A,". Total partida: ",puntaje_partida)
        tiempo_inicio_jugada = time.ticks_ms()
        contador_jugada = contador_jugada + 1  
        ESTADO_PARTIDA = False
        ESTADO_LIBERACION = True
        estado_partida_inicio = True
      
      if(Z4_SENSOR.value() == 1):
        parpadeoLed(Z4_LED_PORT,2,0.3) # Parpadea 5 segundos a 2 Hz
        puntaje_partida = puntaje_partida + PUNTAJE_A
        if jugador_actual == 1:
          puntajes[contador_jugada - 1 ] = PUNTAJE_A
        if jugador_actual == 2:
          puntajes[contador_jugada + 2 ] = PUNTAJE_A        
        print("     Jugador #",jugador_actual," anota Z4",PUNTAJE_A,". Total partida: ",puntaje_partida)
        tiempo_inicio_jugada = time.ticks_ms()
        contador_jugada = contador_jugada + 1  
        ESTADO_PARTIDA = False
        ESTADO_LIBERACION = True
        estado_partida_inicio = True
      
      if(Z5_SENSOR.value() == 1):
        parpadeoLed(Z5_LED_PORT,2,0.3,True) # Parpadea 5 segundos a 2 Hz
        puntaje_partida = puntaje_partida + PUNTAJE_B
        if jugador_actual == 1:
          puntajes[contador_jugada - 1 ] = PUNTAJE_B
        if jugador_actual == 2:
          puntajes[contador_jugada + 2 ] = PUNTAJE_B        
        print("Jugador #",jugador_actual," anota Z5",PUNTAJE_A,". Total partida: ",puntaje_partida)
        tiempo_inicio_jugada = time.ticks_ms()
        contador_jugada = contador_jugada + 1  
        ESTADO_PARTIDA = False
        ESTADO_LIBERACION = True
        estado_partida_inicio = True
      
      if (time.ticks_ms() - tiempo_inicio_jugada) >= TIMEOUT_PARTIDA * 1000:
        print("     Jugador #",jugador_actual," NO anota por fallo. Total partida: ",puntaje_partida)
        contador_jugada = contador_jugada + 1  
        estado_partida_inicio = True # Para que vuelva a inicializar el estado partida
        estado_partida_inicio = True

      puntajes_permanentes = puntajes
      # puntajes[jugador_actual-1] = puntaje_partida

    else:
      print("------------------ Evaluando fin del juego o cambio de jugador -----------------")
      contador_partidas = contador_partidas + 1
      if contador_partidas <= 2:
        if jugador_actual == 1:
          jugador_actual = 2
        else:
          jugador_actual = 1

        contador_jugada = 1
        estado_partida_inicio = True
        puntaje_partida = 0
      else:  # Cuando termina el juego, partidas mayora 2
        puntaje_partida = 0
        ESTADO_INICIAL = True
        ESTADO_PARTIDA = False
        estado_partida_inicio = True

  # Estado para la liberacion de la bola
  if ESTADO_LIBERACION == True:
    if estado_liberacion_inicio == True:
      print("Estado 2 iniciado. Liberando bola")
      estado_liberacion_inicio = False
    for i in range(180):
      SERVO_LIBERACION.write(i)
      time.sleep(SERVO_LIBERACION_TIME)
    time.sleep(1)
    SERVO_LIBERACION.write(0)
    ESTADO_PARTIDA = True
    ESTADO_LIBERACION = False
    estado_liberacion_inicio = True

# initialize the timer object to tick every second (1,000 milliseconds)
myTimer.init(period=50, mode=Timer.PERIODIC, callback=main_process)


########################################################################
# CONEXION A WIFI - SERVIDOR DE MICRODOT PARA ACCESO DEL CLIENTE PC
########################################################################

# Replace the following with your WIFI Credentials
SSID = "ben10"
SSID_PASSWORD = "Zorrillo2005!"

# Conexión a WiFi
def do_connect():
    global wifi_conectado
    import network
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
      print('Conectando a la red...',SSID)
      sta_if.active(True)
      try:
        sta_if.connect(SSID, SSID_PASSWORD)
      except OSError as error:
        print("Error conectando wifi ", error)
      while not sta_if.isconnected():
          #print("no connect")
          wifi_conectado = False
          pass
    print('CONECTADO! Configuración:', sta_if.ifconfig())
    wifi_conectado = True
    
print("Conectando al WiFI ", SSID, " ...")
do_connect()

app = Microdot()

@app.route('/')
def index(request):
    return 'Hello, world!'

@app.route('/led1')
def led1(request):
  print("Receibien led1")
  return "Led1 On"

# Para indicar al sistema que la UI esta en linea y que la UI se de cuenta que hay sistema
@app.route('/pc_active')
def pc_active(request):
  global pc_conectado
  print("Received PC active cmd")
  pc_conectado = True
  return "conectado"

# Para que la UI sepa cual jugador se selecciono con el potenciometro, puede ser 1 o 2
@app.route('/jugador_seleccionado_ui')
def jugador_seleccionado_ui(request):
  global jugador_seleccionado
  print("Enviado a UI JUGADOR_SELECCIONADO = ",jugador_seleccionado)
  return str(jugador_seleccionado)

# Recibe desde UI el jugador que da inicio al juego
@app.route('/jugador_inicial_ui/<int:num_jugador>')
def jugador_inicial_ui(request,num_jugador):
  global jugador_actual
  print("Recibido desde UI jugador inicio = ",num_jugador)
  jugador_actual = num_jugador
  return "ok"

# Manda a UI los datos del juego
@app.route('/estado_juego')
def estado_juego(request):
  global jugador_actual
  global contador_partidas
  global contador_jugada
  global puntaje_partida
  global puntajes
  estado_juego = str(jugador_actual) + "," + str(contador_partidas) + "," + str(contador_jugada) + "," + str(puntajes_permanentes[0]) + "," + str(puntajes_permanentes[1]) + "," + str(puntajes_permanentes[2]) + "," + str(puntajes_permanentes[3]) + "," + str(puntajes_permanentes[4]) + "," + str(puntajes_permanentes[5]) 
  #print("Recibido desde UI solicitud de ESTADO_JUEGO: ",estado_juego)
  return estado_juego

if __name__ == '__main__':
    #app.run(debug=True)
    app.run(debug=False)