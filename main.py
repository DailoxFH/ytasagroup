from src import handler

if __name__ == '__main__':
    from waitress import serve
    serve(handler.get_app(), port=5000)
