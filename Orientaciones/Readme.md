Orientaciones para el laboratorio de Modbus 
===========================================

El mapeo de memoria del PLC Master-k120s se puede encontrar en la página
8-59 del documento
[Master-k-Comm.pdf](http://univirt.em.reduc.edu.cu/mod/resource/view.php?id=690)
y para el analizador de redes en la página 7 del documento
[WM14BXCPv2r0ENG0804.pdf](http://univirt.em.reduc.edu.cu/mod/resource/view.php?id=691).

Tareas: 
-------

Se pide una variante por estudiante que debe verse en el documento
[Variantes.pdf](http://univirt.em.reduc.edu.cu/mod/resource/view.php?id=692).
Usted deberá ejecutar las siguientes acciones:

**PLC**

-   -   -   -   -   -   -   

**Analizador**

-   -   

\

\* Entre paréntesis se muestra la columna que contiene la información
para su variante.

\

![](Orientaciones_para_el_laboratorio_html_6bd9e23fbd7fba31.gif) El
estudiante debe traer al laboratorio elaborado los mensajes que va a
enviar, por ejemplo:

<div align="right">

Acción

Mensaje

Activar la salida P4C

Esclavo

Función

Dirección

Dato/Cantidad

2

05

![](Orientaciones_para_el_laboratorio_html_ce21b96b0a33de96.gif)
![](Orientaciones_para_el_laboratorio_html_b5bb3f65dc684dbb.gif)
![](Orientaciones_para_el_laboratorio_html_6e940c1d15b06656.gif)
![](Orientaciones_para_el_laboratorio_html_f609de33f8ba1d56.gif) 04C0

![](Orientaciones_para_el_laboratorio_html_3f6bb5ef55ade789.gif) FF00

Leer la energía del analizador

1

04

02C6

1

</div>

![](Orientaciones_para_el_laboratorio_html_5374345953771fa1.gif)\
![](Orientaciones_para_el_laboratorio_html_88c38101278ccd41.gif)
![](Orientaciones_para_el_laboratorio_html_c6cd4e2f4dd89535.gif)\



El software ModbusLab se presenta como puede verse en la figura 1.

![](Orientaciones_para_el_laboratorio_html_a3c36e142383942f.png)\
*Figura 1: Ventana principal de Modbuslab.*


En la figura 2 se muestra el área para la configuración del puerto
serie. En esto es suficiente con dejar los valores predeterminados
puesto que así han sido configurados todos los nodos de la red.

![](Orientaciones_para_el_laboratorio_html_c62b4826ed44c77b.png)\
*Figura 2: Configurador del puerto serie.*

\
El editor de mensajes se puede ver en la figura 3. El primer campo hacer
referencia a la dirección del esclavo con el que se establecerá la
conexión (Estación). El segundo campo determina la función del mensaje
(véase en detalle en la figura 3) y determina los campoes que estarán
activos e inactivos. Es importante notar que todas la entradas numéricas
son de valores hexadecimales, el valor decimal será siempre accesible en
un tip como puede verse en la figura 5.

![](Orientaciones_para_el_laboratorio_html_ec145c343e62aaf5.png){width="100%"}\
![](Orientaciones_para_el_laboratorio_html_8f734337a1fa50e9.gif)
![](Orientaciones_para_el_laboratorio_html_c98016e6399cd823.gif) *Figura
3: Editor de mensajes.*

![](Orientaciones_para_el_laboratorio_html_489c99d7597aa168.gif)
![](Orientaciones_para_el_laboratorio_html_39c9dbc14414711a.gif)
![](Orientaciones_para_el_laboratorio_html_de9d50cb7cc3a811.gif)
![](Orientaciones_para_el_laboratorio_html_63c2ae7e09b05987.gif) [
]

![](Orientaciones_para_el_laboratorio_html_80eb937eeb844580.png){width="100%"}\
*Figura 4: Selector de la función modbus.*
\

![](Orientaciones_para_el_laboratorio_html_df9e71cd759a2202.png){width="100%"}\
*Figura 5: Entrada numérica.*

El monitor del analizador de redes nos permite conocer todo el tiempo
los valores medidos por el equipo como se muestra en la figura 6. La
escala de los instrumentos de aguja se puede modificar a través de una
entrada numérica como indica la figura 6.

![](Orientaciones_para_el_laboratorio_html_85c7876e0ada5899.png){width="100%"}\
![](Orientaciones_para_el_laboratorio_html_94003d29ac9cc80f.gif)
![](Orientaciones_para_el_laboratorio_html_27c66f567b34645e.gif)
![](Orientaciones_para_el_laboratorio_html_c105441136e6f938.gif)
![](Orientaciones_para_el_laboratorio_html_659c137372fad3bf.gif) *Figura
6: Monitor del analizador de redes.*

\
![](Orientaciones_para_el_laboratorio_html_42d46b23f69ffded.gif)
![](Orientaciones_para_el_laboratorio_html_cb4c599fca6d62d8.gif)\

En el menú herramientas podemos encontrar la utilidad para configuración
del PLC como se en la figura 8. Esta interfaz nos permite definir el
número de entradas y salidas así como la dirección base de las mismas en
la memoria del PLC. En este caso la base numérica puedes ser decimal o
hexadecimal según sea más conveniente. Esta configuración hace flexible
al programa para interactuar con cualquier autómata. Se puede escoger el
color para la visualización de los leds como se muestra en la figura 8.

Una vez terminado el laboratorio el software permite generar un informe
con el menú que se muestra en la figura 7.
\
![](Orientaciones_para_el_laboratorio_html_854912dafacce3ba.png){width="100%"}\
*Figura 7: Menú para generar informe.*

\

![](Orientaciones_para_el_laboratorio_html_9d68952e0b7948d1.png){width="100%"}\
![](Orientaciones_para_el_laboratorio_html_771611079e88ba38.gif)
![](Orientaciones_para_el_laboratorio_html_1adb9d396ade56c1.gif)
![](Orientaciones_para_el_laboratorio_html_32fd1ce45ee49959.gif) *Figura
8: Configurador del PLC*



