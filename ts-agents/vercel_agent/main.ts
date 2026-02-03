/**
 * Vercel AI SDK Agent with AG-UI Protocol Support (WRAPPED)
 * Port: 7779
 * Endpoints:
 *   POST /agent/anthropic - Claude Haiku
 *   POST /agent/openai - GPT-4o Mini
 *   POST /agent/gemini - Gemini 2.0 Flash
 *
 * Direct Vercel AI SDK wrapped with AG-UI events.
 * Note: There's no native @ag-ui/vercel-ai-sdk package yet.
 */

import 'dotenv/config';
import express, { Request, Response } from 'express';
import { createAnthropic } from '@ai-sdk/anthropic';
import { createOpenAI } from '@ai-sdk/openai';
import { createGoogleGenerativeAI } from '@ai-sdk/google';
import { streamText, tool, LanguageModel } from 'ai';
import { z } from 'zod';

const app = express();
app.use(express.json());

// Initialize all providers
const anthropic = createAnthropic({ apiKey: process.env.ANTHROPIC_API_KEY });
const openai = createOpenAI({ apiKey: process.env.OPENAI_API_KEY });
const google = createGoogleGenerativeAI({ apiKey: process.env.GEMINI_API_KEY });

// Define tools using Vercel AI SDK format
const tools = {
  get_current_time: tool({
    description: 'Get the current date and time',
    parameters: z.object({}),
    execute: async () => {
      return new Date().toISOString().replace('T', ' ').substring(0, 19);
    },
  }),
  calculator: tool({
    description: 'Evaluate a mathematical expression',
    parameters: z.object({
      expression: z.string().describe("A math expression like '2 + 2' or '10 * 5'"),
    }),
    execute: async ({ expression }) => {
      try {
        const allowedChars = new Set('0123456789+-*/.() ');
        if ([...expression].every((c) => allowedChars.has(c))) {
          const result = eval(expression);
          return `${expression} = ${result}`;
        }
        return 'Invalid expression - only basic math allowed';
      } catch (e) {
        return `Error: ${e}`;
      }
    },
  }),
};

// System prompt
const systemPrompt = `You are a helpful assistant running on the Vercel AI SDK framework.
You can tell the current time and do basic math calculations.
Be concise and friendly in your responses.`;

// Helper to encode SSE
function encodeSSE(eventType: string, data: Record<string, any>): string {
  const payload = { type: eventType, ...data };
  return `data: ${JSON.stringify(payload)}\n\n`;
}

// Helper function to handle AG-UI streaming for any model
async function handleAgentRequest(model: LanguageModel, req: Request, res: Response): Promise<void> {
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');

  try {
    const { messages, thread_id, run_id } = req.body;

    // Send RUN_STARTED
    res.write(encodeSSE('RUN_STARTED', { thread_id, run_id }));

    // Convert AG-UI messages to Vercel AI format
    const aiMessages = messages.map((msg: any) => ({
      role: msg.role as 'user' | 'assistant',
      content: msg.content,
    }));

    // Stream response using Vercel AI SDK
    const result = streamText({
      model,
      system: systemPrompt,
      messages: aiMessages,
      tools,
      maxSteps: 5, // Allow tool use
    });

    const messageId = `msg-${Date.now()}`;
    let messageStarted = false;
    let toolCallCounter = 0;

    // Stream the response with AG-UI events
    for await (const part of result.fullStream) {
      if (part.type === 'text-delta') {
        if (!messageStarted) {
          res.write(encodeSSE('TEXT_MESSAGE_START', { message_id: messageId, role: 'assistant' }));
          messageStarted = true;
        }
        res.write(encodeSSE('TEXT_MESSAGE_CONTENT', { message_id: messageId, delta: part.textDelta }));
      } else if (part.type === 'tool-call') {
        const toolCallId = `tc-${++toolCallCounter}`;
        res.write(encodeSSE('TOOL_CALL_START', { toolCallId, toolCallName: part.toolName }));
        res.write(encodeSSE('TOOL_CALL_ARGS', { toolCallId, delta: JSON.stringify(part.args) }));
        res.write(encodeSSE('TOOL_CALL_END', { toolCallId }));
      } else if (part.type === 'tool-result') {
        const toolCallId = `tc-${toolCallCounter}`;
        res.write(encodeSSE('TOOL_CALL_RESULT', { toolCallId, result: String(part.result) }));
      }
    }

    if (messageStarted) {
      res.write(encodeSSE('TEXT_MESSAGE_END', { message_id: messageId }));
    }

    // Send RUN_FINISHED
    res.write(encodeSSE('RUN_FINISHED', { thread_id, run_id }));
    res.end();
  } catch (error) {
    console.error('Error:', error);
    const { thread_id, run_id } = req.body;
    res.write(encodeSSE('RUN_ERROR', { message: String(error), code: 'VERCEL_AI_ERROR' }));
    res.write(encodeSSE('RUN_FINISHED', { thread_id, run_id }));
    res.end();
  }
}

// AG-UI endpoint for Anthropic (Claude)
app.post('/agent/anthropic', async (req: Request, res: Response) => {
  await handleAgentRequest(anthropic('claude-haiku-4-5-20251001'), req, res);
});

// AG-UI endpoint for OpenAI (GPT-4o Mini)
app.post('/agent/openai', async (req: Request, res: Response) => {
  await handleAgentRequest(openai('gpt-5-mini'), req, res);
});

// AG-UI endpoint for Gemini
app.post('/agent/gemini', async (req: Request, res: Response) => {
  await handleAgentRequest(google('gemini-2.5-flash'), req, res);
});

app.get('/health', (_req: Request, res: Response) => {
  res.json({
    status: 'healthy',
    framework: 'vercel-ai-sdk',
    port: 7779,
    providers: {
      anthropic: {
        model: 'claude-haiku-4-5-20251001',
        endpoint: '/agent/anthropic',
      },
      openai: {
        model: 'gpt-5-mini',
        endpoint: '/agent/openai',
      },
      gemini: {
        model: 'gemini-2.5-flash',
        endpoint: '/agent/gemini',
      },
    },
    native_agui: false,
    note: 'Vercel AI SDK with AG-UI wrapper (no native package yet)',
  });
});

app.get('/', (_req: Request, res: Response) => {
  res.json({
    name: 'Vercel AI SDK AG-UI Test Agent',
    framework: 'vercel-ai-sdk',
    endpoints: {
      anthropic: 'POST /agent/anthropic',
      openai: 'POST /agent/openai',
      gemini: 'POST /agent/gemini',
    },
    health_endpoint: 'GET /health',
    native_agui: false,
  });
});

const PORT = 7779;
app.listen(PORT, () => {
  console.log(`Starting Vercel AI SDK Agent on port ${PORT}...`);
  console.log(`AG-UI Endpoints:`);
  console.log(`  - POST http://localhost:${PORT}/agent/anthropic (Claude Haiku)`);
  console.log(`  - POST http://localhost:${PORT}/agent/openai (GPT-4o Mini)`);
  console.log(`  - POST http://localhost:${PORT}/agent/gemini (Gemini 2.0 Flash)`);
  console.log('Using Vercel AI SDK with AG-UI wrapper');
});
