import http from 'node:http'
import path from 'node:path'
import { Codex } from '@openai/codex-sdk'

const port = Number(process.env.GANN_ASTRO_CODEX_PORT || 8789)
const projectRoot = path.resolve(process.env.GANN_ASTRO_PROJECT_ROOT || 'D:\\PycharmProjects')
const snapshotRoot = path.resolve(process.env.GANN_ASTRO_SNAPSHOT_ROOT || 'D:\\GannFinancialAstro\\app_snapshots')
const codex = new Codex()

function send(response, status, payload) {
  const body = JSON.stringify(payload)
  response.writeHead(status, {
    'Content-Type': 'application/json; charset=utf-8',
    'Content-Length': Buffer.byteLength(body),
    'Access-Control-Allow-Origin': 'http://127.0.0.1:5173',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
    'Cache-Control': 'no-store',
  })
  response.end(body)
}

async function readJson(request) {
  const chunks = []
  let size = 0
  for await (const chunk of request) {
    size += chunk.length
    if (size > 2 * 1024 * 1024) throw new Error('request exceeds 2 MB')
    chunks.push(chunk)
  }
  return JSON.parse(Buffer.concat(chunks).toString('utf8') || '{}')
}

function allowedSnapshot(value) {
  if (!value) return null
  const resolved = path.resolve(String(value))
  const relative = path.relative(snapshotRoot, resolved)
  if (relative.startsWith('..') || path.isAbsolute(relative)) {
    throw new Error('image path is outside the application snapshot directory')
  }
  return resolved
}

function analysisPrompt(message, context) {
  return [
    'You are assisting inside Gann Astro Desk, a private financial-astrology research application.',
    'Analyze only. Do not place, recommend, or execute an MT5 order. Treat provisional astrology fields as hypotheses, not certified facts.',
    'Use the deterministic event identity, directional family key, selected annotation coordinates, and displayed evidence as ground truth.',
    'Clearly separate observed price behavior, deterministic calculations, manual interpretation, and uncertain astrological explanations.',
    '',
    `User message: ${message}`,
    '',
    'Attached application context:',
    JSON.stringify(context, null, 2),
  ].join('\n')
}

async function handleChat(request, response) {
  const body = await readJson(request)
  const message = String(body.message || '').trim()
  if (!message) return send(response, 400, { ok: false, error: 'message is required' })
  const context = body.context && typeof body.context === 'object' ? body.context : {}
  const options = {
    workingDirectory: projectRoot,
    sandboxMode: 'read-only',
    approvalPolicy: 'never',
    networkAccessEnabled: false,
    webSearchMode: 'disabled',
    modelReasoningEffort: 'medium',
  }
  const threadId = String(body.threadId || '').trim()
  const thread = threadId ? codex.resumeThread(threadId, options) : codex.startThread(options)
  const imagePath = allowedSnapshot(body.imagePath)
  const prompt = analysisPrompt(message, context)
  const input = imagePath
    ? [{ type: 'text', text: prompt }, { type: 'local_image', path: imagePath }]
    : prompt
  const result = await thread.run(input)
  return send(response, 200, {
    ok: true,
    threadId: thread.id,
    response: result.finalResponse,
    usage: result.usage,
  })
}

const server = http.createServer(async (request, response) => {
  try {
    if (request.method === 'OPTIONS') return send(response, 204, {})
    if (request.method === 'GET' && request.url === '/health') {
      return send(response, 200, {
        ok: true,
        bridge: 'codex-sdk',
        mode: 'read-only-analysis',
        workingDirectory: projectRoot,
      })
    }
    if (request.method === 'POST' && request.url === '/chat') {
      return await handleChat(request, response)
    }
    return send(response, 404, { ok: false, error: 'not found' })
  } catch (error) {
    return send(response, 500, { ok: false, error: error instanceof Error ? error.message : String(error) })
  }
})

server.listen(port, '127.0.0.1', () => {
  process.stdout.write(`Codex bridge listening on http://127.0.0.1:${port}\n`)
})
