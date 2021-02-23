from waitress import serve

# Run application
if __name__ == '__main__':
    from app import app

    # Run production server using waitress
    serve(app, host='0.0.0.0', port=8001)


