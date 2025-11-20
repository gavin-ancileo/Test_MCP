#!/usr/bin/env node
#!/usr/bin/env node
import fetch from "node-fetch";
import { createServer } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

const API_BASE = process.env.API_BASE;   // example: https://13jbacli2e.execute-api.ap-southeast-1.amazonaws.com
const ID_TOKEN = process.env.ID_TOKEN;   // Cognito initiate-auth
const AUTH_SERVICE_URL = process.env.AUTH_SERVICE_URL; // e.g. https://<lambda-url>/prod

let ID_TOKEN = null;  // cache tạm

async function getToken() {
  if (!AUTH_SERVICE_URL) throw new Error("AUTH_SERVICE_URL not configured");
  const resp = await fetch(AUTH_SERVICE_URL);
  if (!resp.ok) throw new Error(`Auth service failed: ${resp.status}`);
  const data = await resp.json();
  ID_TOKEN = data.id_token;
  return ID_TOKEN;
}

async function callAPI(path, method = "GET", body = null) {
  if (!ID_TOKEN) await getToken();
  const resp = await fetch(`${API_BASE}${path}`, {
    method,
    headers: {
      "Authorization": ID_TOKEN,
      "Content-Type": "application/json",
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!resp.ok) {
    const err = await resp.text();
    throw new Error(`API error ${resp.status}: ${err}`);
  }
  return resp.json();
}

// Start MCP server
const server = createServer(
  {
    name: "aap-bridge",
    version: "1.0.0",
  },
  {
    // Claude asks for tools list
    "tools/list": async () => {
      const data = await callAPI("/mcp/tools");
      return { tools: data.tools };   // trả tools y chang BE
    },

    // Claude invokes tool
    "tools/invoke": async ({ name, arguments: args }) => {
      const data = await callAPI(`/mcp/tools/${name}/invoke`, "POST", args);
      return { result: data };  
    }
  }
);

const transport = new StdioServerTransport();
await server.connect(transport);

