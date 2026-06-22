# Proyecto para Laboratorio Clinico Veterinario LACLIVET UAGRM

### Flujo de trabajo correcto
```aiignore
git checkout develop
git pull origin develop
git checkout -b front/dashboard-propietarios
```

### Commits normales
```aiignore
git add .
git commit -m "feat: agregar vista de listado de propietarios"
git push -u origin front/dashboard-propietarios
```
## Abre el Pull Request en GitHub
* Ve a GitHub → tu repo → aparecerá un banner para crear el PR, o ve a Pull Requests → New Pull Request → base: develop ← compare: front/dashboard-propietarios
* Esto disparará automáticamente el job test del pipeline (si configuraste el workflow de tests en feature branches que vimos antes), y verás el estado del check directamente en el PR.
* Una vez aprobado y los checks pasen, mergea
* Desde GitHub, botón Merge pull request (puedes usar "Squash and merge" para mantener el historial limpio).
* Esto disparará automáticamente el deploy a staging.
* Cuando staging esté validado, promueve a producción

```bash
git checkout develop
git pull origin develop
git checkout -b release/v1.0  # opcional, o puedes ir directo develop → master
```
* Pull Requests → New Pull Request → base: master ← compare: develop
* Al mergear, dispara el deploy a producción.
## Agrega un workflow de tests para feature branches
* Esto te da feedback en cada push a una rama de feature, antes incluso de abrir el PR:
```bash
cd "/d/UAGRM/Semestre 1-2026/TALLER/ProyectoLaclivet"
ls .github/workflows/ 
```

## Resumen del flujo final
```aiignore
front/nueva-feature ──PR──→ develop ──(deploy auto a staging)
                                │
                                └──PR──→ master ──(deploy auto a producción)
```
