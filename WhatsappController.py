from fastapi import APIRouter, HTTPException, Request, Response
from database import ejecutar_sp
import httpx

router = APIRouter(
    prefix="/webhook",
    tags=["WhatsApp Bot"]
)

# --- 1. CONFIGURACIÓN Y FUNCIÓN DE ENVÍO (DEBE IR ARRIBA) ---
TOKEN_META = "EAANvrLZC1sGEBRI2mRZC0MXQQsgIH1BfI58ULMk2KkVNXjsGZBCpjzk4IVBJSMnRbSzokHVhNKVaS2Jgl4PYxO3InosAmgj9Rzn0Gsr30LxOu1zwxpKe75ViJfzgJcrriN9SGA9KepJ2pR8FqXIEaCuivw3ZCybwZAKu0FyUZBfmKeZCSnC7FYiGaQgCcoxmMNbhypcrtSpxknvMaYtWdxUSenRHaBMjyItYPoRC1Gb5nVx7sDaCAZDZD"
ID_TELEFONO_META = "1115752214944142"

async def enviar_mensaje_whatsapp(telefono_destino, texto):
    url = f"https://graph.facebook.com/v18.0/{ID_TELEFONO_META}/messages"
    headers = {
        "Authorization": f"Bearer {TOKEN_META}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": telefono_destino,
        "type": "text",
        "text": {"body": texto}
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=data)
        if response.status_code != 200:
            print(f"❌ Error enviando mensaje a Meta: {response.text}")

# --- 2. ENDPOINT DE VERIFICACIÓN (GET) ---
@router.get("/mensaje")
async def verificar_webhook(request: Request):
    params = request.query_params
    token_verificacion = "MiproyectoGastos2026" 
    
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == token_verificacion:
        print("✅ Webhook verificado con Meta")
        return Response(content=str(challenge), media_type="text/plain")
    
    return Response(content="Error", status_code=403)

# --- 3. ENDPOINT DE RECEPCIÓN (POST) ---
@router.post("/mensaje")
async def recibir_mensaje(request: Request):
    body = await request.json()
    
    try:
        if "entry" in body:
            for entry in body["entry"]:
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    if "messages" in value:
                        for msg in value["messages"]:
                            telefono = msg.get("from")
                            mensaje_texto = msg.get("text", {}).get("body", "")
                            
                            mensaje_cliente = mensaje_texto.strip()
                            mensaje_lower = mensaje_cliente.lower()

                            # --- COMANDO CANCELAR ---
                            if "cancelar" in mensaje_lower:
                                usuario_info = ejecutar_sp("sp_ValidarAccesoWhatsapp", [telefono])
                                if usuario_info:
                                    ejecutar_sp("sp_ActualizarEstadoBot", [usuario_info[0]['IdUsuario'], 'IDLE', None])
                                respuesta = "✅ Registro cancelado. ¿Qué deseas hacer ahora?"
                                await enviar_mensaje_whatsapp(telefono, respuesta)
                                return {"status": "ok"}

                            # --- VALIDACIÓN DE ACCESO ---
                            usuario_info = ejecutar_sp("sp_ValidarAccesoWhatsapp", [telefono])
                            if not usuario_info:
                                respuesta = "❌ Hola, no estás registrado en el sistema."
                                await enviar_mensaje_whatsapp(telefono, respuesta)
                                return {"status": "ok"}

                            user = usuario_info[0]
                            id_usuario = user['IdUsuario']
                            nombre = user['PrimerNombre']
                            estado_bot = user['EstadoActual']
                            datos_previos = user['DatosTemporales']

                            # --- MÁQUINA DE ESTADOS ---
                            if estado_bot == 'IDLE':
                                if "gasto" in mensaje_lower or "ingreso" in mensaje_lower:
                                    id_tipo = 2 if "gasto" in mensaje_lower else 1
                                    tipo_txt = "Gasto" if id_tipo == 2 else "Ingreso"
                                    ejecutar_sp("sp_ActualizarEstadoBot", [id_usuario, 'ESPERANDO_CONCEPTO', str(id_tipo)])
                                    respuesta = f"Okey {nombre}, vamos a registrar un {tipo_txt}.💰 ¿Cuál es el concepto?"
                                    await enviar_mensaje_whatsapp(telefono, respuesta)
                                else:
                                    respuesta = f"Hola {nombre}, escribe 'Gasto' o 'Ingreso' para empezar."
                                    await enviar_mensaje_whatsapp(telefono, respuesta)

                            elif estado_bot == 'ESPERANDO_CONCEPTO':
                                combo_datos = f"{datos_previos}|{mensaje_cliente}"
                                ejecutar_sp("sp_ActualizarEstadoBot", [id_usuario, 'ESPERANDO_MONTO', combo_datos])
                                respuesta = f"📝 okey seria entonces '{mensaje_cliente}'. ¿De cuánto es el monto?"
                                await enviar_mensaje_whatsapp(telefono, respuesta)

                            elif estado_bot == 'ESPERANDO_MONTO':
                                try:
                                    monto = float(mensaje_lower.replace(',', '.'))
                                    partes = str(datos_previos).split('|')
                                    # [IdUsuario, Monto, Concepto, Tipo, Categoria, Fuente]
                                    parametros = [id_usuario, monto, partes[1], int(partes[0]), "General", "WhatsApp Bot"]
                                    
                                    ejecutar_sp("sp_RegistrarMovimiento", parametros)
                                    ejecutar_sp("sp_ActualizarEstadoBot", [id_usuario, 'IDLE', None])
                                    
                                    respuesta = f"¡Listo! He guardado tu registro de Q{monto:.2f}. 💵"
                                    Respuesta2 = "Deseas ingresar otro? Escribe Gastos o Ingreso para continuar 👀"
                                    await enviar_mensaje_whatsapp(telefono, respuesta)
                                    await enviar_mensaje_whatsapp(telefono, Respuesta2)
                                except Exception as e:
                                    print(f"Error en monto: {e}")
                                    respuesta = "❌ Monto inválido. Envía solo números (ej: 50.00)."
                                    await enviar_mensaje_whatsapp(telefono, respuesta)

        return {"status": "success"}
    except Exception as e:
        print(f"🔥 Error Crítico Webhook: {e}")
        return {"status": "error"}