from flask import Flask, render_template, request, redirect, url_for, session
from random import shuffle
import time

app = Flask(__name__)
app.secret_key = "cambiar-esto-por-algo-secreto"  # necesario para usar session

preguntas = [
    ("¿Dónde se firmó la declaración de independencia argentina?", ["Tucuman", "Buenos Aires", "Rosario", "Córdoba"], "Tucuman"),
    ("¿Quién fue el primer presidente de la Argentina?", ["Justo José de Urquiza", "Bernardino Rivadavia", "Juan Manuel de Rosas", "Cornelio Saavedra"], "Bernardino Rivadavia"),
    ("¿Cuál de estos libros NO fue escrito por Fiodr Dostoievski?", ["Los Hermanos Karamazov", "El Idiota", "El Jugador", "La Guerra y la Paz"], "La Guerra y la Paz"),
    ("¿A cuál de estos artistas pertenece la famosa canción 'Yo me enamoré'?", ["Leo Mattioli", "Pablito Lescano", "La Mona Jímenez", "Ariel El Traidor"], "Pablito Lescano"),
    ("¿Cuál de estos álbums del rock argentino es el más vendido de la historia?", ["Clics Modernos", "Alta Suciedad", "El Amor Después del Amor", "Oktubre"], "El Amor Después del Amor"),
    ("¿En qué año llegó el hombre a la Luna?", ["1965", "1969", "1971", "1975"], "1969"),
    ("¿Qué famoso general fue secuestrado y asesinado por Montoneros en 1970?", ["Pedro Eugenio Aramburu", "José Félix Uriburu", "Carlos Onganía", "Eduardo Lonardi"], "Pedro Eugenio Aramburu"),
]

CON_TIEMPO = True
LIMITE_SEGUNDOS = 10


@app.route("/")
def inicio():
    # Reinicia el estado del juego (equivalente a arrancar el script de nuevo)
    session["puntaje"] = 0
    session["indice"] = 0
    return redirect(url_for("pregunta"))


@app.route("/pregunta", methods=["GET", "POST"])
def pregunta():
    indice = session.get("indice", 0)

    if indice >= len(preguntas):
        return redirect(url_for("resultado"))

    texto_pregunta, opciones, correcta = preguntas[indice]

    if request.method == "POST":
        opciones_mezcladas = session["opciones_mezcladas"]
        tiempo_usado = time.time() - session["inicio"]

        correcto = False

        if CON_TIEMPO and tiempo_usado > LIMITE_SEGUNDOS:
            mensaje = f"Se acabó el tiempo ({LIMITE_SEGUNDOS} segundos). La respuesta era: {correcta}"
        else:
            respuesta = request.form.get("respuesta")
            try:
                elegida = opciones_mezcladas[int(respuesta) - 1]
                if elegida == correcta:
                    correcto = True
                    mensaje = "¡Correcto!"
                else:
                    mensaje = f"Incorrecto. La respuesta correcta era: {correcta}"
            except (ValueError, IndexError, TypeError):
                mensaje = "Respuesta inválida."

        if correcto:
            session["puntaje"] = session.get("puntaje", 0) + 1

        session["indice"] = indice + 1

        return render_template("resultado_pregunta.html", mensaje=mensaje)

    # GET: se muestra la pregunta por primera vez
    opciones_mezcladas = opciones[:]
    shuffle(opciones_mezcladas)

    session["opciones_mezcladas"] = opciones_mezcladas
    session["inicio"] = time.time()

    return render_template(
        "pregunta.html",
        pregunta=texto_pregunta,
        opciones=opciones_mezcladas,
        numero=indice + 1,
        total=len(preguntas),
        limite=LIMITE_SEGUNDOS if CON_TIEMPO else None,
    )


@app.route("/resultado")
def resultado():
    puntaje = session.get("puntaje", 0)
    total = len(preguntas)
    porcentaje = (puntaje / total) * 100

    if porcentaje == 100:
        mensaje = "¡Puntaje perfecto!"
    elif porcentaje >= 60:
        mensaje = "Bien hecho."
    else:
        mensaje = "Convendría repasar un poco más."

    return render_template(
        "resultado_final.html", puntaje=puntaje, total=total, porcentaje=porcentaje, mensaje=mensaje
    )


if __name__ == "__main__":
    app.run(debug=True)