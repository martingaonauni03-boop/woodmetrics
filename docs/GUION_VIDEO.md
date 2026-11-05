# Tarea 8 · Guion del video de administración MVC

Duración sugerida: 7–9 minutos. Grabar la aplicación funcionando, el código y el repositorio. Utilizar datos ficticios. Antes de grabar, publicar la aplicación y comprobar el acceso del docente al video.

## 0:00–0:45 · Presentación

“Soy Martin Gaona y esta es la administración MVC de WoodMetrics, mi proyecto de Ingeniería Web. El Core propuesto compara planes de corte de tableros para reducir desperdicio. En esta entrega muestro la administración que prepara sus datos: materiales, formatos, condiciones de corte, clientes y pedidos con sus piezas.”

Mostrar la URL real desplegada y el panel de inicio. Aclarar que el cálculo de planes pertenece a otra etapa.

## 0:45–1:30 · Arquitectura MVC y roles

“La aplicación utiliza Python, Flask y SQLite. El modelo está en `models.py`, las vistas son plantillas Jinja2 y los controladores están en `controllers.py`. Las reglas del negocio están separadas en `services.py`. El administrador gestiona catálogos y usuarios; el operador registra clientes, pedidos y piezas.”

Mostrar brevemente las carpetas, sin leer todo el código. Iniciar sesión como administrador. No grabar contraseñas ni secretos.

## 1:30–3:00 · Catálogos y relación dependiente

1. Mostrar las categorías Melamínicos y Contrachapados.
2. Abrir Tipos de tablero y explicar material, espesor y acabado.
3. Crear un formato con código `DEMO-1800`, largo 1800 y ancho 1200 mm.
4. Seleccionar Melamínicos: aparecen MDF y Aglomerado.
5. Cambiar a Contrachapados: aparece Plywood y se elimina una selección incompatible.
6. Guardar con Plywood, editar el formato y demostrar que la relación se conserva.

“No escribo el identificador de una categoría ni de un tipo de tablero. Elijo registros existentes y el segundo selector depende del primero. Además, el backend comprueba que el tipo realmente pertenezca a la categoría enviada.”

## 3:00–4:30 · Validación sensible en backend

Mostrar Configuraciones y el ancho de sierra de 3 mm.

“El ancho de sierra es un dato crítico: afecta el material perdido en cada corte. Por eso no se valida solamente con JavaScript. Antes de guardarlo, el servidor exige un número finito mayor que cero y máximo 20 mm.”

Mostrar `services.py`, función `number` y rama `settings`. Mostrar también la validación de contraseña y que el controlador utiliza `generate_password_hash`: no se guarda en texto plano.

Para probar de forma visible que el rechazo viene del servidor:

1. Abrir un formulario de configuración e ingresar un nombre nuevo, ancho de sierra 3 y mínimos 200 y 100.
2. En las herramientas de desarrollo, pestaña Elements, localizar el input `kerf`.
3. Quitar temporalmente el atributo `min` de ese input y escribir `-3` en el formulario. Mantener todos los demás campos válidos.
4. Guardar. Mostrar el mensaje del servidor y que la configuración no se agregó a la tabla.
5. Alternativamente, ejecutar las pruebas automatizadas y enseñar `test_server_rejects_invalid_sensitive_numbers`: envía directamente POST con valores cero, negativos, `nan`, infinito y texto, y verifica que no se guarda ningún registro.

No afirmes que un bloqueo del navegador demuestra backend. La evidencia debe mostrar la respuesta del servidor o las pruebas HTTP.

## 4:30–6:15 · Pedido que alimentará el Core

1. Mostrar o crear un cliente ficticio.
2. Crear un pedido seleccionando cliente y configuración desde los desplegables.
3. En Piezas, elegir ese pedido y el tipo MDF 18 mm, Roble natural.
4. Registrar 4 entrepaños de 590 × 490 mm, permitiendo giro.
5. Intentar registrar una pieza de 9000 × 9000 mm. El backend la rechaza porque no cabe en un formato habilitado de ese tipo.
6. Marcar el pedido Listo.
7. Editar la cantidad de una pieza y regresar a Pedidos: el estado vuelve a Borrador y la versión aumenta.

“Estos datos alimentarán el cálculo del Core: tipo, medidas, cantidad, giro, formato, sierra y mínimos reutilizables. El administrador prepara la información y el futuro motor comparará las distribuciones de corte.”

## 6:15–7:00 · Integridad y permisos

Intentar eliminar una categoría que tiene tipos de tablero: mostrar que se bloquea el borrado para no romper relaciones. Si dispones de un operador de prueba, iniciar sesión con él y mostrar que no tiene acceso a Usuarios ni Configuraciones. La restricción existe también en las rutas del backend.

## 7:00–8:00 · Git, README, pruebas y despliegue

Mostrar el repositorio `martingaonauni03-boop/woodmetrics`, su historial real de commits y el README. Mostrar la ejecución de las pruebas o el resultado real de Actions; no anunciar éxito si el workflow todavía no ha terminado.

“El README explica cómo instalar, crear el administrador, cargar datos ficticios, ejecutar las pruebas y desplegar. La aplicación está publicada en [leer la URL real]. Voy a guardar un registro desde esa dirección para comprobar que no estoy mostrando solo una maqueta local.”

## Cierre

“La administración MVC permite preparar los datos del Core, valida datos críticos en el servidor y maneja relaciones mediante selectores dependientes. El código está versionado y la aplicación puede revisarse desde los enlaces de la entrega.”

Usar esta frase final solo cuando el código esté subido y el despliegue esté verificado.

## Lista de comprobación antes de entregar

- [ ] Video con voz y pantalla legibles en Loom o YouTube.
- [ ] URL desplegada real visible y funcional.
- [ ] Prueba del rechazo backend y ausencia de inserción inválida.
- [ ] Selectores dependientes y validación de pertenencia.
- [ ] Relación de cada catálogo con el Core aprobado.
- [ ] Repositorio accesible, historial y README.
- [ ] Enlaces probados en una ventana sin sesión del autor, cuando corresponda.
- [ ] Sin contraseñas, tokens, correos reales de clientes ni secretos visibles.
