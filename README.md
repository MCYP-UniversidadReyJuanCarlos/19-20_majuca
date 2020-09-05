# Privacidad en canales y grupos de Telegram
![N|Solid](https://telegram.org/img/td_icon.png)![N|Solid](https://awaywithideas.com/wp-content/uploads/2019/10/Python.svg_-e1571602766898.png)![N|Solid](https://4.bp.blogspot.com/-X7UPkOQjQuQ/WuHLUEM7SDI/AAAAAAAAAOY/rXGXSOfPP2ckF_cSOC3C5d3B_BhIgNcxACLcBGAs/s1600/mongodb%2B%25282%2529.png)

## Índice

1. [Objetivo](#objetivo)
2. [Versiones](#versiones)
3. [Limitaciones](#limitaciones)
4. [Instalación](#instalación)
5. [Configuración](#configuración)
6. [Ejecución](#ejecución)
7. [Uso básico](#uso-básico)
8. [Trabajo futuro](#trabajo-futuro)

## Objetivo
El objetivo de este proyecto ha sido realizar un bot de Telegram que sea capaz de recuperar toda la información posible de usuarios que están dentro de un canal y/o un grupo de Telegram (nombres de usuario, identificadores, fotos, nombre, apellidos, etc.).
La intención es demostrar que aun no siendo el administrador del canal/grupo cualquier usuario puede extraer mucha información de él y sus usuarios.

## Limitaciones
- Para extarer información de los canales/grupos no puede hacerse con bots de telegram, sino con usuarios reales programados.
- Solo se puede extraer información de grupos en los que tengamos la posibilidad de escribir, no se puede en canales de suscripción.

## Versiones
### **1.0.0**
  - Permite obtener todos los datos relevantes de cada usuario y guardar un único archivo json en un directorio local.
  - Permite obtener todas la fotos de perfil de cada usuario y descargarlas en un directorio local.
### **1.1.0**
  - Se añade añade almacenamiento en la base de datos MongoDB.
  - Se modifica las funcionalidades anteriores para almacenar los datos en ella.
### **1.2.0**
  - Permite obtener una cantidad de mensajes concreta del canal/grupo.
  - Permite añadirte al grupo que has introducido automáticamente.
  - Optimización de código y estructuras de la base de datos.

## Instalación

La aplicación requiere tener instalada una versión de [Python](https://www.python.org/downloads/) v3+ para arrancar.
Para todo el funcionamiento de la aplicación se hace uso de la librería _telethon_ y que podemos instalar con el comando pip:
```sh
$ pip install telethon
```
Si queremos usar una version 1.1.0 o superior en la que se hace uso de la base de datos MongoDB debemos instalar el drive _pymongo_
```sh
$ pip install pymongo
```
Si queremos hacer uso de la base de datos MongoDB en un servidor cloud necesitamos una dependencia extra para descifrar las urls que tienen este formato _mongodb+srv://<user>:<password>@clustermongodb.j4now.mongodb.net/test_
```sh
$ pip install dnspython
```
## Configuración

La única configuración que debemos realizar es la de asignar valor a las variables que se encuentran dentro del archivo [config.ini](config.ini).

Dentro de las variables para el uso del cliente de Telegram es necesario asignar:
- api_id = your_api_id
- api_hash = your_api_hash
- phone = your_phone
- username = your_username
- message_limit = your_limit

Dentro de las variables para el uso de la base de datos de MongoDB solo debemos especificar su uri
- uri = your_mongodb_uri

## Ejecución

Una vez hemos instalado todas las dependencias necesarias citadas en la sección **_Instalación_** y configurado todas las variables de la sección **_Configuración_** solo nos queda ejecutar nuestro código. Para ello necesitamos ejecutar nuestro archivo [Main.py](Main.py).
(Suponemos que estamos dentro del directorio del proyecto)

```sh
$ python Main.py
```

## Uso básico

Tras ejecutar el programa principal como se explica en la sección anterior, el programa comprueba si estas autorizado. 
- Si no lo eres, se te pedirá el número de teléfono y _Telegram_ enviará un código a tu teléfono para autorizar el dispositivo desde el cuál quieres iniciar sesión.
El programa te pedirá el código que te han enviado y al introducirlo estarás autorizado e iniciado con la misma identidad que usas en tu teléfono. **_Este paso solo será necesario en la primera ejecución._**
- Una vez estamos autorizados nos pedirá que introduzcamos el enlace del canal o grupo. Un ejemplo de enlace que debemos introducir sería el siguiente _https://telegram.me/joinchat/B-sE9kBz5v_8SvNf-A_Vbw_.
- El programa se encargará de obtener el _hash_ que aparece al final **_B-sE9kBz5v_8SvNf-A_Vbw_** y añadirte a ese grupo si es que no estuvieses ya en él.
- Con el grupo identificado se comprueba si ya existiese una base de datos asignada a este grupo.
  - Si existiese, se hace todo el flujo y solo se añaden los datos que no estuviesen guardados previamente.
  - Si no existiese, se crea una base de datos con el id del canal y se crean las colecciones **_Participants_**, **_Photos_** y **_Messages_** dentro de él.
    - En la colección de **_Participants_** estarán todos los datos relevantes obtenidos de los usuarios.
    - En la colección de **_Photos_** estarán todas las fotos de perfil obtenidas de las usuarios. Podemos discriminar a quien pertenece cada foto por el campo **_participantId_** que se corresponde con el _id del usuario dentro de la colección **_Participants_**.
    - En la colección de **_Messages_** estarán todos los mensajes de **_texto_** obtenidos según el límite indicando en el fichero [config.ini](config.ini).

Dependiendo de los ajustes de privacidad de cada usuario del canal/grupo se podrá extraer más o menos información de ellos.

## Trabajo futuro
- [ ] Realizar este mismo proceso sobre canales o grupos privados.
- [ ] Obtener y almacenar los mensajes que lleven contenido multimedia.
- [ ] Descargar todas las fotos de un usuario concreto almacenadas en la base de datos a un directorio local.
- [ ] Centralizar toda la información obtenida de un usuario concreto en diferentes grupos.
