# Sistema de Validación Completo de DNI

## Resumen

Se ha implementado un sistema completo de validación de DNI en tres capas:

1. **Frontend (React/Zod)**: Validación instantánea mientras el usuario escribe
2. **Backend (Serializer)**: Validación antes de procesar los datos
3. **Modelo (Django)**: Validación final antes de guardar en la base de datos

## Validaciones Implementadas

### Frontend (client/pages/RegistroParticipantes.tsx)

#### Schema de Validación Zod

```typescript
const participantSchema = z.object({
  // ... otros campos
  dni: z
    .string()
    .min(1, "El DNI es requerido")
    .regex(/^\d{7,8}$/, "El DNI debe tener 8 dígitos numéricos")
    .transform((val) => val.replace(/\D/g, "").slice(0, 8)),
});
```

#### Input con Restricción en Tiempo Real

```tsx
<FormInput
  label="DNI"
  icon={<IdCard className="h-4 w-4" />}
  placeholder="12345678"
  {...register("dni")}
  error={getErrorMessage("dni")}
  maxLength={8}
  onInput={(e: React.FormEvent<HTMLInputElement>) => {
    const target = e.target as HTMLInputElement;
    target.value = target.value.replace(/\D/g, "").slice(0, 8);
  }}
/>
```

**Características:**
- Solo acepta dígitos numéricos (caracteres no numéricos son eliminados automáticamente)
- Máximo 8 caracteres
- Validación de formato 7-8 dígitos con regex
- Feedback inmediato al usuario

### Backend (api/serializers.py)

```python
def validate_dni(self, value):
    """Valida que el DNI tenga exactamente 8 dígitos numéricos"""
    if value:
        # Limpiar caracteres no numéricos
        dni_limpio = re.sub(r'\D', '', value)
        # Si tiene 9 dígitos y termina en 0, eliminar el último 0
        if len(dni_limpio) == 9 and dni_limpio.endswith('0'):
            dni_limpio = dni_limpio[:-1]
        # Validar que tenga exactamente 8 dígitos
        if len(dni_limpio) != 8 or not dni_limpio.isdigit():
            raise serializers.ValidationError('El DNI debe tener exactamente 8 dígitos numéricos.')
        return dni_limpio
    return value
```

**Características:**
- Limpia automáticamente caracteres no numéricos (puntos, guiones)
- Corrige DNIs con 9 dígitos terminados en 0 (error común en migraciones)
- Valida longitud exacta de 8 dígitos
- Retorna DNI limpio y normalizado

### Modelo (api/models.py)

```python
def clean(self):
    """Valida que el DNI tenga exactamente 8 dígitos numéricos"""
    super().clean()
    if self.dni:
        # Limpiar caracteres no numéricos
        dni_limpio = re.sub(r'\D', '', self.dni)
        # Si tiene 9 dígitos y termina en 0, eliminar el último 0
        if len(dni_limpio) == 9 and dni_limpio.endswith('0'):
            dni_limpio = dni_limpio[:-1]
        # Validar que tenga exactamente 8 dígitos
        if len(dni_limpio) != 8 or not dni_limpio.isdigit():
            raise ValidationError({
                'dni': 'El DNI debe tener exactamente 8 dígitos numéricos.'
            })
        # Actualizar el DNI limpio
        self.dni = dni_limpio

def save(self, *args, **kwargs):
    """Limpia y valida el DNI antes de guardar"""
    self.full_clean()
    super().save(*args, **kwargs)
```

**Características:**
- Última línea de defensa antes de guardar en la base de datos
- Misma lógica de limpieza y validación que el serializer
- Actualiza automáticamente el DNI con el valor limpio
- Se ejecuta automáticamente en cada `save()`

## Casos de Uso Cubiertos

### ✅ Casos Válidos

1. **DNI de 8 dígitos**: `12345678` → Aceptado
2. **DNI con puntos**: `12.345.678` → Limpiado a `12345678` y aceptado
3. **DNI con guiones**: `12-345-678` → Limpiado a `12345678` y aceptado
4. **DNI con 9 dígitos terminado en 0**: `123456780` → Limpiado a `12345678` y aceptado

### ❌ Casos Rechazados

1. **Email como DNI**: `correo@test.com` → Rechazado
2. **Teléfono como DNI**: `1523456789` → Rechazado (más de 8 dígitos)
3. **DNI muy corto**: `1234567` → Rechazado (7 dígitos, aunque se acepta en frontend para casos especiales)
4. **Texto arbitrario**: `abc123def` → Rechazado
5. **Vacío**: `` → Rechazado (campo requerido)

## Pruebas Realizadas

### Test Backend

```bash
cd backend
./env/bin/python /tmp/test_dni_validation.py
```

**Resultados:**
- ✅ DNI inválido (email) → Status 400
- ✅ DNI válido (8 dígitos) → Status 201
- ✅ DNI con 7 dígitos → Status 400
- ✅ DNI con 9 dígitos terminado en 0 → Status 201 (limpiado a 8 dígitos)

### Test Modelo

```python
from api.models import Asistente
asistente = Asistente(
    first_name='Test',
    last_name='Usuario',
    email='test@test.com',
    phone='123',
    dni='email@test.com',
    profile_type='VISITOR'
)
asistente.full_clean()  # → Lanza ValidationError
```

**Resultado:** ✅ ValidationError: "El DNI debe tener exactamente 8 dígitos numéricos."

### Test Serializer

```python
from api.serializers import AsistenteSerializer
serializer = AsistenteSerializer(data={
    'first_name': 'Test',
    'last_name': 'Usuario',
    'email': 'test@test.com',
    'phone': '123',
    'dni': 'correo@test.com',
    'profile_type': 'VISITOR'
})
serializer.is_valid()  # → False
serializer.errors  # → {'dni': ['El DNI debe tener exactamente 8 dígitos numéricos.']}
```

**Resultado:** ✅ Validación rechaza correctamente

## Pendientes

### ⚠️ Carga Masiva

Los endpoints de carga masiva actualmente utilizan `Asistente.objects.create()` directamente, lo que **sí pasa por la validación del modelo** gracias al método `save()` que ejecuta `full_clean()`.

**Ubicaciones:**
- `backend/api/views.py` línea ~530 (carga masiva formato 1)
- `backend/api/views.py` línea ~710 (carga masiva formato 2)

**Recomendación:** Aunque la validación del modelo protege estos casos, sería ideal refactorizar para usar el serializer y tener validación consistente en todos los puntos de entrada.

## Migración de Datos Existentes

Para limpiar DNIs existentes con datos inválidos, se debe ejecutar el script:

```bash
cd backend
./env/bin/python fix_dni.py
```

Este script:
1. Limpia DNIs con formato incorrecto (puntos, guiones)
2. Corrige DNIs con 9 dígitos terminados en 0
3. Asigna tokens de actualización a registros con DNIs inválidos
4. Permite a los usuarios actualizar su DNI mediante enlace único

Ver: [SISTEMA_VALIDACION_DNI.md](./SISTEMA_VALIDACION_DNI.md) para más detalles sobre el sistema de actualización de DNI.

## Resumen

✅ **Frontend:** Validación instantánea + restricción de entrada
✅ **Backend API:** Validación + limpieza en serializer
✅ **Modelo Django:** Validación final + limpieza antes de guardar
✅ **Tests:** Todos los casos de prueba pasando
⚠️ **Carga Masiva:** Protegida por validación del modelo, recomendable refactorizar

El sistema está **completamente funcional** y protege contra DNIs inválidos en todos los puntos de entrada.
