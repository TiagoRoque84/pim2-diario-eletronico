from flask import Flask, g, request, render_template, session, redirect
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "SENHA_SUPER_SECRETA_PIM2"
DATABASE = "pim2.db"



# ============================================================
#                      BANCO DE DADOS
# ============================================================

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db:
        db.close()


def criar_admin():
    """
    Cria automaticamente o ADMIN caso não exista.
    """
    db = get_db()
    admin = db.execute("SELECT * FROM usuarios WHERE email=?", ("admin@admin.com",)).fetchone()

    if not admin:
        db.execute("""
            INSERT INTO usuarios (nome, email, senha, tipo)
            VALUES ('Administrador', 'admin@admin.com', 'admin', 'admin')
        """)
        db.commit()


def init_db():
    db = get_db()
    with open("schema.sql", "r", encoding="utf-8") as f:
        db.executescript(f.read())
    db.commit()
    criar_admin()



with app.app_context():
    init_db()



# ============================================================
#                            LOGIN
# ============================================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        user = get_db().execute(
            "SELECT * FROM usuarios WHERE email=? AND senha=?",
            (email, senha)
        ).fetchone()

        if user:
            session['usuario'] = user['nome']
            session['tipo']    = user['tipo']
            session['id']      = user['id']
            return redirect('/')

        return "Credenciais inválidas"

    return render_template('login.html')



@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')



# ============================================================
#                           DASHBOARD
# ============================================================

@app.route('/')
def dashboard():
    if 'usuario' not in session:
        return redirect('/login')

    return render_template(
        'dashboard.html',
        usuario=session.get('usuario'),
        tipo=session.get('tipo', 'professor')
    )



# ============================================================
#                       PROFESSORES (ADMIN)
# ============================================================

@app.route('/professores')
def listar_professores():
    if session.get('tipo') != 'admin':
        return redirect('/')

    db = get_db()
    lista = db.execute("SELECT * FROM usuarios").fetchall()

    return render_template(
        'professores.html',
        professores=lista
    )


@app.route('/professores/criar', methods=['POST'])
def criar_professor():
    if session.get('tipo') != 'admin':
        return redirect('/')

    nome = request.form['nome']
    email = request.form['email']
    senha = request.form['senha']

    db = get_db()
    db.execute("""
        INSERT INTO usuarios (nome, email, senha, tipo)
        VALUES (?, ?, ?, 'professor')
    """, (nome, email, senha))
    db.commit()

    return redirect('/professores')


@app.route('/professores/editar/<int:id>', methods=['GET', 'POST'])
def editar_professor(id):
    if session.get('tipo') != 'admin':
        return redirect('/')

    db = get_db()
    professor = db.execute("SELECT * FROM usuarios WHERE id=?", (id,)).fetchone()

    if professor['tipo'] == 'admin':
        return redirect('/professores')

    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']

        db.execute("""
            UPDATE usuarios SET nome=?, email=?, senha=? WHERE id=?
        """, (nome, email, senha, id))
        db.commit()

        return redirect('/professores')

    return render_template('editar_professor.html', professor=professor)


@app.route('/professores/excluir/<int:id>')
def excluir_professor(id):
    if session.get('tipo') != 'admin':
        return redirect('/')

    db = get_db()
    prof = db.execute("SELECT tipo FROM usuarios WHERE id=?", (id,)).fetchone()

    if not prof or prof['tipo'] == 'admin':
        return redirect('/professores')

    db.execute("DELETE FROM usuarios WHERE id=?", (id,))
    db.commit()

    return redirect('/professores')



# ============================================================
#                             TURMAS
# ============================================================

@app.route('/turmas')
def turmas_page():
    if 'usuario' not in session:
        return redirect('/login')

    rows = get_db().execute("SELECT * FROM turmas").fetchall()

    return render_template(
        'turmas.html',
        turmas=rows,
        tipo=session.get('tipo')
    )


@app.route('/turmas/criar', methods=['POST'])
def criar_turma():
    db = get_db()
    nome = request.form['nome']
    alunos = request.form['alunos']

    db.execute("INSERT INTO turmas (nome, alunos) VALUES (?, ?)", (nome, alunos))
    db.commit()

    return redirect('/turmas')


@app.route('/turmas/editar/<int:id>', methods=['GET', 'POST'])
def editar_turma(id):
    db = get_db()

    if request.method == 'POST':
        nome = request.form['nome']
        alunos = request.form['alunos']

        db.execute("UPDATE turmas SET nome=?, alunos=? WHERE id=?", (nome, alunos, id))
        db.commit()
        return redirect('/turmas')

    turma = db.execute("SELECT * FROM turmas WHERE id=?", (id,)).fetchone()
    return render_template('editar_turma.html', turma=turma)


@app.route('/turmas/excluir/<int:id>')
def excluir_turma(id):
    db = get_db()
    db.execute("DELETE FROM turmas WHERE id=?", (id,))
    db.commit()
    return redirect('/turmas')



# ============================================================
#                             ALUNOS
# ============================================================

@app.route('/turmas/<int:turma_id>/alunos')
def listar_alunos(turma_id):
    db = get_db()

    turma = db.execute("SELECT * FROM turmas WHERE id=?", (turma_id,)).fetchone()
    alunos = db.execute("SELECT * FROM alunos WHERE turma_id=?", (turma_id,)).fetchall()

    return render_template('alunos.html', turma=turma, alunos=alunos)


@app.route('/turmas/<int:turma_id>/alunos/criar', methods=['POST'])
def criar_aluno(turma_id):
    db = get_db()

    nome = request.form['nome']
    ra = request.form['ra']
    email = request.form.get('email')

    db.execute("""
        INSERT INTO alunos (nome, ra, email, turma_id)
        VALUES (?, ?, ?, ?)
    """, (nome, ra, email, turma_id))
    db.commit()

    return redirect(f'/turmas/{turma_id}/alunos')


@app.route('/alunos/editar/<int:id>', methods=['GET', 'POST'])
def editar_aluno(id):
    db = get_db()
    aluno = db.execute("SELECT * FROM alunos WHERE id=?", (id,)).fetchone()

    if request.method == 'POST':
        nome = request.form['nome']
        ra = request.form['ra']
        email = request.form['email']

        db.execute("""
            UPDATE alunos SET nome=?, ra=?, email=? WHERE id=?
        """, (nome, ra, email, id))
        db.commit()

        return redirect(f'/turmas/{aluno["turma_id"]}/alunos')

    return render_template('editar_aluno.html', aluno=aluno)


@app.route('/alunos/excluir/<int:id>')
def excluir_aluno(id):
    db = get_db()
    aluno = db.execute("SELECT turma_id FROM alunos WHERE id=?", (id,)).fetchone()

    db.execute("DELETE FROM alunos WHERE id=?", (id,))
    db.commit()

    return redirect(f'/turmas/{aluno["turma_id"]}/alunos')



# ============================================================
#                             DIÁRIO
# ============================================================

@app.route('/turmas/<int:id>/diario')
def diario(id):
    db = get_db()

    turma = db.execute("SELECT * FROM turmas WHERE id=?", (id,)).fetchone()
    registros = db.execute("SELECT * FROM diario WHERE turma_id=?", (id,)).fetchall()

    return render_template('diario.html', turma=turma, registros=registros)


@app.route('/diario/add/<int:id>', methods=['POST'])
def add_diario(id):
    db = get_db()

    db.execute("""
        INSERT INTO diario (turma_id, data, conteudo)
        VALUES (?, ?, ?)
    """, (id, request.form['data'], request.form['conteudo']))

    db.commit()

    return redirect(f'/turmas/{id}/diario')



# ============================================================
#                           AVALIAÇÕES
# ============================================================

@app.route('/turmas/<int:turma_id>/avaliacoes')
def listar_avaliacoes(turma_id):
    db = get_db()

    turma = db.execute("SELECT * FROM turmas WHERE id=?", (turma_id,)).fetchone()
    avaliacoes = db.execute("SELECT * FROM avaliacoes WHERE turma_id=?", (turma_id,)).fetchall()

    return render_template('avaliacoes.html', turma=turma, avaliacoes=avaliacoes)


@app.route('/turmas/<int:turma_id>/avaliacoes/criar', methods=['POST'])
def criar_avaliacao(turma_id):
    db = get_db()
    nome = request.form['nome']

    db.execute("INSERT INTO avaliacoes (turma_id, nome) VALUES (?, ?)", (turma_id, nome))
    db.commit()

    return redirect(f'/turmas/{turma_id}/avaliacoes')


@app.route('/avaliacoes/excluir/<int:id>')
def excluir_avaliacao(id):
    db = get_db()

    turma = db.execute("SELECT turma_id FROM avaliacoes WHERE id=?", (id,)).fetchone()
    turma_id = turma['turma_id']

    db.execute("DELETE FROM notas WHERE avaliacao_id=?", (id,))
    db.execute("DELETE FROM avaliacoes WHERE id=?", (id,))
    db.commit()

    return redirect(f'/turmas/{turma_id}/avaliacoes')



# ============================================================
#                        NOTAS (AUS + SUB)
# ============================================================

@app.route('/avaliacoes/<int:avaliacao_id>/notas')
def notas_avaliacao(avaliacao_id):
    db = get_db()

    avaliacao = db.execute("SELECT * FROM avaliacoes WHERE id=?", (avaliacao_id,)).fetchone()
    turma_id = avaliacao['turma_id']

    alunos = db.execute("SELECT * FROM alunos WHERE turma_id=?", (turma_id,)).fetchall()
    registros = db.execute("SELECT * FROM notas WHERE avaliacao_id=?", (avaliacao_id,)).fetchall()

    notas_dict = {
        n['aluno_id']: {
            "nota": n['nota'],
            "ausente": n['ausente'],
            "substitutiva": n['substitutiva']
        }
        for n in registros
    }

    return render_template(
        'notas.html',
        avaliacao=avaliacao,
        alunos=alunos,
        notas=notas_dict
    )


@app.route('/avaliacoes/<int:avaliacao_id>/notas/salvar', methods=['POST'])
def salvar_notas(avaliacao_id):
    db = get_db()

    for key in request.form:
        if key.startswith("nota_"):

            aluno_id = int(key.replace("nota_", ""))

            nota = request.form.get(f"nota_{ aluno_id }")
            ausente = request.form.get(f"ausente_{ aluno_id }")
            substitutiva = request.form.get(f"sub_{ aluno_id }")

            nota = float(nota) if nota else None
            substitutiva = float(substitutiva) if substitutiva else None
            ausente = 1 if ausente == "on" else 0

            existente = db.execute("""
                SELECT * FROM notas
                WHERE avaliacao_id=? AND aluno_id=?
            """, (avaliacao_id, aluno_id)).fetchone()

            if existente:
                db.execute("""
                    UPDATE notas SET nota=?, ausente=?, substitutiva=?
                    WHERE avaliacao_id=? AND aluno_id=?
                """, (nota, ausente, substitutiva, avaliacao_id, aluno_id))
            else:
                db.execute("""
                    INSERT INTO notas (avaliacao_id, aluno_id, nota, ausente, substitutiva)
                    VALUES (?, ?, ?, ?, ?)
                """, (avaliacao_id, aluno_id, nota, ausente, substitutiva))

    db.commit()

    return redirect(f'/avaliacoes/{avaliacao_id}/notas')



# ============================================================
#                         EXECUTAR SERVIDOR
# ============================================================

if __name__ == "__main__":
    app.run(debug=True)
