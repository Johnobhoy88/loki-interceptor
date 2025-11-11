/**
 * Core Editor Types
 */

export interface EditorDocument {
  id: string;
  content: string;
  title: string;
  language: string;
  version: number;
  createdAt: Date;
  updatedAt: Date;
  metadata?: DocumentMetadata;
}

export interface DocumentMetadata {
  author?: string;
  tags?: string[];
  description?: string;
  customFields?: Record<string, any>;
}

export interface Correction {
  id: string;
  type: CorrectionType;
  range: CorrectionRange;
  original: string;
  corrected: string;
  explanation: string;
  confidence: number;
  category: string;
  status: CorrectionStatus;
  metadata?: CorrectionMetadata;
}

export type CorrectionType =
  | 'grammar'
  | 'spelling'
  | 'style'
  | 'punctuation'
  | 'clarity'
  | 'consistency'
  | 'compliance'
  | 'accessibility';

export type CorrectionStatus = 'pending' | 'accepted' | 'rejected' | 'ignored';

export interface CorrectionRange {
  startLine: number;
  startColumn: number;
  endLine: number;
  endColumn: number;
  startOffset?: number;
  endOffset?: number;
}

export interface CorrectionMetadata {
  rule?: string;
  severity?: 'error' | 'warning' | 'info' | 'suggestion';
  source?: string;
  fixable?: boolean;
  links?: string[];
}

export interface DiffChange {
  type: 'insert' | 'delete' | 'modify';
  lineNumber: number;
  oldText?: string;
  newText?: string;
  corrections?: Correction[];
}

export interface DocumentVersion {
  id: string;
  documentId: string;
  version: number;
  content: string;
  timestamp: Date;
  author?: string;
  message?: string;
  corrections?: Correction[];
}

export interface EditorConfig {
  theme: 'light' | 'dark' | 'high-contrast';
  fontSize: number;
  fontFamily: string;
  lineHeight: number;
  tabSize: number;
  wordWrap: boolean;
  minimap: boolean;
  lineNumbers: boolean;
  autoSave: boolean;
  autoSaveDelay: number;
  suggestOnTriggerCharacters: boolean;
  quickSuggestions: boolean;
  accessibilitySupport: 'auto' | 'on' | 'off';
}

export interface SearchOptions {
  query: string;
  caseSensitive: boolean;
  wholeWord: boolean;
  regex: boolean;
  replaceText?: string;
}

export interface ExportOptions {
  format: 'docx' | 'pdf' | 'html' | 'txt' | 'markdown';
  includeMetadata: boolean;
  includeCorrections: boolean;
  highlightCorrections: boolean;
}

export interface EditorState {
  document: EditorDocument | null;
  corrections: Correction[];
  selectedCorrection: Correction | null;
  versions: DocumentVersion[];
  currentVersion: number;
  isModified: boolean;
  isSaving: boolean;
  config: EditorConfig;
  searchResults: SearchResult[];
  currentSearchIndex: number;
}

export interface SearchResult {
  range: CorrectionRange;
  text: string;
  context: string;
}

export interface KeyboardShortcut {
  key: string;
  ctrl?: boolean;
  shift?: boolean;
  alt?: boolean;
  meta?: boolean;
  action: string;
  description: string;
}

export interface EditorAction {
  type: string;
  payload?: any;
}

export interface HistoryEntry {
  timestamp: Date;
  action: EditorAction;
  beforeState: string;
  afterState: string;
}
