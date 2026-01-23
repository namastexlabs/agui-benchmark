/**
 * Mastra Agent with AG-UI Protocol Support (NATIVE)
 * Port: 7778
 * Endpoint: POST /agent
 *
 * Uses @ag-ui/mastra package for native AG-UI integration.
 */

import 'dotenv/config';
import express, { Request, Response } from 'express';
import { Agent } from '@mastra/core/agent';
import { Mastra } from '@mastra/core';
import { MastraAgent } from '@ag-ui/mastra';
import { createTool } from '@mastra/core/tools';
import { z } from 'zod';
import { Observable } from 'rxjs';

const app = express();
app.use(express.json());

// Define tools using Mastra's createTool
const getCurrentTime = createTool({
  id: 'get_current_time',
  description: 'Get the current date and time',
  inputSchema: z.object({}),
  outputSchema: z.string(),
  execute: async () => {
    return new Date().toISOString().replace('T', ' ').substring(0, 19);
  },
});

const calculator = createTool({
  id: 'calculator',
  description: 'Evaluate a mathematical expression',
  inputSchema: z.object({
    expression: z.string().describe("A math expression like '2 + 2' or '10 * 5'"),
  }),
  outputSchema: z.string(),
  execute: async ({ context }) => {
    const expression = context.expression;
    try {
      const allowedChars = new Set('0123456789+-*/.() ');
      if ([...expression].every((c: string) => allowedChars.has(c))) {
        const result = eval(expression);
        return `${expression} = ${result}`;
      }
      return 'Invalid expression - only basic math allowed';
    } catch (e) {
      return `Error: ${e}`;
    }
  },
});

// Create Mastra agent
const assistant = new Agent({
  id: 'mastra-assistant',
  name: 'Mastra Assistant',
  instructions: `You are a helpful assistant running on the Mastra framework.
    You can tell the current time and do basic math calculations.
    Be concise and friendly in your responses.`,
  model: {
    provider: 'ANTHROPIC',
    name: 'claude-haiku-4-5-20251001',
  },
  tools: {
    get_current_time: getCurrentTime,
    calculator: calculator,
  },
});

// Create Mastra instance
const mastra = new Mastra({
  agents: {
    assistant,
  },
});

// Create AG-UI MastraAgent wrapper
const aguiAgent = new MastraAgent({
  name: 'mastra-assistant',
  description: 'Mastra test agent with AG-UI support',
  agent: assistant,
});

// AG-UI endpoint
app.post('/agent', async (req: Request, res: Response) => {
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');

  try {
    const input = req.body;

    // Run the agent and stream events
    const eventStream: Observable<any> = aguiAgent.run(input);

    eventStream.subscribe({
      next: (event) => {
        res.write(`data: ${JSON.stringify(event)}\n\n`);
      },
      error: (err) => {
        console.error('Stream error:', err);
        res.write(`data: ${JSON.stringify({ type: 'RUN_ERROR', message: String(err) })}\n\n`);
        res.end();
      },
      complete: () => {
        res.end();
      },
    });
  } catch (error) {
    console.error('Error:', error);
    res.write(`data: ${JSON.stringify({ type: 'RUN_ERROR', message: String(error) })}\n\n`);
    res.end();
  }
});

app.get('/health', (_req: Request, res: Response) => {
  res.json({
    status: 'healthy',
    framework: 'mastra',
    port: 7778,
    agui_endpoint: '/agent',
    native_agui: true,
  });
});

app.get('/', (_req: Request, res: Response) => {
  res.json({
    name: 'Mastra AG-UI Test Agent',
    framework: 'mastra',
    agui_endpoint: 'POST /agent',
    health_endpoint: 'GET /health',
    native_agui: true,
  });
});

const PORT = 7778;
app.listen(PORT, () => {
  console.log(`Starting Mastra Agent on port ${PORT}...`);
  console.log(`AG-UI Endpoint: POST http://localhost:${PORT}/agent`);
  console.log('Using NATIVE @ag-ui/mastra package');
});
