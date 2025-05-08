from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
import os

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'usuario')
DB_PASS = os.getenv('DB_PASS', 'password123')
DB_NAME = os.getenv('DB_NAME', 'notasdb')

def get_db():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS,
            dbname=DB_NAME
        )
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al conectar con la base de datos: {e}")


app = FastAPI()


class NoteCreate(BaseModel):
    title: str
    content: str

def create_table():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL
        );
    ''')
    conn.commit()
    cur.close()
    conn.close()

create_table() 


@app.get("/notes")
async def get_notes():
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM notes;")
        notes = cur.fetchall()
        return [{"id": note[0], "title": note[1], "content": note[2]} for note in notes]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener las notas: {e}")
    finally:
        cur.close()
        conn.close()


@app.post("/notes")
async def create_note(note: NoteCreate):
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO notes (title, content) VALUES (%s, %s) RETURNING id;",
            (note.title, note.content)
        )
        note_id = cur.fetchone()[0]
        conn.commit()
        return {"id": note_id, "title": note.title, "content": note.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al insertar la nota: {e}")
    finally:
        cur.close()
        conn.close()


@app.get("/")
async def root():
    return {
        "message": "Welcome to the FastAPI application! "
        "You can use this API to manage your notes."
    }
