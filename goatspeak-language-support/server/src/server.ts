import {
    createConnection,
    TextDocuments,
    Diagnostic,
    DiagnosticSeverity,
    ProposedFeatures,
    InitializeParams,
    TextDocumentSyncKind,
    InitializeResult,
    CompletionItem,
    CompletionItemKind
} from 'vscode-languageserver/node'
import { TextDocument } from 'vscode-languageserver-textdocument'

const connection = createConnection(ProposedFeatures.all)
const documents: TextDocuments<TextDocument> = new TextDocuments(TextDocument)

connection.onInitialize((_params: InitializeParams): InitializeResult => {
    return {
        capabilities: {
            textDocumentSync: TextDocumentSyncKind.Incremental,
            completionProvider: { resolveProvider: true }
        }
    }
})

// --- Completion suggestions ---
connection.onCompletion((_textDocumentPosition): CompletionItem[] => {
    return [
        { label: 'VISIT', kind: CompletionItemKind.Keyword },
        { label: 'SCRAPE', kind: CompletionItemKind.Keyword },
        { label: 'EXTRACT', kind: CompletionItemKind.Keyword },
        { label: 'OUTPUT', kind: CompletionItemKind.Keyword },
        { label: 'CSV', kind: CompletionItemKind.Constant },
        { label: 'JSON', kind: CompletionItemKind.Constant },
        { label: 'IN', kind: CompletionItemKind.Keyword },
        { label: 'IF', kind: CompletionItemKind.Keyword }
    ]
})

// Provide details when the client requests completionItem/resolve
connection.onCompletionResolve((item: CompletionItem): CompletionItem => {
    // Add helpful details/documentation for a few items
    switch (String(item.label)) {
        case 'CSV':
            item.detail = 'CSV output format';
            item.documentation = 'Outputs results as comma-separated values.';
            break;
        case 'JSON':
            item.detail = 'JSON output format';
            item.documentation = 'Outputs results as JSON.';
            break;
        case 'VISIT':
            item.detail = 'VISIT keyword';
            item.documentation = 'Begin visiting a URL or list of URLs.';
            break;
        case 'IF':
            item.detail = 'IF statement';
            item.documentation = 'Conditional branch.';
            break;
        default:
            // Return the item unmodified for other labels
            break;
    }
    return item
})

// --- Diagnostics: warn if line doesn't end with ; ---
documents.onDidChangeContent(change => {
    const text = change.document.getText()
    const diagnostics: Diagnostic[] = []

    const lines = text.split(/\r?\n/)

    lines.forEach((line, i) => {
        const trimmed = line.trim()
        if (!trimmed) return

        // Skip full-line comments
        if (trimmed.startsWith("[") && trimmed.endsWith("]")) return
        if (/^!Goatspeak:?/.test(trimmed)) return // <-- handles !Goatspeak or !Goatspeak:
        
        // Strip inline comments outside quotes
        let inSingleQuote = false
        let inDoubleQuote = false
        let codeOnly = ""

        for (let j = 0; j < line.length; j++) {
            const char = line[j]

            // Track quote state
            if (char === '"' && !inSingleQuote) inDoubleQuote = !inDoubleQuote
            if (char === "'" && !inDoubleQuote) inSingleQuote = !inSingleQuote

            // Start of inline comment outside quotes
            if (!inSingleQuote && !inDoubleQuote && char === '/' && line[j + 1] === '/') break

            codeOnly += char
        }

        const finalCode = codeOnly.trim()
        if (!finalCode) return

        // Check semicolon
        if (!finalCode.endsWith(";")) {
            diagnostics.push({
                severity: DiagnosticSeverity.Warning,
                range: {
                    start: { line: i, character: 0 },
                    end: { line: i, character: line.length }
                },
                message: "Missing semicolon at end of line",
                source: "goat-lsp"
            })
        }
    })

    connection.sendDiagnostics({ uri: change.document.uri, diagnostics })
})

documents.listen(connection)
connection.listen()
