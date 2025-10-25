import { NextResponse } from 'next/server'
import fs from 'fs'
import path from 'path'
import sqlite3 from 'sqlite3'

const dbPath = path.join(process.cwd(), '..', 'storage', 'conversations.db')

function getDb() {
  return new sqlite3.Database(dbPath)
}

const dbAll = (db: sqlite3.Database, query: string, params: any[] = []) => {
  return new Promise((resolve, reject) => {
    db.all(query, params, (err, rows) => {
      if (err) reject(err)
      else resolve(rows)
    })
  })
}

export async function GET(
  request: Request,
  { params }: { params: { id: string } }
) {
  try {
    if (!fs.existsSync(dbPath)) {
      return NextResponse.json(
        { error: 'Database not found' },
        { status: 404 }
      )
    }

    const db = getDb()
    const sessionId = params.id

    // Get session info to check status
    const sessions: any = await dbAll(db, `
      SELECT status FROM sessions WHERE id = ?
    `, [sessionId])

    const session = sessions && sessions.length > 0 ? sessions[0] : null
    const isActive = session && session.status === 'active'

    const messages = await dbAll(db, `
      SELECT * FROM messages
      WHERE session_id = ?
      ORDER BY timestamp ASC
    `, [sessionId])

    db.close()

    return NextResponse.json({
      messages,
      isActive // Include session active status
    })
  } catch (error) {
    console.error('Error fetching messages:', error)
    return NextResponse.json(
      { error: 'Failed to fetch messages' },
      { status: 500 }
    )
  }
}

