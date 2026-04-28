# Contributing to Food Store

¡Gracias por tu interés en contribuir! Este documento te guiará para hacer tu primera contribución.

---

## 🚀 Primeros pasos

1. **Fork** el repositorio
2. **Clone** tu fork: `git clone https://github.com/tu-usuario/food-store.git`
3. **Crear branch**: `git checkout -b feat/nombre-descriptivo`

---

## 📝 Convenciones de commits

Usamos [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(auth): add login with JWT refresh tokens
fix(orders): prevent negative stock on cancellation
docs(categories): update CTE recursion example
chore: add pytest fixtures for orders
test(payments): mock MercadoPago webhook response
refactor(products): extract repository methods
style(cart): adjust button spacing
perf: optimize database queries in product listing
```

### Tipos permitidos

| Tipo | Descripción |
|------|-------------|
| `feat` | Nueva funcionalidad |
| `fix` | Corrección de bug |
| `docs` | Cambios en documentación |
| `style` | Formato, espacios, etc. (sin lógica) |
| `refactor` | Refactor sin cambiar funcionalidad |
| `perf` | Mejoras de performance |
| `test` | Agregar o modificar tests |
| `chore` | Mantenimiento, dependencias, build |

---

## 🧪 Proceso de desarrollo

### Backend

```bash
cd backend
cp .env.example .env

# Setup
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Desarrollo
uvicorn app.main:app --reload

# Tests
pytest
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local

# Desarrollo
npm run dev

# Tests
npm run test
```

---

## 🔍 Code Review

Antes de abrir PR, asegurate de que:

- [ ] Los commits son pequeños y descriptivos
- [ ] El código sigue las convenciones del proyecto
- [ ] Los tests pasan (`pytest` / `npm run test`)
- [ ] No hay errores de lint (`npm run lint`)
- [ ] TypeScript compila sin errores (`npm run typecheck`)

---

## 📤 Abrir Pull Request

1. Push a tu branch: `git push origin feat/nombre-descriptivo`
2. Abrir PR en GitHub
3. Descripción del PR:
   - **Qué**: Resumen del cambio
   - **Por qué**: Motivación, problema que resuelve
   - **Cómo**: Resumen de la implementación
   - **Testing**: Cómo probaste el cambio

---

## 🐛 Reportar bugs

Usá [Issues](https://github.com/tu-usuario/food-store/issues) con:

- **Título claro**: resumen del problema
- **Descripción**: pasos para reproducir, comportamiento esperado vs real
- **Ambiente**: SO, versión de Node/Python, navegador
- **Logs**: cualquier error relevante

---

## 💡 Sugerir features

Abrí un Issue con la etiqueta `enhancement` y descript tu idea.

---

## 📖 Recursos

- [Conventional Commits](https://www.conventionalcommits.org/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [TanStack Query](https://tanstack.com/query)
- [Zustand](https://zustand-demo.pmnd.rs/)

---

**Gracias por contribuir a Food Store! 🚀**