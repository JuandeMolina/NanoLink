"""
Module Name: Error Handlers
Description:
    This module registers HTTP error handlers for the Flask application.
    All errors render a single template (error.html) receiving the HTTP
    status code, a short title and a human-friendly description.
Author: Juande Molina
Copyright: (c) 2026 JuandeMolina
License: MIT
"""

from flask import render_template

def register_error_handlers(app):
    
    @app.errorhandler(403)
    def forbidden(e):
        return render_template(
            "error.html",
            code=403,
            title="Acceso denegado",
            description="¡Te pillé! ¿A dónde te crees que vas? "
            "Voy a hacer como si no te hubiera visto, pero "
            "vete de aquí y vuelve cuando tengas permiso, ¿de acuerdo?"
        )
    
    @app.errorhandler(404)
    def not_found(e):
        return render_template(
            "error.html",
            code=404,
            title="Página no encontrada",
            description="No está mal ir por la vida sin un rumbo fijo, "
            "pero aquí si es necesario. "
            "Te recomiendo mejorar tus habilidades de explorador "
            "cuando vuelvas a la página de inicio."
        )
    
    @app.errorhandler(405)
    def method_not_allowed(e):
        return render_template(
            "error.html",
            code=405,
            title="Método no permitido",
            description="¿Buscando algo? Porque aquí no hay nada que ver. "
            "Circulen, por favor... (y traigan un método válido la próxima vez)."
        )
    
    @app.errorhandler(500)
    def internal_error(e):
        return render_template(
            "error.html",
            code=500,
            title="Error interno del servidor",
            description='"No es por tí, es por mí" '
            "Espero que sea la primera vez que te dicen esto. "
            "Mientras lloras, mi desarrollador intenta salvar nuestra relación."
        )
    
    @app.errorhandler(503)
    def service_unavailable(e):
        return render_template(
            "error.html",
            code=503,
            title="Servicio no disponible",
            description="Te seré totalmente sincero. Estoy durmiendo una siesta. "
            "Vuelve cuando haya despertado y déjame dormir mientras tanto."
        )