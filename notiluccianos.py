# -*- coding: utf-8 -*-
"""
NotiLucciano's - el "diario" de joda de la oficina.
Manda por mail: NotiLucciano's (noticias truchas) + horoscopo laboral +
indices economicos + breves + recomendado + encuesta + meteorologo del cierre
+ frase celebre + cancion al azar de Spotify.
Se dispara A MANO desde GitHub Actions (Run workflow).
"""

import os
import sys
import base64
import random
import smtplib
from datetime import datetime, timedelta, timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

import requests

# =====================================================================
# CONFIGURACION
# =====================================================================

# ----- NotiLucciano's (las noticias de joda; las editamos cada viernes) -----
# Cada item es (VOLANTA, TITULAR, BAJADA, FOTO).
# FOTO es opcional: pone la URL de una imagen, o dejala como "" si no queres foto.
MOSTRAR_NOTILUCCIANOS = True

# Foto adjunta AL TWEET de la nota de tapa (la del grupo de running). Igual que las
# fotos de las noticias: nombre del archivo que esta en el repo (case-sensitive en
# GitHub Actions, que corre en Linux). Dejala en "" si no queres foto en el tweet.
FOTO_TWEET_TAPA = "AMOR RUNNER.jpeg"

# La nota de tapa (Mila & Matias) trae contenido rico (fichas de personajes, cita
# resaltada, alerta, tweet) que no entra en una bajada de una linea. Como el campo
# BAJADA admite HTML crudo, dejo toda esa nota aca, en una variable legible, y se la
# enchufo como bajada del item principal. Uso acentos directos (el archivo ya declara
# utf-8 arriba); conviven sin problema con los \uXXXX del resto.
NOTICIA_PRINCIPAL_BAJADA = """
<p style="font-size:16px; color:#333333; line-height:1.5; font-style:italic; margin:0 0 18px;">La nueva arquitecta platense y el hombre de costos m&aacute;s chamuyero de Lucciano's comparten isla de trabajo, salidas y ahora tambi&eacute;n kil&oacute;metros. Mientras tanto, Catalina observa. Y sus cejas lo dicen todo.</p>

<table cellpadding="0" cellspacing="0" border="0" style="width:100%; margin:0 0 20px;"><tr>
  <td style="width:33%; vertical-align:top; padding:3px;">
    <div style="background:#faf8f2; border:1px solid #e3ddcf; border-radius:6px; padding:12px 8px; text-align:center;">
      <div style="font-size:30px; line-height:1;">&#128105;&#8205;&#128188;</div>
      <div style="font-size:16px; font-weight:bold; color:#111111; margin-top:4px; font-family:Georgia,serif;">Mila</div>
      <div style="font-size:11px; color:#c0000a; font-weight:bold; text-transform:uppercase; letter-spacing:0.4px; margin:2px 0 8px; font-family:Arial,sans-serif;">&#128269; La nueva</div>
      <div style="font-size:12px; color:#555555; line-height:1.8; font-family:Arial,sans-serif;">&#128205; La Plata<br>&#127963;&#65039; Arquitecta<br>&#128197; Desde abril 2026<br>&#127874; ~30 a&ntilde;os<br>&#127939; Running (nuevo)</div>
    </div>
  </td>
  <td style="width:33%; vertical-align:top; padding:3px;">
    <div style="background:#faf8f2; border:1px solid #e3ddcf; border-radius:6px; padding:12px 8px; text-align:center;">
      <div style="font-size:30px; line-height:1;">&#128483;&#65039;</div>
      <div style="font-size:16px; font-weight:bold; color:#111111; margin-top:4px; font-family:Georgia,serif;">Mat&iacute;as</div>
      <div style="font-size:11px; color:#c0000a; font-weight:bold; text-transform:uppercase; letter-spacing:0.4px; margin:2px 0 8px; font-family:Arial,sans-serif;">&#9888;&#65039; El chamuyero</div>
      <div style="font-size:12px; color:#555555; line-height:1.8; font-family:Arial,sans-serif;">&#128188; &Aacute;rea de Costos<br>&#128197; Lleva 2 a&ntilde;os<br>&#127874; 25 a&ntilde;os<br>&#127939; Running (cl&aacute;sico)<br>&#128172; Labia: nivel 10/10</div>
    </div>
  </td>
  <td style="width:33%; vertical-align:top; padding:3px;">
    <div style="background:#fff4e6; border:2px solid #e67e00; border-radius:6px; padding:12px 8px; text-align:center;">
      <div style="font-size:30px; line-height:1;">&#128548;</div>
      <div style="font-size:16px; font-weight:bold; color:#111111; margin-top:4px; font-family:Georgia,serif;">Catalina</div>
      <div style="font-size:11px; color:#e67e00; font-weight:bold; text-transform:uppercase; letter-spacing:0.4px; margin:2px 0 8px; font-family:Arial,sans-serif;">&#128293; La que mira</div>
      <div style="font-size:12px; color:#555555; line-height:1.8; font-family:Arial,sans-serif;">&#128188; Contabilidad<br>&#127874; 27 a&ntilde;os (reci&eacute;n)<br>&#128065;&#65039; Todo lo ve<br>&#9995; Correa puesta<br>&#128544; Humor: variable</div>
    </div>
  </td>
</tr></table>

<p style="font-size:14px; color:#333333; line-height:1.6; margin:0 0 14px; font-family:Arial,sans-serif;">Cuando Mila lleg&oacute; desde La Plata en abril de este a&ntilde;o, nadie imaginaba que su historia en Lucciano's iba a volverse tema de redacci&oacute;n tan r&aacute;pido. Arquitecta, ronda los 30, nueva en la ciudad, nueva en la empresa. La sentaron en una isla de trabajo junto a Mat&iacute;as, el hombre de costos, y ah&iacute; empez&oacute; todo.</p>

<p style="font-size:14px; color:#333333; line-height:1.6; margin:0 0 14px; font-family:Arial,sans-serif;">Porque Mat&iacute;as no es cualquier compa&ntilde;ero de escritorio. Mat&iacute;as tiene labia. Mucha labia. La clase de labia que convierte una consulta sobre una factura en una conversaci&oacute;n de cuarenta minutos. Y esa misma labia fue la que, seg&uacute;n fuentes de esta redacci&oacute;n, lo tuvo durante semanas muy, muy entretenido con Catalina, de contabilidad: miraditas, toquecitos con excusa laboral, risitas que no necesitaban contexto. Catalina sab&iacute;a. Catalina sabe. Catalina siempre sabe.</p>

<div style="border-left:4px solid #c0000a; background:#fff8f8; padding:14px 18px; margin:18px 0; font-family:Georgia,serif; font-size:17px; font-style:italic; color:#222222; line-height:1.4;">&ldquo;La correa que Cata le tiene puesta a Mati fue lo que, en definitiva, le impidi&oacute; venderle el auto a Mila. Correa que salva honras.&rdquo;</div>

<p style="font-size:14px; color:#333333; line-height:1.6; margin:0 0 14px; font-family:Arial,sans-serif;">El cap&iacute;tulo del auto merece p&aacute;rrafo aparte. En un momento dado, circul&oacute; la versi&oacute;n de que Mat&iacute;as le iba a vender su veh&iacute;culo a Mila. Operaci&oacute;n que habr&iacute;a implicado encuentros, pruebas de manejo, negociaciones cara a cara. Sin embargo, un problema con la correa del motor dio por tierra con la transacci&oacute;n. Aunque en los pasillos de Lucciano's la teor&iacute;a m&aacute;s popular es otra: que la correa que realmente trab&oacute; la venta fue la que Cata le tiene puesta al cuello a Mat&iacute;as hace rato. Esa correa no falla.</p>

<div style="background:#fff4e6; border:1px solid #e67e00; border-radius:6px; padding:14px 16px; margin:18px 0;">
  <div style="font-size:13px; font-weight:bold; color:#b35e00; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:6px; font-family:Arial,sans-serif;">&#9888;&#65039; Alerta Catalina &mdash; Estado actual</div>
  <div style="font-size:14px; color:#444444; line-height:1.55; font-family:Arial,sans-serif;">Se la vio a Cata mirando con los ojos entrecerrados cada vez que Mila se acerca al escritorio de Mat&iacute;as. Fuentes confirman que el silencio de Cata en esos momentos &ldquo;es del tipo que asusta m&aacute;s que los gritos&rdquo;. Situaci&oacute;n: tensa y en escalada.</div>
</div>

<p style="font-size:14px; color:#333333; line-height:1.6; margin:0 0 14px; font-family:Arial,sans-serif;">Pero el cap&iacute;tulo m&aacute;s reciente &mdash; y el que encendi&oacute; todas las alarmas &mdash; lleg&oacute; esta semana. Mila se sum&oacute; al grupo de running en el que entrena Mat&iacute;as. Casualidad, dicen algunos. Estrategia, dicen otros. Kil&oacute;metros compartidos al amanecer, zapatillas y falta de excusas para estar juntos, responden los m&aacute;s duchos en estos asuntos. El running, ese deporte tan sano, tan inocente, tan conveniente.</p>

<p style="font-size:14px; color:#333333; line-height:1.6; margin:0 0 4px; font-family:Arial,sans-serif;">Lo que por ahora se desconoce es si fue iniciativa de &eacute;l, de ella, o de alg&uacute;n destino que claramente no ley&oacute; el bolet&iacute;n de Catalina. Lo que s&iacute; est&aacute; claro es que Cata ya sabe del grupo de running, y que su cara al enterarse fue la de alguien que est&aacute; mentalmente redactando un comunicado.</p>

<div style="margin-top:22px;">
  <div style="font-size:13px; font-weight:bold; color:#111111; text-transform:uppercase; letter-spacing:1px; margin-bottom:10px; font-family:Arial,sans-serif;">&#128038; Lo que se dice en las redes</div>
  <div style="border:1px solid #e1e8ed; border-radius:10px; padding:14px 16px; background:#ffffff; font-family:Arial,sans-serif;">
    <table cellpadding="0" cellspacing="0" border="0" style="margin-bottom:8px;"><tr>
      <td style="width:46px; vertical-align:top;"><div style="width:38px; height:38px; border-radius:50%; background:#c0000a; color:#ffffff; text-align:center; line-height:38px; font-weight:bold; font-size:15px;">BP</div></td>
      <td style="vertical-align:top; padding-left:8px;">
        <div style="font-size:14px; font-weight:bold; color:#111111;">Blas Polino</div>
        <div style="font-size:13px; color:#657786;">@BlasPolino</div>
      </td>
    </tr></table>
    <div style="font-size:14px; color:#222222; line-height:1.5; margin-bottom:10px;">acabo d darme cuenta q mila se metio al grupo d running d mati... cata si esto lo ves rez&aacute; porque yo no se como termina esto jajajaja igual mati sos un capo igual, desde la isla hasta las zapatillas todo junto <span style="color:#1da1f2;">#luccianos #running #diostecuide</span></div>
    __FOTO_TWEET__
    <div style="font-size:12px; color:#657786; border-bottom:1px solid #eeeeee; padding-bottom:8px; margin-bottom:8px;">9:42 AM - 24 Jun 2026 &middot; Twitter for iPhone</div>
    <div style="font-size:12px; color:#657786;">&#8629; Responder <strong>47</strong> &nbsp;&nbsp; &#128257; Retweetear <strong>312</strong> &nbsp;&nbsp; &#9733; Favorito <strong>891</strong></div>
  </div>
</div>
"""

NOTILUCCIANOS = [
    # ===== PRINCIPAL: nota de tapa Mila & Matias (su titular sale en la barra de "Urgente") =====
    ("\U0001F3C3 Urgente deportivo",
     "Del mismo escritorio al mismo grupo de running: Mila y Mat\u00edas, \u00bfcompa\u00f1eros o algo m\u00e1s?",
     NOTICIA_PRINCIPAL_BAJADA,
     ""),

    # ===== SECUNDARIA 1: guerra del aire =====
    ("\u00a1TERCERA GUERRA MUNDIAL!",
     "\u00bfEL FIN DE UNA ERA? TIEMBLA EL REINADO T\u00c9RMICO DE LA TIKITITAH",
     "Lo que arranc\u00f3 como una disputa diplom\u00e1tica por el termostato roto escal\u00f3 "
     "a conflicto abierto. Tras a\u00f1os de hegemon\u00eda t\u00e9rmica, la Tikititah vio "
     "amenazado su control absoluto del clima y Clari decidi\u00f3 romper el tratado de "
     "no proliferaci\u00f3n de fr\u00edo. Hubo movimiento de tropas (sweaters), inteligencia "
     "(\u201c\u00bfqui\u00e9n lo toc\u00f3?\u201d) y un alto el fuego que dur\u00f3 lo que un cubito al sol. "
     "La ONU no intervino: tambi\u00e9n ten\u00eda fr\u00edo. \u00bfHabr\u00e1 cascos azules para el "
     "viernes o esto termina en guerra de guerrillas a control remoto?",
     "GUERRA DECLARADA.jpeg"),

    # ===== SECUNDARIA 2: la siesta vs Messi =====
    ("ESC\u00c1NDALO DEPORTIVO",
     "SUE\u00d1O CON MESSI",
     "Parte de la secta no qued\u00f3 conforme con el delantero argentino de 39 a\u00f1os "
     "durante su presentaci\u00f3n ante Austria. El malestar fue tal que el cl\u00edmax del "
     "an\u00e1lisis t\u00e1ctico fue, lisa y llanamente, una \u00a1SIESTA! en pleno partido. "
     "Testigos aseguran haber escuchado un ronquido en el minuto 23. \u00bfFue protesta "
     "silenciosa contra el 10 o simple aburrimiento? \u00bfQui\u00e9n fue el del sue\u00f1o "
     "profundo? Y, sobre todo: \u00bfsab\u00eda que la c\u00e1mara lo estaba enfocando?",
     ""),

    # ===== SECUNDARIA 3: el histeriqueo =====
    ("AMOR EN LA OFICINA",
     "DOMADOR DE YEGUAS",
     "El lunes, durante el Cooling Break de Argentina-Austria, la oficina fue testigo "
     "de un nuevo episodio de cringe en cadena nacional. El histeriqueo entre parte "
     "de la secta y M. de marketing dej\u00f3 de ser novedad para volverse, directamente, "
     "rutina institucional. Ya hay quien propone agregarlo al organigrama. "
     "\u00bfHay sentimientos o es puro espect\u00e1culo para la tribuna? \u00bfPor qu\u00e9 siempre "
     "arranca justo en el momento de mayor audiencia? Y la pregunta del mill\u00f3n: "
     "\u00bfqui\u00e9n doma a qui\u00e9n?",
     ""),

    # ===== SECUNDARIA 4: la miseria aumenta =====
    ("LA MISERIA AUMENTA",
     "FERNET 1882 CON CUNNINGTON SIN GAS: EL FONDO DEL FONDO",
     "Fuentes informan que durante el fin de semana dos miembros del equipo fueron "
     "encontrados bebiendo Fernet 1882 con Cunnington cola sin gas, en lo que los "
     "especialistas describen como \u201cun nuevo piso hist\u00f3rico del poder "
     "adquisitivo\u201d. Lo positivo: ambos a\u00fan siguen con vida. Lo preocupante: "
     "afirman que \u201cno estaba tan mal\u201d. \u00bfRecorte de gastos, apuesta perdida o "
     "simple ca\u00edda libre del paladar? Noticia en desarrollo.",
     ""),
]

# ----- Breves / "Pas\u00f3 y no lo viste" -----
# Noticias de UNA linea, sin desarrollar. Sumar/editar como strings.
# Si la lista queda vacia, la seccion no se muestra.
MOSTRAR_BREVES = True
BREVES = [
    # "Ac\u00e1 va la primera breve.",
    # "Ac\u00e1 va la segunda.",
]

# ----- Horoscopo laboral -----
# Cada item es (SIMBOLO, SIGNO, PERSONAS, TEXTO).
MOSTRAR_HOROSCOPO = True
HOROSCOPO = [
    ("\u2653", "Piscis", "Bauti y Juan",
     "Vas a desconectarte mentalmente cerca de las 15:30 y mirar por la ventana "
     "un rato largo. La oficina sobrevivi\u00f3 sin vos esos veinte minutos. Todo bien."),
    ("\u264d", "Virgo", "Blas",
     "Vas a encontrar UN error en una planilla ajena y no vas a poder pensar en "
     "otra cosa el resto del d\u00eda. Tu perfeccionismo es un don y una condena."),
    ("\u2648", "Aries", "Clari",
     "Tu impulsividad te va a llevar a responder un mail antes de leerlo entero. "
     "Spoiler: la info que necesitabas estaba en el tercer rengl\u00f3n. Respir\u00e1 "
     "antes de tocar \u201cEnviar\u201d."),
    ("\u2649", "Tauro", "Dani",
     "Semana de aferrarte a lo conocido. Alguien va a sugerir \u201ccambiar el "
     "proceso\u201d y vos vas a defender el Excel del 2019 con tu vida. Hac\u00e9s bien."),
    ("\u264c", "Leo", "Agus",
     "Necesit\u00e1s reconocimiento y esta semana no va a llegar. Tu obra maestra "
     "\u2014ese reporte impecable\u2014 va a pasar sin un solo \u201cgracias\u201d. "
     "Guardalo igual, alg\u00fan d\u00eda lo van a valorar."),
]

# ----- Indices economicos -----
MOSTRAR_INDICES = True

# Panel lider LUCC: cada "accion" es (PERSONA, VARIACION_%).
# Positivo = sube (verde), negativo = baja (rojo). Se ordena solo de mayor a menor.
LUCC_ACCIONES = [
    ("Bauti", 18),
    ("Dani", 10),
    ("Blas", 4),
    ("Clari", -12),
    ("Agus", -20),
    ("Juan", -25),
]

# Copete narrado del LUCC (redaccion acomodada).
LUCC_COPETE = (
    "El \u00edndice LUCC cerr\u00f3 la semana en baja. Entre las subas, Dani trep\u00f3 un "
    "10% tras cerrar el cashflow sin complicaciones y Blas sum\u00f3 un 4% por alinear los planetas en USA. "
    "El gran ganador de la rueda fue Bauti, que escal\u00f3 un 18% luego de asesinar "
    "al equipo de conteo de inventario en Europa. Del lado de las "
    "p\u00e9rdidas, Clari retrocedi\u00f3 un 12% por riesgo de pianel, Agus cedi\u00f3 otro "
    "20% tras conseguir peores precios en todas las unidades de negocio del 2026, y "
    "Juan se desplom\u00f3 un 25% despu\u00e9s de pelearse en forma definitiva con la IA y "
    "con Payway."
)

# Sub-indices: cada item es (NOMBRE, VALOR, GLOSA).
INDICES_SECUNDARIOS = [
    ("Volumen del Grupo de WhatsApp", "312 mensajes operados",
     "S\u00f3lo 4 con valor real. El resto, ruido de mercado."),
    ("\u00cdndice de Confianza en que \u201cel viernes lo cerramos\u201d (ICVC)", "3,2 / 100",
     "M\u00ednimo hist\u00f3rico."),
    ("\u00cdndice de Sensaci\u00f3n T\u00e9rmica de Oficina", "40\u00b0C",
     "La temperatura real es 5\u00b0C, pero la Tikitita tiene calor."),
    ("Riesgo Shares", "5180 pts",
     "Sin techo a la vista."),
]

# ----- Meteorologo del cierre contable -----
MOSTRAR_METEO_CIERRE = True
METEO_CIERRE = (
    "Alerta naranja: se aproxima el cierre con un frente de facturas sin imputar. "
    "Tormenta de conciliaciones para este viernes."
)

# ----- Encuesta de la semana -----
# Resultados ya cargados. Cada opcion es (TEXTO, PORCENTAJE).
MOSTRAR_ENCUESTA = True
ENCUESTA_PREGUNTA = "\u00bfLa oficina est\u00e1 fr\u00eda?"
ENCUESTA_OPCIONES = [
    ("S\u00ed", 12),
    ("No", 8),
    ("Dejen de tocar el aire", 80),
]

# ----- Recomendado del editor -----
MOSTRAR_RECOMENDADO = True
RECOMENDADO_ESTRELLAS = 5
RECOMENDADO_TITULO = "Los sorrentinos de Agus"
RECOMENDADO_TEXTO = (
    "Calabaza y muzzarella en su punto justo, masa de autor y un relleno que pide "
    "pista. Cinco estrellas al plato\u2026 y una sola al costo por unidad: parece que "
    "a \u00e9l tambi\u00e9n el proveedor se los vende caros."
)

# ----- Empleado de la semana (apartado destacado, NO es una noticia) -----
MOSTRAR_EMPLEADO = True
EMPLEADO_NOMBRE = "Blas"
EMPLEADO_TEXTO = (
    "El d\u00eda martes trabaj\u00f3 nada m\u00e1s ni nada menos que 7 (siete) segundos. "
    "Impecable desempe\u00f1o, sin un solo error en todo ese lapso. La eficiencia "
    "hecha persona. Desde la redacci\u00f3n destacamos el compromiso y esperamos que "
    "el r\u00e9cord se sostenga\u2026 o se supere a la baja."
)

# ----- Frase de la semana -----
# Frases reales y celebres de figuras del espectaculo/deporte argentino.
# Cada corrida elige una al azar. Cada item es (FRASE, AUTOR). Suma las que quieras.
MOSTRAR_FRASE = True
FRASES = [
    # --- Diego Maradona ---
    ("La pelota no se mancha", "Diego Maradona"),
    ("Me cortaron las piernas", "Diego Maradona"),
    ("Se le escap\u00f3 la tortuga", "Diego Maradona"),
    ("Ganarle a River es como que tu vieja te despierte con un beso", "Diego Maradona"),
    ("A Toresani, Segurola y Habana 4310, s\u00e9ptimo piso; y vamos a ver si me dura treinta segundos", "Diego Maradona"),
    ("Tengo menos piernas que una foto carnet", "Diego Maradona"),
    ("M\u00e1s falso que d\u00f3lar celeste", "Diego Maradona"),
    ("L\u00e1stima no se le tiene a nadie, maestro", "Diego Maradona"),
    ("Si voy al banco es para sacar plata, fiera", "Diego Maradona"),
    # --- Moria Cas\u00e1n ---
    ("\u00bfQui\u00e9nes son?", "Moria Cas\u00e1n"),
    ("Si quer\u00e9s llorar, llor\u00e1", "Moria Cas\u00e1n"),
    ("Sos un helado de pollo, no exist\u00eds", "Moria Cas\u00e1n"),
    ("A llorar al campito", "Moria Cas\u00e1n"),
    ("\u00a1Se calla el decorado!", "Moria Cas\u00e1n"),
    # --- Mirtha Legrand ---
    ("Como te ven, te tratan", "Mirtha Legrand"),
    # --- Ricardo Fort ---
    ("\u00a1Mam\u00e1, cortaste toda la looz!", "Ricardo Fort"),
    ("Yo no manejo el rating, yo manejo un Rolls Royce", "Ricardo Fort"),
    ("Yendo o llendo, da igual: voy arriba de mi Rolls Royce", "Ricardo Fort"),
    ("\u00a1Mam\u00e1, metiste el cutucuchillo!", "Ricardo Fort"),
    # --- Susana Gim\u00e9nez ---
    ("Un dinosaurio\u2026 \u00bfvivo?", "Susana Gim\u00e9nez"),
    # --- Espect\u00e1culo / humor ---
    ("Vermouth con papas fritas y\u2026 good show", "Tato Bores"),
    ("Billetera mata gal\u00e1n", "Jacobo Winograd"),
    ("No me peguen, soy Giordano", "Roberto Giordano"),
    ("Parece que quieren hacer bowling conmigo", "Vicky Xipolitakis"),
    # --- Deporte ---
    ("Me gusta tanto la noche que al d\u00eda le pondr\u00eda un toldo", "Bambino Veira"),
    ("Pusimos un micro en el arco y entr\u00f3 por la ventanilla", "Bambino Veira"),
    ("\u00bfEst\u00e1 crazy, Macaya?", "Marcelo Araujo"),
    ("La experiencia es un peine que te regalan cuando te qued\u00e1s pelado", "Ringo Bonavena"),
    ("\u00bfCu\u00e1ntos pulmones tengo? Uno, como todo el mundo", "Mostaza Merlo"),
    # --- Pol\u00edtica (frases hist\u00f3ricas del folclore) ---
    ("S\u00edganme, no los voy a defraudar", "Carlos Menem"),
    ("La casa est\u00e1 en orden", "Ra\u00fal Alfons\u00edn"),
    ("Soy lo mejor que le puede pasar al pa\u00eds", "Fernando de la R\u00faa"),
    ("El que deposit\u00f3 d\u00f3lares recibir\u00e1 d\u00f3lares", "Eduardo Duhalde"),
    ("Hacia fin de siglo la deuda externa ser\u00e1 insignificante", "Domingo Cavallo"),
]

# ----- Cancion (Spotify) -----
# Cada corrida elige UN artista al azar de esta lista y de ahi un tema al azar
# de su catalogo real. Edita la lista con los artistas que quieras.
ARTISTAS = [
    "Ariana Grande", "Tan Bionica", "Airbag", "Tini",
    "One Direction", "Taylor Swift", "Justin Bieber", "Shakira",
]

# ----- Colores (estilo "portal de noticias") -----
COLOR_HEADER  = "#c0000a"   # rojo bordo (header, tags de seccion)
COLOR_SECCION = "#c0000a"   # idem, para tags
COLOR_ACENTO  = "#ffd700"   # dorado
COLOR_OSCURO  = "#1a1a1a"   # negro de barras
COLOR_BORDE   = "#8a0007"   # rojo mas oscuro (bordes)
COLOR_TEXTO   = "#222222"
COLOR_FONDO   = "#f5f4f0"   # crema (fondo)
COLOR_CAJA    = "#fff8f8"   # rosa muy claro (caja de la frase)
COLOR_SUBA    = "#1a8a1a"   # verde (sube)
COLOR_BAJA    = "#c0000a"   # rojo (baja)
COLOR_NARANJA = "#e07b00"   # alerta meteorologica

# ----- Marca / cabecera (logo + bandera) -----
# Hay DOS formas de poner el logo. El script usa la primera que encuentre:
#
#  1) LOGO_FILE  -> archivo local del repo. RECOMENDADO (y obligatorio si el
#     repo es PRIVADO). El logo se ADJUNTA dentro del mail (Content-ID), asi
#     que no depende de ningun hosting ni de que el repo sea publico. Como el
#     script corre en GitHub Actions, el repo se clona entero y el archivo
#     queda disponible al lado del .py.
#
#  2) LOGO_URL   -> URL publica de la imagen. Solo sirve si la imagen es
#     accesible SIN login (repo publico, CDN, etc.). En repos privados NO anda.
#
# Si las dos quedan vacias, se muestra solo el wordmark de texto, como antes.
LOGO_FILE = "luccianos-logo-png_seeklogo-480057.png"
LOGO_URL  = ""
LOGO_ALTO = 44            # alto del logo en px dentro del header
# El logo va sobre una "pastilla" blanca para que contraste sobre el rojo del header.
# Poné False si tu logo ya tiene fondo propio o lo querés sin recuadro.
LOGO_PASTILLA   = True
MOSTRAR_WORDMARK = True   # mostrar el texto "NOTILUCCIANO'S" debajo del logo

# Bandera argentina. Usamos IMAGEN y no el emoji \U0001F1E6\U0001F1F7 porque en
# Windows/Outlook el emoji de bandera se ve como las 2 letras ("AR").
MOSTRAR_BANDERA = True
BANDERA_AR_URL  = "https://flagcdn.com/w40/ar.png"

# Content-ID interno para el logo adjunto (no lo toques salvo que sepas que hacés).
_LOGO_CID = "logo_noti"

# =====================================================================
# SECRETOS (vienen de los GitHub Secrets)
# =====================================================================

GMAIL_USER         = os.environ.get("GMAIL_USER")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")
MAIL_TO            = os.environ.get("MAIL_TO", GMAIL_USER)

SPOTIFY_CLIENT_ID     = os.environ.get("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")


def faltan_secretos():
    return [n for n, v in [
        ("GMAIL_USER", GMAIL_USER), ("GMAIL_APP_PASSWORD", GMAIL_APP_PASSWORD),
    ] if not v]


# =====================================================================
# DATOS (Spotify)
# =====================================================================

def _spotify_token():
    if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
        return None
    try:
        auth = base64.b64encode(f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()).decode()
        r = requests.post(
            "https://accounts.spotify.com/api/token",
            headers={"Authorization": f"Basic {auth}",
                     "Content-Type": "application/x-www-form-urlencoded"},
            data={"grant_type": "client_credentials"}, timeout=12)
        if r.ok:
            return r.json().get("access_token")
        print(f"[AVISO] Spotify token devolvio {r.status_code}: {r.text[:200]}")
    except Exception as e:
        print(f"[AVISO] No pude obtener token de Spotify: {e}")
    return None


def _spotify_get(url, token, params=None):
    try:
        r = requests.get(url, headers={"Authorization": f"Bearer {token}"}, params=params, timeout=12)
        if r.ok:
            return r.json()
        print(f"[AVISO] Spotify GET {url.split('/')[-1]} devolvio {r.status_code}: {r.text[:150]}")
        return None
    except Exception as e:
        print(f"[AVISO] Spotify GET fallo ({url}): {e}")
        return None


def obtener_cancion():
    if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
        print("[AVISO] Faltan credenciales de Spotify. No muestro cancion.")
        return None

    artista = random.choice(ARTISTAS)  # uno distinto cada corrida
    rng = random.Random()

    token = _spotify_token()
    if not token:
        print("[AVISO] Spotify no devolvio token (revisar credenciales). No muestro cancion.")
        return None

    try:
        bus = _spotify_get("https://api.spotify.com/v1/search", token,
                           {"q": artista, "type": "artist", "limit": 1, "market": "AR"})
        items = (bus or {}).get("artists", {}).get("items", [])
        if not items:
            print(f"[AVISO] No encontre al artista '{artista}' en Spotify.")
            return None
        artista_id = items[0]["id"]
        artista_nombre = items[0].get("name", artista)

        albs = _spotify_get(f"https://api.spotify.com/v1/artists/{artista_id}/albums", token,
                            {"market": "AR", "include_groups": "album", "limit": 10})
        albumes = (albs or {}).get("items", [])
        if not albumes:
            print(f"[AVISO] '{artista_nombre}' no devolvio albumes.")
            return None
        album = rng.choice(albumes)
        imgs = album.get("images", [])
        portada = imgs[0]["url"] if imgs else ""

        trks = _spotify_get(f"https://api.spotify.com/v1/albums/{album['id']}/tracks", token,
                            {"market": "AR", "limit": 10})
        tracks = (trks or {}).get("items", [])
        if not tracks:
            print(f"[AVISO] El album elegido de '{artista_nombre}' no devolvio temas.")
            return None
        t = rng.choice(tracks)

        print(f"[INFO] Cancion: '{t.get('name')}' - {artista_nombre}")
        return {
            "titulo": t.get("name", ""),
            "artista": artista_nombre,
            "link": t.get("external_urls", {}).get("spotify", ""),
            "portada": portada,
        }
    except Exception as e:
        print(f"[AVISO] No pude obtener la cancion de Spotify: {e}")
        return None


# =====================================================================
# ARMADO DEL HTML
# =====================================================================

def _tag_seccion(texto):
    """Tag rojo de seccion, reutilizable."""
    return (f'<span style="display:inline-block; background:{COLOR_HEADER}; color:#ffffff; '
            f'font-size:10px; font-weight:bold; text-transform:uppercase; letter-spacing:1.5px; '
            f'padding:3px 10px; font-family:Arial,Helvetica,sans-serif;">{texto}</span>')


def _resolver_logo():
    """Decide de donde sale el logo. Devuelve (src_para_el_img, ruta_a_adjuntar).
    - Si LOGO_FILE existe en disco -> ('cid:...', ruta)  (se adjunta al mail).
    - Si no, pero hay LOGO_URL      -> (LOGO_URL, None).
    - Si no hay nada                -> ('', None).
    La ruta se resuelve relativa a este .py, asi anda sin importar desde donde
    se ejecute (en GitHub Actions el working dir es la raiz del repo)."""
    if LOGO_FILE:
        ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), LOGO_FILE)
        if os.path.exists(ruta):
            return (f"cid:{_LOGO_CID}", ruta)
        print(f"[AVISO] No encontre el archivo del logo: {ruta}. Pruebo con LOGO_URL.")
    if LOGO_URL:
        return (LOGO_URL, None)
    return ("", None)


# Fotos de las noticias que hay que adjuntar inline al mail (se llena al armar el
# HTML). Cada item es (cid, ruta_en_disco). Misma logica que el logo: en repo
# PRIVADO la unica forma de que la imagen se vea es empotrarla por Content-ID.
_FOTOS_ADJUNTAS = []


def _resolver_foto(foto):
    """Decide de donde sale la foto de una noticia. Devuelve el src para el <img>.
    - "" o None              -> "" (la noticia no muestra foto).
    - empieza con http(s)    -> la URL tal cual (solo sirve si es PUBLICA).
    - archivo local que existe -> 'cid:...' y lo registra para adjuntarlo inline.
      Esta es la unica via que anda en repo PRIVADO (igual que el logo).
    - archivo local que NO existe -> aviso y "" (no rompe el mail, saltea la foto).
    La ruta se resuelve relativa a este .py, asi anda desde donde sea que se ejecute."""
    if not foto:
        return ""
    if foto.startswith("http://") or foto.startswith("https://"):
        return foto
    ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), foto)
    if os.path.exists(ruta):
        cid = f"foto_noti_{len(_FOTOS_ADJUNTAS)}"
        _FOTOS_ADJUNTAS.append((cid, ruta))
        return f"cid:{cid}"
    print(f"[AVISO] No encontre la foto de la noticia: {ruta}. La salteo.")
    return ""


def _bloque_foto_tweet():
    """HTML de la imagen adjunta al tweet de la nota de tapa (estilo 'foto de Twitter':
    ancho completo de la tarjeta, esquinas redondeadas). Reutiliza _resolver_foto, asi
    que en repo PRIVADO la imagen tambien viaja inline por Content-ID.
    Devuelve "" si FOTO_TWEET_TAPA esta vacio o el archivo no existe -> el tweet sale
    sin foto y NO se rompe el mail."""
    if not FOTO_TWEET_TAPA:
        return ""
    src = _resolver_foto(FOTO_TWEET_TAPA)
    if not src:
        return ""
    return (
        '<div style="margin:2px 0 10px;">'
        f'<img src="{src}" alt="Mila y Mat&iacute;as, grupo de running" '
        'style="display:block; width:100%; max-width:100%; height:auto; '
        'border-radius:14px; border:1px solid #e1e8ed;"></div>'
    )


def _caja_notiluccianos():
    if not MOSTRAR_NOTILUCCIANOS or not NOTILUCCIANOS:
        return ""
    notas = ""
    for nota in NOTILUCCIANOS:
        volanta, titular, bajada = nota[0], nota[1], nota[2]
        # Si la bajada trae el token de foto del tweet, lo cambiamos por el <img> real.
        # Va condicionado a "if token in bajada" a proposito: asi _resolver_foto (que
        # registra el CID a adjuntar) corre UNA sola vez, y no en cada vuelta del for.
        if "__FOTO_TWEET__" in bajada:
            bajada = bajada.replace("__FOTO_TWEET__", _bloque_foto_tweet())
        foto = nota[3] if len(nota) > 3 else ""
        foto_src = _resolver_foto(foto)

        # El texto de la bajada (mismo estilo tenga o no foto).
        bajada_html = (f'<div style="font-size:14px; color:#444444; line-height:1.55; '
                       f'font-family:Arial,Helvetica,sans-serif;">{bajada}</div>')

        if foto_src:
            # Con foto: tabla de 2 columnas -> foto chica a la IZQUIERDA, texto a la
            # derecha. Se usa tabla (no float/flex) porque es lo unico que respetan
            # todos los clientes de mail, Outlook incluido. ANCHO_FOTO controla el tamano.
            ANCHO_FOTO = 130
            cuerpo = (
                f'<table cellpadding="0" cellspacing="0" border="0" style="width:100%;">'
                f'<tr>'
                f'<td style="width:{ANCHO_FOTO}px; vertical-align:top; padding-right:14px;">'
                f'<img src="{foto_src}" width="{ANCHO_FOTO}" '
                f'style="display:block; width:{ANCHO_FOTO}px; max-width:{ANCHO_FOTO}px; '
                f'height:auto; border-radius:3px;" alt=""></td>'
                f'<td style="vertical-align:top; border-left:3px solid {COLOR_HEADER}; '
                f'padding-left:13px;">{bajada_html}</td>'
                f'</tr></table>'
            )
        else:
            # Sin foto: la bajada ocupa todo el ancho, con la barra roja a la izquierda.
            cuerpo = (f'<div style="border-left:3px solid {COLOR_HEADER}; '
                      f'padding-left:13px;">{bajada_html}</div>')

        notas += (
            f'<div style="margin-bottom:30px;">'
            f'{_tag_seccion(volanta)}'
            f'<div style="font-size:25px; font-weight:bold; color:#111111; line-height:1.22; '
            f'margin:11px 0; font-family:Georgia,\'Times New Roman\',serif;">{titular}</div>'
            f'{cuerpo}</div>'
        )
    return notas


def _caja_breves():
    if not MOSTRAR_BREVES or not BREVES:
        return ""
    items = ""
    for b in BREVES:
        items += (
            f'<div style="font-size:14px; color:{COLOR_TEXTO}; line-height:1.5; '
            f'padding:8px 0; border-bottom:1px dashed #dddddd; '
            f'font-family:Arial,Helvetica,sans-serif;">'
            f'<span style="color:{COLOR_HEADER}; font-weight:bold;">&raquo;</span>&nbsp; {b}</div>'
        )
    return (
        f'<div style="margin-bottom:30px;">'
        f'{_tag_seccion("Pas\u00f3 y no lo viste")}'
        f'<div style="margin-top:11px;">{items}</div>'
        f'</div>'
    )


def _caja_empleado():
    if not MOSTRAR_EMPLEADO or not EMPLEADO_NOMBRE:
        return ""
    return (
        f'<div style="margin-bottom:30px;">'
        f'{_tag_seccion("Empleado de la semana")}'
        f'<div style="margin-top:11px; background:#fffdf2; border:2px solid {COLOR_ACENTO}; '
        f'border-radius:6px; padding:20px; text-align:center;">'
        f'<div style="font-size:42px; line-height:1; margin-bottom:6px;">\U0001F3C6</div>'
        f'<div style="font-size:11px; color:{COLOR_HEADER}; font-weight:bold; '
        f'text-transform:uppercase; letter-spacing:2px; font-family:Arial,Helvetica,sans-serif;">'
        f'Reconocimiento al m\u00e9rito</div>'
        f'<div style="font-size:30px; font-weight:bold; color:#111111; margin:4px 0 10px; '
        f'font-family:Georgia,\'Times New Roman\',serif;">{EMPLEADO_NOMBRE}</div>'
        f'<div style="font-size:14px; color:#444444; line-height:1.55; '
        f'font-family:Arial,Helvetica,sans-serif;">{EMPLEADO_TEXTO}</div>'
        f'</div></div>'
    )


def _caja_horoscopo():
    if not MOSTRAR_HOROSCOPO or not HOROSCOPO:
        return ""
    filas = ""
    for simbolo, signo, personas, texto in HOROSCOPO:
        filas += (
            f'<tr>'
            f'<td style="width:46px; vertical-align:top; padding:11px 0; '
            f'font-size:26px; color:{COLOR_HEADER}; text-align:center;">{simbolo}</td>'
            f'<td style="vertical-align:top; padding:11px 0 11px 8px; '
            f'border-bottom:1px solid #eeeeee;">'
            f'<div style="font-size:14px; font-weight:bold; color:#111111; '
            f'font-family:Arial,Helvetica,sans-serif;">{signo} '
            f'<span style="color:#999999; font-weight:normal; font-size:12px;">&middot; {personas}</span></div>'
            f'<div style="font-size:13px; color:#444444; line-height:1.5; margin-top:3px; '
            f'font-family:Arial,Helvetica,sans-serif;">{texto}</div>'
            f'</td>'
            f'</tr>'
        )
    return (
        f'<div style="margin-bottom:30px;">'
        f'{_tag_seccion("Hor\u00f3scopo laboral")}'
        f'<table width="100%" cellpadding="0" cellspacing="0" style="margin-top:11px;">{filas}</table>'
        f'</div>'
    )


def _caja_indices():
    if not MOSTRAR_INDICES:
        return ""
    # Panel lider: chips ordenados de mayor a menor variacion.
    chips = ""
    for persona, var in sorted(LUCC_ACCIONES, key=lambda x: x[1], reverse=True):
        color = COLOR_SUBA if var >= 0 else COLOR_BAJA
        flecha = "\u25B2" if var >= 0 else "\u25BC"
        signo = "+" if var >= 0 else ""
        chips += (
            f'<span style="display:inline-block; background:#ffffff; border:1px solid #e3e3e3; '
            f'border-radius:6px; padding:6px 11px; margin:0 6px 6px 0; '
            f'font-family:Arial,Helvetica,sans-serif; font-size:13px;">'
            f'<span style="color:#111111; font-weight:bold;">{persona}</span>&nbsp; '
            f'<span style="color:{color}; font-weight:bold;">{flecha} {signo}{var}%</span></span>'
        )
    # Sub-indices.
    subs = ""
    for nombre, valor, glosa in INDICES_SECUNDARIOS:
        subs += (
            f'<tr>'
            f'<td style="vertical-align:top; padding:9px 10px 9px 0; border-bottom:1px solid #eeeeee;">'
            f'<div style="font-size:13px; font-weight:bold; color:#111111; '
            f'font-family:Arial,Helvetica,sans-serif;">{nombre}</div>'
            f'<div style="font-size:12px; color:#777777; margin-top:2px; '
            f'font-family:Arial,Helvetica,sans-serif;">{glosa}</div></td>'
            f'<td style="vertical-align:top; padding:9px 0; border-bottom:1px solid #eeeeee; '
            f'text-align:right; white-space:nowrap;">'
            f'<span style="font-size:15px; font-weight:bold; color:{COLOR_HEADER}; '
            f'font-family:Arial,Helvetica,sans-serif;">{valor}</span></td>'
            f'</tr>'
        )
    return (
        f'<div style="margin-bottom:30px;">'
        f'{_tag_seccion("\u00cdndices econ\u00f3micos")}'
        f'<div style="background:{COLOR_OSCURO}; border-radius:8px; padding:15px 16px 9px; margin-top:11px;">'
        f'<div style="color:{COLOR_ACENTO}; font-size:13px; font-weight:bold; letter-spacing:1px; '
        f'text-transform:uppercase; margin-bottom:11px; font-family:Arial,Helvetica,sans-serif;">'
        f'\U0001F4C8 \u00cdndice Lucciano\u2019s &middot; LUCC</div>'
        f'<div>{chips}</div></div>'
        f'<div style="font-size:14px; color:#444444; line-height:1.55; margin-top:13px; '
        f'border-left:3px solid {COLOR_HEADER}; padding-left:13px; '
        f'font-family:Arial,Helvetica,sans-serif;">{LUCC_COPETE}</div>'
        f'<table width="100%" cellpadding="0" cellspacing="0" style="margin-top:14px;">{subs}</table>'
        f'</div>'
    )


def _caja_meteo_cierre():
    if not MOSTRAR_METEO_CIERRE or not METEO_CIERRE:
        return ""
    return (
        f'<div style="margin-bottom:30px;">'
        f'{_tag_seccion("El meteor\u00f3logo del cierre contable")}'
        f'<div style="background:#fff6e9; border-left:4px solid {COLOR_NARANJA}; '
        f'border-radius:0 6px 6px 0; padding:14px 16px; margin-top:11px;">'
        f'<span style="font-size:18px; vertical-align:middle;">\u26A0\uFE0F</span>&nbsp; '
        f'<span style="font-size:14px; color:#7a4a00; line-height:1.5; '
        f'font-family:Arial,Helvetica,sans-serif;">{METEO_CIERRE}</span>'
        f'</div></div>'
    )


def _caja_encuesta():
    if not MOSTRAR_ENCUESTA or not ENCUESTA_OPCIONES:
        return ""
    barras = ""
    for texto, pct in ENCUESTA_OPCIONES:
        barras += (
            f'<div style="margin-bottom:9px;">'
            f'<div style="font-size:13px; color:{COLOR_TEXTO}; margin-bottom:3px; '
            f'font-family:Arial,Helvetica,sans-serif;">'
            f'<span>{texto}</span>'
            f'<span style="float:right; font-weight:bold; color:{COLOR_HEADER};">{pct}%</span></div>'
            f'<div style="background:#ececec; border-radius:4px; height:9px; overflow:hidden;">'
            f'<div style="background:{COLOR_HEADER}; width:{pct}%; height:9px;"></div></div>'
            f'</div>'
        )
    return (
        f'<div style="margin-bottom:30px;">'
        f'{_tag_seccion("Encuesta de la semana")}'
        f'<div style="font-size:16px; font-weight:bold; color:#111111; margin:11px 0 12px; '
        f'font-family:Georgia,\'Times New Roman\',serif;">{ENCUESTA_PREGUNTA}</div>'
        f'{barras}'
        f'</div>'
    )


def _caja_recomendado():
    if not MOSTRAR_RECOMENDADO:
        return ""
    estrellas = "\u2605" * max(0, min(5, RECOMENDADO_ESTRELLAS))
    estrellas += "\u2606" * (5 - len(estrellas))
    return (
        f'<div style="margin-bottom:30px;">'
        f'{_tag_seccion("Recomendado del editor")}'
        f'<div style="background:{COLOR_CAJA}; border-radius:8px; padding:16px 18px; margin-top:11px;">'
        f'<div style="color:{COLOR_ACENTO}; font-size:17px; letter-spacing:2px; '
        f'text-shadow:0 0 1px #c9a200;">{estrellas}</div>'
        f'<div style="font-size:16px; font-weight:bold; color:#111111; margin:6px 0 7px; '
        f'font-family:Georgia,\'Times New Roman\',serif;">{RECOMENDADO_TITULO}</div>'
        f'<div style="font-size:13px; color:#555555; line-height:1.55; '
        f'font-family:Arial,Helvetica,sans-serif;">{RECOMENDADO_TEXTO}</div>'
        f'</div></div>'
    )


def _caja_frase(frase):
    if not frase:
        return ""
    texto, autor = frase
    return (
        f'<div style="margin-bottom:30px;">'
        f'{_tag_seccion("Frase de la semana")}'
        f'<div style="border-left:4px solid {COLOR_HEADER}; border-right:4px solid {COLOR_HEADER}; '
        f'background:{COLOR_CAJA}; padding:20px 24px; margin-top:11px; text-align:center;">'
        f'<div style="font-size:21px; font-style:italic; color:{COLOR_BORDE}; line-height:1.4; '
        f'font-family:Georgia,\'Times New Roman\',serif;">\u201c{texto}\u201d</div>'
        f'<div style="font-size:11px; font-weight:bold; color:#999999; margin-top:13px; '
        f'text-transform:uppercase; letter-spacing:1px; font-family:Arial,Helvetica,sans-serif;">'
        f'\u2014 {autor}</div>'
        f'</div></div>'
    )


def _caja_cancion(cancion):
    if not cancion:
        return ""
    titulo = cancion.get("titulo", "")
    artista = cancion.get("artista", "")
    link = cancion.get("link", "")
    portada = cancion.get("portada", "")
    VERDE = "#1DB954"
    NEGRO = "#121212"

    celda_img = ""
    if portada:
        celda_img = (f'<td style="width:88px; vertical-align:middle; padding-right:16px;">'
                     f'<img src="{portada}" width="88" height="88" style="border-radius:6px; display:block;" alt=""></td>')
    boton = ""
    if link:
        boton = (f'<a href="{link}" style="display:inline-block; background:{VERDE}; color:#000000; '
                 f'font-size:13px; font-weight:bold; text-decoration:none; padding:9px 22px; '
                 f'border-radius:500px; margin-top:11px;">\u25B6&nbsp; Escuchar ahora</a>')
    marca = (f'<div style="margin-bottom:13px;">'
             f'<span style="display:inline-block; width:13px; height:13px; background:{VERDE}; '
             f'border-radius:50%; vertical-align:middle;"></span>'
             f'<span style="color:{VERDE}; font-size:13px; font-weight:bold; letter-spacing:0.3px; vertical-align:middle;">&nbsp; Spotify</span>'
             f'<span style="color:#b3b3b3; font-size:11px; text-transform:uppercase; letter-spacing:1px; vertical-align:middle;">'
             f'&nbsp;&middot;&nbsp; Canci&oacute;n de la semana</span></div>')
    return (f'<div style="background:{NEGRO}; border-radius:10px; padding:18px 20px; margin-bottom:10px;">'
            f'{marca}'
            f'<table cellpadding="0" cellspacing="0" style="width:100%;"><tr>{celda_img}'
            f'<td style="vertical-align:middle;">'
            f'<div style="color:#ffffff; font-size:17px; font-weight:bold;">{titulo}</div>'
            f'<div style="color:#b3b3b3; font-size:14px; margin-top:3px;">{artista}</div>'
            f'{boton}</td></tr></table></div>')


def _fecha_en_espanol():
    """Fecha en castellano, sin depender del idioma del servidor (GitHub esta en ingles)."""
    dias = ["Lunes", "Martes", "Mi\u00e9rcoles", "Jueves", "Viernes", "S\u00e1bado", "Domingo"]
    meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
             "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    ahora = datetime.now(timezone(timedelta(hours=-3)))
    return f"{dias[ahora.weekday()]} {ahora.day} de {meses[ahora.month - 1]} de {ahora.year}"


def armar_html(frase, cancion):
    fecha_hoy = _fecha_en_espanol()
    # Breaking bar: usa el titular de la primera noticia, si hay.
    if MOSTRAR_NOTILUCCIANOS and NOTILUCCIANOS:
        breaking = NOTILUCCIANOS[0][1]
    else:
        breaking = "Toda la informaci\u00f3n que no necesit\u00e1s, y un poco m\u00e1s"
    # Aca siempre es viernes.
    bombo = (f'<div style="background:{COLOR_ACENTO}; color:{COLOR_OSCURO}; text-align:center; '
             f'font-family:Arial,Helvetica,sans-serif; font-size:13px; font-weight:bold; '
             f'padding:8px; letter-spacing:1px;">'
             f'\U0001F37A \u00a1VIERNES QUE TE QUIERO VIERNES! \U0001F37A</div>')

    # ----- Logo (archivo adjunto o URL, lo que haya) -----
    logo_src, _ = _resolver_logo()
    if logo_src:
        if LOGO_PASTILLA:
            estilo_img = (f'height:{LOGO_ALTO}px; background:#ffffff; padding:7px 14px; '
                          f'border-radius:8px; display:inline-block;')
        else:
            estilo_img = f'height:{LOGO_ALTO}px; display:inline-block;'
        logo_html = (f'<div style="margin-bottom:10px;">'
                     f'<img src="{logo_src}" alt="Lucciano\u2019s" height="{LOGO_ALTO}" '
                     f'style="{estilo_img}"></div>')
    else:
        logo_html = ""

    # ----- Wordmark de texto (nombre del diario) -----
    if MOSTRAR_WORDMARK:
        wordmark_html = (f'<div style="font-size:34px; font-weight:900; color:#ffffff; '
                         f'letter-spacing:2px; font-family:Georgia,\'Times New Roman\',serif;">'
                         f'NOTI<span style="color:{COLOR_ACENTO};">LUCCIANO\u2019S</span></div>')
    else:
        wordmark_html = ""

    # ----- Bandera argentina (imagen, no emoji) -----
    if MOSTRAR_BANDERA and BANDERA_AR_URL:
        bandera_html = (f'&nbsp;<img src="{BANDERA_AR_URL}" width="20" height="13" '
                        f'alt="Argentina" style="vertical-align:middle; border-radius:2px; '
                        f'border:1px solid #d9c9c9;">')
    else:
        bandera_html = ""

    return f"""<!DOCTYPE html>
<html><body style="margin:0; padding:0; background:{COLOR_FONDO};">
  <div style="max-width:680px; margin:0 auto; background:{COLOR_FONDO};">
    <div style="background:{COLOR_HEADER}; padding:15px 20px 12px; text-align:center; border-bottom:4px solid {COLOR_BORDE};">
      {logo_html}
      {wordmark_html}
      <div style="color:#f2c9cb; font-size:10px; letter-spacing:3px; text-transform:uppercase; margin-top:4px; font-family:Arial,Helvetica,sans-serif;">
        El portal que la empresa no quiere que leas</div>
    </div>
    <div style="background:{COLOR_OSCURO}; color:#ffffff; padding:8px 16px; font-size:12px; font-family:Arial,Helvetica,sans-serif;">
      <span style="background:{COLOR_HEADER}; color:#ffffff; font-weight:bold; font-size:10px; padding:2px 8px; text-transform:uppercase;">\U0001F534 Urgente</span>
      &nbsp;&nbsp;{breaking}</div>
    <div style="background:#ffffff; border-bottom:1px solid #dddddd; padding:7px 20px; font-size:11px; color:#666666; font-family:Arial,Helvetica,sans-serif;">
      {fecha_hoy} &nbsp;&middot;&nbsp; Mar del Plata{bandera_html}</div>
    {bombo}
    <div style="background:#ffffff; padding:24px 22px 8px;">
      {_caja_notiluccianos()}
      {_caja_empleado()}
      {_caja_breves()}
      {_caja_indices()}
      {_caja_horoscopo()}
      {_caja_meteo_cierre()}
      {_caja_encuesta()}
      {_caja_recomendado()}
      {_caja_frase(frase)}
      {_caja_cancion(cancion)}
    </div>
    <div style="background:{COLOR_FONDO}; padding:20px 22px 28px; color:#aaaaaa; font-size:10px; text-align:center; font-family:Arial,Helvetica,sans-serif; line-height:1.8;">
      NotiLucciano\u2019s &middot; \u201cInformamos lo que otros prefieren no ver\u201d &middot; Mar del Plata, 2026<br>
      Las fotos son de dominio p\u00fablico. Los nombres fueron modificados para proteger a los inocentes (y no tanto).<br>
      <span style="font-style:italic;">Aclaraci\u00f3n: todo lo que le\u00e9s hoy puede ser desmentido en la pr\u00f3xima edici\u00f3n sin previo aviso.</span>
    </div>
  </div>
</body></html>"""


def enviar_mail(cuerpo_html, adjuntos_inline=None):
    """adjuntos_inline: lista de (cid, ruta) con las imagenes a empotrar en el mail
    (el logo y las fotos de las noticias). Si la lista esta vacia, manda el mail
    sin adjuntos."""
    fecha_hoy = datetime.now(timezone(timedelta(hours=-3))).strftime("%d/%m/%Y")
    adjuntos_inline = adjuntos_inline or []

    if adjuntos_inline:
        # multipart/related: el HTML + las imagenes inline referenciadas por cid.
        mensaje = MIMEMultipart("related")
        alternativo = MIMEMultipart("alternative")
        alternativo.attach(MIMEText(cuerpo_html, "html", "utf-8"))
        mensaje.attach(alternativo)
        for cid, ruta in adjuntos_inline:
            try:
                ext = os.path.splitext(ruta)[1].lower().lstrip(".")
                subtipo = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png",
                           "gif": "gif", "webp": "webp"}.get(ext, "jpeg")
                with open(ruta, "rb") as f:
                    img = MIMEImage(f.read(), _subtype=subtipo)
                img.add_header("Content-ID", f"<{cid}>")
                img.add_header("Content-Disposition", "inline",
                               filename=os.path.basename(ruta))
                mensaje.attach(img)
                print(f"[INFO] Imagen adjuntada inline: {os.path.basename(ruta)} (cid:{cid})")
            except Exception as e:
                print(f"[AVISO] No pude adjuntar {ruta}: {e}")
    else:
        mensaje = MIMEMultipart("alternative")
        mensaje.attach(MIMEText(cuerpo_html, "html", "utf-8"))

    mensaje["Subject"] = f"NotiLucciano's - {fecha_hoy}"
    mensaje["From"] = GMAIL_USER
    mensaje["To"] = MAIL_TO
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as servidor:
        servidor.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        servidor.sendmail(GMAIL_USER, MAIL_TO.split(","), mensaje.as_string())
    print(f"[OK] Mail enviado a {MAIL_TO}.")


# =====================================================================
# MAIN
# =====================================================================

def main():
    print("[INFO] ====== NotiLucciano's ======")
    faltantes = faltan_secretos()
    if faltantes:
        print(f"[ERROR] Faltan estas variables de entorno: {', '.join(faltantes)}")
        sys.exit(1)
    cancion = obtener_cancion()
    frase = random.choice(FRASES) if (MOSTRAR_FRASE and FRASES) else None
    html = armar_html(frase, cancion)   # al armar el HTML se llena _FOTOS_ADJUNTAS
    _, logo_ruta = _resolver_logo()
    adjuntos = []
    if logo_ruta:
        adjuntos.append((_LOGO_CID, logo_ruta))
    adjuntos.extend(_FOTOS_ADJUNTAS)    # las fotos de las noticias, si las hay
    enviar_mail(html, adjuntos)


if __name__ == "__main__":
    main()
