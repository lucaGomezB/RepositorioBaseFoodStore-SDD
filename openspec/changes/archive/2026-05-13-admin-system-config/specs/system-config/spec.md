## ADDED Requirements

### Requirement: Admin puede ver configuraciones del sistema
El sistema DEBE permitir a un administrador ver todas las configuraciones disponibles.

#### Scenario: Listar configuraciones
- **WHEN** un admin hace GET a `/api/v1/admin/configuracion`
- **THEN** el sistema retorna HTTP 200 con un listado de pares clave-valor más descripción
- **THEN** cada ítem incluye: clave, valor, descripción, updated_at, updated_by

---

### Requirement: Admin puede modificar configuraciones
El sistema DEBE permitir a un administrador actualizar una o más configuraciones simultáneamente.

#### Scenario: Actualización exitosa
- **WHEN** un admin hace PUT a `/api/v1/admin/configuracion` con array de `{clave, valor}`
- **THEN** el sistema actualiza cada configuración en BD
- **THEN** registra el usuario que hizo el cambio y el timestamp
- **THEN** retorna HTTP 200 con las configuraciones actualizadas

#### Scenario: Clave inválida
- **WHEN** un admin intenta actualizar una clave que no existe
- **THEN** el sistema retorna HTTP 400 con mensaje indicando la clave inválida

---

### Requirement: Admin puede ver página de configuración en frontend
El sistema DEBE mostrar una página de configuración accesible desde el panel admin.

#### Scenario: Ver página de configuración
- **WHEN** un admin navega a `/configuracion`
- **THEN** se muestra un formulario con todas las configuraciones agrupadas
- **THEN** cada campo muestra su valor actual y un label descriptivo
- **THEN** hay un botón "Guardar cambios"

#### Scenario: Guardar cambios exitosamente
- **WHEN** un admin modifica valores y hace clic en "Guardar cambios"
- **THEN** se muestran los cambios en la UI inmediatamente (optimistic update)
- **THEN** se muestra un toast de éxito

#### Scenario: Error al guardar
- **WHEN** ocurre un error al guardar los cambios
- **THEN** se muestra un mensaje de error
- **THEN** los campos mantienen los valores editados (no se pierden)
