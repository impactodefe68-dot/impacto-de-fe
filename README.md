# 🏠 De regreso a casa — Agente de publicación diaria

Publica **cada día a las 5:00 PM (hora de Venezuela)** una reflexión de la serie
**«De regreso a casa»** en **Instagram, TikTok y X**, en rotación automática.

## Formato de cada publicación (carrusel de 2 imágenes)

1. **Imagen 1 — El problema:** presenta la situación (tristeza, culpa, camino oscuro…)
   con una flecha verde **«dale a la otra →»**.
2. **Imagen 2 — La respuesta:** la reflexión + el versículo + la marca
   «De regreso a casa · Impacto de Fe · Reflexiones Cristianas».

En Instagram se publica como **carrusel** (deslizable), en X con las **2 imágenes**,
y en TikTok como un **video de 5 segundos** que muestra la imagen 1 y luego la 2.

## Cómo funciona

1. Una vez activado el cron, GitHub Actions ejecuta el agente a las 5:00 PM (Venezuela); las ejecuciones pueden retrasarse.
2. El agente toma la siguiente publicación de `publicaciones.json` (según `estado.json`).
3. Publica el carrusel en Instagram y X, y el video en TikTok.
4. Guarda el avance y pasa a la siguiente reflexión al día siguiente.

## Puesta en marcha (una sola vez)

### 1. Crear el repositorio en GitHub

1. En github.com → **New repository** → nombre: `impacto-de-fe` → **Public** → Create.
2. En el repo nuevo: **Settings → Deploy keys → Add deploy key**, pega la llave pública
   que te dé el asistente, marca **Allow write access** y guarda.
3. Avisa al asistente: él sube todo el código al repo.

### 2. Agregar los secretos (Settings → Secrets and variables → Actions)

| Secreto | De dónde sale |
|---|---|
| `IG_USER_ID` | ID de tu cuenta de Instagram (ver abajo) |
| `IG_ACCESS_TOKEN` | Token de larga duración de Meta (ver abajo) |
| `TIKTOK_ACCESS_TOKEN` | Token de la app de TikTok for Developers (ver abajo) |
| `TIKTOK_PRIVACY` | `PUBLIC_TO_EVERYONE` (o `SELF_ONLY` mientras TikTok aprueba la app) |
| `X_API_KEY` | developer.x.com → tu app |
| `X_API_SECRET` | developer.x.com → tu app |
| `X_ACCESS_TOKEN` | developer.x.com → Access Token (OAuth 1.0a, Read+Write) |
| `X_ACCESS_SECRET` | developer.x.com → Access Token (OAuth 1.0a, Read+Write) |

### 3. Instagram (Meta)

1. En Instagram, cambia tu cuenta a **Empresa/Creador** (Configuración → Tipo de cuenta).
2. Crea una **Página de Facebook** y vincúlala con la cuenta de Instagram.
3. En **developers.facebook.com** → **Create App** (tipo: Business) → agrega los productos
   **Facebook Login** e **Instagram**.
4. En **Graph API Explorer**, genera un token con los permisos:
   `instagram_basic`, `instagram_content_publish`, `pages_read_engagement`, `pages_manage_posts`.
5. En el **Access Token Debugger**, extiende el token a **larga duración** (60 días).
6. Tu **IG_USER_ID**: en Graph API Explorer, consulta `me/accounts` y luego
   `{id-de-la-pagina}?fields=instagram_business_account`.

> ⚠️ El token de Instagram dura 60 días: hay que renovarlo cada 2 meses
> (repetir el paso 5). El asistente te recuerda cómo.

### 4. TikTok

1. En **developers.tiktok.com** crea una app y agrega el producto **Content Posting API**.
2. Solicita los scopes `video.publish` y `user.info` y pasa la **auditoría** de TikTok
   (puede tardar algunos días).
3. Mientras la app no esté aprobada, usa `TIKTOK_PRIVACY = SELF_ONLY` (el video queda
   privado; la disponibilidad y el cambio de privacidad dependen de TikTok). Cuando aprueben, cambia a
   `PUBLIC_TO_EVERYONE` y el agente publica solo.

### 5. X (Twitter)

1. En **developer.x.com** crea un proyecto y una app.
2. En **User authentication settings**: **Read and write**.
3. Genera **API Key/Secret** y **Access Token/Secret** (OAuth 1.0a).
4. Pega los 4 valores en los secretos del repo.

### 6. Probar

El horario automático está desactivado inicialmente. Tras configurar las cuentas, en el repo: **Actions → Publicación diaria → Run workflow**. Si todo está bien,
verás ✔ Instagram / ✔ X / ✔ TikTok en el registro.

## Agregar más reflexiones

1. Pide al asistente nuevas ilustraciones (él las genera y les pone título + versículo).
2. Agrega la entrada en `publicaciones.json` con su `caption` y texto corto `x`.
3. Sube los archivos al repo (o pide al asistente que lo haga).

El agente las publica en orden y vuelve a empezar cuando se acaban.

**Antes de activar el horario:** verifica los resultados y habilita `schedule` en el workflow. El avance es compartido entre redes: si alguna falla y otra tiene éxito, se avanza igualmente; revisa el registro y publica manualmente en la red que falló. TikTok requiere aprobación y credenciales válidas. Solo hay cuatro reflexiones y se repetirán.
