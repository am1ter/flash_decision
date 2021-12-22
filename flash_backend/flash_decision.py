# Run application
if __name__ == '__main__':
    from app import app
    from waitress import serve

    # Run backend server using waitress lib
    serve(app, host='0.0.0.0', port=8001)