from fastapi import APIRouter, HTTPException
from database import ejecutar_sp
from schemas import MensajeWhatsApp

router = APIRouter(
    prefix="/webhook",
    tags=["WhatsApp Bot"]
)

@router.post("/mensaje")
async def recibir_mensaje(datos: MensajeWhatsApp):
    try:
        # 1. LLAMAMOS A TU SP: sp_ValidarAccesoWhatsapp
        # Recuerda que este SP devuelve: IdUsuario, PrimerNombre, EstadoActual
        usuario_info = ejecutar_sp("sp_ValidarAccesoWhatsapp", [datos.telefono])

        if not usuario_info:
            return {"reply": "Lo siento, no reconozco este número. Regístrate en nuestra web."}

        # Extraemos la info del primer resultado
        user = usuario_info[0]
        id_usuario = user['IdUsuario']
        nombre = user['PrimerNombre']
        estado_bot = user['EstadoActual']

        # 2. LÓGICA DE DECISIÓN (EL CEREBRO)
        mensaje_cliente = datos.mensaje.strip().lower()

        # CASO A: El usuario está libre y quiere registrar algo
        if estado_bot == 'IDLE':
            if "gasto" in mensaje_cliente or "ingreso" in mensaje_cliente:
                nuevo_estado = 'ESPERANDO_CONCEPTO'
                # Guardamos el cambio de estado en la DB
                ejecutar_sp("sp_ActualizarEstadoBot", [id_usuario, nuevo_estado, None])
                return {"reply": f"Hola {nombre}, ¡entendido! ¿En qué consistió el movimiento?"}
            else:
                return {"reply": f"Hola {nombre}, ¿en qué puedo ayudarte hoy? Escribe 'Gasto' para empezar."}

        # CASO B: Ya sabíamos que quería registrar algo y ahora nos dio el concepto
        elif estado_bot == 'ESPERANDO_CONCEPTO':
            nuevo_estado = 'ESPERANDO_MONTO'
            # Guardamos el concepto en DatosTemporales
            ejecutar_sp("sp_ActualizarEstadoBot", [id_usuario, nuevo_estado, datos.mensaje])
            return {"reply": f"Anotado: '{datos.mensaje}'. Ahora dime, ¿de cuánto fue el monto?"}

        # Aquí seguirían los demás estados...
        
    except Exception as e:
        # Si el SP lanzó el error 50001 (Usuario no registrado), lo manejamos aquí
        error_msg = str(e)
        if "Usuario no registrado" in error_msg:
            return {"reply": "¡Hola! Veo que no tienes una cuenta. Regístrate aquí: [Link]"}
        
        raise HTTPException(status_code=500, detail=error_msg)