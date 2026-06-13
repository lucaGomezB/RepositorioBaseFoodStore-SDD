Paso 1: Levantar ngrok
En una terminal aparte (dejála corriendo):
ngrok http 8000
Te va a mostrar una URL tipo https://xxxx-xxxx.ngrok-free.app.

Paso 2: Configurar APP_URL
En backend/.env, asegurate de tener:
APP_URL=https://xxxx-xxxx.ngrok-free.app
Reemplazá con la URL que te mostró ngrok.

Paso 3: Configurar el webhook en MercadoPago
1. Andá a https://www.mercadopago.com.ar/developers/panel/apps (https://www.mercadopago.com.ar/developers/panel/apps)
2. Seleccioná la app de Food Store
3. En Webhooks & IPN, agregá: https://xxxx-xxxx.ngrok-free.app/api/v1/pagos/webhook
4. Copiá el Webhook Secret que te dan y ponelo en backend/.env como:
MERCADOPAGO_WEBHOOK_SECRET=el-secreto-que-te-dio-mp

Paso 4: Verificar que el webhook responde
curl -X POST https://xxxx-xxxx.ngrok-free.app/api/v1/pagos/webhook ^
  -H "Content-Type: application/json" ^
  -d "{\"type\": \"test\", \"data\": {}}"
Debería responder {"status": "ok", "message": "..."}.

Paso 5: Probar flujo completo
- Iniciá el backend con uvicorn app.main:app --reload
- Hacé un pago desde el frontend con una tarjeta de prueba (las de docs/MERCADO_PAGO.md)
- MP te redirige post-pago, envía el webhook, y si todo funciona el pedido pasa a CONFIRMADO
- El KDS de cocina (/cocina) recibe el evento en tiempo real