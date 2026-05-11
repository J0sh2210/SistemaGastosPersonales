## Persly
Persly es un sistema financiero diseñado para simplificar el registro de gastos e ingresos diarios y analizar el estado financiero personal. El proyecto contiene la facilidad de acceso de un Bot de Whatsapp para capturar los datos en tiempo realn con un Dashbooard Web para gestionar presupuestos y visualizar estadísticas.

## Propuesta
El registro de movimientos diarios suele ser tedioso al necesitar una aplicación o un bloc de notas, el sistema Persly soluciona esta problematica permitiendo que el usuario registre movimientos facilmente a través de un chat de Whatsapp, enviando datos a una arquitectura en la nube.

## Arquitectura del Sistema 
* Backend: API REST Construida con FastAPI
* Base de datos: AZURE SQL Server gestionada a través de SQLAlchemy y Procedimientos almacenados
* Integración: Integra Meta Cloud API para manejar el Bot de Whatsapp funcionando a través de estados
* Infraestructura: Despliegue automatizado en Render mediante contenedor Docker

#Funcionalidades 
* Rápido registro: Flujo conversacional con el bot de manera dinámica
* Validación de identidad: Filtro de seguridad de número registrado
* Estados: Gestiona la posición en la que se encuentra el usuario en el flujo.
* Persistencia: Almacenamiento seguro con logs de auditoria.

## Desarrollo

* Completado: Integración Whatsapp, Registro movimientos, Despliegue Cloud (Render/Azure).
* En progreso : Dashboard Web, Estadísticas, Login con gmail authentication.




## Endpoints
<img width="1901" height="688" alt="image" src="https://github.com/user-attachments/assets/d43a2178-78e1-45d4-8733-a4cc5a285946" />

## Diagrama Base de datos
<img width="1158" height="821" alt="image" src="https://github.com/user-attachments/assets/23a43e0c-a9e4-43c4-b817-16aaf22834f1" />

## Flujo conversacional
<img width="907" height="1600" alt="WhatsApp Image 2026-05-11 at 1 08 03 AM" src="https://github.com/user-attachments/assets/1756af36-ff0b-4adf-b5cc-dca91c80bd4f" />


