# Run application
if __name__ == '__main__':
    from app import flask_app
    from waitress import serve

    # Run backend server using waitress lib
    serve(flask_app, host=flask_app.config['FLASK_HOST'], port=flask_app.config['FLASK_PORT'])
