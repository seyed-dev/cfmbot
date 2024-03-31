tel:
	watchmedo auto-restart --recursive --pattern="*.py" --directory="./" -- python main.py tel

dis:
	python main.py dis

env:
	source env.sh

upload:
	python main.py upload $(file)