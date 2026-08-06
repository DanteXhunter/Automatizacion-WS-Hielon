## Depende de

Nada del código. Se puede provisionar en cualquier momento; solo requiere
cuenta de AWS.

## Objetivo

Levantar el servidor de producción en AWS.

## Especificación mínima

- Instancia `t3.small` o similar (2 vCPU, 2 GB RAM alcanza para este volumen)
- Ubuntu Server 22.04 LTS
- Docker y Docker Compose instalados
- IP elástica asignada, para que no cambie si la instancia se reinicia

## Security Group

| Puerto | Origen | Motivo |
|---|---|---|
| 22 (SSH) | Solo tu IP | Administración |
| 80 (HTTP) | 0.0.0.0/0 | Redirección a HTTPS |
| 443 (HTTPS) | 0.0.0.0/0 | Tráfico real, incluye el webhook |

**El puerto 5432 de Postgres NO debe exponerse a internet.** Solo el backend,
dentro de la misma red de Docker, necesita hablarle a la base. Un Postgres
público con credenciales débiles es de los vectores de compromiso más
comunes en despliegues mal configurados.

## Pasos

1. Crear la instancia desde la consola de AWS o CLI
2. Asignar y asociar la IP elástica
3. Conectar por SSH y correr el script de instalación de Docker
4. Clonar el repo (o transferir vía `scp`/CI, decidir el mecanismo)

## Criterio de aceptación

- [ ] Instancia corriendo con Docker funcional (`docker run hello-world`)
- [ ] Security group permite solo 22 (restringido), 80 y 443
- [ ] Confirmado que 5432 no es alcanzable desde fuera de la VPC
- [ ] IP elástica asociada y anotada
