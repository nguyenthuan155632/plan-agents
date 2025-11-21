import { NextRequest, NextResponse } from 'next/server'
import { writeFile, mkdir } from 'fs/promises'
import { existsSync } from 'fs'
import path from 'path'
import { exec } from 'child_process'
import { promisify } from 'util'

const execAsync = promisify(exec)

const PROJECT_ROOT = path.join(process.cwd(), '..')
const RAG_DIR = path.join(PROJECT_ROOT, 'rag')
const CODEBASE_PATH = path.join(RAG_DIR, 'codebase.json')
const VENV_PYTHON = path.join(PROJECT_ROOT, '.venv', 'bin', 'python')

// GET - Get current codebase info
export async function GET() {
  try {
    const hasCodebase = existsSync(CODEBASE_PATH)

    if (!hasCodebase) {
      return NextResponse.json({
        indexed: false,
        message: 'No codebase indexed yet'
      })
    }

    // Get file stats
    const { stat } = await import('fs/promises')
    const stats = await stat(CODEBASE_PATH)

    // Read codebase to get file count
    const { readFile } = await import('fs/promises')
    const content = await readFile(CODEBASE_PATH, 'utf-8')
    const data = JSON.parse(content)

    return NextResponse.json({
      indexed: true,
      fileCount: data.files?.length || 0,
      lastModified: stats.mtime.toISOString(),
      size: stats.size
    })
  } catch (error: any) {
    return NextResponse.json(
      { error: error.message || 'Failed to get codebase info' },
      { status: 500 }
    )
  }
}

// POST - Upload new codebase JSON or trigger re-index
export async function POST(request: NextRequest) {
  try {
    const contentType = request.headers.get('content-type') || ''

    // Handle JSON upload (repomix format)
    if (contentType.includes('application/json')) {
      const body = await request.json()

      // Validate structure
      if (!body.files || !Array.isArray(body.files)) {
        return NextResponse.json(
          { error: 'Invalid codebase format. Expected { files: [...] }' },
          { status: 400 }
        )
      }

      // Validate each file has path and content
      for (const file of body.files) {
        if (!file.path || typeof file.content !== 'string') {
          return NextResponse.json(
            { error: 'Each file must have "path" and "content" fields' },
            { status: 400 }
          )
        }
      }

      // Write to codebase.json
      await writeFile(CODEBASE_PATH, JSON.stringify(body, null, 2), 'utf-8')

      // Trigger RAG indexing using venv python
      try {
        const { stdout, stderr } = await execAsync(
          `cd ${RAG_DIR} && ${VENV_PYTHON} -c "from rag_system import create_rag_system; create_rag_system('${CODEBASE_PATH}')"`,
          { timeout: 120000, maxBuffer: 1024 * 1024 * 10 } // 2 minute timeout, 10MB buffer
        )
        console.log('RAG indexing output:', stdout)
        if (stderr) console.error('RAG indexing stderr:', stderr)
      } catch (indexError: any) {
        console.error('RAG indexing failed:', indexError)
        // Don't fail the upload, just warn
      }

      return NextResponse.json({
        success: true,
        message: 'Codebase uploaded and indexed',
        fileCount: body.files.length
      })
    }

    // Handle multipart form data (file upload)
    if (contentType.includes('multipart/form-data')) {
      const formData = await request.formData()
      const file = formData.get('file') as File

      if (!file) {
        return NextResponse.json(
          { error: 'No file provided' },
          { status: 400 }
        )
      }

      const content = await file.text()
      const fileName = file.name.toLowerCase()
      let data

      // Handle different file types
      if (fileName.endsWith('.json')) {
        // JSON format - expect { files: [...] } structure
        try {
          data = JSON.parse(content)
        } catch {
          return NextResponse.json(
            { error: 'Invalid JSON file' },
            { status: 400 }
          )
        }

        // Validate structure for JSON
        if (!data.files || !Array.isArray(data.files)) {
          return NextResponse.json(
            { error: 'Invalid codebase format. Expected { files: [...] }' },
            { status: 400 }
          )
        }
      } else if (fileName.endsWith('.md') || fileName.endsWith('.txt')) {
        // Markdown or Text - treat entire content as single file
        data = {
          files: [{
            path: file.name,
            content: content
          }]
        }
      } else {
        return NextResponse.json(
          { error: 'Unsupported file type. Use .json, .md, or .txt' },
          { status: 400 }
        )
      }

      // Write to codebase.json
      await writeFile(CODEBASE_PATH, JSON.stringify(data, null, 2), 'utf-8')

      // Trigger RAG indexing using venv python
      try {
        await execAsync(
          `cd ${RAG_DIR} && ${VENV_PYTHON} -c "from rag_system import create_rag_system; create_rag_system('${CODEBASE_PATH}')"`,
          { timeout: 120000, maxBuffer: 1024 * 1024 * 10 } // 10MB buffer
        )
      } catch (indexError: any) {
        console.error('RAG indexing failed:', indexError)
      }

      return NextResponse.json({
        success: true,
        message: 'Codebase uploaded and indexed',
        fileCount: data.files.length
      })
    }

    // Handle re-index request (no body, just trigger scan)
    const action = request.nextUrl.searchParams.get('action')
    if (action === 'reindex') {
      try {
        const { stdout } = await execAsync(
          `cd ${RAG_DIR} && ${VENV_PYTHON} cli.py index`,
          { timeout: 180000, maxBuffer: 1024 * 1024 * 10 } // 3 minute timeout, 10MB buffer
        )
        console.log('Re-index output:', stdout)

        return NextResponse.json({
          success: true,
          message: 'Codebase re-indexed from project files'
        })
      } catch (error: any) {
        return NextResponse.json(
          { error: error.message || 'Re-indexing failed' },
          { status: 500 }
        )
      }
    }

    return NextResponse.json(
      { error: 'Invalid request. Send JSON codebase or use ?action=reindex' },
      { status: 400 }
    )

  } catch (error: any) {
    console.error('Codebase upload error:', error)
    return NextResponse.json(
      { error: error.message || 'Failed to process codebase' },
      { status: 500 }
    )
  }
}

// DELETE - Clear codebase
export async function DELETE() {
  try {
    const { unlink } = await import('fs/promises')

    if (existsSync(CODEBASE_PATH)) {
      await unlink(CODEBASE_PATH)
    }

    // Also clear vectorstore cache
    const vectorstorePath = path.join(RAG_DIR, 'vectorstore_cache')
    if (existsSync(vectorstorePath)) {
      const { rm } = await import('fs/promises')
      await rm(vectorstorePath, { recursive: true, force: true })
    }

    return NextResponse.json({
      success: true,
      message: 'Codebase cleared'
    })
  } catch (error: any) {
    return NextResponse.json(
      { error: error.message || 'Failed to clear codebase' },
      { status: 500 }
    )
  }
}
