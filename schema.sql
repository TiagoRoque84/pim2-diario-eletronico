CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    senha TEXT NOT NULL,
    tipo TEXT DEFAULT 'professor'
);

CREATE TABLE IF NOT EXISTS turmas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    alunos INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS alunos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    ra TEXT NOT NULL,
    email TEXT,
    turma_id INTEGER NOT NULL,
    FOREIGN KEY(turma_id) REFERENCES turmas(id)
);

CREATE TABLE IF NOT EXISTS avaliacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    turma_id INTEGER NOT NULL,
    FOREIGN KEY(turma_id) REFERENCES turmas(id)
);

CREATE TABLE IF NOT EXISTS notas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    avaliacao_id INTEGER NOT NULL,
    aluno_id INTEGER NOT NULL,
    nota REAL,
    ausente INTEGER DEFAULT 0,
    substitutiva REAL,
    FOREIGN KEY(avaliacao_id) REFERENCES avaliacoes(id),
    FOREIGN KEY(aluno_id) REFERENCES alunos(id)
);

CREATE TABLE IF NOT EXISTS diario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    turma_id INTEGER NOT NULL,
    data TEXT NOT NULL,
    conteudo TEXT NOT NULL,
    FOREIGN KEY(turma_id) REFERENCES turmas(id)
);
