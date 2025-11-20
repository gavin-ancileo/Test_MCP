#!/usr/bin/env node
/**
 * Google Drive MCP Server with Multi-User OAuth Support
 *
 * Architecture:
 * - Spawned per-request with user's OAuth token in environment
 * - Uses official Google APIs Node.js client library
 * - Implements MCP protocol using @modelcontextprotocol/sdk
 * - STDIO transport for communication with Agent API
 *
 * Environment Variables:
 * - GOOGLE_DRIVE_ACCESS_TOKEN (required): User's OAuth access token
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { google } from 'googleapis';

// Validate environment
const ACCESS_TOKEN = process.env.GOOGLE_DRIVE_ACCESS_TOKEN;
if (!ACCESS_TOKEN) {
  console.error('ERROR: GOOGLE_DRIVE_ACCESS_TOKEN environment variable is required');
  process.exit(1);
}

// Initialize Google Drive client with user's OAuth token
const oauth2Client = new google.auth.OAuth2();
oauth2Client.setCredentials({ access_token: ACCESS_TOKEN });
const drive = google.drive({ version: 'v3', auth: oauth2Client });

// Create MCP server
const server = new Server(
  {
    name: 'drive-mcp-server',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'drive_list_files',
        description: 'List files in Google Drive with optional filtering',
        inputSchema: {
          type: 'object',
          properties: {
            query: {
              type: 'string',
              description: 'Optional Google Drive query (e.g., "name contains \'report\'")'
            },
            page_size: {
              type: 'number',
              description: 'Number of results to return (default: 10, max: 100)',
              default: 10
            },
            folder_id: {
              type: 'string',
              description: 'Optional folder ID to list files from specific folder'
            },
          },
        },
      },
      {
        name: 'drive_search_files',
        description: 'Search for files in Google Drive by name or content',
        inputSchema: {
          type: 'object',
          properties: {
            query: {
              type: 'string',
              description: 'Search query - searches in file names and content'
            },
            max_results: {
              type: 'number',
              description: 'Maximum number of results (default: 50)',
              default: 50
            },
          },
          required: ['query'],
        },
      },
      {
        name: 'drive_read_file',
        description: 'Read file content from Google Drive. Handles Google Workspace files (Docs, Sheets) and regular files.',
        inputSchema: {
          type: 'object',
          properties: {
            file_id: {
              type: 'string',
              description: 'Google Drive file ID'
            },
          },
          required: ['file_id'],
        },
      },
      {
        name: 'drive_create_file',
        description: 'Create a new file in Google Drive',
        inputSchema: {
          type: 'object',
          properties: {
            name: {
              type: 'string',
              description: 'File name'
            },
            mime_type: {
              type: 'string',
              description: 'MIME type (default: text/plain)',
              default: 'text/plain'
            },
            content: {
              type: 'string',
              description: 'File content (for text files)'
            },
            parent_folder_id: {
              type: 'string',
              description: 'Optional parent folder ID'
            },
          },
          required: ['name'],
        },
      },
      {
        name: 'drive_update_file',
        description: 'Update an existing file in Google Drive',
        inputSchema: {
          type: 'object',
          properties: {
            file_id: {
              type: 'string',
              description: 'File ID to update'
            },
            content: {
              type: 'string',
              description: 'New file content'
            },
          },
          required: ['file_id', 'content'],
        },
      },
      {
        name: 'drive_export_file',
        description: 'Export Google Workspace files (Docs, Sheets, Slides, Forms, Drawings) to other formats',
        inputSchema: {
          type: 'object',
          properties: {
            file_id: {
              type: 'string',
              description: 'File ID to export'
            },
            mime_type: {
              type: 'string',
              description: 'Export MIME type (e.g., application/pdf, text/plain, text/csv)',
              default: 'application/pdf'
            },
          },
          required: ['file_id'],
        },
      },
      {
        name: 'drive_api_call',
        description: 'Universal Google Drive API v3 caller for advanced operations',
        inputSchema: {
          type: 'object',
          properties: {
            endpoint: {
              type: 'string',
              description: 'API endpoint (e.g., "files", "files/{fileId}", "files/{fileId}/permissions")'
            },
            method: {
              type: 'string',
              enum: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
              default: 'GET',
              description: 'HTTP method'
            },
            params: {
              type: 'object',
              description: 'Query parameters (e.g., {q: "name contains \'test\'", fields: "files(id,name)"})'
            },
            body: {
              type: 'object',
              description: 'Request body for POST/PUT/PATCH operations'
            },
          },
          required: ['endpoint'],
        },
      },
    ],
  };
});

// Handle tool execution
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  // Ensure args is defined
  if (!args) {
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            error: 'No arguments provided',
            tool: name,
          }, null, 2),
        },
      ],
      isError: true,
    };
  }

  try {
    switch (name) {
      case 'drive_list_files': {
        const query = args.query as string | undefined;
        const pageSize = Math.min((args.page_size as number) || 10, 100);
        const folderId = args.folder_id as string | undefined;

        const params: any = {
          pageSize,
          fields: 'files(id,name,mimeType,modifiedTime,size)',
        };

        // Build query - wrap simple keyword in Drive query syntax (match Python wrapper behavior)
        const queryParts: string[] = [];
        if (query) {
          queryParts.push(`name contains '${query}'`);
        }
        if (folderId) {
          queryParts.push(`'${folderId}' in parents`);
        }
        // Google Drive API excludes trashed files by default

        if (queryParts.length > 0) {
          params.q = queryParts.join(' and ');
        }

        const response = await drive.files.list(params);
        const files = response.data.files || [];

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify({
                files,
                count: files.length,
                query: params.q
              }, null, 2),
            },
          ],
        };
      }

      case 'drive_search_files': {
        const query = args.query as string;
        const maxResults = Math.min((args.max_results as number) || 50, 100);

        // Search in both name and full text content
        const searchQuery = `name contains '${query}' or fullText contains '${query}'`;

        const response = await drive.files.list({
          q: searchQuery,
          pageSize: maxResults,
          fields: 'files(id,name,mimeType,modifiedTime)',
        });

        const files = response.data.files || [];

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify({
                files,
                count: files.length,
                search_query: query
              }, null, 2),
            },
          ],
        };
      }

      case 'drive_read_file': {
        const fileId = args.file_id as string;

        // Get file metadata first
        const metadata = await drive.files.get({
          fileId,
          fields: 'id,name,mimeType,size',
        });

        const mimeType = metadata.data.mimeType || '';
        let content: string;
        let contentType: string;

        // Handle Google Workspace files - need export
        if (mimeType.startsWith('application/vnd.google-apps')) {
          let exportMimeType = 'text/plain';

          if (mimeType.includes('document')) {
            exportMimeType = 'text/plain';
            contentType = 'text/plain';
          } else if (mimeType.includes('spreadsheet')) {
            exportMimeType = 'text/csv';
            contentType = 'text/csv';
          } else if (mimeType.includes('presentation')) {
            exportMimeType = 'application/pdf';
            contentType = 'application/pdf';
          } else if (mimeType.includes('drawing')) {
            exportMimeType = 'application/pdf';
            contentType = 'application/pdf';
          } else if (mimeType.includes('form')) {
            // Forms need special handling - export as ZIP
            exportMimeType = 'application/zip';
            contentType = 'application/zip';
          } else {
            exportMimeType = 'text/plain';
            contentType = 'text/plain';
          }

          const exportResponse = await drive.files.export({
            fileId,
            mimeType: exportMimeType,
          });

          content = exportResponse.data as string;
        } else {
          // Download regular files
          const fileResponse = await drive.files.get({
            fileId,
            alt: 'media',
          }, { responseType: 'text' });

          content = fileResponse.data as string;
          contentType = mimeType;
        }

        // Limit content size for response
        const maxContentLength = 50000;
        const truncated = content.length > maxContentLength;
        const displayContent = truncated ? content.substring(0, maxContentLength) : content;

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify({
                file_id: fileId,
                name: metadata.data.name,
                mime_type: mimeType,
                size: metadata.data.size,
                content: displayContent,
                content_length: content.length,
                truncated,
              }, null, 2),
            },
          ],
        };
      }

      case 'drive_create_file': {
        const name = args.name as string;
        const mimeType = (args.mime_type as string) || 'text/plain';
        const content = (args.content as string) || '';
        const parentFolderId = args.parent_folder_id as string | undefined;

        const fileMetadata: any = { name, mimeType };
        if (parentFolderId) {
          fileMetadata.parents = [parentFolderId];
        }

        const media = {
          mimeType,
          body: content,
        };

        const response = await drive.files.create({
          requestBody: fileMetadata,
          media,
          fields: 'id,name,mimeType,webViewLink',
        });

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify({
                ...response.data,
                success: true,
                message: `File "${name}" created successfully`
              }, null, 2),
            },
          ],
        };
      }

      case 'drive_update_file': {
        const fileId = args.file_id as string;
        const content = args.content as string;

        // Get file metadata to preserve MIME type
        const metadata = await drive.files.get({
          fileId,
          fields: 'mimeType',
        });

        const media = {
          mimeType: metadata.data.mimeType || 'text/plain',
          body: content,
        };

        const response = await drive.files.update({
          fileId,
          media,
          fields: 'id,name,modifiedTime',
        });

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify({
                ...response.data,
                success: true,
                message: `File updated successfully`
              }, null, 2),
            },
          ],
        };
      }

      case 'drive_export_file': {
        const fileId = args.file_id as string;
        const exportMimeType = (args.mime_type as string) || 'application/pdf';

        // Get file metadata first to validate
        const metadata = await drive.files.get({
          fileId,
          fields: 'id,name,mimeType',
        });

        const sourceMimeType = metadata.data.mimeType || '';

        // Validate that file is exportable (Google Workspace file)
        if (!sourceMimeType.startsWith('application/vnd.google-apps')) {
          return {
            content: [
              {
                type: 'text',
                text: JSON.stringify({
                  error: 'File is not a Google Workspace file and cannot be exported',
                  file_id: fileId,
                  mime_type: sourceMimeType,
                  suggestion: 'Use drive_read_file to download regular files'
                }, null, 2),
              },
            ],
            isError: true,
          };
        }

        const response = await drive.files.export({
          fileId,
          mimeType: exportMimeType,
        });

        const content = response.data as string;
        const maxContentLength = 50000;
        const truncated = content.length > maxContentLength;
        const displayContent = truncated ? content.substring(0, maxContentLength) : content;

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify({
                file_id: fileId,
                file_name: metadata.data.name,
                source_mime_type: sourceMimeType,
                export_mime_type: exportMimeType,
                content: displayContent,
                content_size: content.length,
                truncated,
                success: true
              }, null, 2),
            },
          ],
        };
      }

      case 'drive_api_call': {
        const endpoint = (args.endpoint as string).replace(/^\//, '');
        const method = ((args.method as string) || 'GET').toUpperCase();
        const params = (args.params as any) || {};
        const body = (args.body as any) || {};

        // Basic endpoint routing
        // This is a simplified implementation - you can expand based on needs
        let response: any;

        if (endpoint.startsWith('files')) {
          if (method === 'GET') {
            response = await drive.files.list(params);
          } else if (method === 'POST') {
            response = await drive.files.create({
              requestBody: body,
              ...params
            });
          } else if (method === 'PATCH' && params.fileId) {
            response = await drive.files.update({
              fileId: params.fileId,
              requestBody: body,
            });
          } else if (method === 'DELETE' && params.fileId) {
            response = await drive.files.delete({
              fileId: params.fileId,
            });
          } else {
            throw new Error(`Unsupported method ${method} for endpoint ${endpoint}`);
          }
        } else {
          throw new Error(`Unsupported endpoint: ${endpoint}`);
        }

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify({
                endpoint,
                method,
                status_code: 200,
                data: response.data,
                success: true,
              }, null, 2),
            },
          ],
        };
      }

      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error: any) {
    // Enhanced error handling
    const errorMessage = error.message || 'Unknown error';
    const errorCode = error.code || error.status || 'UNKNOWN_ERROR';

    // Log error to stderr (for debugging)
    console.error(`[Drive MCP] Error executing ${name}:`, errorMessage);

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            error: errorMessage,
            code: errorCode,
            tool: name,
            details: error.errors || [],
          }, null, 2),
        },
      ],
      isError: true,
    };
  }
});

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);

  // Log to stderr so it doesn't interfere with STDIO protocol
  console.error('[Drive MCP] Server started successfully');
}

// Error handling
main().catch((error) => {
  console.error('[Drive MCP] Fatal error:', error);
  process.exit(1);
});
