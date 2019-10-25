# NAO Connect 4
Repositorio de Inteligencia artificial para que NAO juegue 4 en linea.
* [Softbank Robotics Software](https://community.ald.softbankrobotics.com/en/resources/software/language/en-gb/field_software_type/sdk): De aqui descargar Pepper Software Suite 2.5.10 para controlar a NAO y Python NAOqi SDK, ya sea para Linux o Ubuntu

## Requisitos
### Para windows
Librerias necesarias:
* [Python 2.7.16](https://www.python.org/downloads/release/python-2716/).
Descargar la version de 32 bits unicamente.
* [OpenCV 2.3.1 para Windows](https://sourceforge.net/projects/opencvlibrary/files/opencv-win/2.3.1/OpenCV-2.3.1-win-superpack.exe/download)
De aqui copiar los dos archivos de la carpeta opencv/builds/python/2.7 a la carpeta C:/Python27/lib/site-packages/
* [Softbank Robotics Software](https://community.ald.softbankrobotics.com/en/resources/software/language/en-gb/field_software_type/sdk)
De aqui descargar Pepper Software Suite 2.5.10 o superior para controlar a NAO y Python NAOqi SDK for Windows
* [Pythom Imaging Library (PIL)](http://www.pythonware.com/products/pil/)
Necesaria para capturar las fotos de NAO

### Para Ubuntu/Linux
Librerias necesarias:
* [Python 2.7.15+](https://www.python.org/downloads/release/python-2716/)
Puedes usar el siguiente comando para installarlo, o si quieres hacer una instalacion de los Sources.
    ```sh
    sudo apt install python2.7 python-pip
   ``` 
* [OpenCV 2.3.1 for Unix](https://sourceforge.net/projects/opencvlibrary/files/opencv-unix/2.3.1/).
De aqui copiar los dos archivos de la carpeta opencv/builds/python/2.7 a la carpeta /usr/local/lib/python2.7/dist-packages
* [Softbank Robotics Software](https://community.ald.softbankrobotics.com/en/resources/software/language/en-gb/field_software_type/sdk): De aqui descargar Pepper Software Suite 2.5.10 o superior para controlar a NAO y Python NAOqi SDK for Ubuntu
* [Pythom Imaging Library (PIL)](http://www.pythonware.com/products/pil/): Necesaria para capturar las fotos de NAO, puede compilarla desde el source (Recomendado) o usar el siguiente comando
    ```sh
    pip install Pillow
    ```

## Uso
El software funciona de tal forma que se conecta directamente a NAO, obtiene las imagenes y se hace el procesamiento localmente, con el fin de no llenar la memoria de NAO.

Es recomendable que con el Choregraphe, mantener a NAO "Suspendido" para que las fotos queden mas precisas.

En caso de tener la direccion IP de NAO, utilizar el siguiente comando.

```sh
python __main__.py NAO_IP_ADDRES
```

En otro caso, buscará a NAO con la dirección 'nao.local' de forma predeterminada.

```sh
python __main__.py
```
Su funcionamiento despues de ejecutar, consiste en que primero el juegador haga su jugada, toque algun sensor de NAO y este dira cual es su jugada.


## Sugerencias
* Para ubicar la camara de nao, ejecutar:
    ```sh
    python getImageRealTime.py
    ```
    Ajustan manualmente la cabeza de NAO, para que quede centrado el trablero.
* Se recomienda que el tablero esté pegado en la pared con un fondo que contraste con el tablero, en unestro caso el tablero era de color rojo, el fondo verde y las fichas blancas y negras.
* El jugador son las fichas Negras y NAO las fichas Blancas.