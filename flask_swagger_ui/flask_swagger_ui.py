import os
import json
from flask import Blueprint, send_from_directory, render_template, request, jsonify


def get_swaggerui_blueprint(
        base_url,
        api_url,
        config=None,
        oauth_config=None,
        blueprint_name='swagger_ui'
):

    swagger_ui = Blueprint(blueprint_name,
                           __name__,
                           static_folder='dist',
                           template_folder='templates')

    default_config = {
        'app_name': 'Swagger UI',
        'dom_id': '#swagger-ui',
        'url': api_url,
        'layout': 'StandaloneLayout',
        'deepLinking': True
    }

    if config:
        default_config.update(config)

    fields = {
        # Some fields are used directly in template
        'base_url': base_url,
        'app_name': default_config.pop('app_name'),
        # Rest are just serialized into json string for inclusion in the .js file
        'config_json': json.dumps(default_config),

    }
    if oauth_config:
        fields['oauth_config_json'] = json.dumps(oauth_config)

    @swagger_ui.route('/')
    @swagger_ui.route('/<path:path>')
    def show(path=None):
        if not path or path == 'index.html':
            if not default_config.get('oauth2RedirectUrl', None):
                default_config.update(
                    {"oauth2RedirectUrl": os.path.join(
                        request.base_url, "oauth2-redirect.html")}
                )
                fields['config_json'] = json.dumps(default_config)
            # Added password protection via query parameter.
            swagger_pass = os.getenv('SWAGGER_PASSWORD', default=None)
            if swagger_pass:
                user_pass = request.args.get('pass')
                if swagger_pass != user_pass:
                    response = jsonify({'error': 'password incorrect'})
                    response.status_code = 401
                    return response
            return render_template('index.template.html', **fields)
        else:
            return send_from_directory(
                # A bit of a hack to not pollute the default /static path with our files.
                os.path.join(
                    swagger_ui.root_path,
                    swagger_ui._static_folder
                ),
                path
            )

    return swagger_ui
