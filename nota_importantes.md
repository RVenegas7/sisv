Nota importnte para el agente:

Vamos a dejar de ultimo el uso de la base de datos, mantendremos la base de datos original de oracle10g, para comenzar a migrar las ventanas, modernizar las ventanas actuales, en la carpeta capturas estaran las diferentes capturas de pantallas para analizarlas mejoralarlas modernizarlas. 

en la carpeta legancy_conf estara lo relacionado a las credenciales del sisitema viejo. o el tnsnames.ora 

El backend sera Django

El archivo models_legacy.py: Ejecuta el comando python manage.py inspectdb > vigilancia/models_legacy.py para extraer el mapa de las tablas.
Analizar las tablas extraídas por Django y ordenarlas por prioridades.Diseñar las nuevas pantallas web en base a las capturas de Centuria que me compartas.Escribir las primeras pruebas de lectura y escritura sin alterar el flujo del sistema.

En Agents actualmente:
## Stack del proyecto

- **Backend:** Django REST Framework (no creado aún).
- **Frontend:** React + Vite, consumo de API con Axios (no creado aún).
- **BD destino:** MariaDB 10.11 vía Docker Compose.
- **BD origen:** Oracle 10g en servidor openSUSE 11.4 (acceso por SSH con usuario de sistema `oracle`, privilegios DBA implícitos).

## Base de datos local (MariaDB vía Docker) - EN ACTIVO

se cambiara a:
## Stack del proyecto

- **Backend:** Django (Core) + Django REST Framework (no creado aún).
- **Frontend:** React + Vite, consumo de API con Axios (no creado aún).
- **BD destino:** PostgreSql vía Docker Compose.
- **BD origen:** Oracle 10g en servidor openSUSE 11.4 (acceso por SSH con usuario de sistema `oracle`, privilegios DBA implícitos).

## Base de datos local (MariaDB vía Docker) - no usar

hay que considerar la opcion mas viable y profesional.
