from name_generator.generator import WordGenerator
from flask import Flask, render_template

app = Flask(__name__)

with app.open_instance_resource('data/first-names_en-US.txt') as fin:
  names = [name.strip().lower() for name in fin.readlines()]
generator = WordGenerator(names)

@app.route('/')
def Home():
  name = generator.GenerateWord()
  return render_template('home.html', name=name)
