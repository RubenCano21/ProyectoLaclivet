# Runbook: Recrear Base de Datos (Staging / Producción)

Este documento describe el procedimiento seguro para borrar y recrear la base de datos
de la aplicación VetLab en Cloud SQL, evitando los errores comunes de:

- `password authentication failed for user "..."`
- `permission denied for schema public`
- Migraciones aplicadas parcialmente por falta de permisos

> ⚠️ **Este procedimiento BORRA TODOS LOS DATOS de la base indicada.**
> En producción, **jamás** ejecutar sin un respaldo (backup) previo confirmado.

---

## Variables de entorno por ambiente (confirmadas el 2026-06-23)

| Variable             | Staging                  | Producción                |
|----------------------|---------------------------|----------------------------|
| Instancia Cloud SQL  | `vetlab-db`               | `vetlab-db` ⚠️ **MISMA INSTANCIA** |
| Base de datos        | `vetlab_staging`          | `vetlab_prod`               |
| Usuario de la app    | `staging_user`            | `prod_user`                 |
| Secreto DATABASE_URL | `database-url-staging`    | `database-url-prod`         |
| Job de migración     | `migrate-job-staging`     | `migrate-job-prod`          |
| Región               | `us-central1`             | `us-central1`               |

> ⚠️ **ALERTA DE ARQUITECTURA**: Staging y producción comparten la MISMA instancia
> de Cloud SQL (`vetlab-db`, tier `db-f1-micro`, el más pequeño disponible). No hay
> aislamiento de instancia entre ambientes. Esto implica:
>
> - Un **typo en el nombre de la base** (`vetlab_prod` en vez de `vetlab_staging`, o
>   viceversa) en cualquier comando puede afectar el ambiente equivocado directamente.
>   **Siempre verificar dos veces el nombre de la base antes de un `delete`.**
> - El usuario admin `postgres` es compartido entre ambos ambientes — resetear su
>   password afecta el acceso admin a producción también.
> - Operaciones pesadas en staging (migraciones largas, conexiones múltiples) consumen
>   los mismos recursos limitados (`db-f1-micro`) que producción, pudiendo causar
>   lentitud perceptible en la app de producción mientras se trabaja en staging.
> - **Recomendación a futuro**: considerar separar producción a su propia instancia
>   cuando el presupuesto lo permita, para eliminar este riesgo de raíz.

Si se necesita reconfirmar estos valores en el futuro:
```bash
gcloud sql instances list
gcloud sql databases list --instance=vetlab-db
gcloud sql users list --instance=vetlab-db
gcloud secrets list
gcloud run jobs list --region=us-central1
```

---

## PASO 0 (SOLO PRODUCCIÓN): Respaldo antes de borrar

```bash
gcloud sql backups create \
  --instance=vetlab-db-prod \
  --description="Backup manual previo a recreación de BD $(date +%Y-%m-%d)"
```

Verifica que el backup se haya completado antes de continuar:

```bash
gcloud sql backups list --instance=vetlab-db-prod
```

También es recomendable exportar la base completa a un archivo `.sql` en un bucket de GCS, como respaldo adicional fuera del sistema de backups de Cloud SQL:

```bash
gcloud sql export sql vetlab-db-prod gs://TU_BUCKET/backups/vetlab_prod_$(date +%Y%m%d_%H%M%S).sql \
  --database=vetlab_prod
```

**No continuar al PASO 1 sin confirmar que el backup existe y es accesible.**

---

## PASO 1: Borrar y crear la base de datos

```bash
gcloud sql databases delete <NOMBRE_BD> --instance=<INSTANCIA>
gcloud sql databases create <NOMBRE_BD> --instance=<INSTANCIA>
```

Ejemplo (staging):
```bash
gcloud sql databases delete vetlab_staging --instance=vetlab-db
gcloud sql databases create vetlab_staging --instance=vetlab-db
```

---

## PASO 2: Otorgar permisos al usuario de la app

Conectarse como `postgres` (usuario admin de la instancia). Recomendado hacerlo desde
**Cloud Shell** (ya trae `psql` y `cloud-sql-proxy` preinstalados, evita instalar nada local):

```bash
gcloud sql connect <INSTANCIA> --user=postgres
```

Te pedirá la contraseña del usuario `postgres`. Si no la tienes, resetéala primero:

```bash
gcloud sql users set-password postgres \
  --instance=<INSTANCIA> \
  --password="UNA_PASSWORD_TEMPORAL_SEGURA"
```

Una vez dentro de `psql`, ejecutar **línea por línea** (no pegar todo de golpe, `\c` puede
romper el resto del bloque si se pega junto):

```sql
GRANT ALL PRIVILEGES ON DATABASE <NOMBRE_BD> TO <USUARIO_APP>;
```
Presiona Enter, confirma que diga `GRANT`.

```sql
\c <NOMBRE_BD>
```
Presiona Enter, confirma `You are now connected to database "..."`.

```sql
GRANT ALL ON SCHEMA public TO <USUARIO_APP>;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO <USUARIO_APP>;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO <USUARIO_APP>;
```

Salir:
```sql
\q
```

Ejemplo (staging):
```sql
GRANT ALL PRIVILEGES ON DATABASE vetlab_staging TO staging_user;
\c vetlab_staging
GRANT ALL ON SCHEMA public TO staging_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO staging_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO staging_user;
\q
```

---

## PASO 3: Sincronizar la password del usuario de la app con el secreto

Este es el paso que más fallos causó en staging — la base se recrea pero el usuario
de la app conserva (o pierde) una password distinta a la que está guardada en
Secret Manager, y Django falla con `password authentication failed`.

1. Ver la password que el secreto espera:
```bash
gcloud secrets versions access latest --secret=<SECRETO_DATABASE_URL>
```
Esto imprime algo como:
```
postgres://<USUARIO_APP>:<PASSWORD>@/<NOMBRE_BD>?host=/cloudsql/<CONEXION>
```
Copia exactamente el valor de `<PASSWORD>`.

2. Igualar la password real del usuario en Cloud SQL a esa password:
```bash
gcloud sql users set-password <USUARIO_APP> \
  --instance=<INSTANCIA> \
  --password="LA_PASSWORD_COPIADA_DEL_SECRETO"
```

> Si la password tiene caracteres especiales (`$`, `!`, `&`, etc.), ponla siempre entre
> comillas simples o dobles según tu shell para evitar que se interprete mal.

Ejemplo (staging):
```bash
gcloud secrets versions access latest --secret=database-url-staging
gcloud sql users set-password staging_user --instance=vetlab-db --password="grEsHIs7qAsptZRilyviZYSPQuLzcu7"
```

---

## PASO 4: Ejecutar el job de migración

```bash
gcloud run jobs execute <JOB_MIGRACION> --region=us-central1 --wait
```

Ejemplo (staging):
```bash
gcloud run jobs execute migrate-job-staging --region=us-central1 --wait
```

Si el job falla, revisar el log inmediatamente:
```bash
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=<JOB_MIGRACION>" \
  --limit=50 --format="value(textPayload)" --project=<PROJECT_ID>
```

---

## Checklist rápido — STAGING (copiar y pegar)

```bash
# === Variables ===
INSTANCIA="vetlab-db"
NOMBRE_BD="vetlab_staging"
USUARIO_APP="staging_user"
SECRETO="database-url-staging"
JOB_MIGRACION="migrate-job-staging"

# === Paso 1: recrear BD ===
gcloud sql databases delete $NOMBRE_BD --instance=$INSTANCIA
gcloud sql databases create $NOMBRE_BD --instance=$INSTANCIA

# === Paso 2: permisos (ejecutar dentro de psql, línea por línea) ===
gcloud sql connect $INSTANCIA --user=postgres
# GRANT ALL PRIVILEGES ON DATABASE vetlab_staging TO staging_user;
# \c vetlab_staging
# GRANT ALL ON SCHEMA public TO staging_user;
# ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO staging_user;
# ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO staging_user;
# \q

# === Paso 3: sincronizar password ===
gcloud secrets versions access latest --secret=$SECRETO
gcloud sql users set-password $USUARIO_APP --instance=$INSTANCIA --password="PEGAR_PASSWORD_DEL_SECRETO"

# === Paso 4: migrar ===
gcloud run jobs execute $JOB_MIGRACION --region=us-central1 --wait
```

---

## Checklist rápido — PRODUCCIÓN (copiar y pegar)

⚠️ **No ejecutar de corrido.** Revisar la salida de cada comando antes de continuar
al siguiente. Idealmente con una segunda persona revisando en pantalla compartida.

```bash
# === Variables ===
INSTANCIA="vetlab-db"
NOMBRE_BD="vetlab_prod"
USUARIO_APP="prod_user"
SECRETO="database-url-prod"
JOB_MIGRACION="migrate-job-prod"

# === Paso 0: BACKUP OBLIGATORIO — no continuar sin confirmar que termina OK ===
gcloud sql backups create --instance=$INSTANCIA \
  --description="Backup manual previo a recreacion $(date +%Y-%m-%d)"
gcloud sql backups list --instance=$INSTANCIA   # confirmar que aparece el backup nuevo

gcloud sql export sql $INSTANCIA gs://TU_BUCKET/backups/vetlab_prod_$(date +%Y%m%d_%H%M%S).sql \
  --database=$NOMBRE_BD

# === PAUSA: avisar al equipo que produccion quedara caida ===

# === Paso 1: recrear BD ===
# Verificar DOS VECES que NOMBRE_BD = vetlab_prod antes de ejecutar el delete
echo "Vas a borrar: $NOMBRE_BD en instancia: $INSTANCIA"
gcloud sql databases delete $NOMBRE_BD --instance=$INSTANCIA
gcloud sql databases create $NOMBRE_BD --instance=$INSTANCIA

# === Paso 2: permisos (ejecutar dentro de psql, línea por línea) ===
gcloud sql connect $INSTANCIA --user=postgres
# GRANT ALL PRIVILEGES ON DATABASE vetlab_prod TO prod_user;
# \c vetlab_prod
# GRANT ALL ON SCHEMA public TO prod_user;
# ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO prod_user;
# ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO prod_user;
# \q

# === Paso 3: sincronizar password ===
gcloud secrets versions access latest --secret=$SECRETO
gcloud sql users set-password $USUARIO_APP --instance=$INSTANCIA --password="PEGAR_PASSWORD_DEL_SECRETO"

# === Paso 4: migrar ===
gcloud run jobs execute $JOB_MIGRACION --region=us-central1 --wait

# === Paso 5: verificación end-to-end ===
# Probar login, lectura de datos criticos, endpoints clave ANTES de avisar
# al equipo que produccion esta de vuelta.
```

---

## Diferencias clave al aplicar esto en PRODUCCIÓN

1. **Backup obligatorio** (Paso 0) — no es opcional como en staging.
2. **Ventana de mantenimiento**: avisar a usuarios/equipo antes de borrar la BD de
   producción; la app quedará caída durante el proceso.
3. **Confirmar nombres reales** de instancia, base, usuario, secreto y job — no asumir
   que son los mismos que staging con el sufijo cambiado; verificar con los comandos
   de la sección "Variables de entorno por ambiente".
4. **Doble confirmación humana** antes de `gcloud sql databases delete` en producción
   (recomendado: pedir a otra persona del equipo que revise el comando antes de
   ejecutarlo).
5. Después de migrar, **verificar la aplicación end-to-end** (login, lectura de datos
   críticos) antes de cerrar la ventana de mantenimiento.
6. Si algo falla a mitad de camino, **restaurar desde el backup del Paso 0** en lugar
   de intentar reparar manualmente la base a medias:
   ```bash
   gcloud sql backups list --instance=<INSTANCIA>
   gcloud sql backups restore <BACKUP_ID> --restore-instance=<INSTANCIA>
   ```

---

## Causa raíz de los fallos documentados (referencia histórica)

- **Error:** `password authentication failed for user "staging_user"`
- **Causa:** Al recrear la base de datos con `gcloud sql databases create`, el usuario
  de la app (`staging_user`) y su password **no se ven afectados** — son independientes
  de la base de datos lógica. El fallo ocurrió porque la password real del usuario en
  Cloud SQL no coincidía con la que estaba guardada en el secreto `database-url-staging`
  (posiblemente desincronizada desde la creación inicial del usuario).
- **Solución aplicada:** Igualar la password del usuario en Cloud SQL a la que ya
  existía en el secreto, usando `gcloud sql users set-password` (Paso 3 de este runbook).
- **Lección:** Recrear la base de datos NO requiere tocar el usuario ni su password.
  Pero si surge un error de autenticación después de recrear la base, lo primero a
  revisar es la sincronía entre el secreto y la password real del usuario — no asumir
  que es un problema de permisos sin antes confirmar el mensaje exacto del error.
