import bottle
from bottle import route, run, template, static_file, redirect, request


@route('/static/<filename:path>')
def send_static(filename):
	return static_file(filename, root='webui-assets')

@route('/')
def home():
	redirect("/static/index.html")

@route('/set')
def temp_set():
	saved=False
	if request.query.temps1 and request.query.temps2:
		saved=True
	elif request.query.temps:
		saved=True
	return template('{ "done":{{done}} }', done=str(saved).lower())

@route('/get')
def temp_get():
	return '18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18'


if __name__ == '__main__':
	bottle.debug(True)
	run(host='0.0.0.0', port=8080)
