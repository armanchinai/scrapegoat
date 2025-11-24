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
    CompletionItemKind,
    HoverParams,
    MarkupKind,
    MarkupContent
} from 'vscode-languageserver/node'
import { TextDocument } from 'vscode-languageserver-textdocument'

const connection = createConnection(ProposedFeatures.all)
const documents: TextDocuments<TextDocument> = new TextDocuments(TextDocument)

connection.onInitialize((_params: InitializeParams): InitializeResult => {
    return {
        capabilities: {
            textDocumentSync: TextDocumentSyncKind.Incremental,
            completionProvider: { resolveProvider: true },
            hoverProvider: true
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

connection.onHover((params: HoverParams) => {
    const doc = documents.get(params.textDocument.uri)
    if (!doc) return null

    const word = getWordAt(doc.getText(), params.position)
    if (!word) return null

    const hoverContent: Record<string, MarkupContent> = {
        VISIT: { kind: MarkupKind.Markdown, value: "Load the HTML DOM contents from a URL into the program. This is the starting point for scraping; all scripts will start from the root HTML tag unless rebased with a SELECT." },
        SCRAPE: { kind: MarkupKind.Markdown, value: "Select elements from the current page. Use this to gather raw elements you want to process or extract data from." },
        SELECT: { kind: MarkupKind.Markdown, value: "Narrow or rebase your focus to a subset of elements. Used in place of a conditional IN, where the condition needs to be applied to the parent element rather than the child." },
        EXTRACT: { kind: MarkupKind.Markdown, value: "Pull specific attributes or content from the selected elements, such as id, class, or text content, to store or output later." },
        OUTPUT: { kind: MarkupKind.Markdown, value: "Write scraped or extracted data to a file in a specified format (CSV or JSON). Supports custom filenames and file paths." },
        IF: { kind: MarkupKind.Markdown, value: "Create a conditional to filter elements during scraping. Use IF statements to scrape elements only when specific conditions are met." },
        IN: { kind: MarkupKind.Markdown, value: "Apply a condition to filter elements during scraping. USE IN to scrape elements only when specific position conditions are met." },
        POSITION: { kind: MarkupKind.Markdown, value: "Refers to the index of the current element within the selection. Useful for targeting specific elements based on their order. POSITION can only be used with IN conditional statements." },
        CSV: { kind: MarkupKind.Markdown, value: "Comma-Separated Values format. A simple text format for tabular data, where each line represents a row and each value is separated by a comma." },
        JSON: { kind: MarkupKind.Markdown, value: "JavaScript Object Notation format. A lightweight data-interchange format that is easy for humans to read and write, and easy for machines to parse and generate." }
    }

    if (hoverContent[word]) {
        return { contents: hoverContent[word] }
    }

    return null
})

function getWordAt(text: string, position: { line: number; character: number }) {
    const lines = text.split(/\r?\n/)
    const line = lines[position.line]
    if (!line) return null

    const left = line.slice(0, position.character).match(/[A-Z]+$/)?.[0]
    const right = line.slice(position.character).match(/^[A-Z]+/)?.[0]
    return (left || "") + (right || "")
}

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

documents.onDidChangeContent(change => {
    const text = change.document.getText()
    const diagnostics: Diagnostic[] = []

    const lines = text.split(/\r?\n/)
    let state = 0

    const resetState = () => { state = 0 }

    const isCommand = (word: string) =>
        ["SELECT", "SCRAPE", "EXTRACT", "OUTPUT"].includes(word)

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim()
        if (!line) continue
        if (line.startsWith("[") && line.endsWith("]")) {
            resetState() // New query block
            continue
        }
        if (/^!Goatspeak:?/.test(line)) continue

        const firstWord = line.split(/\s+/)[0]
        if (!isCommand(firstWord)) continue

        switch (firstWord) {
            case "SELECT":
                if (state !== 0) {
                    diagnostics.push({
                        severity: DiagnosticSeverity.Error,
                        range: { start: { line: i, character: 0 }, end: { line: i, character: line.length } },
                        message: "SELECT can only appear at the start of a query.",
                        source: "goat-lsp"
                    })
                }
                state = 1
                break

            case "SCRAPE":
                if (![0,1,2].includes(state)) {
                    diagnostics.push({
                        severity: DiagnosticSeverity.Error,
                        range: { start: { line: i, character: 0 }, end: { line: i, character: line.length } },
                        message: "SCRAPE must follow start, SELECT, or another SCRAPE.",
                        source: "goat-lsp"
                    })
                }
                state = 2
                break

            case "EXTRACT":
                if (state !== 2) {
                    diagnostics.push({
                        severity: DiagnosticSeverity.Error,
                        range: { start: { line: i, character: 0 }, end: { line: i, character: line.length } },
                        message: "EXTRACT must follow at least one SCRAPE.",
                        source: "goat-lsp"
                    })
                }
                state = 3
                break

            case "OUTPUT":
                if (![2,3].includes(state)) {
                    diagnostics.push({
                        severity: DiagnosticSeverity.Error,
                        range: { start: { line: i, character: 0 }, end: { line: i, character: line.length } },
                        message: "OUTPUT must follow SCRAPE or EXTRACT.",
                        source: "goat-lsp"
                    })
                }
                state = 4
                break
        }

        // Reset state if next line starts a new SELECT or [query]
        const nextLine = (lines[i+1] || "").trim()
        if (["SELECT"].includes(nextLine.split(/\s+/)[0]) || (nextLine.startsWith("[") && nextLine.endsWith("]"))) {
            resetState()
        }
    }

    connection.sendDiagnostics({ uri: change.document.uri, diagnostics })
})

documents.onDidChangeContent(change => {
    const text = change.document.getText()
    const diagnostics: Diagnostic[] = []

    const lines = text.split(/\r?\n/)

    let hasVisit = false
    let hasOutput = false
    let visitLine = -1

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim()
        if (!line) continue
        if (line.startsWith("[") && line.endsWith("]")) continue
        if (/^!Goatspeak:?/.test(line)) continue

        const firstWord = line.split(/\s+/)[0]

        // Track VISIT / OUTPUT for file-level checks
        if (firstWord === "VISIT") {
            hasVisit = true
            if (visitLine === -1) visitLine = i
        }
        if (firstWord === "OUTPUT") {
            hasOutput = true
        }

        // Ensure VISIT happens before any other command
        const otherCommands = ["SELECT", "SCRAPE", "EXTRACT"]
        if (otherCommands.includes(firstWord) && !hasVisit) {
            diagnostics.push({
                severity: DiagnosticSeverity.Error,
                range: { start: { line: i, character: 0 }, end: { line: i, character: line.length } },
                message: "You must have a VISIT command before running any other commands.",
                source: "goat-lsp"
            })
        }
    }

    // File-level warnings / errors
    if (!hasVisit) {
        diagnostics.push({
            severity: DiagnosticSeverity.Error,
            range: { start: { line: 0, character: 0 }, end: { line: 0, character: 0 } },
            message: "File must include at least one VISIT command.",
            source: "goat-lsp"
        })
    }

    if (!hasOutput) {
        diagnostics.push({
            severity: DiagnosticSeverity.Warning,
            range: { start: { line: 0, character: 0 }, end: { line: 0, character: 0 } },
            message: "File does not include any OUTPUT command. No results will be saved.",
            source: "goat-lsp"
        })
    }

    connection.sendDiagnostics({ uri: change.document.uri, diagnostics })
})




documents.listen(connection)
connection.listen()
