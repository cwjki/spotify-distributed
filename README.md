# Proyecto Final de la Asignatura de Sistemas Distribuidos

## Tema: Distpotify (Spotify Distribuido)

### Estructura del proyecto

El proyecto está conformado por tres tipos de nodos: chord, spotify y client

-   Los nodos de tipo chord se encargan del almacenamiento de los datos, en nuestro caso las canciones con
    sus respectivos metadatos (título, autor, género). Estos nodos se basan en las funcionalidades descritas en el
    documento "Chord: A Scalable Peer-to-peer Lookup Service for Internet Application", permitiendo guardar y buscar canciones, además de la unión y abandono de nodos a la red sin que colapse el sistema.

-   Los nodos de tipo spotify son los encargados de recibir las peticiones de los nodos client, y comunicarse con los nodos de tipo chord para satisfacer las mismas.

-   Los nodos de tipo client se comunican solo con nodos de tipo spotify a los cuales realizan sus peticiones.

### Comunicación

Para la comunicación entre los nodos se hace uso de la
biblioteca Pyro4, la cual de forma sencilla permite el acceso
a los métodos y propiedades de otro nodo que se encuentre en la red. Se hizo uso además de un servidor de nombres para asignarles identificadores a los nodos a partir de su ip y puerto creando su proxy para evitar conocer la uri del mismo.

### Funcionalidades

El cliente puede realizar las siguientes peticiones a los
nodos spotify:

-   get_all_songs(): Retorna todas las canciones disponibles en
    el sistema

-   get_song(song_key): Retorna la canción asociada a una llave.
    La llave de cada canción está conformada por su título y autor.

-   save_song(song_key, song_value): Permite el almacenamiento de una canción en el sistema, song_value contiene los metadatos y el contenido de la canción a almacenar.

-   get_songs_by_author(author): Retorna de las canciones almacenadas aquellas que tengan en sus metadatos el 'autor'
    especificado.

-   get_songs_by_title(title): Retorna de las canciones almacenadas aquellas que tengan en sus metadatos el 'título'
    especificado.

-   get_songs_by_gender(gender): Retorna de las canciones almacenadas aquellas que tengan en sus metadatos el 'género'
    especificado.

### Sobre el sistema

-   Para el funcionamiento del sistema es necesario la existencia de, al menos, un nodo de tipo chord, un nodo de tipo
    spotify y uno de tipo client.

-   Para la visualización del proyecto se hizo uso del framework
    Flask para la creación de un sitio web en el cual probar las
    funcionalidades descritas.

-   Para distribuir el balance de las peticiones, los nodos client eligen de manera aleatoria entre los
    nodos spotify disponibles (spotify_nodes_list). Cada nodo spotify conoce en todo
    momento los nodos spotify activos, y al procesar una
    petición de los nodos client le envía a los mismos la disponibilidad de estos actualizada (spotify_nodes_list). De igual forma, si un cliente realiza una
    petición a un nodo spotify y este se encuentra inactivo,
    el nodo client intentará enviar la petición al próximo
    nodo spotify que tenga en su lista, hasta que la petición
    sea atendida o hasta que transcurran 20 segundos,
    donde se considera que no existe nodo spotify disponible
    para atender el pedido.

-   Los nodos spotify contienen tanto el id de un nodo chord
    como su lista de sucesores de forma tal que si el nodo chord se cae los nodos spotify se conectan a uno de los sucesores activos para continuar con la petición.
-   Cada nodo chord guarda las llaves almacenadas en su predecesor, para evitar la pérdida de datos en caso de que
    este se desconecte. De igual forma cada nodo chord está constantemente ejecutando un hilo que reestabiliza el sistema, actualizando su sucesor y su finger table.

### Ejecución del proyecto

Para la ejecución del proyecto primeramente se deben
instalar los paquetes necesarios:

```
pip install requirements.txt
```

Luego se inicia un servidor de nombres de Pyro

```
pyro4-ns
```

Luego se inicializa el primer nodo chord, el cual solo
necesita \<ip:port> y la cantidad de bits \<m>

```
python3 chord.py <ip:port> <m>
```

Los nodos de tipo chord restantes deben añadir como segundo parámetro el ip y puerto de un nodo chord
existente al cual le realizan la petición de join

```
python3 chord.py <ip:port> <ip_chord:port_chord> <m>
```

Luego se deben iniciar los nodos de tipo spotify, de igual
forma el primer nodo spotify solo necesita el \<ip:port>, un \<ip_chord:port_chord> de un nodo chord activo y \<m>
la cantidad de bits

```
python3 spotify.py <ip:port> <ip_chord:port_chord> <m>
```

Los nodos de tipo spotify restantes deben agragar el
\<ip_spotify:port_spotify> de un nodo spotify activo

```
python3 spotify.py <ip:port> <ip_spotify:port_spotify> <ip_chord:port_chord> <m>
```

Finalmente para iniciar los clientes, estos deben conocer el ip y puerto de uno de los nodos spotify activos \<ip_spotify:port_spotify>

```
python3 client.py <ip_spotify:port_spotify>
```

### Integrantes:

| Nombre(s) y Apellidos            | Grupo | Github       | Telegram      |
| -------------------------------- | ----- | ------------ | ------------- |
| Olivia González Peña             | C511  | @livi98      | @Livi_en_rose |
| Juan Carlos Casteleiro Wong      | C511  | @cwjki       | @Jki97        |
| Daniel Reynel Domínguez Ceballos | C511  | @Zondekallix | @gatoman      |
