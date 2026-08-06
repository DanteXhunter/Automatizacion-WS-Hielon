> **Fase 5.1 — opcional, no bloquea producción (revisado 6-ago-2026).**
> Railway construye y despliega desde el repo sin Dockerfile. Este issue dejó
> de ser requisito para salir a producción y pasó a ser trabajo de aprendizaje
> y de portabilidad: sirve para no quedar amarrado a un proveedor y para
> levantar el stack completo en local. Hacerlo **después** de estar desplegado.

## Depende de

Nada. Es formación; se puede hacer en paralelo a cualquier fase y conviene
adelantarlo si hay tiempos muertos esperando a Meta. **Sigue siendo necesario**
para el issue #61 (n8n) y para entender qué hace Railway por debajo.

## Objetivo

Entender lo suficiente de Docker antes de copiar y pegar configuraciones que
no se comprenden.

## Temario mínimo

1. **Imagen vs contenedor**: la imagen es el molde inmutable, el contenedor es
   una instancia corriendo de esa imagen.
2. **Capas y caché de build**: cada instrucción del Dockerfile crea una capa;
   Docker reutiliza capas sin cambios. El orden de las instrucciones importa
   para no invalidar el caché en cada build.
3. **Dockerfile**: `FROM`, `COPY`, `RUN`, `CMD`/`ENTRYPOINT`, multi-stage
   builds.
4. **Volúmenes**: cómo persistir datos (la base de Postgres) fuera del ciclo
   de vida del contenedor.
5. **Redes de Docker Compose**: por qué los servicios se llaman entre sí por
   nombre (`postgres`, no `localhost`) dentro de la misma red compuesta.
6. **docker compose**: levantar varios servicios coordinados con un archivo.

## Ejercicio de validación

Antes de escribir el Dockerfile real (issue #53), debe poder explicarse sin
consultar nada:

- Por qué `COPY requirements.txt .` y el `RUN pip install` van **antes** de
  `COPY . .` en el Dockerfile
- Por qué la base de datos necesita un volumen y el backend no
- Qué pasa con los datos de Postgres si se hace `docker compose down` sin
  `-v`, y qué pasa si se agrega `-v`

## Recursos

- Documentación oficial de Docker (`docs.docker.com/get-started`)
- Play with Docker para practicar sin instalar nada localmente primero

## Criterio de aceptación

- [ ] Los 6 temas del temario quedan claros, no solo leídos
- [ ] Se puede responder las 3 preguntas del ejercicio sin buscar
- [ ] `docker run hello-world` funciona en la máquina local
